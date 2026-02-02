urllib3
=======

The `urllib3 <https://urllib3.readthedocs.io/en/stable/>`_ library is a powerful HTTP client for Python. This page describes how to use urllib3 with proxies and how to send and receive custom proxy headers.

Getting Started
---------------

This section shows you how to quickly get up and running with proxy headers in urllib3.

**Prerequisites:**

1. Install the package:

   .. code-block:: bash

      pip install python-proxy-headers urllib3

2. Import the module:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager

**Quick Example - Send and Receive Proxy Headers:**

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   
   # Create a proxy manager that captures proxy response headers
   proxy = urllib3_proxy_manager.ProxyHeaderManager(
       'http://PROXYHOST:PORT',
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   
   # Make a request
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   
   # Access the response data
   print(r.data.decode())  # {"ip": "..."}
   
   # Access proxy response headers (these come from the proxy, not the target server)
   print(r.headers.get('X-ProxyMesh-IP'))  # The IP address assigned by the proxy

That's it! The ``ProxyHeaderManager`` handles sending your custom headers to the proxy and makes proxy response headers available in the response.

Using Proxies with urllib3
--------------------------

urllib3 provides built-in support for proxies through the ``urllib3.ProxyManager`` class. You can create a proxy manager that routes all requests through a proxy server.

Basic Proxy Usage (Standard urllib3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a proxy with standard urllib3:

.. code-block:: python

   import urllib3
   
   proxy = urllib3.ProxyManager('http://PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   print(r.data.decode())

This routes requests through the specified proxy server.

Proxy Authentication
~~~~~~~~~~~~~~~~~~~~

To use a proxy that requires authentication:

.. code-block:: python

   import urllib3
   
   # Include credentials in the URL
   proxy = urllib3.ProxyManager('http://username:password@PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')

Or use the ``proxy_headers`` parameter to set the ``Proxy-Authorization`` header manually.

Sending Custom Proxy Headers
----------------------------

If you just want to send custom proxy headers, but don't need to receive proxy response headers, you can use ``urllib3.ProxyManager`` with the ``proxy_headers`` parameter:

.. code-block:: python

   import urllib3
   
   proxy = urllib3.ProxyManager(
       'http://PROXYHOST:PORT',
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   r = proxy.request('GET', 'https://api.ipify.org?format=json')

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

.. note::

   When using this method, if you keep reusing the same ``ProxyManager`` instance, you may be re-using the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with `ProxyMesh <https://proxymesh.com>`_ you may keep getting the same IP address if you reuse the proxy connection.

Receiving Proxy Response Headers
---------------------------------

Standard urllib3 does not expose proxy response headers from the CONNECT request. To get proxy response headers, use our extension module ``python_proxy_headers.urllib3_proxy_manager``:

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   
   proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   
   # Proxy response headers are now available
   proxy_ip = r.headers.get('X-ProxyMesh-IP')
   print(f"Request was made through: {proxy_ip}")

The ``ProxyHeaderManager`` extends the standard ``ProxyManager`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

Sending and Receiving Proxy Headers
------------------------------------

You can combine sending custom headers with receiving proxy response headers:

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   
   # Send country preference, receive assigned IP
   proxy = urllib3_proxy_manager.ProxyHeaderManager(
       'http://PROXYHOST:PORT',
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   
   # Check which IP was assigned
   assigned_ip = r.headers.get('X-ProxyMesh-IP')
   print(f"Assigned IP: {assigned_ip}")

You can also pass back the same ``X-ProxyMesh-IP`` header to ensure you get the same IP address on subsequent requests:

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   
   # First request - get an IP
   proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   assigned_ip = r.headers.get('X-ProxyMesh-IP')
   
   # Second request - request the same IP
   proxy = urllib3_proxy_manager.ProxyHeaderManager(
       'http://PROXYHOST:PORT',
       proxy_headers={'X-ProxyMesh-IP': assigned_ip}
   )
   r = proxy.request('GET', 'https://api.ipify.org?format=json')

Helper Function
~~~~~~~~~~~~~~~

The module also provides a convenience function for creating a ``ProxyHeaderManager``:

.. code-block:: python

   from python_proxy_headers.urllib3_proxy_manager import proxy_from_url
   
   proxy = proxy_from_url(
       'http://PROXYHOST:PORT',
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   r.headers['X-ProxyMesh-IP']

The ``proxy_from_url()`` function is a convenience wrapper around ``ProxyHeaderManager`` that creates a proxy manager from a URL string, similar to urllib3's standard ``proxy_from_url()`` function.

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

API Reference
-------------

ProxyHeaderManager
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from python_proxy_headers.urllib3_proxy_manager import ProxyHeaderManager
   
   proxy = ProxyHeaderManager(
       proxy_url,           # The proxy URL (e.g., 'http://proxy.example.com:8080')
       proxy_headers=None,  # Optional dict of headers to send to the proxy
       **kwargs             # Additional arguments passed to urllib3.ProxyManager
   )

**Parameters:**

* ``proxy_url`` (str): The URL of the proxy server
* ``proxy_headers`` (dict, optional): Headers to send to the proxy in the CONNECT request
* ``**kwargs``: Additional arguments passed to the parent ``ProxyManager`` class

proxy_from_url
~~~~~~~~~~~~~~

.. code-block:: python

   from python_proxy_headers.urllib3_proxy_manager import proxy_from_url
   
   proxy = proxy_from_url(url, **kwargs)

A convenience function that creates a ``ProxyHeaderManager`` from a URL string.

Internal Classes
----------------

The ``ProxyHeaderManager`` internally uses extension classes that extend urllib3's connection and connection pool classes:

* ``HTTPSProxyConnection`` - Extends ``urllib3.connection.HTTPSConnection`` to capture proxy response headers from the CONNECT response
* ``HTTPSProxyConnectionPool`` - Extends ``urllib3.connectionpool.HTTPSConnectionPool`` to merge proxy response headers into the final HTTP response

These classes work together to make proxy response headers available in your application's response object.

HTTPSProxyConnection
~~~~~~~~~~~~~~~~~~~~

The ``HTTPSProxyConnection`` class extends the standard ``HTTPSConnection`` to capture proxy response headers during tunnel establishment. When a CONNECT request is made to establish the tunnel, it:

1. Sends the CONNECT request with any custom proxy headers
2. Reads the CONNECT response from the proxy server
3. Captures the proxy response headers (e.g., ``X-ProxyMesh-IP``)
4. Stores them for later retrieval via ``get_proxy_response_headers()``

The ``get_proxy_response_headers()`` method returns a dictionary containing the headers from the proxy's CONNECT response, or ``None`` if the CONNECT request hasn't been sent yet.

HTTPSProxyConnectionPool
~~~~~~~~~~~~~~~~~~~~~~~~

The ``HTTPSProxyConnectionPool`` class extends ``HTTPSConnectionPool`` to automatically merge proxy response headers into the final HTTP response. It:

1. Uses ``HTTPSProxyConnection`` as its connection class
2. Captures proxy response headers after preparing the proxy connection
3. Merges these headers into the response headers when ``urlopen()`` is called

This ensures that proxy response headers are automatically available in the response object returned to your application.
