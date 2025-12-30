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

   When using this method, if you keep reusing the same ``ProxyManager`` instance, you may be re-using the proxy connection, which may have different behavior than if you create a new proxy connection for each request. For example, with ProxyMesh you may keep getting the same IP address if you reuse the proxy connection.

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

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

