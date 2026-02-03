"""
PycURL extension for sending and receiving proxy headers.

This module provides helper functions and classes for working with proxy headers
in pycurl. It can be used in two ways:

1. Low-level helpers for existing pycurl code:

    import pycurl
    from python_proxy_headers.pycurl_proxy import set_proxy_headers, HeaderCapture

    c = pycurl.Curl()
    c.setopt(pycurl.URL, 'https://example.com')
    c.setopt(pycurl.PROXY, 'http://proxy:8080')
    
    # Add proxy headers
    set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})
    
    # Capture response headers (including proxy CONNECT headers)
    capture = HeaderCapture(c)
    
    c.perform()
    
    print(capture.proxy_headers)   # Headers from proxy CONNECT response
    print(capture.origin_headers)  # Headers from origin server

2. High-level convenience functions:

    from python_proxy_headers.pycurl_proxy import get

    response = get('https://example.com',
                   proxy='http://proxy:8080',
                   proxy_headers={'X-ProxyMesh-Country': 'US'})
    print(response.proxy_headers)
"""

from io import BytesIO
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

try:
    import pycurl
except ImportError:
    raise ImportError(
        "pycurl is required for this module. "
        "Install it with: pip install pycurl"
    )


# =============================================================================
# Low-level helper functions
# =============================================================================

def set_proxy_headers(curl, headers: Dict[str, str]) -> None:
    """
    Set custom headers to send to the proxy server during CONNECT.
    
    Args:
        curl: A pycurl.Curl instance
        headers: Dict of headers to send to the proxy
    
    Example:
        c = pycurl.Curl()
        c.setopt(pycurl.PROXY, 'http://proxy:8080')
        set_proxy_headers(c, {'X-ProxyMesh-Country': 'US'})
        c.perform()
    """
    if not headers:
        return
    
    header_list = [f"{k}: {v}" for k, v in headers.items()]
    
    # Set CURLOPT_PROXYHEADER
    try:
        curl.setopt(pycurl.PROXYHEADER, header_list)
    except AttributeError:
        # Fallback to numeric option (10228) if not exposed
        curl.setopt(10228, header_list)
    
    # Set CURLOPT_HEADEROPT to CURLHEADER_SEPARATE so proxy headers
    # are only sent to the proxy, not the origin
    try:
        curl.setopt(pycurl.HEADEROPT, pycurl.HEADER_SEPARATE)
    except AttributeError:
        try:
            curl.setopt(229, 1)  # CURLOPT_HEADEROPT = 229, CURLHEADER_SEPARATE = 1
        except pycurl.error:
            pass  # Option may not be available in older libcurl versions


class HeaderCapture:
    """
    Captures and parses HTTP response headers from pycurl requests.
    
    For HTTPS requests through a proxy, this separates:
    - proxy_headers: Headers from the proxy's CONNECT response
    - origin_headers: Headers from the origin server's response
    
    Example:
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'https://example.com')
        c.setopt(pycurl.PROXY, 'http://proxy:8080')
        
        capture = HeaderCapture(c)  # Installs HEADERFUNCTION callback
        
        c.perform()
        
        print(capture.proxy_headers)   # {'X-ProxyMesh-IP': '1.2.3.4', ...}
        print(capture.origin_headers)  # {'Content-Type': 'text/html', ...}
        print(capture.proxy_status)    # 200
    """
    
    def __init__(self, curl=None):
        """
        Initialize header capture.
        
        Args:
            curl: Optional pycurl.Curl instance. If provided, automatically
                  installs the HEADERFUNCTION callback.
        """
        self._header_lines: List[bytes] = []
        self._parsed = False
        self._sections: List[Tuple[Optional[int], Dict[str, str]]] = []
        
        if curl is not None:
            self.install(curl)
    
    def install(self, curl) -> 'HeaderCapture':
        """
        Install the header callback on a pycurl.Curl instance.
        
        Args:
            curl: A pycurl.Curl instance
            
        Returns:
            self, for chaining
        """
        curl.setopt(pycurl.HEADERFUNCTION, self._header_callback)
        return self
    
    def _header_callback(self, header_line: bytes) -> int:
        """Callback for pycurl HEADERFUNCTION."""
        self._header_lines.append(header_line)
        self._parsed = False  # Invalidate cache
        return len(header_line)
    
    def _parse(self) -> None:
        """Parse collected header lines into sections."""
        if self._parsed:
            return
        
        self._sections = []
        current_headers: Dict[str, str] = {}
        current_status: Optional[int] = None
        
        for line in self._header_lines:
            line_str = line.decode('utf-8', errors='replace').strip()
            
            if line_str.startswith('HTTP/'):
                # New response section - save previous if exists
                if current_headers or current_status is not None:
                    self._sections.append((current_status, current_headers))
                current_headers = {}
                # Parse status line: HTTP/1.1 200 OK
                parts = line_str.split(' ', 2)
                if len(parts) >= 2:
                    try:
                        current_status = int(parts[1])
                    except ValueError:
                        current_status = None
                else:
                    current_status = None
            elif ':' in line_str:
                key, value = line_str.split(':', 1)
                current_headers[key.strip()] = value.strip()
        
        # Don't forget the last section
        if current_headers or current_status is not None:
            self._sections.append((current_status, current_headers))
        
        self._parsed = True
    
    def reset(self) -> None:
        """Clear captured headers for reuse."""
        self._header_lines.clear()
        self._sections.clear()
        self._parsed = False
    
    @property
    def proxy_headers(self) -> Dict[str, str]:
        """
        Headers from the proxy's CONNECT response.
        
        Returns empty dict if not an HTTPS-via-proxy request or no headers captured.
        """
        self._parse()
        if len(self._sections) >= 2:
            return self._sections[0][1]
        return {}
    
    @property
    def proxy_status(self) -> Optional[int]:
        """
        Status code from the proxy's CONNECT response.
        
        Returns None if not an HTTPS-via-proxy request.
        """
        self._parse()
        if len(self._sections) >= 2:
            return self._sections[0][0]
        return None
    
    @property
    def origin_headers(self) -> Dict[str, str]:
        """Headers from the origin server's response."""
        self._parse()
        if self._sections:
            return self._sections[-1][1]
        return {}
    
    @property
    def origin_status(self) -> Optional[int]:
        """Status code from the origin server's response."""
        self._parse()
        if self._sections:
            return self._sections[-1][0]
        return None
    
    @property 
    def all_headers(self) -> Dict[str, str]:
        """All headers merged (proxy headers take precedence for conflicts)."""
        self._parse()
        merged = {}
        for _, headers in self._sections:
            merged.update(headers)
        return merged


# =============================================================================
# High-level convenience API
# =============================================================================

@dataclass
class Response:
    """Response object from high-level API."""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    proxy_headers: Dict[str, str] = field(default_factory=dict)
    proxy_status: Optional[int] = None
    
    @property
    def text(self) -> str:
        """Response body as text."""
        return self.content.decode('utf-8', errors='replace')
    
    def raise_for_status(self) -> None:
        """Raise exception if status code indicates error."""
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}")


def request(
    method: str,
    url: str,
    proxy: Optional[str] = None,
    proxy_headers: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: Optional[int] = None,
    verify: bool = True,
) -> Response:
    """
    Make an HTTP request with proxy header support.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Target URL
        proxy: Proxy URL (e.g., 'http://user:pass@proxy:8080')
        proxy_headers: Headers to send to the proxy
        headers: Headers to send to the origin server
        data: Request body for POST/PUT/PATCH
        timeout: Request timeout in seconds
        verify: Whether to verify SSL certificates
        
    Returns:
        Response object with body, headers, and proxy_headers
    """
    c = pycurl.Curl()
    body = BytesIO()
    capture = HeaderCapture(c)
    
    try:
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEFUNCTION, body.write)
        
        # HTTP method
        method = method.upper()
        if method == 'GET':
            c.setopt(pycurl.HTTPGET, 1)
        elif method == 'POST':
            c.setopt(pycurl.POST, 1)
            if data:
                c.setopt(pycurl.POSTFIELDS, data)
        elif method == 'PUT':
            c.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            if data:
                c.setopt(pycurl.POSTFIELDS, data)
        elif method == 'DELETE':
            c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        elif method == 'HEAD':
            c.setopt(pycurl.NOBODY, 1)
        elif method == 'PATCH':
            c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
            if data:
                c.setopt(pycurl.POSTFIELDS, data)
        else:
            c.setopt(pycurl.CUSTOMREQUEST, method)
        
        # Request headers
        if headers:
            c.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])
        
        # Proxy
        if proxy:
            c.setopt(pycurl.PROXY, proxy)
            if proxy_headers:
                set_proxy_headers(c, proxy_headers)
        
        # Timeout
        if timeout:
            c.setopt(pycurl.TIMEOUT, timeout)
        
        # SSL
        if not verify:
            c.setopt(pycurl.SSL_VERIFYPEER, 0)
            c.setopt(pycurl.SSL_VERIFYHOST, 0)
        
        c.perform()
        
        return Response(
            status_code=c.getinfo(pycurl.RESPONSE_CODE),
            headers=capture.origin_headers,
            content=body.getvalue(),
            proxy_headers=capture.proxy_headers,
            proxy_status=capture.proxy_status,
        )
    finally:
        c.close()


def get(url: str, **kwargs) -> Response:
    """Make a GET request."""
    return request('GET', url, **kwargs)


def post(url: str, **kwargs) -> Response:
    """Make a POST request."""
    return request('POST', url, **kwargs)


def put(url: str, **kwargs) -> Response:
    """Make a PUT request."""
    return request('PUT', url, **kwargs)


def delete(url: str, **kwargs) -> Response:
    """Make a DELETE request."""
    return request('DELETE', url, **kwargs)


def head(url: str, **kwargs) -> Response:
    """Make a HEAD request."""
    return request('HEAD', url, **kwargs)


def patch(url: str, **kwargs) -> Response:
    """Make a PATCH request."""
    return request('PATCH', url, **kwargs)
