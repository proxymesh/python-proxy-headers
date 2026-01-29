httpx
=====

`HTTPX <https://www.python-httpx.org/>`_ is a fully featured HTTP client for Python 3, which provides sync and async APIs, and support for both HTTP/1.1 and HTTP/2. This page describes how to use httpx with proxies and how to interact with proxy headers.

Overview
--------

httpx provides built-in support for proxies through the ``httpx.Proxy`` class. You can create a proxy object and use it with httpx clients. It supports sending proxy headers by default, though it's not documented. You can use the ``httpx.Proxy`` class with custom headers:

.. code-block:: python

   import httpx
   from httpx import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')

This creates a proxy with custom headers and uses it with an httpx client.

To get response headers from a proxy server, you need to use our extension module ``python_proxy_headers.httpx_proxy``:

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')
   
   r.headers['X-ProxyMesh-IP']

The ``HTTPProxyTransport`` class from our extension module extends the standard transport to make proxy response headers available in the response headers.

Key Features
------------

* **send custom proxy headers**
* **receive proxy response headers**
* **proxy authentication**
* **country-based proxy selection**
* **rotating proxies**
* **proxy session management**
* **connection pooling**
* **HTTP/2 proxy support**
* **async proxy support**

Using Proxies with httpx
------------------------

httpx provides built-in support for proxies through the ``httpx.Proxy`` class. You can create a proxy object and use it with httpx clients.

Basic Proxy Usage
~~~~~~~~~~~~~~~~~

httpx supports sending proxy headers by default, though it's not documented. You can use the ``httpx.Proxy`` class with custom headers:

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

But to get response headers from a proxy server, you need to use our extension module ``python_proxy_headers.httpx_proxy``:

.. code-block:: python

   import httpx
   from python_proxy_headers.httpx_proxy import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')
   
   r.headers['X-ProxyMesh-IP']

The ``HTTPProxyTransport`` class from our extension module extends the standard transport to make proxy response headers available in the response headers.

Helper Methods
--------------

This module also provides helper methods similar to ``requests`` for convenience:

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
   
   # Access proxy response headers
   proxy_ip = r.headers.get('X-ProxyMesh-IP')

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

Usage Patterns
--------------

This section covers various usage patterns for using httpx with proxies, both with and without our extension module.

Without Extension Module
~~~~~~~~~~~~~~~~~~~~~~~

1. **Basic proxy usage with httpx.Client and Proxy object**

   .. code-block:: python

      import httpx
      from httpx import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

2. **Sending custom proxy headers (built-in headers parameter)**

   .. code-block:: python

      import httpx
      from httpx import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

3. **Proxy authentication with Proxy object**

   .. code-block:: python

      import httpx
      from httpx import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

4. **Async proxy usage with AsyncClient**

   .. code-block:: python

      import httpx
      from httpx import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
          r = await client.get('https://api.ipify.org?format=json')

5. **Session usage with built-in proxy support**

   .. code-block:: python

      import httpx
      from httpx import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

With Extension Module
~~~~~~~~~~~~~~~~~~~~~

1. **Using HTTPProxyTransport**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

2. **Using AsyncHTTPProxyTransport**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import AsyncHTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = AsyncHTTPProxyTransport(proxy=proxy)
      async with httpx.AsyncClient(mounts={'http://': transport, 'https://': transport}) as client:
          r = await client.get('https://api.ipify.org?format=json')

3. **Using helper functions**

   .. code-block:: python

      import httpx
      from python_proxy_headers import httpx_proxy
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
      r.headers['X-ProxyMesh-IP']

4. **Using stream context manager**

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

5. **Session consistency patterns**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

Advanced Usage Patterns
~~~~~~~~~~~~~~~~~~~~~~~

1. **Rotating proxies across requests**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxies = [
          httpx.Proxy('http://PROXYHOST1:PORT', headers={'X-ProxyMesh-Country': 'US'}),
          httpx.Proxy('http://PROXYHOST2:PORT', headers={'X-ProxyMesh-Country': 'US'}),
          httpx.Proxy('http://PROXYHOST3:PORT', headers={'X-ProxyMesh-Country': 'US'}),
      ]
      transport = HTTPProxyTransport(proxy=proxies[0])
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

2. **Proxy failover scenarios**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxies = [
          httpx.Proxy('http://PROXYHOST1:PORT', headers={'X-ProxyMesh-Country': 'US'}),
          httpx.Proxy('http://PROXYHOST2:PORT', headers={'X-ProxyMesh-Country': 'US'}),
          httpx.Proxy('http://PROXYHOST3:PORT', headers={'X-ProxyMesh-Country': 'US'}),
      ]
      transport = HTTPProxyTransport(proxy=proxies[0])
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

3. **Connection pooling with clients**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

4. **Timeout configuration with proxies**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

5. **Error handling for proxy failures**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

6. **HTTP/2 proxy support**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

7. **Cookie persistence with proxy sessions**

   .. code-block:: python

      import httpx
      from python_proxy_headers.httpx_proxy import HTTPProxyTransport
      proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
      transport = HTTPProxyTransport(proxy=proxy)
      with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
          r = client.get('https://api.ipify.org?format=json')

Comparison Table
~~~~~~~~~~~~~~~~

+-----------------------------+-----------------------------+-----------------------------+
| Feature                     | Without Extension Module    | With Extension Module       |
+=============================+=============================+=============================+
| Basic proxy usage           | httpx.Client, Proxy object   | HTTPProxyTransport          |
| Sending custom headers      | headers parameter           | HTTPProxyTransport          |
| Proxy authentication        | Proxy object                | HTTPProxyTransport          |
| Async usage                 | AsyncClient                 | AsyncHTTPProxyTransport     |
| Session support             | built-in proxy support      | HTTPProxyTransport          |
| Receiving proxy headers     | not available               | HTTPProxyTransport          |
| Helper methods              | httpx_proxy module          | httpx_proxy module          |
| Streaming responses         | httpx_proxy.stream          | httpx_proxy.stream          |
| Rotating proxies            | manual implementation       | HTTPProxyTransport          |
| Proxy failover              | manual implementation       | HTTPProxyTransport          |
| Connection pooling          | built-in                    | HTTPProxyTransport          |
| Timeout configuration       | built-in                    | HTTPProxyTransport          |
| Error handling              | built-in                    | HTTPProxyTransport          |
| HTTP/2 support              | built-in                    | HTTPProxyTransport          |
| Cookie persistence        | built-in                    | HTTPProxyTransport          |
+-----------------------------+-----------------------------+-----------------------------+

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They can allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

httpcore Integration
--------------------

Our httpx helper module internally provides extension classes for `httpcore <https://www.encode.io/httpcore/>`_, for handling proxy headers over tunnel connections. These classes extend httpcore's internal proxy implementation to capture and merge proxy response headers.

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

API Reference
-------------

HTTPProxyTransport
~~~~~~~~~~~~~~~~~~

The transport class for synchronous HTTP requests.

.. class:: HTTPProxyTransport

   .. method:: __init__(proxy, **kwargs)

      :param proxy: The proxy to use.
      :type proxy: httpx.Proxy
      :param kwargs: Additional keyword arguments to pass to the underlying transport.

   .. method:: request(method, url, headers=None, stream=None, timeout=None)

      :param method: The HTTP method to use.
      :type method: str
      :param url: The URL to request.
      :type url: str
      :param headers: The headers to include in the request.
      :type headers: dict
      :param stream: The stream to use for the request.
      :type stream: httpx._types.StreamType
      :param timeout: The timeout to use for the request.
      :type timeout: httpx._types.TimeoutTypes
      :return: The response object.
      :rtype: httpx.Response

AsyncHTTPProxyTransport
~~~~~~~~~~~~~~~~~~~~~~

The transport class for asynchronous HTTP requests.

.. class:: AsyncHTTPProxyTransport

   .. method:: __init__(proxy, **kwargs)

      :param proxy: The proxy to use.
      :type proxy: httpx.Proxy
      :param kwargs: Additional keyword arguments to pass to the underlying transport.

   .. method:: request(method, url, headers=None, stream=None, timeout=None)

      :param method: The HTTP method to use.
      :type method: str
      :param url: The URL to request.
      :type url: str
      :param headers: The headers to include in the request.
      :type headers: dict
      :param stream: The stream to use for the request.
      :type stream: httpx._types.StreamType
      :param timeout: The timeout to use for the request.
      :type timeout: httpx._types.TimeoutTypes
      :return: The response object.
      :rtype: httpx.Response

request()
~~~~~~~~~

The function to make a request.

.. function:: request(method, url, headers=None, stream=None, timeout=None)

   :param method: The HTTP method to use.
   :type method: str
   :param url: The URL to request.
   :type url: str
   :param headers: The headers to include in the request.
   :type headers: dict
   :param stream: The stream to use for the request.
   :type stream: httpx._types.StreamType
   :param timeout: The timeout to use for the request.
   :type timeout: httpx._types.TimeoutTypes
   :return: The response object.
   :rtype: httpx.Response

Helper Methods
~~~~~~~~~~~~~~

This module also provides helper methods similar to ``requests`` for convenience:

.. code-block:: python

   import httpx
   from python_proxy_headers import httpx_proxy
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   r = httpx_proxy.get('https://api.ipify.org?format=json', proxy=proxy)
   r.headers['X-ProxyMesh-IP']

The helper module supports all standard HTTP methods: ``get``, ``post``, ``put``, ``delete``, ``patch``, ``head``, and ``options``.

stream()
~~~~~~~~

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

Built-in Support
-----------------

httpx supports sending proxy headers via headers parameter

.. code-block:: python

   import httpx
   from httpx import HTTPProxyTransport
   proxy = httpx.Proxy('http://PROXYHOST:PORT', headers={'X-ProxyMesh-Country': 'US'})
   transport = HTTPProxyTransport(proxy=proxy)
   with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
       r = client.get('https://api.ipify.org?format=json')

This creates a proxy with custom headers and uses it with an httpx client.

