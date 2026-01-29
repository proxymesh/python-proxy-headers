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

Purpose
-------

None of these modules provide good support for parsing custom response headers from proxy servers. And some of them make it hard to send custom headers to proxy servers. So we at `ProxyMesh <https://proxymesh.com>`_ made these extension modules to support our customers that use Python and want to use custom headers to control our proxy behavior. But these modules can work for handling custom headers with any proxy.

If you are looking for `Scrapy <https://scrapy.org/>`_ support, please see our `scrapy-proxy-headers <https://github.com/proxymesh/scrapy-proxy-headers>`_ project.

Features
--------

* **proxy CONNECT headers**: Easily handle custom headers for HTTPS CONNECT requests.
* **HTTPS tunnel proxy**: Support for using HTTPS tunnel proxies.
* **proxy IP address**: Control which proxy IP address is used for requests.
* **country proxy selection**: Select proxies based on their country of origin.
* **rotating proxy**: Use rotating proxies to avoid IP blocking.
* **proxy session**: Maintain a session with a proxy for multiple requests.
* **proxy connection pooling**: Efficiently manage connections to proxies.
* **async proxy**: Support for asynchronous proxy requests.
* **HTTP/2 proxy support**: Use HTTP/2 for faster proxy connections.

Why Use python-proxy-headers?
----------------------------

* **Ease of use**: Our extensions make it easy to add custom proxy headers to your existing Python code.
* **Flexibility**: You can use these extensions with any proxy, not just our own.
* **Performance**: Our extensions are optimized for performance, with support for connection pooling and asynchronous requests.
* **Compatibility**: We support the most popular Python HTTP libraries, so you can use these extensions with your existing code.

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
