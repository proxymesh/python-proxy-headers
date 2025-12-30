httpx
=====

The `httpx <https://www.python-httpx.org/>`_ library is a modern HTTP client for Python with support for both sync and async requests. This page describes how to use httpx with proxies and how to interact with proxy headers.

Using Proxies with httpx
------------------------

httpx provides built-in support for proxies through the ``httpx.Proxy`` class. You can create a proxy object and use it with httpx clients.

Basic Proxy Usage
~~~~~~~~~~~~~~~~~

httpx also supports proxy headers by default, though it's not documented. You can use the ``httpx.Proxy`` class with custom headers:

.. code-block:: python

   import httpx
   from httpx import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')

This creates a proxy with custom headers and uses it with an httpx client.

Receiving Proxy Response Headers
---------------------------------

But to get the response headers, you need to use our extension module ``python_proxy_headers.httpx_proxy``:

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')
   
   r.headers['X-ProxyMesh-IP']

The ``HTTPProxyTransport`` from our extension module extends the standard transport to make proxy response headers available in the response headers.

Helper Methods
--------------

This module also provides helper methods similar to requests for convenience:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
   r.headers['X-ProxyMesh-IP']

The helper module supports all standard HTTP methods: ``get``, ``post``, ``put``, ``delete``, ``patch``, ``head``, and ``options``.

Async Support
-------------

httpx supports async requests, so we provide an async extension too:

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = AsyncHTTPProxyTransport(proxy=proxy)
   async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
       r = await client.get('https://api.ipify.org?format=json')
   
   r.headers['X-ProxyMesh-IP']

The ``AsyncHTTPProxyTransport`` works just like the sync version but for async clients.

Complete Examples
-----------------

Synchronous Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')
       data = r.json()
       proxy_ip = r.headers.get('X-ProxyMesh-IP')
       print(f"Your IP: {data['ip']}")
       print(f"Proxy IP: {proxy_ip}")

Asynchronous Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
   
   async def main():
       proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
       transport = AsyncHTTPProxyTransport(proxy=proxy)
       
       async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
           r = await client.get('https://api.ipify.org?format=json')
           data = r.json()
           proxy_ip = r.headers.get('X-ProxyMesh-IP')
           print(f"Your IP: {data['ip']}")
           print(f"Proxy IP: {proxy_ip}")
   
   import asyncio
   asyncio.run(main())

Using Helper Methods
~~~~~~~~~~~~~~~~~~~~

For simpler use cases, you can use the helper methods:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   # GET request
   r = httpx_proxy.get('https://api.example.com', proxy=proxy)
   
   # POST request
   r = httpx_proxy.post('https://api.example.com', json={'key': 'value'}, proxy=proxy)
   
   # Access proxy response headers
   proxy_ip = r.headers.get('X-ProxyMesh-IP')

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

httpcore Integration
--------------------

Our httpx helper module internally provides extension classes for `httpcore <https://www.encode.io/httpcore/>`_, for handling proxy headers over tunnel connections. You can use those classes if you're building on top of httpcore directly.

