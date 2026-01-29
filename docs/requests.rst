requests
========

The `requests <https://docs.python-requests.org/en/latest/index.html>`_ library is a simple HTTP library for Python. This page describes how to use requests with proxies and how to interact with proxy headers.

Using Proxies with requests
---------------------------

The requests library provides built-in support for proxies through the ``proxies`` parameter. You can specify proxies for HTTP and HTTPS requests separately.

Basic Proxy Usage
~~~~~~~~~~~~~~~~~

To use a proxy with requests, you can pass the ``proxies`` parameter to any request method:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies)

This routes the request through the specified proxy server. You can specify different proxies for HTTP and HTTPS if needed.

Sending Custom Proxy Headers
-----------------------------

The requests adapter builds on our ``urllib3_proxy_manager`` module to make it easy to pass in proxy headers and receive proxy response headers.

Using the Extension Module
~~~~~~~~~~~~~~~~~~~~~~~~~~

To send custom proxy headers and receive proxy response headers, use our ``python_proxy_headers.requests_adapter`` module:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   r = requests_adapter.get('https://api.ipify.org?format=json', 
                            proxies={'http': 'http://PROXYHOST:PORT', 
                                    'https': 'http://PROXYHOST:PORT'}, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'})
   r.headers['X-ProxyMesh-IP']

The ``requests_adapter`` module supports all the standard requests methods: ``get``, ``post``, ``put``, ``delete``, ``patch``, ``head``, and ``options``.

Available Methods
~~~~~~~~~~~~~~~~~

All standard requests methods are available through the adapter:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   
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

All parameters that work with standard requests methods also work with the adapter methods, including ``params``, ``data``, ``json``, ``headers``, ``cookies``, ``auth``, and more.

Receiving Proxy Response Headers
---------------------------------

When using the ``requests_adapter`` module, proxy response headers are automatically available in the response headers:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   r = requests_adapter.get('https://api.ipify.org?format=json', 
                           proxies=proxies, 
                           proxy_headers={'X-ProxyMesh-Country': 'US'})
   
   # Access proxy response headers
   proxy_ip = r.headers.get('X-ProxyMesh-IP')
   print(f"Proxy IP: {proxy_ip}")

Usage Patterns
--------------

Without Extension Module
~~~~~~~~~~~~~~~~~~~~~~~

1. **Basic proxy usage with requests.get() and proxies parameter**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies)

2. **Proxy authentication with auth parameter**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   auth = ('username', 'password')
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies, auth=auth)

3. **Different proxies for HTTP and HTTPS**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies)

4. **Session usage with built-in proxy support**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   session = requests.Session()
   session.proxies = proxies
   r = session.get('https://api.ipify.org?format=json')

With Extension Module
~~~~~~~~~~~~~~~~~~~~~

1. **Using requests_adapter helper functions**:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   r = requests_adapter.get('https://api.ipify.org?format=json', 
                            proxies={'http': 'http://PROXYHOST:PORT', 
                                    'https': 'http://PROXYHOST:PORT'}, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'})

2. **Using ProxySession with mounts**:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   import requests
   
   session = requests.Session()
   session.mount('http://', requests_adapter.HTTPAdapter())
   session.mount('https://', requests_adapter.HTTPAdapter())
   
   r = session.get('https://api.example.com', 
                   proxies=proxies, 
                   proxy_headers={'X-ProxyMesh-Country': 'US'})

3. **Sending and receiving proxy headers**:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   r = requests_adapter.get('https://api.ipify.org?format=json', 
                            proxies={'http': 'http://PROXYHOST:PORT', 
                                    'https': 'http://PROXYHOST:PORT'}, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'})
   r.headers['X-ProxyMesh-IP']

4. **Session consistency patterns**:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   import requests
   
   session = requests.Session()
   session.mount('http://', requests_adapter.HTTPAdapter())
   session.mount('https://', requests_adapter.HTTPAdapter())
   
   r = session.get('https://api.example.com', 
                   proxies=proxies, 
                   proxy_headers={'X-ProxyMesh-Country': 'US'})

Advanced Usage Patterns
~~~~~~~~~~~~~~~~~~~~~~~

1. **Rotating proxies across requests**:

.. code-block:: python

   import requests
   proxies = [
       {'http': 'http://PROXYHOST1:PORT', 'https': 'http://PROXYHOST1:PORT'},
       {'http': 'http://PROXYHOST2:PORT', 'https': 'http://PROXYHOST2:PORT'}
   ]
   for proxy in proxies:
       r = requests.get('https://api.ipify.org?format=json', proxies=proxy)

2. **Proxy failover scenarios**:

.. code-block:: python

   import requests
   proxies = [
       {'http': 'http://PROXYHOST1:PORT', 'https': 'http://PROXYHOST1:PORT'},
       {'http': 'http://PROXYHOST2:PORT', 'https': 'http://PROXYHOST2:PORT'}
   ]
   for proxy in proxies:
       try:
           r = requests.get('https://api.ipify.org?format=json', proxies=proxy)
       except requests.exceptions.RequestException:
           continue

3. **Connection pooling with sessions**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   session = requests.Session()
   session.proxies = proxies
   r = session.get('https://api.ipify.org?format=json')

4. **Timeout configuration with proxies**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   r = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)

5. **Error handling for proxy failures**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   try:
       r = requests.get('https://api.ipify.org?format=json', proxies=proxies)
   except requests.exceptions.RequestException:
       pass

6. **Cookie persistence with proxy sessions**:

.. code-block:: python

   import requests
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   session = requests.Session()
   session.proxies = proxies
   r = session.get('https://api.ipify.org?format=json')

Comparison Table
~~~~~~~~~~~~~~~~

+-----------------------------+-----------------------------+-----------------------------+
| Feature                     | Without Extension Module    | With Extension Module       |
+-----------------------------+-----------------------------+-----------------------------+
| Basic proxy usage           | ``requests.get(url, proxies)`` | ``requests_adapter.get(url, proxies)`` |
| Proxy authentication        | ``requests.get(url, proxies, auth)`` | ``requests_adapter.get(url, proxies, auth)`` |
| Different proxies for HTTP  | ``requests.get(url, proxies)`` | ``requests_adapter.get(url, proxies)`` |
| and HTTPS                 |                             |                             |
| Session usage               | ``session = requests.Session()`` | ``session = requests.Session()`` |
|                             | ``session.proxies = proxies`` | ``session.mount('http://', HTTPAdapter())`` |
|                             | ``session.mount('https://', HTTPAdapter())`` | ``session.mount('https://', HTTPAdapter())`` |
|                             | ``r = session.get(url, proxies)`` | ``r = session.get(url, proxies)`` |
| Sending custom headers      | ``requests.get(url, proxies, headers)`` | ``requests_adapter.get(url, proxies, proxy_headers)`` |
| Receiving proxy headers     | Not available               | ``r.headers['X-ProxyMesh-IP']`` |
| Session consistency       | Not available               | ``session.mount('http://', HTTPAdapter())`` |
|                             | ``session.mount('https://', HTTPAdapter())`` | ``session.mount('https://', HTTPAdapter())`` |
| Rotating proxies          | ``proxies = [...]`` | ``proxies = [...]`` |
|                             | ``for proxy in proxies:`` | ``for proxy in proxies:`` |
|                             | ``r = requests.get(url, proxies=proxy)`` | ``r = requests_adapter.get(url, proxies=proxy)`` |
| Proxy failover            | ``try:`` | ``try:`` |
|                             | ``r = requests.get(url, proxies=proxy)`` | ``r = requests_adapter.get(url, proxies=proxy)`` |
|                             | ``except requests.exceptions.RequestException:`` | ``except requests.exceptions.RequestException:`` |
|                             | ``continue`` | ``continue`` |
| Connection pooling        | ``session = requests.Session()`` | ``session = requests.Session()`` |
|                             | ``session.proxies = proxies`` | ``session.mount('http://', HTTPAdapter())`` |
|                             | ``r = session.get(url, proxies)`` | ``session.mount('https://', HTTPAdapter())`` |
|                             | ``r = session.get(url, proxies)`` | ``r = session.get(url, proxies)`` |
| Timeout configuration     | ``requests.get(url, proxies, timeout)`` | ``requests_adapter.get(url, proxies, timeout)`` |
| Error handling            | ``try:`` | ``try:`` |
|                             | ``r = requests.get(url, proxies)`` | ``r = requests_adapter.get(url, proxies)`` |
|                             | ``except requests.exceptions.RequestException:`` | ``except requests.exceptions.RequestException:`` |
| Cookie persistence        | ``session = requests.Session()`` | ``session = requests.Session()`` |
|                             | ``session.proxies = proxies`` | ``session.mount('http://', HTTPAdapter())`` |
|                             | ``r = session.get(url, proxies)`` | ``session.mount('https://', HTTPAdapter())`` |
|                             | ``r = session.get(url, proxies)`` | ``r = session.get(url, proxies)`` |
+-----------------------------+-----------------------------+-----------------------------+

Proxy Headers Overview
----------------------

Proxy headers are custom HTTP headers that can be used to communicate with proxy servers. They allow you to:

* **Control proxy behavior**: Send headers like ``X-ProxyMesh-Country`` to select a specific country for your proxy connection
* **Receive proxy information**: Get headers like ``X-ProxyMesh-IP`` to know which IP address was assigned to your request
* **Maintain session consistency**: Use headers like ``X-ProxyMesh-IP`` to ensure you get the same IP address across multiple requests

The exact headers available depend on your proxy provider. Check your proxy provider's documentation for the specific headers they support.

Session Support
---------------

You can also use the adapter with requests Sessions for better connection pooling and cookie handling:

.. code-block:: python

   from python_proxy_headers import requests_adapter
   import requests
   
   session = requests.Session()
   session.mount('http://', requests_adapter.HTTPAdapter())
   session.mount('https://', requests_adapter.HTTPAdapter())
   
   r = session.get('https://api.example.com', 
                   proxies=proxies, 
                   proxy_headers={'X-ProxyMesh-Country': 'US'})

API Reference
-------------

HTTPProxyHeaderAdapter
~~~~~~~~~~~~~~~~~~~~~~

The adapter class for sending custom proxy headers and receiving proxy response headers.

.. autoclass:: python_proxy_headers.requests_adapter.HTTPProxyHeaderAdapter
   :members:
   :undoc-members:
   :show-inheritance:

ProxySession
~~~~~~~~~~~~

The session class for using the adapter with requests Sessions.

.. autoclass:: python_proxy_headers.requests_adapter.ProxySession
   :members:
   :undoc-members:
   :show-inheritance:

request()
~~~~~~~~~

The main function for sending HTTP requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.request

get()
~~~~

The function for sending HTTP GET requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.get

post()
~~~~~

The function for sending HTTP POST requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.post

put()
~~~~~

The function for sending HTTP PUT requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.put

delete()
~~~~~~~

The function for sending HTTP DELETE requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.delete

patch()
~~~~~~~

The function for sending HTTP PATCH requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.patch

head()
~~~~~~~

The function for sending HTTP HEAD requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.head

options()
~~~~~~~~~

The function for sending HTTP OPTIONS requests with custom proxy headers.

.. autofunction:: python_proxy_headers.requests_adapter.options

Connection Pool Configuration
---------------------------

You can configure the connection pool for the adapter using the ``pool_connections`` and ``pool_maxsize`` parameters.

.. code-block:: python

   from python_proxy_headers import requests_adapter
   import requests
   
   session = requests.Session()
   session.mount('http://', requests_adapter.HTTPAdapter(pool_connections=10, pool_maxsize=10))
   session.mount('https://', requests_adapter.HTTPAdapter(pool_connections=10, pool_maxsize=10))
   
   r = session.get('https://api.example.com', 
                   proxies=proxies, 
                   proxy_headers={'X-ProxyMesh-Country': 'US'})

Proxy Authentication
-------------------

You can use the ``auth`` parameter to pass in a tuple of username and password for proxy authentication.

.. code-block:: python

   from python_proxy_headers import requests_adapter
   import requests
   
   proxies = {
       'http': 'http://PROXYHOST:PORT',
       'https': 'http://PROXYHOST:PORT'
   }
   auth = ('username', 'password')
   
   r = requests_adapter.get('https://api.ipify.org?format=json', 
                            proxies=proxies, 
                            proxy_headers={'X-ProxyMesh-Country': 'US'}, 
                            auth=auth)

