"""
PycURL extension for sending and receiving proxy headers.

This module provides wrappers around pycurl that enable:
1. Sending custom headers to proxy servers during CONNECT
2. Capturing response headers from proxy servers

Example usage:
    from python_proxy_headers.pycurl_proxy import ProxyCurl, request

    # Using the ProxyCurl class
    curl = ProxyCurl(proxy_headers={'X-ProxyMesh-Country': 'US'})
    response = curl.get('https://example.com', proxy='http://proxy:8080')
    print(response.proxy_headers)  # Headers from proxy CONNECT response

    # Using convenience function
    response = request('GET', 'https://example.com',
                       proxy='http://proxy:8080',
                       proxy_headers={'X-Custom': 'value'})
"""

from io import BytesIO
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

try:
    import pycurl
except ImportError:
    raise ImportError(
        "pycurl is required for this module. "
        "Install it with: pip install pycurl"
    )


@dataclass
class ProxyResponse:
    """Response object containing body and headers from both proxy and origin."""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    proxy_headers: Dict[str, str] = field(default_factory=dict)
    proxy_status_code: Optional[int] = None
    
    @property
    def text(self) -> str:
        """Return response body as text."""
        return self.content.decode('utf-8', errors='replace')
    
    def raise_for_status(self):
        """Raise an exception if status code indicates an error."""
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}")


class ProxyCurl:
    """
    PycURL wrapper with proxy header support.
    
    This class wraps pycurl.Curl to provide easy access to:
    - Sending custom headers to proxy servers
    - Receiving headers from proxy CONNECT responses
    
    Args:
        proxy_headers: Dict of headers to send to the proxy server
    
    Example:
        curl = ProxyCurl(proxy_headers={'X-ProxyMesh-Country': 'US'})
        response = curl.get('https://httpbin.org/ip', proxy='http://proxy:8080')
        print(response.proxy_headers)
    """
    
    def __init__(self, proxy_headers: Optional[Dict[str, str]] = None):
        self._proxy_headers = proxy_headers or {}
        self._curl = pycurl.Curl()
    
    def close(self):
        """Close the underlying curl handle."""
        if self._curl:
            self._curl.close()
            self._curl = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def request(
        self,
        method: str,
        url: str,
        proxy: Optional[str] = None,
        proxy_headers: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        timeout: Optional[int] = None,
        verify: bool = True,
        **kwargs
    ) -> ProxyResponse:
        """
        Make an HTTP request with proxy header support.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            proxy: Proxy URL (e.g., 'http://user:pass@proxy:8080')
            proxy_headers: Headers to send to the proxy (merged with instance headers)
            headers: Headers to send to the origin server
            data: Request body for POST/PUT
            timeout: Request timeout in seconds
            verify: Whether to verify SSL certificates
            
        Returns:
            ProxyResponse with body, headers, and proxy_headers
        """
        c = pycurl.Curl()
        
        try:
            # Response buffers
            body_buffer = BytesIO()
            header_lines: List[bytes] = []
            
            # Track if we're in CONNECT phase (for HTTPS through proxy)
            parsed_url = urlparse(url)
            is_https_via_proxy = proxy and parsed_url.scheme == 'https'
            
            # Header callback to capture all headers
            def header_callback(header_line: bytes) -> int:
                header_lines.append(header_line)
                return len(header_line)
            
            # Basic options
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.WRITEFUNCTION, body_buffer.write)
            c.setopt(pycurl.HEADERFUNCTION, header_callback)
            
            # HTTP method
            if method.upper() == 'GET':
                c.setopt(pycurl.HTTPGET, 1)
            elif method.upper() == 'POST':
                c.setopt(pycurl.POST, 1)
                if data:
                    c.setopt(pycurl.POSTFIELDS, data)
            elif method.upper() == 'PUT':
                c.setopt(pycurl.UPLOAD, 1)
                if data:
                    c.setopt(pycurl.POSTFIELDS, data)
            elif method.upper() == 'DELETE':
                c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            elif method.upper() == 'HEAD':
                c.setopt(pycurl.NOBODY, 1)
            elif method.upper() == 'OPTIONS':
                c.setopt(pycurl.CUSTOMREQUEST, 'OPTIONS')
            elif method.upper() == 'PATCH':
                c.setopt(pycurl.CUSTOMREQUEST, 'PATCH')
                if data:
                    c.setopt(pycurl.POSTFIELDS, data)
            
            # Request headers for origin
            if headers:
                header_list = [f"{k}: {v}" for k, v in headers.items()]
                c.setopt(pycurl.HTTPHEADER, header_list)
            
            # Proxy configuration
            if proxy:
                c.setopt(pycurl.PROXY, proxy)
                
                # Merge instance proxy headers with request-specific ones
                all_proxy_headers = {**self._proxy_headers}
                if proxy_headers:
                    all_proxy_headers.update(proxy_headers)
                
                # Set proxy headers (CURLOPT_PROXYHEADER)
                if all_proxy_headers:
                    proxy_header_list = [f"{k}: {v}" for k, v in all_proxy_headers.items()]
                    # PROXYHEADER option value is 10228 in libcurl
                    # pycurl may expose it as PROXYHEADER or we use the numeric value
                    try:
                        c.setopt(pycurl.PROXYHEADER, proxy_header_list)
                    except AttributeError:
                        # Fallback to numeric option if not exposed
                        c.setopt(10228, proxy_header_list)
                    
                    # Enable header sending to proxy for CONNECT
                    # CURLOPT_HEADEROPT = 229
                    try:
                        c.setopt(pycurl.HEADEROPT, pycurl.HEADER_SEPARATE)
                    except AttributeError:
                        # CURLHEADER_SEPARATE = 1
                        try:
                            c.setopt(229, 1)
                        except pycurl.error:
                            pass  # Option may not be available in older versions
            
            # Timeout
            if timeout:
                c.setopt(pycurl.TIMEOUT, timeout)
            
            # SSL verification
            if not verify:
                c.setopt(pycurl.SSL_VERIFYPEER, 0)
                c.setopt(pycurl.SSL_VERIFYHOST, 0)
            
            # Perform the request
            c.perform()
            
            # Get status code
            status_code = c.getinfo(pycurl.RESPONSE_CODE)
            
            # Parse headers
            origin_headers = {}
            proxy_response_headers = {}
            proxy_status = None
            
            # Parse header lines
            # For HTTPS via proxy, we get headers from both CONNECT response and final response
            # They're separated by blank lines (HTTP/1.1 ... headers ... blank ... HTTP/1.1 ... headers)
            current_headers = {}
            current_status = None
            header_sections = []
            
            for line in header_lines:
                line_str = line.decode('utf-8', errors='replace').strip()
                
                if line_str.startswith('HTTP/'):
                    # New response section
                    if current_headers or current_status:
                        header_sections.append((current_status, current_headers))
                    current_headers = {}
                    # Parse status line: HTTP/1.1 200 OK
                    parts = line_str.split(' ', 2)
                    if len(parts) >= 2:
                        try:
                            current_status = int(parts[1])
                        except ValueError:
                            current_status = None
                elif ':' in line_str:
                    key, value = line_str.split(':', 1)
                    current_headers[key.strip()] = value.strip()
            
            # Don't forget the last section
            if current_headers or current_status:
                header_sections.append((current_status, current_headers))
            
            # For HTTPS through proxy:
            # - First section is CONNECT response (from proxy)
            # - Last section is actual response (from origin)
            if is_https_via_proxy and len(header_sections) >= 2:
                proxy_status, proxy_response_headers = header_sections[0]
                status_code_from_headers, origin_headers = header_sections[-1]
            elif header_sections:
                _, origin_headers = header_sections[-1]
            
            return ProxyResponse(
                status_code=status_code,
                headers=origin_headers,
                content=body_buffer.getvalue(),
                proxy_headers=proxy_response_headers,
                proxy_status_code=proxy_status
            )
            
        finally:
            c.close()
    
    def get(self, url: str, **kwargs) -> ProxyResponse:
        """Make a GET request."""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> ProxyResponse:
        """Make a POST request."""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> ProxyResponse:
        """Make a PUT request."""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> ProxyResponse:
        """Make a DELETE request."""
        return self.request('DELETE', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> ProxyResponse:
        """Make a HEAD request."""
        return self.request('HEAD', url, **kwargs)
    
    def options(self, url: str, **kwargs) -> ProxyResponse:
        """Make an OPTIONS request."""
        return self.request('OPTIONS', url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> ProxyResponse:
        """Make a PATCH request."""
        return self.request('PATCH', url, **kwargs)


def request(
    method: str,
    url: str,
    proxy: Optional[str] = None,
    proxy_headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> ProxyResponse:
    """
    Make a one-off request with proxy header support.
    
    Args:
        method: HTTP method
        url: Target URL
        proxy: Proxy URL
        proxy_headers: Headers to send to the proxy
        **kwargs: Additional arguments passed to ProxyCurl.request
        
    Returns:
        ProxyResponse object
    """
    with ProxyCurl(proxy_headers=proxy_headers) as curl:
        return curl.request(method, url, proxy=proxy, **kwargs)


def get(url: str, **kwargs) -> ProxyResponse:
    """Make a GET request with proxy header support."""
    return request('GET', url, **kwargs)


def post(url: str, **kwargs) -> ProxyResponse:
    """Make a POST request with proxy header support."""
    return request('POST', url, **kwargs)


def put(url: str, **kwargs) -> ProxyResponse:
    """Make a PUT request with proxy header support."""
    return request('PUT', url, **kwargs)


def delete(url: str, **kwargs) -> ProxyResponse:
    """Make a DELETE request with proxy header support."""
    return request('DELETE', url, **kwargs)


def head(url: str, **kwargs) -> ProxyResponse:
    """Make a HEAD request with proxy header support."""
    return request('HEAD', url, **kwargs)


def options(url: str, **kwargs) -> ProxyResponse:
    """Make an OPTIONS request with proxy header support."""
    return request('OPTIONS', url, **kwargs)


def patch(url: str, **kwargs) -> ProxyResponse:
    """Make a PATCH request with proxy header support."""
    return request('PATCH', url, **kwargs)
