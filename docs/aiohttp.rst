aiohttp
=======

The `aiohttp <https://docs.aiohttp.org/en/stable/index.html>`_ library is an async HTTP client/server framework for Python. This page describes how to use aiohttp with proxies and how to send and receive custom proxy headers.

Getting Started
---------------

This section shows you how to quickly get up and running with proxy headers in aiohttp.

**Prerequisites:**

1. Install the packages:

   .. code-block:: bash

      pip install python-proxy-headers aiohttp

2. Import the module:

   .. code-block:: python

      from python_proxy_headers import aiohttp_proxy

**Quick Example - Send and Receive Proxy Headers:**

.. code-block:: python

   import asyncio
   from python_proxy_headers import aiohttp_proxy
   
   async def main():
       async with aiohttp_proxy.ProxyClientSession() as session:
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT',
               proxy_headers={'X-ProxyMesh-Country': 'US'}
           ) as response:
               # Access the response data
               data = await response.json()
               print(data)  # {"ip": "..."}
               
               # Access proxy response headers
               print(response.headers.get('X-ProxyMesh-IP'))
   
   asyncio.run(main())

That's it! The ``ProxyClientSession`` handles sending your custom headers to the proxy and makes proxy response headers available in the response.

Using Proxies with aiohttp
---------------------------

aiohttp provides built-in support for proxies through the ``proxy`` parameter in request methods. You can specify a proxy URL for each request.

Basic Proxy Usage (Standard aiohttp)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a proxy with standard aiohttp:

.. code-block:: python

   import aiohttp
   import asyncio
   
   async def main():
       async with aiohttp.ClientSession() as session:
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT'
           ) as response:
               text = await response.text()
               print(text)
   
   asyncio.run(main())

This routes the request through the specified proxy server.

Proxy Authentication
~~~~~~~~~~~~~~~~~~~~

To use a proxy that requires authentication:

.. code-block:: python

   import aiohttp
   import asyncio
   
   async def main():
       async with aiohttp.ClientSession() as session:
           # Method 1: Include credentials in the URL
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://username:password@PROXYHOST:PORT'
           ) as response:
               text = await response.text()
               
           # Method 2: Use proxy_auth parameter
           auth = aiohttp.BasicAuth('username', 'password')
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT',
               proxy_auth=auth
           ) as response:
               text = await response.text()
   
   asyncio.run(main())

Session-Level Proxy
~~~~~~~~~~~~~~~~~~~

You can set a default proxy for all requests in a session:

.. code-block:: python

   import aiohttp
   import asyncio
   
   async def main():
       async with aiohttp.ClientSession(
           proxy='http://PROXYHOST:PORT',
           proxy_auth=aiohttp.BasicAuth('user', 'pass')
       ) as session:
           # All requests will use this proxy
           async with session.get('https://api.ipify.org?format=json') as response:
               text = await response.text()
   
   asyncio.run(main())

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

aiohttp can read proxy settings from environment variables when ``trust_env=True``:

.. code-block:: bash

   export HTTP_PROXY="http://PROXYHOST:PORT"
   export HTTPS_PROXY="http://PROXYHOST:PORT"

.. code-block:: python

   import aiohttp
   import asyncio
   
   async def main():
       async with aiohttp.ClientSession(trust_env=True) as session:
           # Will automatically use proxies from environment variables
           async with session.get('https://api.ipify.org?format=json') as response:
               text = await response.text()
   
   asyncio.run(main())

Sending Custom Proxy Headers
-----------------------------

While it's not documented, aiohttp does support passing in custom proxy headers by default using the ``proxy_headers`` parameter:

.. code-block:: python

   import aiohttp
   import asyncio
   
   async def main():
       async with aiohttp.ClientSession() as session:
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT',
               proxy_headers={'X-ProxyMesh-Country': 'US'}
           ) as response:
               text = await response.text()
   
   asyncio.run(main())

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

Receiving Proxy Response Headers
---------------------------------

Standard aiohttp does not expose proxy response headers from the CONNECT request. To get proxy response headers, use our extension module ``python_proxy_headers.aiohttp_proxy``:

.. code-block:: python

   import asyncio
   from python_proxy_headers import aiohttp_proxy
   
   async def main():
       async with aiohttp_proxy.ProxyClientSession() as session:
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT',
               proxy_headers={'X-ProxyMesh-Country': 'US'}
           ) as response:
               data = await response.json()
               
               # Proxy response headers are now available
               proxy_ip = response.headers.get('X-ProxyMesh-IP')
               print(f"Request was made through: {proxy_ip}")
   
   asyncio.run(main())

The ``ProxyClientSession`` extends the standard ``ClientSession`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

Complete Example
----------------

Here's a complete example showing how to use aiohttp with proxy headers:

.. code-block:: python

   import asyncio
   from python_proxy_headers import aiohttp_proxy
   
   async def main():
       async with aiohttp_proxy.ProxyClientSession() as session:
           async with session.get(
               'https://api.ipify.org?format=json',
               proxy='http://PROXYHOST:PORT',
               proxy_headers={'X-ProxyMesh-Country': 'US'}
           ) as response:
               data = await response.json()
               proxy_ip = response.headers.get('X-ProxyMesh-IP')
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

Extension Classes
-----------------

The ``python_proxy_headers.aiohttp_proxy`` module provides several extension classes that work together to capture and expose proxy response headers. These classes extend aiohttp's internal classes.

ProxyClientSession
~~~~~~~~~~~~~~~~~~

The main entry point for using proxy headers with aiohttp. This class extends ``aiohttp.ClientSession`` and automatically configures the session to use the other extension classes.

.. code-block:: python

   from python_proxy_headers.aiohttp_proxy import ProxyClientSession
   
   async with ProxyClientSession() as session:
       async with session.get('https://example.com', proxy='http://PROXYHOST:PORT') as r:
           proxy_ip = r.headers.get('X-ProxyMesh-IP')

The ``ProxyClientSession`` constructor accepts all the same arguments as ``aiohttp.ClientSession``, and automatically sets:

* ``connector`` to ``ProxyTCPConnector()``
* ``response_class`` to ``ProxyClientResponse``
* ``request_class`` to ``ProxyClientRequest``

ProxyTCPConnector
~~~~~~~~~~~~~~~~~

Extends ``aiohttp.TCPConnector`` to capture proxy response headers during HTTPS tunnel establishment. This class overrides the ``_create_proxy_connection`` method to:

1. Send the CONNECT request with custom proxy headers
2. Capture the proxy's response headers from the CONNECT response
3. Store them on the protocol object for later retrieval

When establishing an HTTPS connection through a proxy, the connector:

* Creates a CONNECT request to the proxy server
* Includes any custom proxy headers you've specified
* Captures the proxy's response headers (e.g., ``X-ProxyMesh-IP``)
* Stores them so they can be merged into the final response

You typically don't need to use this class directly - it's automatically configured when using ``ProxyClientSession``.

ProxyClientRequest
~~~~~~~~~~~~~~~~~~

Extends ``aiohttp.ClientRequest`` to transfer proxy headers from the connection protocol to the response object. This class overrides the ``send`` method to check if the connection's protocol has captured proxy headers and attaches them to the response.

This class is used internally by ``ProxyClientSession`` and typically doesn't need to be used directly.

ProxyClientResponse
~~~~~~~~~~~~~~~~~~~

Extends ``aiohttp.ClientResponse`` to merge proxy response headers into the response's headers property. This class overrides the ``headers`` property to:

1. Check if proxy headers were captured during tunnel establishment
2. If present, merge them with the target server's response headers
3. Return a combined ``CIMultiDictProxy`` containing both sets of headers

This allows you to access proxy response headers (like ``X-ProxyMesh-IP``) directly from the response object's ``headers`` property, alongside the target server's response headers.

How It Works
~~~~~~~~~~~~

The extension classes work together in the following flow:

1. **ProxyClientSession** creates a session configured with all the extension classes
2. **ProxyTCPConnector** intercepts the CONNECT request/response during tunnel establishment and captures proxy headers
3. **ProxyClientRequest** transfers the captured headers from the protocol to the response object
4. **ProxyClientResponse** merges the proxy headers into the response's ``headers`` property

This allows proxy response headers to be transparently available in your application without any special handling.
