# Python Proxy Headers

[![Documentation Status](https://readthedocs.org/projects/python-proxy-headers/badge/?version=latest)](https://python-proxy-headers.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/python-proxy-headers.svg)](https://badge.fury.io/py/python-proxy-headers)

Extensions for Python HTTP libraries to support **sending and receiving custom proxy headers** during HTTPS CONNECT tunneling.

## The Problem

When making HTTPS requests through a proxy, the connection is established via a CONNECT tunnel. During this process:

1. **Sending headers to the proxy** - Most Python HTTP libraries don't provide an easy way to send custom headers (like `X-ProxyMesh-Country`) to the proxy server during the CONNECT handshake.

2. **Receiving headers from the proxy** - The proxy's response headers from the CONNECT request are typically discarded, making it impossible to read custom headers (like `X-ProxyMesh-IP`) that the proxy sends back.

This library solves both problems for popular Python HTTP libraries.

## Supported Libraries

| Library | Module | Use Case |
|---------|--------|----------|
| [urllib3](https://python-proxy-headers.readthedocs.io/en/latest/urllib3.html) | `urllib3_proxy_manager` | Low-level HTTP client |
| [requests](https://python-proxy-headers.readthedocs.io/en/latest/requests.html) | `requests_adapter` | Simple HTTP requests |
| [aiohttp](https://python-proxy-headers.readthedocs.io/en/latest/aiohttp.html) | `aiohttp_proxy` | Async HTTP client |
| [httpx](https://python-proxy-headers.readthedocs.io/en/latest/httpx.html) | `httpx_proxy` | Modern HTTP client |
| [pycurl](https://python-proxy-headers.readthedocs.io/en/latest/pycurl.html) | `pycurl_proxy` | libcurl bindings |
| [cloudscraper](https://python-proxy-headers.readthedocs.io/en/latest/cloudscraper.html) | `cloudscraper_proxy` | Cloudflare bypass |
| [autoscraper](https://python-proxy-headers.readthedocs.io/en/latest/autoscraper.html) | `autoscraper_proxy` | Automatic web scraping |

## Installation

```bash
pip install python-proxy-headers
```

Then install the HTTP library you want to use (e.g., `pip install requests`).

> **Note:** This package has no dependencies by default - install only what you need.

## Quick Start

### requests

```python
from python_proxy_headers.requests_adapter import ProxySession

with ProxySession(proxy_headers={'X-ProxyMesh-Country': 'US'}) as session:
    session.proxies = {'https': 'http://user:pass@proxy.example.com:8080'}
    response = session.get('https://httpbin.org/ip')
    
    # Proxy headers are merged into response.headers
    print(response.headers.get('X-ProxyMesh-IP'))
```

### httpx

```python
from python_proxy_headers.httpx_proxy import get

response = get(
    'https://httpbin.org/ip',
    proxy='http://user:pass@proxy.example.com:8080'
)

# Proxy CONNECT response headers are merged into response.headers
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
            # Proxy headers merged into response.headers
            print(response.headers.get('X-ProxyMesh-IP'))

asyncio.run(main())
```

### pycurl (low-level)

```python
import pycurl
from python_proxy_headers.pycurl_proxy import set_proxy_headers, HeaderCapture

c = pycurl.Curl()
c.setopt(pycurl.URL, 'https://httpbin.org/ip')
c.setopt(pycurl.PROXY, 'http://proxy.example.com:8080')

# Add these two lines to any existing pycurl code
set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})
capture = HeaderCapture(c)

c.perform()

print(capture.proxy_headers)  # Headers from proxy CONNECT response
c.close()
```

### cloudscraper

```python
from python_proxy_headers.cloudscraper_proxy import create_scraper

# Drop-in replacement for cloudscraper.create_scraper()
scraper = create_scraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
scraper.proxies = {'https': 'http://proxy.example.com:8080'}

response = scraper.get('https://example.com')
# All CloudScraper features (Cloudflare bypass) preserved
```

## Testing

A test harness is included to verify proxy header functionality:

```bash
# Set your proxy
export PROXY_URL='http://user:pass@proxy.example.com:8080'

# Test all modules
python test_proxy_headers.py

# Test specific modules
python test_proxy_headers.py requests httpx

# Verbose output (show header values)
python test_proxy_headers.py -v
```

## Documentation

For detailed documentation, API reference, and more examples:

- **Full Documentation:** [python-proxy-headers.readthedocs.io](https://python-proxy-headers.readthedocs.io/en/latest/)
- **Example Code:** [proxy-examples for Python](https://github.com/proxymesh/proxy-examples/tree/main/python)

## Related Projects

- **[scrapy-proxy-headers](https://github.com/proxymesh/scrapy-proxy-headers)** - Proxy header support for Scrapy

## About

Created by [ProxyMesh](https://proxymesh.com) to help our customers use custom headers to control proxy behavior. Works with any proxy that supports custom headers.

## License

MIT License
