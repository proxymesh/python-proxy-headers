CloudScraper
============

The ``cloudscraper_proxy`` module provides proxy header support for CloudScraper.

Installation
------------

First, install CloudScraper::

    pip install cloudscraper

Then you can use the proxy header extension.

Usage
-----

Using create_scraper()
~~~~~~~~~~~~~~~~~~~~~~

The ``create_scraper()`` function is a drop-in replacement for ``cloudscraper.create_scraper()`` 
that adds proxy header capabilities:

.. code-block:: python

    from python_proxy_headers.cloudscraper_proxy import create_scraper

    # Create a scraper with proxy headers
    scraper = create_scraper(
        proxy_headers={'X-ProxyMesh-Country': 'US'},
        browser='chrome'
    )

    # Set proxy
    scraper.proxies = {'https': 'http://user:pass@proxy.example.com:8080'}

    # Make requests - proxy headers are automatically sent
    response = scraper.get('https://httpbin.org/ip')
    print(response.text)

Using ProxyCloudScraper Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also use the ``ProxyCloudScraper`` class directly:

.. code-block:: python

    from python_proxy_headers.cloudscraper_proxy import ProxyCloudScraper

    scraper = ProxyCloudScraper(
        proxy_headers={'X-Custom-Header': 'value'},
        enable_stealth=True
    )

    scraper.proxies = {'https': 'http://proxy.example.com:8080'}
    response = scraper.get('https://example.com')

Updating Proxy Headers
~~~~~~~~~~~~~~~~~~~~~~

You can update proxy headers after creating the scraper:

.. code-block:: python

    scraper = create_scraper(proxy_headers={'X-Header': 'initial'})
    
    # Later, update headers
    scraper.set_proxy_headers({'X-Header': 'updated', 'X-New': 'value'})

All CloudScraper Features Preserved
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The extension preserves all CloudScraper features:

- Cloudflare bypass (v1, v2, v3, Turnstile)
- Browser emulation and user agent handling
- Cipher suite customization
- Proxy rotation
- Stealth mode
- Session management

.. code-block:: python

    scraper = create_scraper(
        proxy_headers={'X-ProxyMesh-Country': 'US'},
        browser='chrome',
        enable_stealth=True,
        stealth_options={
            'min_delay': 1.0,
            'max_delay': 3.0,
            'human_like_delays': True
        }
    )

API Reference
-------------

create_scraper()
~~~~~~~~~~~~~~~~

.. py:function:: create_scraper(proxy_headers=None, sess=None, **kwargs)

    Create a CloudScraper with proxy header support.

    :param proxy_headers: Dict of headers to send to proxy servers
    :param sess: Existing session to copy attributes from
    :param kwargs: All other arguments passed to CloudScraper
    :returns: ProxyCloudScraper instance

ProxyCloudScraper Class
~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: ProxyCloudScraper(proxy_headers=None, **kwargs)

    CloudScraper subclass with proxy header support.

    Inherits all methods and attributes from ``cloudscraper.CloudScraper``.

    :param proxy_headers: Dict of headers to send to proxy servers
    :param kwargs: All other arguments passed to CloudScraper

    .. py:method:: set_proxy_headers(proxy_headers)

        Update the proxy headers and remount adapters.

        :param proxy_headers: New proxy headers to use
