from http import HTTPStatus
from aiohttp.client_reqrep import ClientRequest, ClientResponse
from aiohttp.connector import TCPConnector, Connection
from aiohttp.client_exceptions import ClientHttpProxyError, ClientProxyConnectionError
from aiohttp.client import ClientSession
from aiohttp.helpers import reify
from aiohttp import hdrs
from multidict import CIMultiDict, CIMultiDictProxy

class ProxyTCPConnector(TCPConnector):
	async def _create_proxy_connection(self, req: ClientRequest, traces, timeout):
		self._fail_on_no_start_tls(req)
		runtime_has_start_tls = self._loop_supports_start_tls()

		headers = {}
		if req.proxy_headers is not None:
			headers = req.proxy_headers  # type: ignore[assignment]
		headers[hdrs.HOST] = req.headers[hdrs.HOST]

		url = req.proxy
		assert url is not None
		proxy_req = ClientRequest(
			hdrs.METH_GET,
			url,
			headers=headers,
			auth=req.proxy_auth,
			loop=self._loop,
			ssl=req.ssl,
		)

		# create connection to proxy server
		transport, proto = await self._create_direct_connection(
			proxy_req, [], timeout, client_error=ClientProxyConnectionError
		)

		auth = proxy_req.headers.pop(hdrs.AUTHORIZATION, None)
		if auth is not None:
			if not req.is_ssl():
				req.headers[hdrs.PROXY_AUTHORIZATION] = auth
			else:
				proxy_req.headers[hdrs.PROXY_AUTHORIZATION] = auth

		if req.is_ssl():
			if runtime_has_start_tls:
				self._warn_about_tls_in_tls(transport, req)

			# For HTTPS requests over HTTP proxy
			# we must notify proxy to tunnel connection
			# so we send CONNECT command:
			#   CONNECT www.python.org:443 HTTP/1.1
			#   Host: www.python.org
			#
			# next we must do TLS handshake and so on
			# to do this we must wrap raw socket into secure one
			# asyncio handles this perfectly
			proxy_req.method = hdrs.METH_CONNECT
			proxy_req.url = req.url
			key = req.connection_key._replace(
				proxy=None, proxy_auth=None, proxy_headers_hash=None
			)
			conn = Connection(self, key, proto, self._loop)
			proxy_resp = await proxy_req.send(conn)
			try:
				protocol = conn._protocol
				assert protocol is not None

				# read_until_eof=True will ensure the connection isn't closed
				# once the response is received and processed allowing
				# START_TLS to work on the connection below.
				protocol.set_response_params(
					read_until_eof=runtime_has_start_tls,
					timeout_ceil_threshold=self._timeout_ceil_threshold,
				)
				resp = await proxy_resp.start(conn)
			except BaseException:
				proxy_resp.close()
				conn.close()
				raise
			else:
				conn._protocol = None
				try:
					if resp.status != 200:
						message = resp.reason
						if message is None:
							message = HTTPStatus(resp.status).phrase
						raise ClientHttpProxyError(
							proxy_resp.request_info,
							resp.history,
							status=resp.status,
							message=message,
							headers=resp.headers,
						)
					if not runtime_has_start_tls:
						rawsock = transport.get_extra_info("socket", default=None)
						if rawsock is None:
							raise RuntimeError(
								"Transport does not expose socket instance"
							)
						# Duplicate the socket, so now we can close proxy transport
						rawsock = rawsock.dup()
				except BaseException:
					# It shouldn't be closed in `finally` because it's fed to
					# `loop.start_tls()` and the docs say not to touch it after
					# passing there.
					transport.close()
					raise
				finally:
					if not runtime_has_start_tls:
						transport.close()

				# TODO: try adding resp.headers to the proto returned as 2nd tuple element below
				if not runtime_has_start_tls:
					# HTTP proxy with support for upgrade to HTTPS
					sslcontext = self._get_ssl_context(req)
					transport, proto = await self._wrap_existing_connection(
						self._factory,
						timeout=timeout,
						ssl=sslcontext,
						sock=rawsock,
						server_hostname=req.host,
						req=req,
					)

				transport, proto = await self._start_tls_connection(
					# Access the old transport for the last time before it's
					# closed and forgotten forever:
					transport,
					req=req,
					timeout=timeout,
				)
			finally:
				proxy_resp.close()

			proto._proxy_headers = resp.headers
		return transport, proto


class ProxyClientRequest(ClientRequest):
	async def send(self, conn):
		resp = await super().send(conn)
		if hasattr(conn.protocol, '_proxy_headers'):
			resp._proxy_headers = conn.protocol._proxy_headers
		return resp

class ProxyClientResponse(ClientResponse):
	@reify
	def headers(self):
		proxy_headers = getattr(self, '_proxy_headers', None)

		if proxy_headers:
			headers = CIMultiDict(self._headers)
			headers.extend(proxy_headers)
			return CIMultiDictProxy(headers)
		else:
			return self._headers

class ProxyClientSession(ClientSession):
	def __init__(self, *args, **kwargs):
		super().__init__(connector=ProxyTCPConnector(), response_class=ProxyClientResponse,request_class=ProxyClientRequest, *args, **kwargs)