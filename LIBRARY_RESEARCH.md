# Python Library Proxy Header Support Research

This document analyzes Python web scraping/automation libraries for their proxy support and potential for python-proxy-headers extension modules.

## Executive Summary

After reviewing 14 Python libraries, **none of them natively support sending custom headers to proxies or receiving proxy response headers** during HTTPS CONNECT tunneling. This is because:

1. Browser automation tools (Playwright, Selenium, etc.) delegate proxy handling to the browser, which doesn't expose proxy headers
2. Higher-level scraping frameworks use underlying HTTP libraries (requests, httpx, aiohttp) that already lack this support
3. Libraries wrapping curl inherit libcurl's limitations around proxy header handling

---

## Library Analysis

### 1. cloudscraper (6,060 stars)
**GitHub:** https://github.com/venomous/cloudscraper  
**Last Pushed:** 2025-06-10  
**Description:** Python module to bypass Cloudflare's anti-bot page

**Proxy Support:**
- Uses `requests` library under the hood
- Supports proxy rotation via `rotating_proxies` parameter
- Standard requests-style proxy dict: `proxies={"http": "...", "https": "..."}`

**Custom Proxy Headers:** ❌ No
- Inherits requests' limitations
- Cannot send custom headers to proxy or receive proxy response headers

**Extension Feasibility:** ✅ HIGH
- Since cloudscraper wraps requests.Session, users can use our existing `HTTPProxyHeaderAdapter` 
- Could create a `CloudScraperProxySession` that combines cloudscraper's features with proxy header support

---

### 2. curl_cffi (4,873 stars)
**GitHub:** https://github.com/lexiforest/curl_cffi  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** Python binding for curl-impersonate via cffi, can impersonate browser TLS/JA3 fingerprints

**Proxy Support:**
- Supports HTTP/SOCKS proxies via `proxies` parameter
- Uses libcurl under the hood

**Custom Proxy Headers:** ❌ No
- libcurl's `CURLOPT_PROXYHEADER` could theoretically be exposed but isn't
- No mechanism to capture proxy CONNECT response headers

**Extension Feasibility:** ⚠️ MEDIUM-HIGH
- Would require adding Python bindings for `CURLOPT_PROXYHEADER`
- Could potentially capture CONNECT response via `CURLOPT_HEADERFUNCTION`
- Significant value as this library is used for anti-bot bypass

---

### 3. pycurl (1,146 stars)
**GitHub:** https://github.com/pycurl/pycurl  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** Python interface to libcurl

**Proxy Support:**
- Full libcurl proxy support via `CURLOPT_PROXY`
- Supports `CURLOPT_PROXYHEADER` for sending headers to proxy

**Custom Proxy Headers:** ⚠️ Partial
- `CURLOPT_PROXYHEADER` allows sending custom headers to proxy
- Receiving proxy response headers during CONNECT is tricky but possible via `CURLOPT_HEADERFUNCTION`

**Extension Feasibility:** ✅ HIGH
- Already has underlying support via libcurl options
- Need a wrapper module to simplify the API for sending/receiving proxy headers
- Could create `ProxyCurl` class with easy `proxy_headers` parameter

---

### 4. autoscraper (7,082 stars)
**GitHub:** https://github.com/alirezamika/autoscraper  
**Last Pushed:** 2025-06-09  
**Description:** Smart, automatic web scraper for Python

**Proxy Support:**
- Uses requests under the hood
- Proxy passed via `request_args=dict(proxies=proxies)`

**Custom Proxy Headers:** ❌ No
- Inherits requests' limitations

**Extension Feasibility:** ✅ HIGH
- Since it uses requests, could integrate with our existing requests adapter
- Low priority as it's a higher-level abstraction

---

### 5. treq (606 stars)
**GitHub:** https://github.com/twisted/treq  
**Last Pushed:** 2026-01-03  
**Description:** Python requests-like API built on Twisted's HTTP client

**Proxy Support:**
- Uses Twisted's `Agent` for HTTP operations
- Proxy support via `twisted.web.client.ProxyAgent`

**Custom Proxy Headers:** ❌ No
- ProxyAgent doesn't expose custom proxy header handling
- CONNECT tunnel headers not accessible

**Extension Feasibility:** ⚠️ MEDIUM
- Would require creating custom `ProxyAgent` subclass
- Twisted's Agent architecture is complex
- Lower priority due to smaller user base

---

### 6. crawl4ai (59,235 stars) 🔥
**GitHub:** https://github.com/unclecode/crawl4ai  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** LLM-friendly web crawler & scraper

**Proxy Support:**
- Uses Playwright under the hood for browser automation
- Proxy configuration via `BrowserConfig`

**Custom Proxy Headers:** ❌ No
- Browser handles proxy connection internally
- No access to CONNECT tunnel headers

**Extension Feasibility:** ❌ LOW
- Browser-based - proxy handling is delegated to Chromium/Firefox
- Would require browser extension or CDP protocol hacks
- Not practical for this project

---

### 7. Scrapegraph-ai (22,434 stars)
**GitHub:** https://github.com/ScrapeGraphAI/Scrapegraph-ai  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** Python scraper based on AI/LLM

**Proxy Support:**
- Uses Playwright for browser automation
- Configurable via graph config

**Custom Proxy Headers:** ❌ No
- Same limitations as crawl4ai - browser handles proxy

**Extension Feasibility:** ❌ LOW
- Browser-based, same limitations as above

---

### 8. Selenium (Selenium Python bindings)
**Docs:** https://selenium-python.readthedocs.io/  
**Description:** Browser automation library

**Proxy Support:**
- Proxy configured via browser options/capabilities
- Different methods for Chrome, Firefox, etc.

**Custom Proxy Headers:** ❌ No
- Browser handles proxy CONNECT internally
- No programmatic access to proxy headers

**Extension Feasibility:** ❌ LOW
- Would require browser extension
- Not practical for HTTP-level header manipulation

---

### 9. requestium (1,838 stars)
**GitHub:** https://github.com/tryolabs/requestium  
**Last Pushed:** 2026-01-26  
**Description:** Integration layer between Requests and Selenium

**Proxy Support:**
- Requests-side: standard proxy dict
- Selenium-side: browser proxy settings

**Custom Proxy Headers:** ❌ No
- Requests portion inherits requests' limitations
- Selenium portion has browser limitations

**Extension Feasibility:** ⚠️ MEDIUM
- Could integrate our requests adapter for the requests portion
- Selenium side would still lack support

---

### 10. splash (4,198 stars)
**GitHub:** https://github.com/scrapinghub/splash  
**Last Pushed:** 2024-08-02 (less active)  
**Description:** Lightweight browser as a service with HTTP API

**Proxy Support:**
- Proxy can be configured per request
- Uses Qt WebKit/WebEngine internally

**Custom Proxy Headers:** ❌ No
- Browser-based rendering
- Proxy handled by Qt networking layer

**Extension Feasibility:** ❌ LOW
- Would require Qt-level modifications
- Project appears less actively maintained

---

### 11. playwright-python (14,209 stars)
**GitHub:** https://github.com/microsoft/playwright-python  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** Python version of Playwright testing/automation library

**Proxy Support:**
- Proxy configured via `browser.launch(proxy={...})`
- Supports username/password authentication

**Custom Proxy Headers:** ❌ No
- Browser handles CONNECT tunnel internally
- No CDP protocol support for custom proxy headers

**Extension Feasibility:** ❌ LOW
- Browser delegates to system/browser proxy handling
- Would require Chromium DevTools Protocol extensions that don't exist

---

### 12. SeleniumBase (12,139 stars)
**GitHub:** https://github.com/seleniumbase/SeleniumBase  
**Last Pushed:** 2026-01-27 (very active)  
**Description:** Web automation framework with anti-bot detection bypass

**Proxy Support:**
- `--proxy=IP:PORT` command line option
- Supports authenticated proxies
- SOCKS4/SOCKS5 support

**Custom Proxy Headers:** ❌ No
- Uses Selenium under the hood - browser handles proxy

**Extension Feasibility:** ❌ LOW
- Browser-based, same Selenium limitations

---

### 13. botasaurus (3,808 stars)
**GitHub:** https://github.com/omkarcloud/botasaurus  
**Last Pushed:** 2026-01-10  
**Description:** Framework to build undetectable scrapers

**Proxy Support:**
- `@browser(proxy="...")` decorator
- `@request(proxy="...")` for HTTP requests
- Uses custom driver and requests under the hood

**Custom Proxy Headers:** ❌ No
- Browser portion: browser handles proxy
- Request portion: uses requests-like interface but no proxy header support

**Extension Feasibility:** ⚠️ MEDIUM
- The `@request` decorator could potentially be extended
- Would require understanding their custom request implementation

---

### 14. crawlee-python (7,968 stars)
**GitHub:** https://github.com/apify/crawlee-python  
**Last Pushed:** 2026-01-30 (very active)  
**Description:** Web scraping/browser automation library by Apify

**Proxy Support:**
- Integrated proxy rotation
- Supports both HTTP (httpx-based) and browser (Playwright) crawlers

**Custom Proxy Headers:** ❌ No
- BeautifulSoupCrawler uses httpx - inherits its limitations
- PlaywrightCrawler - browser handles proxy

**Extension Feasibility:** ⚠️ MEDIUM
- BeautifulSoupCrawler could use our httpx extension
- Would require creating integration middleware

---

## Summary Table

| Library | Stars | Last Active | Proxy Headers | Extension Priority |
|---------|-------|-------------|---------------|-------------------|
| crawl4ai | 59,235 | 2026-01-30 | ❌ | LOW (browser-based) |
| Scrapegraph-ai | 22,434 | 2026-01-30 | ❌ | LOW (browser-based) |
| playwright-python | 14,209 | 2026-01-30 | ❌ | LOW (browser-based) |
| SeleniumBase | 12,139 | 2026-01-27 | ❌ | LOW (browser-based) |
| crawlee-python | 7,968 | 2026-01-30 | ❌ | MEDIUM (httpx portion) |
| autoscraper | 7,082 | 2025-06-09 | ❌ | HIGH (uses requests) |
| cloudscraper | 6,060 | 2025-06-10 | ❌ | HIGH (uses requests) |
| curl_cffi | 4,873 | 2026-01-30 | ❌ | HIGH (libcurl potential) |
| splash | 4,198 | 2024-08-02 | ❌ | LOW (Qt-based) |
| botasaurus | 3,808 | 2026-01-10 | ❌ | MEDIUM |
| requestium | 1,838 | 2026-01-26 | ❌ | MEDIUM |
| pycurl | 1,146 | 2026-01-30 | ⚠️ Partial | HIGH (has libcurl support) |
| treq | 606 | 2026-01-03 | ❌ | MEDIUM |

---

## Conclusion

**Browser-based libraries (Playwright, Selenium, crawl4ai, etc.) cannot support custom proxy headers** because the browser handles proxy CONNECT tunneling internally without exposing headers to the automation layer.

**HTTP client libraries have the best potential for extension modules:**
1. **pycurl** - Already has libcurl's `CURLOPT_PROXYHEADER`, just needs wrapper
2. **curl_cffi** - Could expose libcurl's proxy header options
3. **cloudscraper** - Uses requests, can leverage existing adapter
4. **autoscraper** - Uses requests, can leverage existing adapter

---

*Research conducted: January 30, 2026*
