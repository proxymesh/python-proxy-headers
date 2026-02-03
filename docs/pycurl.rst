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

Low-Level Helpers (for existing pycurl code)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you already have pycurl code, you can add proxy header support with minimal changes:

.. code-block:: python

    import pycurl
    from python_proxy_headers.pycurl_proxy import set_proxy_headers, HeaderCapture

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://httpbin.org/ip')
    c.setopt(pycurl.PROXY, 'http://proxy.example.com:8080')

    # Add custom headers to send to the proxy
    set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})

    # Capture response headers (installs HEADERFUNCTION callback)
    capture = HeaderCapture(c)

    c.perform()

    # Access headers from the proxy's CONNECT response
    print(capture.proxy_headers)   # {'X-ProxyMesh-IP': '1.2.3.4', ...}
    print(capture.proxy_status)    # 200

    # Access headers from the origin server
    print(capture.origin_headers)  # {'Content-Type': 'application/json', ...}

    c.close()

High-Level Convenience Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For simpler use cases, use the module-level functions:

.. code-block:: python

    from python_proxy_headers.pycurl_proxy import get

    response = get(
        'https://httpbin.org/ip',
        proxy='http://proxy.example.com:8080',
        proxy_headers={'X-ProxyMesh-Country': 'US'}
    )

    print(response.status_code)
    print(response.text)
    print(response.proxy_headers)

API Reference
-------------

Low-Level Functions
~~~~~~~~~~~~~~~~~~~

.. py:function:: set_proxy_headers(curl, headers)

    Set custom headers to send to the proxy server during CONNECT.

    :param curl: A pycurl.Curl instance
    :param headers: Dict of headers to send to the proxy

.. py:class:: HeaderCapture(curl=None)

    Captures and parses HTTP response headers from pycurl requests.

    :param curl: Optional pycurl.Curl instance. If provided, automatically
                 installs the HEADERFUNCTION callback.

    .. py:method:: install(curl)

        Install the header callback on a pycurl.Curl instance.

        :param curl: A pycurl.Curl instance
        :returns: self, for chaining

    .. py:method:: reset()

        Clear captured headers for reuse.

    .. py:attribute:: proxy_headers
        :type: dict

        Headers from the proxy's CONNECT response.

    .. py:attribute:: proxy_status
        :type: int or None

        Status code from the proxy's CONNECT response.

    .. py:attribute:: origin_headers
        :type: dict

        Headers from the origin server's response.

    .. py:attribute:: origin_status
        :type: int or None

        Status code from the origin server's response.

    .. py:attribute:: all_headers
        :type: dict

        All headers merged (proxy headers first, then origin).

High-Level Functions
~~~~~~~~~~~~~~~~~~~~

.. py:function:: request(method, url, proxy=None, proxy_headers=None, headers=None, data=None, timeout=None, verify=True)

    Make an HTTP request with proxy header support.

    :param method: HTTP method (GET, POST, etc.)
    :param url: Target URL
    :param proxy: Proxy URL (e.g., 'http://user:pass@proxy:8080')
    :param proxy_headers: Headers to send to the proxy
    :param headers: Headers to send to the origin server
    :param data: Request body for POST/PUT/PATCH
    :param timeout: Request timeout in seconds
    :param verify: Whether to verify SSL certificates
    :returns: Response object

.. py:function:: get(url, **kwargs)
.. py:function:: post(url, **kwargs)
.. py:function:: put(url, **kwargs)
.. py:function:: delete(url, **kwargs)
.. py:function:: head(url, **kwargs)
.. py:function:: patch(url, **kwargs)

Response Class
~~~~~~~~~~~~~~

.. py:class:: Response

    Response object from high-level API.

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

    .. py:attribute:: proxy_status
        :type: int or None

        Status code from the proxy's CONNECT response (HTTPS only).

    .. py:attribute:: text
        :type: str

        Response body decoded as UTF-8.

    .. py:method:: raise_for_status()

        Raise an exception if the status code indicates an error.
