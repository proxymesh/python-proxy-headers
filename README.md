# Python Proxy Headers

The `python-proxy-headers` package provides support for handling custom proxy headers when making HTTPS requests in various Python modules.

We currently provide extensions to the following packages:

* [urllib3](https://python-proxy-headers.readthedocs.io/en/latest/urllib3.html) - a user-friendly HTTP client library for Python
* [requests](https://python-proxy-headers.readthedocs.io/en/latest/requests.html) - a simple, yet elegant, HTTP library
* [aiohttp](https://python-proxy-headers.readthedocs.io/en/latest/aiohttp.html) - asynchronous HTTP client/server framework for asyncio and Python
* [httpx](https://python-proxy-headers.readthedocs.io/en/latest/httpx.html) - a next generation HTTP client for Python

## Purpose

None of these modules provide good support for parsing custom response headers from proxy servers. And some of them make it hard to send custom headers to proxy servers. So we at [ProxyMesh](https://proxymesh.com) made these extension modules to support our customers that use Python and want to use custom headers to control our proxy behavior. But these modules can work for handling custom headers with any proxy.

*If you are looking for [Scrapy](https://scrapy.org/) support, please see our [scrapy-proxy-headers](https://github.com/proxymesh/scrapy-proxy-headers) project.*

## Installation

To use these extension modules, you must first do the following:

1. `pip install python-proxy-headers`
2. Install the appropriate package based on the Python library you want to use.

This package does not have any dependencies because we don't know which library you want to use.

## Documentation

For detailed documentation, examples, and usage instructions, please see the [full documentation](https://python-proxy-headers.readthedocs.io/en/latest/).

You can also find more example code in our [proxy-examples for python](https://github.com/proxymesh/proxy-examples/tree/main/python).