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

## Features

* Proxy CONNECT headers support
* HTTPS tunnel proxy support
* Proxy IP address selection
* Country proxy selection
* Rotating proxy support
* Proxy session management
* Proxy connection pooling
* Async proxy support
* HTTP/2 proxy support

## Installation

To use these extension modules, you must first do the following:

1. `pip install python-proxy-headers`
2. Install the appropriate package based on the Python library you want to use.

This package does not have any dependencies because we don't know which library you want to use.

## Why Use python-proxy-headers?

The `python-proxy-headers` package is the perfect solution for developers who need to handle custom proxy headers in their Python applications. It provides a simple and easy-to-use interface for managing proxy connections, and it supports a wide range of popular Python libraries. Whether you're using `urllib3`, `requests`, `aiohttp`, or `httpx`, this package has you covered.

## Quick Start

Here are some quick examples to get you started:

### urllib3

import urllib3
from python_proxy_headers.urllib3 import ProxyHeaders

http = urllib3.PoolManager()
proxy_headers = ProxyHeaders(http)

# Set a custom header for the proxy
proxy_headers.set_header('X-Proxy-Header', 'value')

# Make a request using the proxy
response = http.request('GET', 'https://httpbin.org/get', headers=proxy_headers)

print(response.data)

### requests

import requests
from python_proxy_headers.requests import ProxyHeaders

session = requests.Session()
proxy_headers = ProxyHeaders(session)

# Set a custom header for the proxy
proxy_headers.set_header('X-Proxy-Header', 'value')

# Make a request using the proxy
response = session.get('https://httpbin.org/get', headers=proxy_headers)

print(response.text)

### aiohttp

import aiohttp
from python_proxy_headers.aiohttp import ProxyHeaders

async def main():
    async with aiohttp.ClientSession() as session:
        proxy_headers = ProxyHeaders(session)

        # Set a custom header for the proxy
        proxy_headers.set_header('X-Proxy-Header', 'value')

        # Make a request using the proxy
        async with session.get('https://httpbin.org/get', headers=proxy_headers) as response:
            print(await response.text())

### httpx

import httpx
from python_proxy_headers.httpx import ProxyHeaders

async def main():
    async with httpx.AsyncClient() as client:
        proxy_headers = ProxyHeaders(client)

        # Set a custom header for the proxy
        proxy_headers.set_header('X-Proxy-Header', 'value')

        # Make a request using the proxy
        response = await client.get('https://httpbin.org/get', headers=proxy_headers)

        print(response.text)

## Documentation

For detailed documentation, examples, and usage instructions, please see the [full documentation](https://python-proxy-headers.readthedocs.io/en/latest/).

You can also find more example code in our [proxy-examples for python](https://github.com/proxymesh/proxy-examples/tree/main/python).