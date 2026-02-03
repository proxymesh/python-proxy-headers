.. python-proxy-headers documentation master file, created by
   sphinx-quickstart on Tue Dec 30 13:19:25 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-proxy-headers's documentation!
================================================

The ``python-proxy-headers`` package provides support for handling custom proxy headers when making HTTPS requests in various Python modules.

We currently provide extensions to the following packages:

* :doc:`urllib3 <urllib3>` - HTTP client library
* :doc:`requests <requests>` - Simple HTTP library for Python
* :doc:`aiohttp <aiohttp>` - Async HTTP client/server framework
* :doc:`httpx <httpx>` - Modern HTTP client library
* :doc:`pycurl <pycurl>` - Python interface to libcurl
* :doc:`autoscraper <autoscraper>` - Smart automatic web scraper

Purpose
-------

None of these modules provide good support for parsing custom response headers from proxy servers. And some of them make it hard to send custom headers to proxy servers. So we at `ProxyMesh <https://proxymesh.com>`_ made these extension modules to support our customers that use Python and want to use custom headers to control our proxy behavior. But these modules can work for handling custom headers with any proxy.

If you are looking for `Scrapy <https://scrapy.org/>`_ support, please see our `scrapy-proxy-headers <https://github.com/proxymesh/scrapy-proxy-headers>`_ project.

Installation
------------

To use these extension modules, you must first do the following:

1. Install the package:

   .. code-block:: bash

      pip install python-proxy-headers

2. Install the appropriate package based on the Python module you want to use.

This package does not have any dependencies because we don't know which module you want to use.

You can also find more example code in our `proxy-examples for python <https://github.com/proxymesh/proxy-examples/tree/main/python>`_.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   urllib3
   requests
   aiohttp
   httpx
   pycurl
   autoscraper

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
