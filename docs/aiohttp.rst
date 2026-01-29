aiohttp
=======

The `aiohttp <https://docs.aiohttp.org/en/stable/index.html>`_ library is an async HTTP client/server framework for Python. This page describes how to use aiohttp with proxies and how to interact with proxy headers.

Using Proxies with aiohttp
---------------------------

aiohttp provides built-in support for proxies through the ``proxy`` parameter in request methods. You can specify a proxy URL for each request.

Basic Proxy Usage
~~~~~~~~~~~~~~~~~

To use a proxy with aiohttp, you can pass the ``proxy`` parameter to any request method:

.. code-block:: python

   import aiohttp
   async with aiohttp.ClientSession() as session:
       async with session.get('https://api.ipify.org?format=json', 
                             proxy="http://PROXYHOST:PORT") as r:
           text = await r.text()

This routes the request through the specified proxy server.

Sending Custom Proxy Headers
-----------------------------

While it's not documented, aiohttp does support passing in custom proxy headers by default using the ``proxy_headers`` parameter:

.. code-block:: python

   import aiohttp
   async with aiohttp.ClientSession() as session:
       async with session.get('https://api.ipify.org?format=json', 
                             proxy="http://PROXYHOST:PORT", 
                             proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
           text = await r.text()

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

Receiving Proxy Response Headers
---------------------------------

However, if you want to get proxy response headers, you should use our extension module ``python_proxy_headers.aiohttp_proxy``:

.. code-block:: python

   from python_proxy_headers import aiohttp_proxy
   async with aiohttp_proxy.ProxyClientSession() as session:
       async with session.get('https://api.ipify.org?format=json', 
                             proxy="http://PROXYHOST:PORT", 
                             proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
           text = await r.text()
           proxy_ip = r.headers['X-ProxyMesh-IP']

The ``ProxyClientSession`` extends the standard ``ClientSession`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

Complete Example
----------------

Here's a complete example showing how to use aiohttp with proxy headers:

.. code-block:: python

   import asyncio
   from python_proxy_headers import aiohttp_proxy
   
   async def main():
       async with aiohttp_proxy.ProxyClientSession() as session:
           async with session.get('https://api.ipify.org?format=json', 
                                 proxy="http://PROXYHOST:PORT", 
                                 proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
               data = await r.json()
               proxy_ip = r.headers.get('X-ProxyMesh-IP')
               print(f"Your IP: {data['ip']}")
               print(f"Proxy IP: {proxy_ip}")
   
   asyncio.run(main())

Usage Patterns
--------------

This section covers various usage patterns for using proxies with aiohttp, both with and without our extension module.

Without Extension Module
~~~~~~~~~~~~~~~~~~~~~~~~

1. **Basic proxy usage with ClientSession and proxy parameter**

   To use a proxy with aiohttp, you can pass the ``proxy`` parameter to any request method:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT") as r:
              text = await r.text()

   This routes the request through the specified proxy server.

2. **Sending custom proxy headers (built-in proxy_headers parameter)**

   While it's not documented, aiohttp does support passing in custom proxy headers by default using the ``proxy_headers`` parameter:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
              text = await r.text()

   The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

3. **Proxy authentication with proxy_auth parameter**

   To use proxy authentication, you can pass the ``proxy_auth`` parameter to any request method:

   .. code-block:: python

      import aiohttp
      from aiohttp import BasicAuth
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_auth=BasicAuth('username', 'password')) as r:
              text = await r.text()

   This will send the specified username and password to the proxy server for authentication.

4. **Different proxies for different requests**

   You can specify a different proxy for each request by passing the ``proxy`` parameter to each request method:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST1:PORT") as r:
              text = await r.text()
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST2:PORT") as r:
              text = await r.text()

   This will route the first request through the first proxy and the second request through the second proxy.

5. **Session usage with built-in proxy support**

   You can use the built-in proxy support with a ``ClientSession`` by passing the ``proxy`` parameter to the session constructor:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession(proxy="http://PROXYHOST:PORT") as session:
          async with session.get('https://api.ipify.org?format=json') as r:
              text = await r.text()

   This will route all requests made with this session through the specified proxy.

With Extension Module
~~~~~~~~~~~~~~~~~~~~~

1. **Using ProxyClientSession**

   To use the extension module, you can use the ``ProxyClientSession`` class:

   .. code-block:: python

      from python_proxy_headers import aiohttp_proxy
      async with aiohttp_proxy.ProxyClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
              text = await r.text()

   The ``ProxyClientSession`` extends the standard ``ClientSession`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

2. **Sending and receiving proxy headers**

   To send and receive proxy headers, you can use the ``proxy_headers`` parameter:

   .. code-block:: python

      from python_proxy_headers import aiohttp_proxy
      async with aiohttp_proxy.ProxyClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
              text = await r.text()
              proxy_ip = r.headers['X-ProxyMesh-IP']

   The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

3. **Session consistency patterns**

   To ensure session consistency, you can use the ``proxy_headers`` parameter to specify a specific IP address or country:

   .. code-block:: python

      from python_proxy_headers import aiohttp_proxy
      async with aiohttp_proxy.ProxyClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_headers={'X-ProxyMesh-IP': '1.2.3.4'}) as r:
              text = await r.text()

   This will ensure that the same IP address is used for all requests made with this session.

4. **Country-based proxy selection**

   To select a proxy based on country, you can use the ``proxy_headers`` parameter to specify a country:

   .. code-block:: python

      from python_proxy_headers import aiohttp_proxy
      async with aiohttp_proxy.ProxyClientSession() as session:
          async with session.get('https://api.ipify.org?format=json', 
                                proxy="http://PROXYHOST:PORT", 
                                proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
              text = await r.text()

   This will select a proxy in the specified country for the request.

Advanced Usage Patterns
~~~~~~~~~~~~~~~~~~~~~~~

1. **Rotating proxies across requests**

   To rotate proxies across requests, you can use a list of proxies and select a proxy for each request:

   .. code-block:: python

      import aiohttp
      proxies = ["http://PROXYHOST1:PORT", "http://PROXYHOST2:PORT"]
      async with aiohttp.ClientSession() as session:
          for proxy in proxies:
              async with session.get('https://api.ipify.org?format=json', 
                                    proxy=proxy) as r:
                  text = await r.text()

   This will route each request through a different proxy.

2. **Proxy failover scenarios**

   To handle proxy failures, you can use a list of proxies and try each proxy in turn:

   .. code-block:: python

      import aiohttp
      proxies = ["http://PROXYHOST1:PORT", "http://PROXYHOST2:PORT"]
      async with aiohttp.ClientSession() as session:
          for proxy in proxies:
              try:
                  async with session.get('https://api.ipify.org?format=json', 
                                        proxy=proxy) as r:
                      text = await r.text()
              except Exception:
                  continue

   This will try each proxy in turn until a request is successful.

3. **Connection pooling with sessions**

   To use connection pooling, you can use the ``ClientSession`` class:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json') as r:
              text = await r.text()

   This will use a connection pool to reuse connections for multiple requests.

4. **Timeout configuration with proxies**

   To configure timeouts, you can use the ``timeout`` parameter:

   .. code-block:: python

      import aiohttp
      from aiohttp import ClientTimeout
      timeout = ClientTimeout(total=10)
      async with aiohttp.ClientSession(timeout=timeout) as session:
          async with session.get('https://api.ipify.org?format=json') as r:
              text = await r.text()

   This will set a timeout of 10 seconds for all requests made with this session.

5. **Error handling for proxy failures**

   To handle proxy failures, you can use a try-except block:

   .. code-block:: python

      import aiohttp
      try:
          async with aiohttp.ClientSession() as session:
              async with session.get('https://api.ipify.org?format=json', 
                                    proxy="http://PROXYHOST:PORT") as r:
                  text = await r.text()
      except Exception:
          pass

   This will catch any exceptions that occur during the request.

6. **Cookie persistence with proxy sessions**

   To persist cookies across requests, you can use the ``ClientSession`` class:

   .. code-block:: python

      import aiohttp
      async with aiohttp.ClientSession() as session:
          async with session.get('https://api.ipify.org?format=json') as r:
              text = await r.text()

   This will persist cookies across all requests made with this session.

Comparison Table
~~~~~~~~~~~~~~~~

This table shows what's available with/without extension:

+-----------------------------+-----------------------------+-----------------------------+
| Feature                     | Without Extension Module    | With Extension Module       |
+=============================+=============================+=============================+
| Basic proxy usage           | Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Sending custom proxy headers| Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Proxy authentication        | Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Different proxies for       | Yes                         | Yes                         |
| different requests          |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Session usage with built-in | Yes                         | Yes                         |
| proxy support               |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Receiving proxy response    | No                          | Yes                         |
| headers                     |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Session consistency         | No                          | Yes                         |
| patterns                    |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Country-based proxy         | No                          | Yes                         |
| selection                   |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Rotating proxies across     | Yes                         | Yes                         |
| requests                    |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Proxy failover scenarios    | Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Connection pooling          | Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Timeout configuration       | Yes                         | Yes                         |
+-----------------------------+-----------------------------+-----------------------------+
| Error handling for proxy    | Yes                         | Yes                         |
| failures                    |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+
| Cookie persistence with     | Yes                         | Yes                         |
| proxy sessions              |                             |                             |
+-----------------------------+-----------------------------+-----------------------------+

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

Async Context Managers
-----------------------

The ``ProxyClientSession`` works just like the standard ``ClientSession`` and supports all the same features, including:

* Connection pooling
* Cookie handling
* Timeout configuration
* SSL verification settings

All standard aiohttp request methods are supported: ``get``, ``post``, ``put``, ``delete``, ``patch``, ``head``, and ``options``.

API Reference
-------------

This section provides detailed documentation for all classes and methods in the ``python_proxy_headers.aiohttp_proxy`` module.

ProxyClientSession
~~~~~~~~~~~~~~~~~~

The main public class for interacting with proxies.

.. autoclass:: python_proxy_headers.aiohttp_proxy.ProxyClientSession
   :members:
   :undoc-members:
   :show-inheritance:

ProxyTCPConnector
~~~~~~~~~~~~~~~~~

The connector class for the ``ProxyClientSession``.

.. autoclass:: python_proxy_headers.aiohttp_proxy.ProxyTCPConnector
   :members:
   :undoc-members:
   :show-inheritance:

ProxyClientRequest
~~~~~~~~~~~~~~~~~~

The request class for the ``ProxyClientSession``.

.. autoclass:: python_proxy_headers.aiohttp_proxy.ProxyClientRequest
   :members:
   :undoc-members:
   :show-inheritance:

ProxyClientResponse
~~~~~~~~~~~~~~~~~~

The response class for the ``ProxyClientSession``.

.. autoclass:: python_proxy_headers.aiohttp_proxy.ProxyClientResponse
   :members:
   :undoc-members:
   :show-inheritance:

Built-in Support
----------------

aiohttp supports sending proxy headers via the ``proxy_headers`` parameter, which is documented in the aiohttp documentation.

.. code-block:: python

   import aiohttp
   async with aiohttp.ClientSession() as session:
       async with session.get('https://api.ipify.org?format=json', 
                             proxy="http://PROXYHOST:PORT", 
                             proxy_headers={'X-ProxyMesh-Country': 'US'}) as r:
           text = await r.text()

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

