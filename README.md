# Python Proxy Headers

The `python-proxy-headers` package provides support for handling custom proxy headers when making HTTPS requests in various python modules.

We currently provide extensions to the following packages:

* [urllib3](https://urllib3.readthedocs.io/en/stable/)
* [requests](https://docs.python-requests.org/en/latest/index.html)
* [aiohttp](https://docs.aiohttp.org/en/stable/index.html)
* [httpx](https://www.python-httpx.org/)

None of these modules provide good support for parsing custom response headers from proxy servers. And some of them make it hard to send custom headers to proxy servers. So we at [ProxyMesh](https://proxymesh.com) made these extension modules to support our customers that use Python and want to use custom headers to control our proxy behavior. But these modules can work for handling custom headers with any proxy.

*If you are looking for [Scrapy](https://scrapy.org/) support, please see our [scrapy-proxy-headers](https://github.com/proxymesh/scrapy-proxy-headers) project.*

## Installation

Examples for how to use these extension modules are described below. You must first do the following:

1. `pip install python-proxy-headers`
2. Install the appropriate package based on the python module you want to use.

This package does not have any dependencies because we don't know which module you want to use.

You can also find more example code in our [proxy-examples for python](https://github.com/proxymesh/proxy-examples/tree/main/python).

## urllib3

If you just want to send custom proxy headers, but don't need to receive proxy response headers, then you can [urllib3.ProxyManager](https://urllib3.readthedocs.io/en/stable/reference/urllib3.poolmanager.html#urllib3.ProxyManager), like so:

``` python
import urllib3
proxy = urllib3.ProxyManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-Country': 'US'})
r = proxy.request('GET', 'https://api.ipify.org?format=json')
```

Note that when using this method, if you keep reusing the same `ProxyManager` instance, you may be re-using the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with ProxyMesh you may keep getting the same IP address if you reuse the proxy connection.

To get proxy response headers, use our extension module like this:

``` python
from python_proxy_headers import urllib3_proxy_manager
proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT')
r = proxy.request('GET', 'https://api.ipify.org?format=json')
r.headers['X-ProxyMesh-IP']
```

You can also pass `proxy_headers` into our `ProxyHeaderManager` as well. For example, you can pass back the same `X-ProxyMesh-IP` header to ensure you get the same IP address on subsequent requests.

## requests

The requests adapter builds on our `urllib3_proxy_manager` module to make it easy to pass in proxy headers and receive proxy response headers.

``` python
from python_proxy_headers import requests_adapter
r = requests_adapter.get('https://api.ipify.org?format=json', proxies={'http': 'http://PROXYHOST:PORT', 'https': 'http://PROXYHOST:PORT'}, proxy_headers={'X-ProxyMesh-Country': 'US'})
r.headers['X-ProxyMesh-IP']
```

The `requests_adapter` module supports all the standard requests methods: `get`, `post`, `put`, `delete`, etc.

## aiohttp

While it's not documented, aiohttp does support passing in custom proxy headers by default.

``` python
import aiohttp
async with aiohttp.ClientSession() as session:
	async with session.get('https://api.ipify.org?format=json', proxy="http://PROXYHOST:PORT", proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
		await r.text()
```

However, if you want to get proxy response, you should use our extension module:

``` python
from python_proxy_headers import aiohttp_proxy
async with aiohttp_proxy.ProxyClientSession() as session:
	async with session.get('https://api.ipify.org?format=json', proxy="http://PROXYHOST:PORT", proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
		await r.text()

r.headers['X-ProxyMesh-IP']
```

## httpx

httpx also supports proxy headers by default, though it's not documented:

``` python
import httpx
proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
transport = HTTPProxyTransport(proxy=proxy)
with httpx.Client(mounts={'http://': transort, 'https://': transport}) as client:
	r = client.get('https://api.ipify.org?format=json')
```

But to get the response headers, you need to use our extension module:

``` python
import httpx
from python_proxy_headers.httpx_proxy import HTTPProxyTransport
proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
transport = HTTPProxyTransport(proxy=proxy)
with httpx.Client(mounts={'http://': transort, 'https://': transport}) as client:
	r = client.get('https://api.ipify.org?format=json')

r.headers['X-ProxyMesh-IP']
```

This module also provide helper methods similar to requests:

``` python
import httpx
from python_proxy_headers import httpx_proxy
proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
r.headers['X-ProxyMesh-IP']
```

And finally, httpx supports async requests, so we provide an async extension too:

``` python
import httpx
from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
transport = AsyncHTTPProxyTransport(proxy=proxy)
async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
	r = await client.get('https://api.ipify.org?format=json')

r.headers['X-ProxyMesh-IP']
```

Our httpx helper module internally provides extension classes for [httpcore](https://www.encode.io/httpcore/), for handling proxy headers over tunnel connections.
You can use those classes if you're building on top of httpcore.