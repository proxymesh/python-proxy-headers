# python-proxy-headers Outreach Drafts

This document contains draft text for reaching out to library maintainers to add links to python-proxy-headers.

---

## 1. HTTPX (PR Ready)

**Status:** Branch created, ready to submit PR  
**Fork:** https://github.com/proxymesh/httpx  
**Branch:** `docs/add-python-proxy-headers`  
**Target:** https://github.com/encode/httpx

### PR Title
```
Add python-proxy-headers to Third Party Packages
```

### PR Description
```
## Summary

Add python-proxy-headers to the Third Party Packages documentation.

python-proxy-headers is a library that enables:
- Sending custom headers to proxy servers during HTTPS CONNECT requests
- Receiving and accessing proxy response headers from the CONNECT response

This is useful for proxy services like ProxyMesh that use custom headers for country selection (X-ProxyMesh-Country) and provide metadata like assigned IP addresses (X-ProxyMesh-IP).

- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/
```

### To Submit PR
```bash
cd /home/jacob/proxymesh-httpx
gh pr create --repo encode/httpx --title "Add python-proxy-headers to Third Party Packages" --body "## Summary

Add python-proxy-headers to the Third Party Packages documentation.

python-proxy-headers is a library that enables:
- Sending custom headers to proxy servers during HTTPS CONNECT requests
- Receiving and accessing proxy response headers from the CONNECT response

This is useful for proxy services like ProxyMesh that use custom headers for country selection (X-ProxyMesh-Country) and provide metadata like assigned IP addresses (X-ProxyMesh-IP).

- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/"
```

---

## 2. Requests (Manual Fork Required)

**Status:** Fork failed due to token permissions - need to fork manually  
**Target:** https://github.com/psf/requests  
**File to edit:** `docs/community/recommended.rst`

### Steps
1. Go to https://github.com/psf/requests and click "Fork"
2. Clone your fork:
   ```bash
   git clone https://github.com/proxymesh/requests.git
   cd requests
   git config user.email "cursor@proxymesh.com"
   git config user.name "Cursor"
   ```
3. Create branch:
   ```bash
   git checkout -b docs/add-python-proxy-headers
   ```
4. Edit `docs/community/recommended.rst` and add before the last entry:
   ```rst
   python-proxy-headers
   ---------------------

   `python-proxy-headers <https://github.com/proxymesh/python-proxy-headers>`_ 
   enables sending custom headers to proxy servers and receiving proxy response 
   headers from HTTPS CONNECT requests. This is useful for proxy services that 
   use custom headers for features like country selection or session management.

   .. code-block:: python

       from python_proxy_headers import requests_adapter
       
       response = requests_adapter.get(
           'https://api.ipify.org',
           proxies={'https': 'http://proxy:8080'},
           proxy_headers={'X-ProxyMesh-Country': 'US'}
       )
       print(response.headers.get('X-ProxyMesh-IP'))
   ```
5. Commit and push:
   ```bash
   git add docs/community/recommended.rst
   git commit -m "Add python-proxy-headers to Recommended Packages"
   git push -u origin docs/add-python-proxy-headers
   ```
6. Create PR to psf/requests

### PR Title
```
Add python-proxy-headers to Recommended Packages
```

### PR Description
```
## Summary

Add python-proxy-headers to the Recommended Packages documentation.

python-proxy-headers enables sending custom headers to proxy servers and receiving 
proxy response headers from HTTPS CONNECT requests. This fills a gap in the requests 
library where proxy headers from the CONNECT response are not normally accessible.

Use cases:
- Proxy services that use custom headers for country/region selection
- Accessing metadata from proxy servers (e.g., assigned IP address)
- Session management with rotating proxies

- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/
```

---

## 3. urllib3 (Discord/Discussion)

**Status:** No third-party page exists - contact maintainers  
**Discord:** https://discord.gg/urllib3  
**Discussions:** https://github.com/urllib3/urllib3/discussions

### Discord Message
```
Hi! I maintain python-proxy-headers, a library that extends urllib3 (and other 
HTTP libraries) to support:
- Sending custom headers to proxy servers during HTTPS CONNECT
- Receiving and accessing proxy response headers from the CONNECT response

This is useful for proxy services like ProxyMesh that communicate via custom 
headers (e.g., X-ProxyMesh-Country for country selection, X-ProxyMesh-IP for 
the assigned IP).

GitHub: https://github.com/proxymesh/python-proxy-headers
Docs: https://python-proxy-headers.readthedocs.io/

Would you be interested in linking to this from the urllib3 docs or README? 
I noticed there's a "Who uses urllib3?" section - perhaps a section for 
extensions/ecosystem projects would be valuable?
```

### GitHub Discussion Title
```
Request: Add ecosystem/extensions section to documentation
```

### GitHub Discussion Body
```
Hi urllib3 maintainers!

I maintain python-proxy-headers, a library that extends urllib3 to support 
sending custom headers to proxy servers and receiving proxy response headers 
from HTTPS CONNECT requests.

This functionality isn't available in standard urllib3 because the CONNECT 
response headers are not exposed to the caller.

**Use cases:**
- Proxy services that use custom headers for country/region selection
- Accessing metadata from proxy servers (e.g., assigned IP address)
- Session management with rotating proxies

**Links:**
- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/

**Request:**
Would you consider:
1. Adding a link in the README or docs?
2. Creating an "Ecosystem" or "Extensions" section for third-party projects?

I'm happy to submit a PR if you point me to the right location.

Thanks for maintaining such a foundational library!
```

---

## 4. pycurl (Mailing List)

**Status:** No third-party page - contact via mailing list  
**Mailing List:** https://lists.haxx.se/listinfo/curl-and-python  
**Archive:** https://curl.haxx.se/mail/list.cgi?list=curl-and-python

### Email Subject
```
[ANN] python-proxy-headers: Proxy header support for pycurl
```

### Email Body
```
Hi curl-and-python community,

I'd like to announce python-proxy-headers, a library that provides convenient 
proxy header support for pycurl (and other Python HTTP libraries).

The library provides:
- set_proxy_headers(): Helper to set CURLOPT_PROXYHEADER and CURLOPT_HEADEROPT
- HeaderCapture: Class to capture and parse headers from both proxy CONNECT 
  response and origin server response
- High-level convenience functions (get, post, etc.) for simple use cases

Example usage with existing pycurl code:

    import pycurl
    from python_proxy_headers.pycurl_proxy import set_proxy_headers, HeaderCapture

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://httpbin.org/ip')
    c.setopt(pycurl.PROXY, 'http://proxy:8080')

    # Add custom headers to send to the proxy
    set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})

    # Capture response headers
    capture = HeaderCapture(c)

    c.perform()

    # Access proxy CONNECT response headers
    print(capture.proxy_headers)  # {'X-ProxyMesh-IP': '1.2.3.4', ...}
    c.close()

Links:
- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/en/latest/pycurl.html

Would the maintainers consider linking to this from the pycurl documentation 
or examples directory?

Best regards,
ProxyMesh Team
```

---

## 5. CloudScraper (GitHub Issue)

**Status:** Contact maintainer via GitHub issue  
**URL:** https://github.com/VeNoMouS/cloudscraper/issues/new

### Issue Title
```
Request: Add python-proxy-headers to README/documentation
```

### Issue Body
```
Hi @VeNoMouS,

I maintain python-proxy-headers, which provides proxy header support for 
cloudscraper (and other Python HTTP libraries).

## What it does

When using cloudscraper with HTTPS through a proxy, the library enables:
- Sending custom headers to the proxy server (e.g., `X-ProxyMesh-Country`)
- Receiving proxy response headers from the CONNECT response (e.g., `X-ProxyMesh-IP`)

This is useful for proxy services like ProxyMesh that use custom headers for 
country selection and provide metadata about the connection.

## Usage

```python
from python_proxy_headers.cloudscraper_proxy import create_scraper

# Drop-in replacement for cloudscraper.create_scraper()
scraper = create_scraper(
    proxy_headers={'X-ProxyMesh-Country': 'US'},
    browser='chrome'
)

scraper.proxies = {'https': 'http://proxy:8080'}
response = scraper.get('https://example.com')

# Access proxy response headers
print(response.headers.get('X-ProxyMesh-IP'))
```

All cloudscraper features (Cloudflare bypass, stealth mode, etc.) are preserved.

## Links

- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/en/latest/cloudscraper.html

## Request

Would you consider adding a link to python-proxy-headers in the README or 
creating an "Integrations" section? Happy to submit a PR if you prefer.

Thanks for maintaining cloudscraper!
```

---

## 6. AutoScraper (GitHub Issue)

**Status:** Contact maintainer via GitHub issue  
**URL:** https://github.com/alirezamika/autoscraper/issues/new

### Issue Title
```
Request: Add python-proxy-headers integration to README
```

### Issue Body
```
Hi @alirezamika,

I maintain python-proxy-headers, which provides proxy header support for 
autoscraper (and other Python HTTP libraries).

## What it does

When using autoscraper with proxies, the library enables:
- Sending custom headers to the proxy server during requests
- Useful for proxy services that support custom headers for features like 
  country selection or session management

## Usage

```python
from python_proxy_headers.autoscraper_proxy import ProxyAutoScraper

# Drop-in replacement for AutoScraper
scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})

result = scraper.build(
    url='https://example.com',
    wanted_list=['Example text'],
    request_args={'proxies': {'https': 'http://proxy:8080'}}
)
```

All autoscraper features (rule learning, saving/loading, etc.) are preserved.

## Links

- GitHub: https://github.com/proxymesh/python-proxy-headers
- PyPI: https://pypi.org/project/python-proxy-headers/
- Docs: https://python-proxy-headers.readthedocs.io/en/latest/autoscraper.html

## Request

Would you consider mentioning python-proxy-headers in the README, perhaps in 
the proxy usage section? Happy to submit a PR if you prefer.

Thanks for creating autoscraper!
```

---

## Summary

| Library | Method | Status |
|---------|--------|--------|
| httpx | PR | Branch ready at `proxymesh/httpx:docs/add-python-proxy-headers` |
| requests | PR | Need to manually fork first |
| urllib3 | Discord/Discussion | Draft message ready |
| pycurl | Mailing list | Draft email ready |
| cloudscraper | GitHub Issue | Draft issue ready |
| autoscraper | GitHub Issue | Draft issue ready |
