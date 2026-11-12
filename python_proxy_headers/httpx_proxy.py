"""CONNECT proxy headers for httpx 0.28.

httpx >= 1 has no httpcore, HTTPTransport, or proxy support. Import warns
instead of crashing, and the helpers raise UnsupportedHttpxVersion.
The [httpx] extra is httpx>=0.28,<1.
"""

import warnings
from contextlib import contextmanager
from typing import Any, Callable, Optional

from .header_utils import filter_connect_headers

_HELPERS = (
	"ProxyTunnelHTTPConnection", "AsyncProxyTunnelHTTPConnection",
	"HTTPProxyHeaders", "AsyncHTTPProxyHeaders",
	"HTTPProxyTransport", "AsyncHTTPProxyTransport",
	"request", "get", "options", "head", "post", "put", "patch", "delete", "stream",
)


class UnsupportedHttpxVersion(RuntimeError):
	"""The installed httpx cannot send or read CONNECT proxy headers."""


def httpx_major(version: Optional[str]) -> Optional[int]:
	"""Numeric major version. ``1.0.dev6`` is 1 and ``0.28.1`` is 0."""
	if not version:
		return None
	digits = ""
	for char in version.strip().split(".", 1)[0]:
		if not char.isdigit():
			break
		digits += char
	return int(digits) if digits else None


def _blocked_httpx_version() -> Optional[str]:
	try:
		import httpx
	except ImportError:
		return None
	version = getattr(httpx, "__version__", None)
	version = version if isinstance(version, str) and version else None
	major = httpx_major(version)
	if major is not None:
		return version if major >= 1 else None
	has_transport = hasattr(httpx, "HTTPTransport") and hasattr(httpx, "AsyncHTTPTransport")
	return None if has_transport else (version or "1")


def _use_httpx_blockers(version: str) -> None:
	"""Warn once, then make the public helpers raise UnsupportedHttpxVersion."""
	message = (
		f"httpx {version} is installed, but python-proxy-headers only supports "
		"httpx>=0.28,<1. httpx 1.0 drops httpcore, HTTPTransport, and proxy "
		"support (https://github.com/encode/httpx/issues/947). "
		"Calling these helpers raises UnsupportedHttpxVersion. "
		"Install a compatible release with pip install 'python-proxy-headers[httpx]'."
	)
	warnings.warn(message, UserWarning, stacklevel=3)

	def raiser(name: str) -> Callable[..., Any]:
		def _raise(*_args: Any, **_kwargs: Any) -> Any:
			raise UnsupportedHttpxVersion(message)

		_raise.__name__ = name
		return _raise

	for name in _HELPERS:
		if name[:1].islower():
			globals()[name] = raiser(name)
			continue
		fn = raiser(name)

		def _init(self: Any, *args: Any, _fn: Callable[..., Any] = fn, **kwargs: Any) -> None:
			_fn(*args, **kwargs)

		cls = type(name, (), {"__init__": _init})
		cls.__module__ = __name__
		globals()[name] = cls


_HTTPX_BLOCKED = _blocked_httpx_version()
if _HTTPX_BLOCKED:
	class _HttpxMissing:
		pass

	HTTPProxy = TunnelHTTPConnection = AsyncHTTPProxy = AsyncTunnelHTTPConnection = _HttpxMissing
	HTTPTransport = AsyncHTTPTransport = URL = _HttpxMissing
	DEFAULT_LIMITS = DEFAULT_TIMEOUT_CONFIG = None
else:
	from httpcore._sync.http_proxy import HTTPProxy, TunnelHTTPConnection, merge_headers, logger
	from httpcore._sync.http11 import HTTP11Connection
	from httpcore._async.http_proxy import AsyncHTTPProxy, AsyncTunnelHTTPConnection
	from httpcore._async.http11 import AsyncHTTP11Connection
	from httpcore._models import URL, Request
	from httpcore._exceptions import ProxyError
	from httpcore._ssl import default_ssl_context
	from httpcore._trace import Trace
	from httpx import AsyncHTTPTransport, HTTPTransport, Client
	from httpx._config import DEFAULT_LIMITS, DEFAULT_TIMEOUT_CONFIG, Proxy, create_ssl_context


class ProxyTunnelHTTPConnection(TunnelHTTPConnection):
	# Unfortunately the only way to get connect_response.headers into the Response
	# is to override this whole method
	def handle_request(self, request):
		timeouts = request.extensions.get("timeout", {})
		timeout = timeouts.get("connect", None)

		with self._connect_lock:
			if not self._connected:
				target = b"%b:%d" % (self._remote_origin.host, self._remote_origin.port)

				connect_url = URL(
					scheme=self._proxy_origin.scheme,
					host=self._proxy_origin.host,
					port=self._proxy_origin.port,
					target=target,
				)
				connect_headers = merge_headers(
					[(b"Host", target), (b"Accept", b"*/*")], self._proxy_headers
				)
				connect_request = Request(
					method=b"CONNECT",
					url=connect_url,
					headers=connect_headers,
					extensions=request.extensions,
				)
				connect_response = self._connection.handle_request(
					connect_request
				)

				if connect_response.status < 200 or connect_response.status > 299:
					reason_bytes = connect_response.extensions.get("reason_phrase", b"")
					reason_str = reason_bytes.decode("ascii", errors="ignore")
					msg = "%d %s" % (connect_response.status, reason_str)
					self._connection.close()
					raise ProxyError(msg)

				stream = connect_response.extensions["network_stream"]

				# Upgrade the stream to SSL
				ssl_context = (
					default_ssl_context()
					if self._ssl_context is None
					else self._ssl_context
				)
				alpn_protocols = ["http/1.1", "h2"] if self._http2 else ["http/1.1"]
				ssl_context.set_alpn_protocols(alpn_protocols)

				kwargs = {
					"ssl_context": ssl_context,
					"server_hostname": self._remote_origin.host.decode("ascii"),
					"timeout": timeout,
				}
				with Trace("start_tls", logger, request, kwargs) as trace:
					stream = stream.start_tls(**kwargs)
					trace.return_value = stream

				# Determine if we should be using HTTP/1.1 or HTTP/2
				ssl_object = stream.get_extra_info("ssl_object")
				http2_negotiated = (
					ssl_object is not None
					and ssl_object.selected_alpn_protocol() == "h2"
				)

				# Create the HTTP/1.1 or HTTP/2 connection
				if http2_negotiated or (self._http2 and not self._http1):
					from httpcore._sync.http2 import HTTP2Connection

					self._connection = HTTP2Connection(
						origin=self._remote_origin,
						stream=stream,
						keepalive_expiry=self._keepalive_expiry,
					)
				else:
					self._connection = HTTP11Connection(
						origin=self._remote_origin,
						stream=stream,
						keepalive_expiry=self._keepalive_expiry,
					)

				self._connect_response_headers = connect_response.headers
				self._connected = True
		# Merge safe CONNECT headers without overwriting origin values
		response = self._connection.handle_request(request)
		response.headers = merge_headers(
			response.headers,
			filter_connect_headers(
				response.headers, getattr(self, "_connect_response_headers", ())
			),
		)
		return response

class AsyncProxyTunnelHTTPConnection(AsyncTunnelHTTPConnection):
	async def handle_async_request(self, request):
		timeouts = request.extensions.get("timeout", {})
		timeout = timeouts.get("connect", None)

		async with self._connect_lock:
			if not self._connected:
				target = b"%b:%d" % (self._remote_origin.host, self._remote_origin.port)

				connect_url = URL(
					scheme=self._proxy_origin.scheme,
					host=self._proxy_origin.host,
					port=self._proxy_origin.port,
					target=target,
				)
				connect_headers = merge_headers(
					[(b"Host", target), (b"Accept", b"*/*")], self._proxy_headers
				)
				connect_request = Request(
					method=b"CONNECT",
					url=connect_url,
					headers=connect_headers,
					extensions=request.extensions,
				)
				connect_response = await self._connection.handle_async_request(
					connect_request
				)

				if connect_response.status < 200 or connect_response.status > 299:
					reason_bytes = connect_response.extensions.get("reason_phrase", b"")
					reason_str = reason_bytes.decode("ascii", errors="ignore")
					msg = "%d %s" % (connect_response.status, reason_str)
					await self._connection.aclose()
					raise ProxyError(msg)

				stream = connect_response.extensions["network_stream"]

				# Upgrade the stream to SSL
				ssl_context = (
					default_ssl_context()
					if self._ssl_context is None
					else self._ssl_context
				)
				alpn_protocols = ["http/1.1", "h2"] if self._http2 else ["http/1.1"]
				ssl_context.set_alpn_protocols(alpn_protocols)

				kwargs = {
					"ssl_context": ssl_context,
					"server_hostname": self._remote_origin.host.decode("ascii"),
					"timeout": timeout,
				}
				async with Trace("start_tls", logger, request, kwargs) as trace:
					stream = await stream.start_tls(**kwargs)
					trace.return_value = stream

				# Determine if we should be using HTTP/1.1 or HTTP/2
				ssl_object = stream.get_extra_info("ssl_object")
				http2_negotiated = (
					ssl_object is not None
					and ssl_object.selected_alpn_protocol() == "h2"
				)

				# Create the HTTP/1.1 or HTTP/2 connection
				if http2_negotiated or (self._http2 and not self._http1):
					from httpcore._async.http2 import AsyncHTTP2Connection

					self._connection = AsyncHTTP2Connection(
						origin=self._remote_origin,
						stream=stream,
						keepalive_expiry=self._keepalive_expiry,
					)
				else:
					self._connection = AsyncHTTP11Connection(
						origin=self._remote_origin,
						stream=stream,
						keepalive_expiry=self._keepalive_expiry,
					)

				self._connect_response_headers = connect_response.headers
				self._connected = True
		# Merge safe CONNECT headers without overwriting origin values
		response = await self._connection.handle_async_request(request)
		response.headers = merge_headers(
			response.headers,
			filter_connect_headers(
				response.headers, getattr(self, "_connect_response_headers", ())
			),
		)
		return response

class HTTPProxyHeaders(HTTPProxy):
	def create_connection(self, origin):
		if origin.scheme == b"http":
			return super().create_connection(origin)
		return ProxyTunnelHTTPConnection(
			proxy_origin=self._proxy_url.origin,
			proxy_headers=self._proxy_headers,
			remote_origin=origin,
			ssl_context=self._ssl_context,
			proxy_ssl_context=self._proxy_ssl_context,
			keepalive_expiry=self._keepalive_expiry,
			http1=self._http1,
			http2=self._http2,
			network_backend=self._network_backend,
		)

class AsyncHTTPProxyHeaders(AsyncHTTPProxy):
	def create_connection(self, origin):
		if origin.scheme == b"http":
			return super().create_connection(origin)
		return AsyncProxyTunnelHTTPConnection(
			proxy_origin=self._proxy_url.origin,
			proxy_headers=self._proxy_headers,
			remote_origin=origin,
			ssl_context=self._ssl_context,
			proxy_ssl_context=self._proxy_ssl_context,
			keepalive_expiry=self._keepalive_expiry,
			http1=self._http1,
			http2=self._http2,
			network_backend=self._network_backend,
		)

# class ProxyConnectionPool(ConnectionPool):
# 	def create_connection(self, origin):
# 		if self._proxy is not None:
# 			if self._proxy.url.scheme in (b"socks5", b"socks5h"):
# 				return super().create_connection(origin)
# 			elif origin.scheme == b"http":
# 				return super().create_connection(origin)
			
# 			return ProxyTunnelHTTPConnection(
# 				proxy_origin=self._proxy.url.origin,
# 				proxy_headers=self._proxy.headers,
# 				proxy_ssl_context=self._proxy.ssl_context,
# 				remote_origin=origin,
# 				ssl_context=self._ssl_context,
# 				keepalive_expiry=self._keepalive_expiry,
# 				http1=self._http1,
# 				http2=self._http2,
# 				network_backend=self._network_backend,
# 			)

# 		return super().create_connection(origin)

class HTTPProxyTransport(HTTPTransport):
	def __init__(
		self,
		verify = True,
		cert = None,
		trust_env: bool = True,
		http1: bool = True,
		http2: bool = False,
		limits = DEFAULT_LIMITS,
		proxy = None,
		uds: str | None = None,
		local_address: str | None = None,
		retries: int = 0,
		socket_options = None,
	) -> None:
		proxy = Proxy(url=proxy) if isinstance(proxy, (str, URL)) else proxy
		ssl_context = create_ssl_context(verify=verify, cert=cert, trust_env=trust_env)

		if proxy and proxy.url.scheme in ("http", "https"):
			self._pool = HTTPProxyHeaders(
				proxy_url=URL(
					scheme=proxy.url.raw_scheme,
					host=proxy.url.raw_host,
					port=proxy.url.port,
					target=proxy.url.raw_path,
				),
				proxy_auth=proxy.raw_auth,
				proxy_headers=proxy.headers.raw,
				ssl_context=ssl_context,
				proxy_ssl_context=proxy.ssl_context,
				max_connections=limits.max_connections,
				max_keepalive_connections=limits.max_keepalive_connections,
				keepalive_expiry=limits.keepalive_expiry,
				http1=http1,
				http2=http2,
				socket_options=socket_options,
			)
		else:
			super().__init__(verify, cert, trust_env, http1, http2, limits, proxy, uds, local_address, retries, socket_options)

class AsyncHTTPProxyTransport(AsyncHTTPTransport):
	def __init__(
		self,
		verify = True,
		cert = None,
		trust_env: bool = True,
		http1: bool = True,
		http2: bool = False,
		limits = DEFAULT_LIMITS,
		proxy = None,
		uds: str | None = None,
		local_address: str | None = None,
		retries: int = 0,
		socket_options = None,
	) -> None:
		proxy = Proxy(url=proxy) if isinstance(proxy, (str, URL)) else proxy
		ssl_context = create_ssl_context(verify=verify, cert=cert, trust_env=trust_env)

		if proxy and proxy.url.scheme in ("http", "https"):
			self._pool = AsyncHTTPProxyHeaders(
				proxy_url=URL(
					scheme=proxy.url.raw_scheme,
					host=proxy.url.raw_host,
					port=proxy.url.port,
					target=proxy.url.raw_path,
				),
				proxy_auth=proxy.raw_auth,
				proxy_headers=proxy.headers.raw,
				proxy_ssl_context=proxy.ssl_context,
				ssl_context=ssl_context,
				max_connections=limits.max_connections,
				max_keepalive_connections=limits.max_keepalive_connections,
				keepalive_expiry=limits.keepalive_expiry,
				http1=http1,
				http2=http2,
				socket_options=socket_options,
			)
		else:
			super().__init__(verify, cert, trust_env, http1, http2, limits, proxy, uds, local_address, retries, socket_options)

def request(method: str,
			url: URL | str,
			*,
			cookies = None,
			proxy = None,
			timeout = DEFAULT_TIMEOUT_CONFIG,
			verify = True,
			trust_env: bool = True,
			**kwargs):
	transport = HTTPProxyTransport(proxy=proxy)
	with Client(
		cookies=cookies,
		verify=verify,
		timeout=timeout,
		trust_env=trust_env,
		mounts={'http://': transport, 'https://': transport}
	) as client:
		return client.request(method=method, url=url, **kwargs)

def get(*args, **kwargs):
	return request('GET', *args, **kwargs)

def options(*args, **kwargs):
	return request('OPTIONS', *args, **kwargs)

def head(*args, **kwargs):
	return request('HEAD', *args, **kwargs)

def post(*args, **kwargs):
	return request('POST', *args, **kwargs)

def put(*args, **kwargs):
	return request('PUT', *args, **kwargs)

def patch(*args, **kwargs):
	return request('PATCH', *args, **kwargs)

def delete(*args, **kwargs):
	return request('DELETE', *args, **kwargs)

@contextmanager
def stream(method: str,
		   url: URL | str,
		   *,
		   cookies = None,
		   proxy = None,
		   timeout = DEFAULT_TIMEOUT_CONFIG,
		   verify = True,
		   trust_env: bool = True,
		   **kwargs):
	transport = HTTPProxyTransport(proxy=proxy)
	with Client(
		cookies=cookies,
		verify=verify,
		timeout=timeout,
		trust_env=trust_env,
		mounts={'http://': transport, 'https://': transport}
	) as client:
		with client.stream(method=method, url=url, **kwargs) as response:
			yield response


if _HTTPX_BLOCKED:
	_use_httpx_blockers(_HTTPX_BLOCKED)
