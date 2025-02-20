# python-proxy-headers

## urllib3

ProxyManager inherits from PoolManager, __init__ accepts proxy_headers kwarg, puts into connection_pool_kw

PoolManager passes connection_pool_kw as kwargs into HTTPSConnectionPool (HTTPConnectionPool just adds them to normal headers)

//urlopen() creates conn through multiple calls ending up in _new_pool()

HTTPSConnectionPool __init__() receives _proxy_headers kwarg
in _prepare_proxy(), passes self.proxy_headers to HTTPSConnection.set_tunnel() as headers
_prepare_proxy() is called in HTTPConnectionPool.urlopen() with conn
conn is created in _new_conn() using ConnectionCls
_new_conn() is called by _get_conn()
HTTPSConnectionPool sets ConnectionCls to HTTPSConnection

HTTPSConnection inherits from HTTPConnection
HTTPConnection inherits from http.client.HTTPConnection
HTTPConnection.set_tunnel() is simple wrapper around http.client.HTTPConnection.set_tunnel()
HTTPConnection defines own _tunnel() method for python < 3.11.4
_tunnel() is called by connect()

response headers are only available within _tunnel() method, set_tunnel() only sets the proxy headers

## http.client is python stdlib

HTTPConnection.set_tunnel() receives headers, stores for passing in CONNECT method in _tunnel()

in python3.12, _tunnel() reads proxy headers, saves them in _raw_proxy_headers
can get _raw_proxy_headers using get_proxy_response_headers()

for older python, need to patch _tunnel() to get response headers

## TODO
1. figure easiest urllib3 based method to pass in proxy_headers for requests
``` python
import urllib3
proxy = urllib3.ProxyManager('http://de.proxymesh.com:31280', proxy_headers={'X-ProxyMesh-IP': '165.232.115.32'})
r = proxy.request('GET', 'https://proxymesh.com/api/headers/')
# NOTE that when using this method, even without proxy_headers, the proxymesh proxy might still keep the same IP
# because urllib3 by default re-uses the connection
```
2. potentially create helper method(s) for doing this
3. figure out how to patch or extend urllib3 ProxyManager to get proxy response headers in python3.12
``` python
from python_proxy_headers import connection
proxy = connection.ProxyHeaderManager('http://de.proxymesh.com:31280', proxy_headers={'X-ProxyMesh-IP': '46.101.181.63'})
r = proxy.request('GET', 'https://proxymesh.com/api/headers/')
r.headers['X-ProxyMesh-IP']
```
4. figure out how to do create equivalent functionality for older pythons
	* tested with python3.7 & urllib3 1.26.20
	* tested with python3.12 & urllib3 2.3.0
5. figure out how python requests uses urllib3 and easiest method for passing in proxy headers
6. potentially create helper methods for doing this
``` python
from python_proxy_headers import adapter
r = adapter.get('https://proxymesh.com/api/headers/', proxies={'http': 'http://de.proxymesh.com:31280', 'https': 'http://de.proxymesh.com:31280'}, proxy_headers={'x-proxymesh-ip': '46.101.236.88'})
r.headers['X-ProxyMesh-IP']
```
7. pass proxy response headers from urllib3 functions back to requests response
	* tested on python3.7 & requests 2.31.0
	* tested with python3.12 & requests 2.32.3
8. create adapters/extension for httpx library too