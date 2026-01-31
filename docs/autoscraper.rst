AutoScraper
===========

The ``autoscraper_proxy`` module provides proxy header support for AutoScraper.

Installation
------------

First, install AutoScraper::

    pip install autoscraper

Then you can use the proxy header extension.

Usage
-----

Basic Usage
~~~~~~~~~~~

The ``ProxyAutoScraper`` class is a drop-in replacement for ``AutoScraper`` 
that adds proxy header capabilities:

.. code-block:: python

    from python_proxy_headers.autoscraper_proxy import ProxyAutoScraper

    # Create a scraper with proxy headers
    scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})

    # Build rules from a sample page
    result = scraper.build(
        url='https://finance.yahoo.com/quote/AAPL/',
        wanted_list=['Apple Inc.'],
        request_args={'proxies': {'https': 'http://proxy.example.com:8080'}}
    )

    print(result)

Using Learned Rules
~~~~~~~~~~~~~~~~~~~

Once you've built rules, you can use them on other pages:

.. code-block:: python

    from python_proxy_headers.autoscraper_proxy import ProxyAutoScraper

    scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})

    # Build rules
    scraper.build(
        url='https://finance.yahoo.com/quote/AAPL/',
        wanted_list=['Apple Inc.'],
        request_args={'proxies': {'https': 'http://proxy:8080'}}
    )

    # Use rules on another page
    result = scraper.get_result_similar(
        url='https://finance.yahoo.com/quote/GOOG/',
        request_args={'proxies': {'https': 'http://proxy:8080'}}
    )

    print(result)  # ['Alphabet Inc.']

Saving and Loading Rules
~~~~~~~~~~~~~~~~~~~~~~~~

You can save and load learned rules:

.. code-block:: python

    scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})

    # Build and save rules
    scraper.build(url='...', wanted_list=['...'])
    scraper.save('my_rules.json')

    # Later, load rules
    scraper2 = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'UK'})
    scraper2.load('my_rules.json')

Context Manager
~~~~~~~~~~~~~~~

Use as a context manager to ensure proper cleanup:

.. code-block:: python

    with ProxyAutoScraper(proxy_headers={'X-Custom': 'value'}) as scraper:
        result = scraper.build(
            url='https://example.com',
            wanted_list=['Example Domain'],
            request_args={'proxies': {'https': 'http://proxy:8080'}}
        )

Updating Proxy Headers
~~~~~~~~~~~~~~~~~~~~~~

You can update proxy headers at runtime:

.. code-block:: python

    scraper = ProxyAutoScraper(proxy_headers={'X-Country': 'US'})

    # Make some requests...

    # Change proxy headers
    scraper.set_proxy_headers({'X-Country': 'UK'})

    # Subsequent requests use new headers

API Reference
-------------

ProxyAutoScraper Class
~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: ProxyAutoScraper(proxy_headers=None, stack_list=None)

    AutoScraper subclass with proxy header support.

    Inherits all methods from ``autoscraper.AutoScraper``.

    :param proxy_headers: Dict of headers to send to proxy servers
    :param stack_list: Initial stack list (rules) for the scraper

    .. py:method:: set_proxy_headers(proxy_headers)

        Update the proxy headers. Creates a new session on next request.

        :param proxy_headers: New proxy headers to use

    .. py:method:: close()

        Close the underlying session.

    .. py:method:: build(url=None, wanted_list=None, wanted_dict=None, html=None, request_args=None, update=False, text_fuzz_ratio=1.0)

        Build scraping rules with proxy header support.

        :param url: URL of the target web page
        :param wanted_list: List of needed contents to be scraped
        :param wanted_dict: Dict of needed contents (keys are aliases)
        :param html: HTML string (alternative to URL)
        :param request_args: Request arguments including proxies
        :param update: If True, add to existing rules
        :param text_fuzz_ratio: Fuzziness ratio for matching
        :returns: List of similar results

    .. py:method:: get_result_similar(url=None, html=None, soup=None, request_args=None, ...)

        Get similar results with proxy header support.

    .. py:method:: get_result_exact(url=None, html=None, soup=None, request_args=None, ...)

        Get exact results with proxy header support.

    .. py:method:: get_result(url=None, html=None, request_args=None, ...)

        Get both similar and exact results with proxy header support.
