httpx
=====

`HTTPX <https://www.python-httpx.org/>`_ is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2. This page describes how to use httpx with proxies and how to send and receive custom proxy headers.

Getting Started
---------------

This section shows you how to quickly get up and running with proxy headers in httpx.

**Prerequisites:**

1. Install the packages:

   .. code-block:: bash

      pip install python-proxy-headers httpx

2. Import the module:

   .. code-block:: python

      from python_proxy_headers import httpx_proxy

**Quick Example - Send and Receive Proxy Headers:**

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   
   # Create a proxy with custom headers
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   # Make a request using our helper function
   r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
   
   # Access the response data
   print(r.json())  # {"ip": "..."}
   
   # Access proxy response headers
   print(r.headers.get('X-ProxyMesh-IP'))  # The IP address assigned by the proxy

That's it! The ``httpx_proxy`` module handles sending your custom headers to the proxy and makes proxy response headers available in the response.

Using Proxies with httpx
------------------------

httpx provides built-in support for proxies through the ``proxy`` parameter. You can pass a proxy URL to the client.

Basic Proxy Usage (Standard httpx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a proxy with standard httpx:

.. code-block:: python

   import httpx
   
   # Simple proxy URL
   with httpx.Client(proxy='http://PROXYHOST:PORT') as client:
       r = client.get('https://api.ipify.org?format=json')
       print(r.json())

This routes requests through the specified proxy server.

Proxy Authentication
~~~~~~~~~~~~~~~~~~~~

To use a proxy that requires authentication:

.. code-block:: python

   import httpx
   
   # Include credentials in the URL
   with httpx.Client(proxy='http://username:password@PROXYHOST:PORT') as client:
       r = client.get('https://api.ipify.org?format=json')

Different Proxies for HTTP and HTTPS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure different proxies for HTTP and HTTPS using mounts:

.. code-block:: python

   import httpx
   
   proxy_mounts = {
       'http://': httpx.HTTPTransport(proxy='http://localhost:8030'),
       'https://': httpx.HTTPTransport(proxy='http://localhost:8031'),
   }
   with httpx.Client(mounts=proxy_mounts) as client:
       r = client.get('https://api.ipify.org?format=json')

SOCKS Proxies
~~~~~~~~~~~~~

httpx supports SOCKS proxies with an additional dependency:

.. code-block:: bash

   pip install httpx[socks]

.. code-block:: python

   import httpx
   
   with httpx.Client(proxy='socks5://user:pass@host:port') as client:
       r = client.get('https://api.ipify.org?format=json')

Sending Custom Proxy Headers
----------------------------

httpx supports sending proxy headers by default through the ``httpx.Proxy`` class:

.. code-block:: python

   import httpx
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   with httpx.Client(proxy=proxy) as client:
       r = client.get('https://api.ipify.org?format=json')

The ``headers`` parameter on the ``Proxy`` object allows you to send custom headers to the proxy server.

Receiving Proxy Response Headers
---------------------------------

Standard httpx does not expose proxy response headers from the CONNECT request. To get response headers from a proxy server, use our extension module ``python_proxy_headers.httpx_proxy``:

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')
   
   # Proxy response headers are now available
   proxy_ip = r.headers.get('X-ProxyMesh-IP')
   print(f"Request was made through: {proxy_ip}")

The ``HTTPProxyTransport`` class from our extension module extends the standard transport to make proxy response headers available in the response headers.

Helper Methods
--------------

For simpler use cases, this module provides helper methods similar to ``requests``:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   # GET request
   r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
   
   # Access proxy response headers
   print(r.headers.get('X-ProxyMesh-IP'))

The helper module supports all standard HTTP methods:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   # GET request
   r = httpx_proxy.get('https://api.example.com', proxy=proxy)
   
   # POST request
   r = httpx_proxy.post('https://api.example.com', json={'key': 'value'}, proxy=proxy)
   
   # PUT request
   r = httpx_proxy.put('https://api.example.com/resource/1', json={'name': 'updated'}, proxy=proxy)
   
   # PATCH request
   r = httpx_proxy.patch('https://api.example.com/resource/1', json={'status': 'active'}, proxy=proxy)
   
   # DELETE request
   r = httpx_proxy.delete('https://api.example.com/resource/1', proxy=proxy)
   
   # HEAD request
   r = httpx_proxy.head('https://api.example.com', proxy=proxy)
   
   # OPTIONS request
   r = httpx_proxy.options('https://api.example.com', proxy=proxy)

Async Support
-------------

httpx supports async requests, so we provide an async extension too:

.. code-block:: python

   import httpx
   import asyncio
   from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
   
   async def main():
       proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
       transport = AsyncHTTPProxyTransport(proxy=proxy)
       
       async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
           r = await client.get('https://api.ipify.org?format=json')
       
       # Access proxy response headers
       proxy_ip = r.headers.get('X-ProxyMesh-IP')
       print(f"Proxy IP: {proxy_ip}")
   
   asyncio.run(main())

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
   import asyncio
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
   
   asyncio.run(main())

Streaming Responses
~~~~~~~~~~~~~~~~~~~~

For streaming large responses, you can use the ``stream`` context manager:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   
   with httpx_proxy.stream('GET', 'https://api.example.com/large-file', proxy=proxy) as response:
       # Access proxy response headers
       proxy_ip = response.headers.get('X-ProxyMesh-IP')
       print(f"Proxy IP: {proxy_ip}")
       
       # Stream the response content
       for chunk in response.iter_bytes():
           # Process each chunk as it arrives
           print(f"Received {len(chunk)} bytes")

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They can allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

API Reference
-------------

Helper Functions
~~~~~~~~~~~~~~~~

* ``request(method, url, *, proxy=None, **kwargs)`` - Make a request with the specified method
* ``get(url, *, proxy=None, **kwargs)`` - Make a GET request
* ``post(url, *, proxy=None, **kwargs)`` - Make a POST request
* ``put(url, *, proxy=None, **kwargs)`` - Make a PUT request
* ``patch(url, *, proxy=None, **kwargs)`` - Make a PATCH request
* ``delete(url, *, proxy=None, **kwargs)`` - Make a DELETE request
* ``head(url, *, proxy=None, **kwargs)`` - Make a HEAD request
* ``options(url, *, proxy=None, **kwargs)`` - Make an OPTIONS request
* ``stream(method, url, *, proxy=None, **kwargs)`` - Stream a response (context manager)

HTTPProxyTransport
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   
   transport = HTTPProxyTransport(
       proxy=proxy,          # httpx.Proxy object or proxy URL string
       verify=True,          # SSL verification
       cert=None,            # Client certificate
       trust_env=True,       # Trust environment variables
       http1=True,           # Enable HTTP/1.1
       http2=False,          # Enable HTTP/2
       limits=DEFAULT_LIMITS,
       **kwargs
   )

AsyncHTTPProxyTransport
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
   
   transport = AsyncHTTPProxyTransport(
       proxy=proxy,          # httpx.Proxy object or proxy URL string
       verify=True,          # SSL verification
       cert=None,            # Client certificate
       trust_env=True,       # Trust environment variables
       http1=True,           # Enable HTTP/1.1
       http2=False,          # Enable HTTP/2
       limits=DEFAULT_LIMITS,
       **kwargs
   )

httpcore Integration
--------------------

Our httpx extension module internally provides extension classes for `httpcore <https://www.encode.io/httpcore/>`_, for handling proxy headers over tunnel connections. These classes extend httpcore's internal proxy implementation to capture and merge proxy response headers.

Extension Classes
~~~~~~~~~~~~~~~~~

The module provides four main extension classes:

* ``ProxyTunnelHTTPConnection`` - Extends ``httpcore._sync.http_proxy.TunnelHTTPConnection`` to merge proxy response headers from the CONNECT response into the final HTTP response
* ``AsyncProxyTunnelHTTPConnection`` - Async version that extends ``httpcore._async.http_proxy.AsyncTunnelHTTPConnection``
* ``HTTPProxyHeaders`` - Extends ``httpcore._sync.http_proxy.HTTPProxy`` to use the custom tunnel connection classes for HTTPS connections
* ``AsyncHTTPProxyHeaders`` - Async version that extends ``httpcore._async.http_proxy.AsyncHTTPProxy``

These classes are used internally by ``HTTPProxyTransport`` and ``AsyncHTTPProxyTransport``. They automatically merge proxy response headers (like ``X-ProxyMesh-IP``) from the CONNECT response into the final HTTP response headers, making them accessible to your application.

How It Works
~~~~~~~~~~~~

The extension classes work by intercepting the CONNECT request/response cycle during tunnel establishment:

1. **CONNECT Request**: When establishing a tunnel connection through the proxy, ``ProxyTunnelHTTPConnection`` sends the CONNECT request with your custom proxy headers (e.g., ``X-ProxyMesh-Country: US``)

2. **CONNECT Response**: The proxy responds with a CONNECT response (status 200) that may include proxy information headers in the response (e.g., ``X-ProxyMesh-IP: 192.168.1.1``)

3. **Header Merging**: These proxy response headers are captured during the tunnel establishment and stored. When the actual HTTP request is made through the tunnel, the proxy response headers are merged into the final HTTP response headers using ``merge_headers()``

4. **Access**: Your application can then access both the target server's response headers and the proxy's response headers from the same response object

This is particularly useful for proxy services that provide metadata about the proxy connection (such as the assigned IP address, country, or session information) in the CONNECT response headers.

Internal Usage
~~~~~~~~~~~~~~

These classes are used internally by ``HTTPProxyTransport`` and ``AsyncHTTPProxyTransport``. When you create a transport with a proxy, it automatically uses ``HTTPProxyHeaders`` (or ``AsyncHTTPProxyHeaders``) as the connection pool, which in turn uses ``ProxyTunnelHTTPConnection`` (or ``AsyncProxyTunnelHTTPConnection``) for HTTPS tunnel connections.

If you're building custom functionality on top of httpcore, you can import and use these classes directly, but note that they depend on httpcore's internal APIs which may change between versions.
