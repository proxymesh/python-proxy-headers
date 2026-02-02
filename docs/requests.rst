requests
========

The `requests <https://docs.python-requests.org/en/latest/index.html>`_ library is a simple HTTP library for Python. This page describes how to use requests with proxies and how to send and receive custom proxy headers.

Getting Started
---------------

This section shows you how to quickly get up and running with proxy headers in requests.

**Prerequisites:**

1. Install the packages:

   .. code-block:: bash

      pip install python-proxy-headers requests

2. Import the module:

   .. code-block:: python

      from python_proxy_headers import requests_adapter

**Quick Example - Send and Receive Proxy Headers:**

.. code-block:: python

   from python_proxy_headers import requests_adapter
   
   # Make a request with custom proxy headers
   r = requests_adapter.get(
       'https://api.ipify.org?format=json',
       proxies={
           'http': 'http://PROXYHOST:PORT',
           'https': 'http://PROXYHOST:PORT'
       },
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   
   # Access the response data
   print(r.json())  # {"ip": "..."}
   
   # Access proxy response headers
   print(r.headers.get('X-ProxyMesh-IP'))  # The IP address assigned by the proxy

That's it! The ``requests_adapter`` module handles sending your custom headers to the proxy and makes proxy response headers available in the response.

Using Proxies with requests
---------------------------

The requests library provides built-in support for proxies through the ``proxies`` parameter. You can specify proxies for HTTP and HTTPS requests separately.

Basic Proxy Usage (Standard requests)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a proxy with standard requests:

.. code-block:: python

   import requests
   
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies)
   print(r.json())

This routes the request through the specified proxy server. You can specify different proxies for HTTP and HTTPS if needed.

Proxy Authentication
~~~~~~~~~~~~~~~~~~~~

To use a proxy that requires authentication:

.. code-block:: python

   import requests
   
   proxies = {
       'http': 'http://username:password@PROXYHOST:PORT',
       'https': 'http://username:password@PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies)

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

requests can also read proxy settings from environment variables:

.. code-block:: bash

   export HTTP_PROXY="http://PROXYHOST:PORT"
   export HTTPS_PROXY="http://PROXYHOST:PORT"

Then in your code:

.. code-block:: python

   import requests
   
   # Will automatically use proxies from environment variables
   r = requests.get('https://api.ipify.org?format=json')

Session-Level Proxies
~~~~~~~~~~~~~~~~~~~~~

You can configure proxies at the session level:

.. code-block:: python

   import requests
   
   session = requests.Session()
   session.proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = session.get('https://api.ipify.org?format=json')

Sending Custom Proxy Headers
----------------------------

Standard requests does not provide an easy way to send custom headers to the proxy (as opposed to the target server). Our ``requests_adapter`` module makes this easy:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   
   r = requests_adapter.get(
       'https://api.ipify.org?format=json',
       proxies={
           'http': 'http://PROXYHOST:PORT',
           'https': 'http://PROXYHOST:PORT'
       },
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )

The ``proxy_headers`` parameter allows you to send custom headers to the proxy server. This is useful for controlling proxy behavior, such as selecting a specific country or IP address.

Receiving Proxy Response Headers
---------------------------------

Standard requests does not expose proxy response headers from the CONNECT request. When using the ``requests_adapter`` module, proxy response headers are automatically available in the response headers:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   
   r = requests_adapter.get(
       'https://api.ipify.org?format=json',
       proxies={
           'http': 'http://PROXYHOST:PORT',
           'https': 'http://PROXYHOST:PORT'
       },
       proxy_headers={'X-ProxyMesh-Country': 'US'}
   )
   
   # Access proxy response headers
   proxy_ip = r.headers.get('X-ProxyMesh-IP')
   print(f"Request was made through: {proxy_ip}")

Available Methods
~~~~~~~~~~~~~~~~~

All standard requests methods are available through the adapter:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   
   # GET request
   r = requests_adapter.get('https://api.example.com', 
                           proxies=proxies, 
                           proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # POST request
   r = requests_adapter.post('https://api.example.com', 
                            json={'key': 'value'}, 
                            proxies=proxies, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # PUT request
   r = requests_adapter.put('https://api.example.com', 
                           json={'key': 'value'}, 
                           proxies=proxies, 
                           proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # DELETE request
   r = requests_adapter.delete('https://api.example.com', 
                              proxies=proxies, 
                              proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # PATCH request
   r = requests_adapter.patch('https://api.example.com', 
                             json={'status': 'active'}, 
                             proxies=proxies, 
                             proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # HEAD request
   r = requests_adapter.head('https://api.example.com', 
                            proxies=proxies, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # OPTIONS request
   r = requests_adapter.options('https://api.example.com', 
                               proxies=proxies, 
                               proxy_headers={'X-ProxyMesh-Country': 'US'})

All parameters that work with standard requests methods also work with the adapter methods, including ``params``, ``data``, ``json``, ``headers``, ``cookies``, ``auth``, ``timeout``, and more.

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

Session Support
---------------

For better connection pooling and cookie handling, you can use ``ProxySession``:

.. code-block:: python

   from python_proxy_headers.requests_adapter import ProxySession
   
   with ProxySession(proxy_headers={'X-ProxyMesh-Country': 'US'}) as session:
       session.proxies = {
           'http': 'http://PROXYHOST:PORT',
           'https': 'http://PROXYHOST:PORT'
       }
       
       # All requests through this session will include proxy headers
       r = session.get('https://api.example.com')
       proxy_ip = r.headers.get('X-ProxyMesh-IP')
       
       # Make multiple requests with the same session
       r2 = session.get('https://api.example.com/other')

Or you can manually mount the adapter to a standard requests Session:

.. code-block:: python

   from python_proxy_headers.requests_adapter import HTTPProxyHeaderAdapter
   import requests
   
   session = requests.Session()
   session.mount('http://', HTTPProxyHeaderAdapter(proxy_headers={'X-ProxyMesh-Country': 'US'}))
   session.mount('https://', HTTPProxyHeaderAdapter(proxy_headers={'X-ProxyMesh-Country': 'US'}))
   
   session.proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   
   r = session.get('https://api.example.com')
   proxy_ip = r.headers.get('X-ProxyMesh-IP')

API Reference
-------------

Helper Functions
~~~~~~~~~~~~~~~~

The module provides convenience functions that mirror the standard ``requests`` API:

* ``request(method, url, proxy_headers=None, **kwargs)`` - Make a request with the specified method
* ``get(url, proxy_headers=None, **kwargs)`` - Make a GET request
* ``post(url, proxy_headers=None, **kwargs)`` - Make a POST request
* ``put(url, proxy_headers=None, **kwargs)`` - Make a PUT request
* ``patch(url, proxy_headers=None, **kwargs)`` - Make a PATCH request
* ``delete(url, proxy_headers=None, **kwargs)`` - Make a DELETE request
* ``head(url, proxy_headers=None, **kwargs)`` - Make a HEAD request
* ``options(url, proxy_headers=None, **kwargs)`` - Make an OPTIONS request

Each function creates a temporary ``ProxySession`` with the specified ``proxy_headers`` and makes the request. All standard requests parameters (``params``, ``data``, ``json``, ``headers``, ``cookies``, ``auth``, ``proxies``, ``timeout``, etc.) are supported.

Extension Classes
-----------------

The ``python_proxy_headers.requests_adapter`` module provides extension classes that build on top of the ``urllib3_proxy_manager`` module to integrate proxy header support with the requests library.

HTTPProxyHeaderAdapter
~~~~~~~~~~~~~~~~~~~~~~

Extends ``requests.adapters.HTTPAdapter`` to use our custom ``ProxyHeaderManager`` for proxy connections. This adapter enables both sending custom proxy headers and receiving proxy response headers.

.. code-block:: python

   from python_proxy_headers.requests_adapter import HTTPProxyHeaderAdapter
   
   adapter = HTTPProxyHeaderAdapter(proxy_headers={'X-ProxyMesh-Country': 'US'})

**Constructor Parameters:**

* ``proxy_headers`` (dict, optional): A dictionary of custom headers to send to the proxy server. These headers will be included in the CONNECT request when establishing HTTPS tunnel connections.

The adapter overrides the ``proxy_manager_for`` method to:

1. Check if the proxy URL is already cached in ``self.proxy_manager``
2. For SOCKS proxies, delegate to the parent class
3. For HTTP/HTTPS proxies, create a ``ProxyHeaderManager`` from the ``urllib3_proxy_manager`` module with the custom proxy headers

This ensures that all proxy connections made through the adapter will include your custom headers and capture proxy response headers.

ProxySession
~~~~~~~~~~~~

Extends ``requests.Session`` with pre-configured ``HTTPProxyHeaderAdapter`` instances for both HTTP and HTTPS connections. This provides a convenient way to create a session that automatically handles proxy headers.

.. code-block:: python

   from python_proxy_headers.requests_adapter import ProxySession
   
   with ProxySession(proxy_headers={'X-ProxyMesh-Country': 'US'}) as session:
       session.proxies = {
           'http': 'http://PROXYHOST:PORT',
           'https': 'http://PROXYHOST:PORT'
       }
       r = session.get('https://api.example.com')
       proxy_ip = r.headers.get('X-ProxyMesh-IP')

**Constructor Parameters:**

* ``proxy_headers`` (dict, optional): A dictionary of custom headers to send to the proxy server.

The ``ProxySession`` automatically mounts ``HTTPProxyHeaderAdapter`` instances for both ``http://`` and ``https://`` URL schemes, so all requests through the session will use proxy header support.
