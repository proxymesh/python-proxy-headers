PycURL
======

The ``pycurl_proxy`` module provides proxy header support for PycURL.

Installation
------------

First, install PycURL::

    pip install pycurl

Then you can use the proxy header extension.

Usage
-----

Using the ProxyCurl Class
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ProxyCurl`` class wraps pycurl to provide easy proxy header handling:

.. code-block:: python

    from python_proxy_headers.pycurl_proxy import ProxyCurl

    # Create a ProxyCurl instance with proxy headers
    curl = ProxyCurl(proxy_headers={'X-ProxyMesh-Country': 'US'})

    # Make a request through a proxy
    response = curl.get(
        'https://httpbin.org/ip',
        proxy='http://user:pass@proxy.example.com:8080'
    )

    # Access the response
    print(response.status_code)
    print(response.text)

    # Access headers from the proxy's CONNECT response
    print(response.proxy_headers)
    print(response.proxy_status_code)

Using Convenience Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For one-off requests, use the module-level functions:

.. code-block:: python

    from python_proxy_headers import pycurl_proxy

    response = pycurl_proxy.get(
        'https://httpbin.org/ip',
        proxy='http://proxy.example.com:8080',
        proxy_headers={'X-Custom-Header': 'value'}
    )

    print(response.text)
    print(response.proxy_headers)

API Reference
-------------

ProxyCurl Class
~~~~~~~~~~~~~~~

.. py:class:: ProxyCurl(proxy_headers=None)

    PycURL wrapper with proxy header support.

    :param proxy_headers: Dict of headers to send to the proxy server

    .. py:method:: request(method, url, proxy=None, proxy_headers=None, headers=None, data=None, timeout=None, verify=True)

        Make an HTTP request with proxy header support.

        :param method: HTTP method (GET, POST, etc.)
        :param url: Target URL
        :param proxy: Proxy URL (e.g., 'http://user:pass@proxy:8080')
        :param proxy_headers: Headers to send to the proxy (merged with instance headers)
        :param headers: Headers to send to the origin server
        :param data: Request body for POST/PUT
        :param timeout: Request timeout in seconds
        :param verify: Whether to verify SSL certificates
        :returns: ProxyResponse object

    .. py:method:: get(url, **kwargs)
    .. py:method:: post(url, **kwargs)
    .. py:method:: put(url, **kwargs)
    .. py:method:: delete(url, **kwargs)
    .. py:method:: head(url, **kwargs)
    .. py:method:: options(url, **kwargs)
    .. py:method:: patch(url, **kwargs)

ProxyResponse Class
~~~~~~~~~~~~~~~~~~~

.. py:class:: ProxyResponse

    Response object containing body and headers from both proxy and origin.

    .. py:attribute:: status_code
        :type: int

        HTTP status code from the origin server.

    .. py:attribute:: headers
        :type: dict

        Headers from the origin server response.

    .. py:attribute:: content
        :type: bytes

        Response body as bytes.

    .. py:attribute:: proxy_headers
        :type: dict

        Headers from the proxy's CONNECT response (HTTPS only).

    .. py:attribute:: proxy_status_code
        :type: int or None

        Status code from the proxy's CONNECT response (HTTPS only).

    .. py:attribute:: text
        :type: str

        Response body decoded as UTF-8.

    .. py:method:: raise_for_status()

        Raise an exception if the status code indicates an error.
