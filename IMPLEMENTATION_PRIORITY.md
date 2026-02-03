# Implementation Priority List for python-proxy-headers Extensions

Based on library analysis considering GitHub stars, activity level, technical feasibility, and user impact.

---

## Priority Rankings

### 🔴 Priority 1: HIGH - Implement First

#### 1. pycurl Extension
**File:** `python_proxy_headers/pycurl_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 1,146 |
| Last Active | 2026-01-30 |
| Feasibility | ✅ HIGH |
| Impact | HIGH - Direct libcurl access |

**Why High Priority:**
- libcurl already supports `CURLOPT_PROXYHEADER` for sending custom headers
- Can capture CONNECT response headers via `CURLOPT_HEADERFUNCTION`
- Foundation for curl_cffi work

**Implementation Plan:**
```python
# pycurl_proxy.py - Proposed API

class ProxyCurl:
    """PycURL wrapper with proxy header support."""
    
    def __init__(self, proxy_headers=None):
        self.proxy_headers = proxy_headers or {}
        self._response_proxy_headers = {}
    
    def get(self, url, proxy=None) -> ProxyResponse:
        """Make GET request with proxy header support."""
        pass
    
    @property
    def received_proxy_headers(self) -> dict:
        """Headers received from proxy during CONNECT."""
        return self._response_proxy_headers

def request(method, url, proxy=None, proxy_headers=None) -> ProxyResponse:
    """Convenience function for one-off requests."""
    pass
```

**Technical Approach:**
1. Use `pycurl.PROXYHEADER` option to send custom headers
2. Use `HEADERFUNCTION` callback to capture CONNECT response headers
3. Parse headers to separate proxy headers from origin headers
4. Expose via clean API matching existing python-proxy-headers style

---

#### 2. curl_cffi Extension
**File:** `python_proxy_headers/curl_cffi_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 4,873 |
| Last Active | 2026-01-30 |
| Feasibility | ⚠️ MEDIUM-HIGH |
| Impact | VERY HIGH - Popular anti-bot library |

**Why High Priority:**
- Very popular for bypassing bot detection
- Uses libcurl which has proxy header capabilities
- Active development means potential upstream contributions

**Implementation Plan:**
```python
# curl_cffi_proxy.py - Proposed API

from curl_cffi import Session

class ProxySession(Session):
    """curl_cffi Session with proxy header support."""
    
    def __init__(self, proxy_headers=None, **kwargs):
        super().__init__(**kwargs)
        self._proxy_headers = proxy_headers or {}
        self._last_proxy_response_headers = {}
    
    def request(self, method, url, **kwargs) -> ProxyResponse:
        """Make request capturing proxy headers."""
        pass
    
    @property
    def proxy_response_headers(self) -> dict:
        """Headers from last proxy CONNECT response."""
        return self._last_proxy_response_headers

# Convenience functions
def get(url, proxy=None, proxy_headers=None, impersonate=None, **kwargs):
    pass
```

**Technical Approach:**
1. Investigate if curl_cffi exposes low-level curl options
2. If yes: Use `CURLOPT_PROXYHEADER` directly
3. If no: Create PR to curl_cffi to expose these options
4. May need to work with curl_cffi maintainers

**Upstream Contribution Opportunity:**
- File issue requesting `proxy_headers` parameter
- Contribute PR if welcomed

---

#### 3. cloudscraper Extension  
**File:** `python_proxy_headers/cloudscraper_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 6,060 |
| Last Active | 2025-06-10 |
| Feasibility | ✅ HIGH |
| Impact | HIGH - Popular for Cloudflare bypass |

**Why High Priority:**
- Built on requests - can use our existing adapter
- Popular for accessing protected sites
- Easy integration

**Implementation Plan:**
```python
# cloudscraper_proxy.py - Proposed API

import cloudscraper
from .requests_adapter import HTTPProxyHeaderAdapter

class ProxyCloudScraper(cloudscraper.CloudScraper):
    """CloudScraper with proxy header support."""
    
    def __init__(self, proxy_headers=None, **kwargs):
        super().__init__(**kwargs)
        adapter = HTTPProxyHeaderAdapter(proxy_headers=proxy_headers)
        self.mount('https://', adapter)
        self.mount('http://', adapter)

def create_scraper(proxy_headers=None, **kwargs):
    """Create a CloudScraper with proxy header support."""
    return ProxyCloudScraper(proxy_headers=proxy_headers, **kwargs)
```

**Technical Approach:**
1. Subclass `cloudscraper.CloudScraper`
2. Mount our `HTTPProxyHeaderAdapter` 
3. Preserve all cloudscraper functionality
4. Simple integration - likely <50 lines of code

---

### 🟡 Priority 2: MEDIUM - Implement Second

#### 4. autoscraper Extension
**File:** `python_proxy_headers/autoscraper_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 7,082 |
| Last Active | 2025-06-09 |
| Feasibility | ✅ HIGH |
| Impact | MEDIUM - Niche use case |

**Implementation Plan:**
```python
# autoscraper_proxy.py

from autoscraper import AutoScraper
from .requests_adapter import ProxySession

class ProxyAutoScraper(AutoScraper):
    """AutoScraper with proxy header support."""
    
    def __init__(self, proxy_headers=None):
        super().__init__()
        self._proxy_session = ProxySession(proxy_headers=proxy_headers)
    
    def build(self, url, wanted_list, proxy_headers=None, **kwargs):
        """Build scraper with proxy header support."""
        # Use our ProxySession for requests
        pass
```

---

#### 5. treq Extension
**File:** `python_proxy_headers/treq_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 606 |
| Last Active | 2026-01-03 |
| Feasibility | ⚠️ MEDIUM |
| Impact | MEDIUM - Twisted ecosystem |

**Implementation Plan:**
```python
# treq_proxy.py

from twisted.web.client import Agent, ProxyAgent
from twisted.internet import reactor

class ProxyHeaderAgent(ProxyAgent):
    """Twisted Agent with proxy header support."""
    
    def __init__(self, proxy_headers=None, **kwargs):
        super().__init__(**kwargs)
        self._proxy_headers = proxy_headers or {}
    
    # Override connection methods to inject headers
```

**Technical Approach:**
1. Subclass `ProxyAgent`
2. Override `_connect` method to add custom headers
3. Capture CONNECT response headers
4. More complex due to Twisted's async nature

---

#### 6. crawlee-python Extension
**File:** `python_proxy_headers/crawlee_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 7,968 |
| Last Active | 2026-01-30 |
| Feasibility | ⚠️ MEDIUM |
| Impact | MEDIUM - Only HTTP crawler portion |

**Implementation Plan:**
```python
# crawlee_proxy.py

from crawlee.crawlers import BeautifulSoupCrawler
from .httpx_proxy import HTTPProxyTransport

class ProxyBeautifulSoupCrawler(BeautifulSoupCrawler):
    """Crawler with proxy header support for HTTP requests."""
    
    def __init__(self, proxy_headers=None, **kwargs):
        # Configure httpx client with our transport
        pass
```

**Note:** Only applies to `BeautifulSoupCrawler`, not `PlaywrightCrawler`

---

#### 7. requestium Extension
**File:** `python_proxy_headers/requestium_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 1,838 |
| Last Active | 2026-01-26 |
| Feasibility | ⚠️ MEDIUM |
| Impact | LOW - Requests portion only |

**Implementation Plan:**
```python
# requestium_proxy.py

from requestium import Session
from .requests_adapter import HTTPProxyHeaderAdapter

class ProxySession(Session):
    """Requestium Session with proxy header support."""
    
    def __init__(self, proxy_headers=None, **kwargs):
        super().__init__(**kwargs)
        adapter = HTTPProxyHeaderAdapter(proxy_headers=proxy_headers)
        self.mount('https://', adapter)
        self.mount('http://', adapter)
```

---

#### 8. botasaurus Extension
**File:** `python_proxy_headers/botasaurus_proxy.py`

| Metric | Value |
|--------|-------|
| GitHub Stars | 3,808 |
| Last Active | 2026-01-10 |
| Feasibility | ⚠️ MEDIUM |
| Impact | LOW - Request decorator only |

**Implementation Plan:**
- Investigate botasaurus's request module internals
- May require monkey-patching or upstream PR

---

### 🟢 Priority 3: LOW - Browser-Based (Not Recommended)

These libraries use browser automation where proxy handling is delegated to the browser engine. Custom proxy header support is **not feasible** without browser extensions or significant browser-level modifications.

| Library | Stars | Reason for Low Priority |
|---------|-------|------------------------|
| crawl4ai | 59,235 | Browser-based (Playwright) |
| Scrapegraph-ai | 22,434 | Browser-based (Playwright) |
| playwright-python | 14,209 | Browser handles proxy |
| SeleniumBase | 12,139 | Browser handles proxy |
| Selenium | N/A | Browser handles proxy |
| splash | 4,198 | Qt WebKit-based |

**Recommendation:** Do not implement extensions for these libraries. Instead, document that proxy header support is not possible due to browser architecture limitations.

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
1. ✅ pycurl extension
2. ✅ cloudscraper extension (quick win)

### Phase 2: High-Impact (Weeks 3-4)
3. curl_cffi extension (may require upstream work)
4. autoscraper extension

### Phase 3: Ecosystem (Weeks 5-6)
5. treq extension
6. crawlee-python extension
7. requestium extension

### Phase 4: Optional
8. botasaurus extension (if feasible)

---

## File Structure

```
python_proxy_headers/
├── __init__.py
├── urllib3_proxy_manager.py     # Existing
├── requests_adapter.py          # Existing
├── httpx_proxy.py               # Existing
├── aiohttp_proxy.py             # Existing
├── pycurl_proxy.py              # NEW - Priority 1
├── curl_cffi_proxy.py           # NEW - Priority 1
├── cloudscraper_proxy.py        # NEW - Priority 1
├── autoscraper_proxy.py         # NEW - Priority 2
├── treq_proxy.py                # NEW - Priority 2
├── crawlee_proxy.py             # NEW - Priority 2
├── requestium_proxy.py          # NEW - Priority 2
└── botasaurus_proxy.py          # NEW - Priority 2
```

---

## Documentation Updates

For each new extension, add:
1. RST doc file in `docs/`
2. Entry in `docs/index.rst`
3. Usage example in README.md
4. Example code in proxy-examples repo

---

*Created: January 30, 2026*
