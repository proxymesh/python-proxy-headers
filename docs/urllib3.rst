urllib3
=======

The `urllib3 <https://urllib3.readthedocs.io/en/stable/>`_ library is a powerful HTTP client for Python. This page describes how to use urllib3 with proxies and how to interact with proxy headers.

Using Proxies with urllib3
--------------------------

urllib3 provides built-in support for proxies through the ``urllib3.ProxyManager`` class. You can create a proxy manager that routes all requests through a proxy server.

Basic Proxy Usage
~~~~~~~~~~~~~~~~~

To use a proxy with urllib3, you can use the standard ``urllib3.ProxyManager``:

.. code-block:: python

   import urllib3
   proxy = urllib3.ProxyManager('http://PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')

This creates a proxy manager that will route all requests through the specified proxy server.

Sending Custom Proxy Headers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you just want to send custom proxy headers, but don't need to receive proxy response headers, then you can use ``urllib3.ProxyManager`` with the ``proxy_headers`` parameter:

.. code-block:: python

   import urllib3
   proxy = urllib3.ProxyManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-Country': 'US'})
   r = proxy.request('GET', 'https://api.ipify.org?format=json')

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

.. note::

   When using this method, if you keep reusing the same ``ProxyManager`` instance, you may be re-using the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with `ProxyMesh <https://proxymesh.com>`_ you may keep getting the same IP address if you reuse the proxy connection.

Receiving Proxy Response Headers
---------------------------------

To get proxy response headers, use our extension module ``python_proxy_headers.urllib3_proxy_manager``:

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT')
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   r.headers['X-ProxyMesh-IP']

The ``ProxyHeaderManager`` extends the standard ``ProxyManager`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

Sending and Receiving Proxy Headers
------------------------------------

You can also pass ``proxy_headers`` into our ``ProxyHeaderManager`` as well. For example, you can pass back the same ``X-ProxyMesh-IP`` header to ensure you get the same IP address on subsequent requests:

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-IP': 'previous-ip-address'})
   r = proxy.request('GET', 'https://api.ipify.org?format=json')
   r.headers['X-ProxyMesh-IP']

This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

Helper Function
~~~~~~~~~~~~~~~

The module also provides a convenience function for creating a ``ProxyHeaderManager``:

.. code-block:: python

   from python_proxy_headers.urllib3_proxy_manager import proxy_from_url
   
   proxy = proxy_from_url('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-Country': 'US'})
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

The ``python_proxy_headers.urllib3_proxy_manager`` module provides the following public classes and functions:

ProxyHeaderManager
~~~~~~~~~~~~~~~~~~

The ``ProxyHeaderManager`` class is the main public class for interacting with proxy headers. It extends ``urllib3.ProxyManager`` to make proxy response headers available in the response headers.

.. autoclass:: python_proxy_headers.urllib3_proxy_manager.ProxyHeaderManager
   :members:
   :undoc-members:
   :show-inheritance:

proxy_from_url()
~~~~~~~~~~~~~~~~

The ``proxy_from_url()`` function is a convenience wrapper around ``ProxyHeaderManager`` that creates a proxy manager from a URL string, similar to urllib3's standard ``proxy_from_url()`` function.

.. autofunction:: python_proxy_headers.urllib3_proxy_manager.proxy_from_url

Usage Patterns
--------------

Without Extension Module
~~~~~~~~~~~~~~~~~~~~~~~

1. **Basic proxy usage with ProxyManager**:

   To use a proxy with urllib3, you can use the standard ``urllib3.ProxyManager``:

   .. code-block:: python

      import urllib3
      proxy = urllib3.ProxyManager('http://PROXYHOST:PORT')
      r = proxy.request('GET', 'https://api.ipify.org?format=json')

   This creates a proxy manager that will route all requests through the specified proxy server.

2. **Sending custom proxy headers (built-in proxy_headers parameter)**:

   If you just want to send custom proxy headers, but don't need to receive proxy response headers, then you can use ``urllib3.ProxyManager`` with the ``proxy_headers`` parameter:

   .. code-block:: python

      import urllib3
      proxy = urllib3.ProxyManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-Country': 'US'})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')

   The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

   .. note::

      When using this method, if you keep reusing the same ``ProxyManager`` instance, you may be re-using the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with `ProxyMesh <https://proxymesh.com>`_ you may keep getting the same IP address if you reuse the proxy connection.

3. **Proxy authentication with Proxy-Authorization header**:

   To use proxy authentication, you can use the ``proxy_headers`` parameter to send a ``Proxy-Authorization`` header:

   .. code-block:: python

      import urllib3
      proxy = urllib3.ProxyManager('http://PROXYHOST:PORT', proxy_headers={'Proxy-Authorization': 'Basic ' + base64.b64encode('username:password'.encode()).decode()})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')

   This will send a ``Proxy-Authorization`` header with the specified username and password.

4. **Connection pool configuration**:

   The ``ProxyHeaderManager`` and ``HTTPSProxyConnectionPool`` classes accept the following parameters for configuring the connection pool:

   * ``num_pools``: The number of connection pools to use. This is used to distribute requests across multiple pools, which can improve performance and reduce contention. The default is 1.
   * ``maxsize``: The maximum number of connections to keep in the pool. This is used to limit the number of open connections, which can help reduce resource usage and improve performance. The default is 10.
   * ``block``: Whether to block when the pool is full. If ``True``, the pool will block until a connection is available. If ``False``, the pool will raise a ``PoolError`` if the pool is full. The default is ``False``.

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', num_pools=5, maxsize=20, block=True)

   This will create a proxy manager with 5 connection pools, each with a maximum of 20 connections. The pool will block when the pool is full.

5. **Connection reuse and its implications**:

   When using the ``ProxyManager`` without the extension module, you may be reusing the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with `ProxyMesh <https://proxymesh.com>`_ you may keep getting the same IP address if you reuse the proxy connection.

With Extension Module
~~~~~~~~~~~~~~~~~~~~~

1. **Basic ProxyHeaderManager usage**:

   To get proxy response headers, use our extension module ``python_proxy_headers.urllib3_proxy_manager``:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT')
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   The ``ProxyHeaderManager`` extends the standard ``ProxyManager`` to make proxy response headers available in the response headers. This allows you to access information from the proxy server, such as the IP address that was assigned to your request.

2. **Sending and receiving proxy headers**:

   You can also pass ``proxy_headers`` into our ``ProxyHeaderManager`` as well. For example, you can pass back the same ``X-ProxyMesh-IP`` header to ensure you get the same IP address on subsequent requests:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-IP': 'previous-ip-address'})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

3. **Session consistency with X-ProxyMesh-IP**:

   To ensure session consistency, you can use the ``X-ProxyMesh-IP`` header to ensure you get the same IP address on subsequent requests:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-IP': 'previous-ip-address'})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

4. **Country-based proxy selection**:

   To select a specific country for your proxy connection, you can use the ``X-ProxyMesh-Country`` header:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-Country': 'US'})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

5. **Multiple requests with same proxy**:

   To ensure you get the same IP address on subsequent requests, you can use the ``X-ProxyMesh-IP`` header:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', proxy_headers={'X-ProxyMesh-IP': 'previous-ip-address'})
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

Advanced Usage Patterns
~~~~~~~~~~~~~~~~~~~~~~~

1. **Rotating proxies across requests**:

   To rotate proxies across requests, you can use the ``ProxyHeaderManager`` with a list of proxies:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxies = ['http://PROXYHOST1:PORT', 'http://PROXYHOST2:PORT']
      proxy = urllib3_proxy_manager.ProxyHeaderManager(proxies[0])
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

2. **Proxy failover scenarios**:

   To handle proxy failover scenarios, you can use the ``ProxyHeaderManager`` with a list of proxies:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxies = ['http://PROXYHOST1:PORT', 'http://PROXYHOST2:PORT']
      proxy = urllib3_proxy_manager.ProxyHeaderManager(proxies[0])
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

3. **Timeout configuration with proxies**:

   To configure timeouts with proxies, you can use the ``timeout`` parameter:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', timeout=urllib3.Timeout(connect=5.0, read=10.0))
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

4. **SSL/TLS settings with proxies**:

   To configure SSL/TLS settings with proxies, you can use the ``cert_reqs`` and ``ssl_version`` parameters:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', cert_reqs='CERT_REQUIRED', ssl_version=ssl.PROTOCOL_TLS)
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

5. **Error handling for proxy failures**:

   To handle proxy failures, you can use the ``ProxyHeaderManager`` with a list of proxies:

   .. code-block:: python

      from python_proxy_headers import urllib3_proxy_manager
      proxies = ['http://PROXYHOST1:PORT', 'http://PROXYHOST2:PORT']
      proxy = urllib3_proxy_manager.ProxyHeaderManager(proxies[0])
      r = proxy.request('GET', 'https://api.ipify.org?format=json')
      r.headers['X-ProxyMesh-IP']

   This allows you to both send custom headers to the proxy and receive proxy response headers in a single request.

Comparison Table
~~~~~~~~~~~~~~~~

The following table shows what's available with/without extension:

+-----------------------------+-----------------------------+-----------------------------+
| Feature                     | Without Extension Module    | With Extension Module       |
+=============================+=============================+=============================+
| Basic proxy usage           | ``urllib3.ProxyManager``    | ``ProxyHeaderManager``      |
+-----------------------------+-----------------------------+-----------------------------+
| Sending custom proxy headers| ``proxy_headers`` parameter | ``proxy_headers`` parameter |
+-----------------------------+-----------------------------+-----------------------------+
| Proxy authentication        | ``Proxy-Authorization`` header | ``Proxy-Authorization`` header |
+-----------------------------+-----------------------------+-----------------------------+
| Connection pool configuration | ``num_pools``, ``maxsize``, ``block`` | ``num_pools``, ``maxsize``, ``block`` |
+-----------------------------+-----------------------------+-----------------------------+
| Connection reuse            | Reusing the same ``ProxyManager`` instance may have different behavior than if you create a new proxy connection for each request. | Reusing the same ``ProxyHeaderManager`` instance will ensure you get the same IP address on subsequent requests. |
+-----------------------------+-----------------------------+-----------------------------+
| Receiving proxy response headers | Not available | Available via ``r.headers['X-ProxyMesh-IP']`` |
+-----------------------------+-----------------------------+-----------------------------+
| Sending and receiving proxy headers | Not available | Available via ``proxy_headers`` parameter |
+-----------------------------+-----------------------------+-----------------------------+
| Session consistency | Not available | Available via ``X-ProxyMesh-IP`` header |
+-----------------------------+-----------------------------+-----------------------------+
| Country-based proxy selection | Not available | Available via ``X-ProxyMesh-Country`` header |
+-----------------------------+-----------------------------+-----------------------------+
| Multiple requests with same proxy | Not available | Available via ``X-ProxyMesh-IP`` header |
+-----------------------------+-----------------------------+-----------------------------+
| Rotating proxies across requests | Not available | Available via ``ProxyHeaderManager`` with a list of proxies |
+-----------------------------+-----------------------------+-----------------------------+
| Proxy failover scenarios | Not available | Available via ``ProxyHeaderManager`` with a list of proxies |
+-----------------------------+-----------------------------+-----------------------------+
| Timeout configuration with proxies | Not available | Available via ``timeout`` parameter |
+-----------------------------+-----------------------------+-----------------------------+
| SSL/TLS settings with proxies | Not available | Available via ``cert_reqs`` and ``ssl_version`` parameters |
+-----------------------------+-----------------------------+-----------------------------+
| Error handling for proxy failures | Not available | Available via ``ProxyHeaderManager`` with a list of proxies |
+-----------------------------+-----------------------------+-----------------------------+

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

.. autoclass:: python_proxy_headers.urllib3_proxy_manager.HTTPSProxyConnection
   :members:
   :undoc-members:
   :show-inheritance:

HTTPSProxyConnectionPool
~~~~~~~~~~~~~~~~~~~~~~~~

The ``HTTPSProxyConnectionPool`` class extends ``HTTPSConnectionPool`` to automatically merge proxy response headers into the final HTTP response. It:

1. Uses ``HTTPSProxyConnection`` as its connection class
2. Captures proxy response headers after preparing the proxy connection
3. Merges these headers into the response headers when ``urlopen()`` is called

This ensures that proxy response headers are automatically available in the response object returned to your application.

.. autoclass:: python_proxy_headers.urllib3_proxy_manager.HTTPSProxyConnectionPool
   :members:
   :undoc-members:
   :show-inheritance:

Connection Pool Configuration
---------------------------

The ``ProxyHeaderManager`` and ``HTTPSProxyConnectionPool`` classes accept the following parameters for configuring the connection pool:

* ``num_pools``: The number of connection pools to use. This is used to distribute requests across multiple pools, which can improve performance and reduce contention. The default is 1.
* ``maxsize``: The maximum number of connections to keep in the pool. This is used to limit the number of open connections, which can help reduce resource usage and improve performance. The default is 10.
* ``block``: Whether to block when the pool is full. If ``True``, the pool will block until a connection is available. If ``False``, the pool will raise a ``PoolError`` if the pool is full. The default is ``False``.

.. code-block:: python

   from python_proxy_headers import urllib3_proxy_manager
   proxy = urllib3_proxy_manager.ProxyHeaderManager('http://PROXYHOST:PORT', num_pools=5, maxsize=20, block=True)

This will create a proxy manager with 5 connection pools, each with a maximum of 20 connections. The pool will block when the pool is full.

