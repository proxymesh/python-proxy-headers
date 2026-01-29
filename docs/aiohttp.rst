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

