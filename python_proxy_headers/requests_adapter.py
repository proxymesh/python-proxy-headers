from requests.adapters import HTTPAdapter
from requests.sessions import Session
from .urllib3_proxy_manager import proxy_from_url

class HTTPProxyHeaderAdapter(HTTPAdapter):
	def __init__(self, proxy_headers=None):
		super().__init__()
		self._proxy_headers = proxy_headers or {}
	
	def proxy_manager_for(self, proxy, **proxy_kwargs):
		"""Return urllib3 ProxyManager for the given proxy.

		This method should not be called from user code, and is only
		exposed for use when subclassing the
		:class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

		:param proxy: The proxy to return a urllib3 ProxyManager for.
		:param proxy_kwargs: Extra keyword arguments used to configure the Proxy Manager.
		:returns: ProxyManager
		:rtype: urllib3.ProxyManager
		"""
		if proxy in self.proxy_manager:
			manager = self.proxy_manager[proxy]
		elif proxy.lower().startswith("socks"):
			return super().proxy_manager_for(proxy, **proxy_kwargs)
		else:
			# HTTPAdapter.proxy_headers only gets Proxy-Authorization
			_proxy_headers = self.proxy_headers(proxy)
			if self._proxy_headers:
				_proxy_headers.update(self._proxy_headers)
			
			manager = self.proxy_manager[proxy] = proxy_from_url(
				proxy,
				proxy_headers=_proxy_headers,
				num_pools=self._pool_connections,
				maxsize=self._pool_maxsize,
				block=self._pool_block,
				**proxy_kwargs,
			)

		return manager

class ProxySession(Session):
	def __init__(self, proxy_headers=None):
		super().__init__()
		self.mount('https://', HTTPProxyHeaderAdapter(proxy_headers=proxy_headers))
		self.mount('http://', HTTPProxyHeaderAdapter(proxy_headers=proxy_headers))

def request(method, url, proxy_headers=None, **kwargs):
	with ProxySession(proxy_headers) as session:
		return session.request(method=method, url=url, **kwargs)

def get(*args, **kwargs):
	return request('get', *args, **kwargs)

def options(*args, **kwargs):
	return request('options', *args, **kwargs)

def head(*args, **kwargs):
	kwargs.setdefault("allow_redirects", False)
	return request('head', *args, **kwargs)

def post(*args, **kwargs):
	return request('post', *args, **kwargs)

def put(*args, **kwargs):
	return request('put', *args, **kwargs)

def patch(*args, **kwargs):
	return request('patch', *args, **kwargs)

def delete(*args, **kwargs):
	return request('delete', *args, **kwargs)