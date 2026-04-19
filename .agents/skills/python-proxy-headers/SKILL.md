---
name: python-proxy-headers
description: >-
  Send and receive custom headers during HTTPS CONNECT tunneling in Python.
  Use when integrating proxy headers with requests, httpx, aiohttp, urllib3,
  pycurl, cloudscraper, or autoscraper.
---

# python-proxy-headers

Send custom headers to proxies and receive proxy response headers during HTTPS CONNECT tunneling.

## Installation

```bash
pip install python-proxy-headers
```

Install your HTTP client as needed (requests, httpx, aiohttp, etc.).

## Quick Reference

| Library | Module | Main Class/Function |
|---------|--------|---------------------|
| requests | `python_proxy_headers.requests_adapter` | `ProxySession` |
| httpx | `python_proxy_headers.httpx_proxy` | `get`, `post`, etc. |
| aiohttp | `python_proxy_headers.aiohttp_proxy` | `ProxyClientSession` |
| urllib3 | `python_proxy_headers.urllib3_proxy_manager` | `ProxyHeadersPoolManager` |
| pycurl | `python_proxy_headers.pycurl_proxy` | `set_proxy_headers`, `HeaderCapture` |
| cloudscraper | `python_proxy_headers.cloudscraper_proxy` | `create_scraper` |
| autoscraper | `python_proxy_headers.autoscraper_proxy` | `ProxyAutoScraper` |

## Usage Patterns

### requests

```python
from python_proxy_headers.requests_adapter import ProxySession

with ProxySession(proxy_headers={'X-ProxyMesh-Country': 'US'}) as session:
    session.proxies = {'https': 'http://user:pass@proxy.example.com:8080'}
    response = session.get('https://httpbin.org/ip')
    print(response.headers.get('X-ProxyMesh-IP'))
```

### httpx

```python
from python_proxy_headers.httpx_proxy import get

response = get(
    'https://httpbin.org/ip',
    proxy='http://user:pass@proxy.example.com:8080'
)
print(response.headers.get('X-ProxyMesh-IP'))
```

### aiohttp

```python
import asyncio
from python_proxy_headers.aiohttp_proxy import ProxyClientSession

async def main():
    async with ProxyClientSession() as session:
        async with session.get(
            'https://httpbin.org/ip',
            proxy='http://user:pass@proxy.example.com:8080'
        ) as response:
            print(response.headers.get('X-ProxyMesh-IP'))

asyncio.run(main())
```

### pycurl

```python
import pycurl
from python_proxy_headers.pycurl_proxy import set_proxy_headers, HeaderCapture

c = pycurl.Curl()
c.setopt(pycurl.URL, 'https://httpbin.org/ip')
c.setopt(pycurl.PROXY, 'http://proxy.example.com:8080')

set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})
capture = HeaderCapture(c)

c.perform()
print(capture.proxy_headers)
c.close()
```

### cloudscraper

```python
from python_proxy_headers.cloudscraper_proxy import create_scraper

scraper = create_scraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
scraper.proxies = {'https': 'http://proxy.example.com:8080'}
response = scraper.get('https://example.com')
```

## Proxy Headers

Custom headers sent during CONNECT are proxy-specific. Check your proxy provider's docs.

Example with [ProxyMesh](https://proxymesh.com):

| Header | Direction | Purpose |
|--------|-----------|---------|
| `X-ProxyMesh-Country` | Send | Route through specific country |
| `X-ProxyMesh-IP` | Send/Receive | Request or receive sticky IP |

## Testing

```bash
export PROXY_URL='http://user:pass@proxy.example.com:8080'
python test_proxy_headers.py -v
# or specific modules:
python test_proxy_headers.py requests httpx
```

## Documentation

Full docs at [python-proxy-headers.readthedocs.io](https://python-proxy-headers.readthedocs.io/).
