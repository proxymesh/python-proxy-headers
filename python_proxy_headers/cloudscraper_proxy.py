"""
CloudScraper extension for sending and receiving proxy headers.

This module provides a CloudScraper subclass that enables:
1. Sending custom headers to proxy servers during CONNECT
2. Capturing response headers from proxy servers

Example usage:
    from python_proxy_headers.cloudscraper_proxy import create_scraper

    scraper = create_scraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
    scraper.proxies = {'https': 'http://proxy:8080'}
    response = scraper.get('https://example.com')
    
    # Access proxy response headers (stored on the response object)
    print(response.proxy_headers)
"""

from typing import Dict, Optional, Any

try:
    import cloudscraper
    from cloudscraper import CipherSuiteAdapter
except ImportError:
    raise ImportError(
        "cloudscraper is required for this module. "
        "Install it with: pip install cloudscraper"
    )

from .urllib3_proxy_manager import proxy_from_url


class CipherSuiteProxyHeaderAdapter(CipherSuiteAdapter):
    """
    Combines CloudScraper's CipherSuiteAdapter with proxy header support.
    
    This adapter:
    - Maintains CloudScraper's TLS/cipher suite customization
    - Adds the ability to send custom headers to proxy servers
    - Uses our custom ProxyManager that captures proxy response headers
    """
    
    def __init__(self, proxy_headers: Optional[Dict[str, str]] = None, **kwargs):
        self._proxy_headers = proxy_headers or {}
        super().__init__(**kwargs)
    
    def proxy_manager_for(self, proxy, **proxy_kwargs):
        """
        Return a ProxyManager for the given proxy with custom header support.
        
        Overrides the default proxy_manager_for to use our custom ProxyManager
        that supports sending and receiving proxy headers.
        """
        if proxy in self.proxy_manager:
            manager = self.proxy_manager[proxy]
        elif proxy.lower().startswith("socks"):
            # SOCKS proxies don't support custom headers
            return super().proxy_manager_for(proxy, **proxy_kwargs)
        else:
            # Get standard proxy headers (e.g., Proxy-Authorization)
            _proxy_headers = self.proxy_headers(proxy)
            
            # Merge with our custom proxy headers
            if self._proxy_headers:
                _proxy_headers.update(self._proxy_headers)
            
            # Pass SSL context if available
            if hasattr(self, 'ssl_context') and self.ssl_context:
                proxy_kwargs['ssl_context'] = self.ssl_context
            
            if hasattr(self, 'source_address') and self.source_address:
                proxy_kwargs['source_address'] = self.source_address
            
            manager = self.proxy_manager[proxy] = proxy_from_url(
                proxy,
                proxy_headers=_proxy_headers,
                num_pools=self._pool_connections,
                maxsize=self._pool_maxsize,
                block=self._pool_block,
                **proxy_kwargs,
            )
        
        return manager


class ProxyCloudScraper(cloudscraper.CloudScraper):
    """
    CloudScraper with proxy header support.
    
    This class extends CloudScraper to add the ability to:
    - Send custom headers to proxy servers during CONNECT tunneling
    - Receive and access headers from proxy server responses
    
    Args:
        proxy_headers: Dict of headers to send to proxy servers
        **kwargs: All other arguments passed to CloudScraper
    
    Example:
        scraper = ProxyCloudScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
        scraper.proxies = {'https': 'http://proxy.example.com:8080'}
        response = scraper.get('https://httpbin.org/ip')
        print(response.proxy_headers)  # Headers from proxy CONNECT response
    """
    
    def __init__(self, proxy_headers: Optional[Dict[str, str]] = None, **kwargs):
        self._proxy_headers = proxy_headers or {}
        
        # Call parent init
        super().__init__(**kwargs)
        
        # Replace the HTTPS adapter with our proxy-header-aware version
        # We need to preserve the cipher suite settings from the parent
        self.mount(
            'https://',
            CipherSuiteProxyHeaderAdapter(
                proxy_headers=self._proxy_headers,
                cipherSuite=self.cipherSuite,
                ecdhCurve=getattr(self, 'ecdhCurve', 'prime256v1'),
                server_hostname=getattr(self, 'server_hostname', None),
                source_address=getattr(self, 'source_address', None),
                ssl_context=getattr(self, 'ssl_context', None)
            )
        )
        
        # Also mount for HTTP (though proxy headers are mainly for HTTPS CONNECT)
        self.mount(
            'http://',
            CipherSuiteProxyHeaderAdapter(
                proxy_headers=self._proxy_headers,
                cipherSuite=self.cipherSuite,
                ecdhCurve=getattr(self, 'ecdhCurve', 'prime256v1'),
                server_hostname=getattr(self, 'server_hostname', None),
                source_address=getattr(self, 'source_address', None),
                ssl_context=getattr(self, 'ssl_context', None)
            )
        )
    
    def set_proxy_headers(self, proxy_headers: Dict[str, str]):
        """
        Update the proxy headers and remount adapters.
        
        Args:
            proxy_headers: New proxy headers to use
        """
        self._proxy_headers = proxy_headers
        
        # Remount adapters with new headers
        self.mount(
            'https://',
            CipherSuiteProxyHeaderAdapter(
                proxy_headers=self._proxy_headers,
                cipherSuite=self.cipherSuite,
                ecdhCurve=getattr(self, 'ecdhCurve', 'prime256v1'),
                server_hostname=getattr(self, 'server_hostname', None),
                source_address=getattr(self, 'source_address', None),
                ssl_context=getattr(self, 'ssl_context', None)
            )
        )
        self.mount(
            'http://',
            CipherSuiteProxyHeaderAdapter(
                proxy_headers=self._proxy_headers,
                cipherSuite=self.cipherSuite,
                ecdhCurve=getattr(self, 'ecdhCurve', 'prime256v1'),
                server_hostname=getattr(self, 'server_hostname', None),
                source_address=getattr(self, 'source_address', None),
                ssl_context=getattr(self, 'ssl_context', None)
            )
        )


def create_scraper(
    proxy_headers: Optional[Dict[str, str]] = None,
    sess: Optional[Any] = None,
    **kwargs
) -> ProxyCloudScraper:
    """
    Create a CloudScraper with proxy header support.
    
    This is a drop-in replacement for cloudscraper.create_scraper() that
    adds proxy header capabilities.
    
    Args:
        proxy_headers: Dict of headers to send to proxy servers
        sess: Existing session to copy attributes from
        **kwargs: All other arguments passed to CloudScraper
    
    Returns:
        ProxyCloudScraper instance
    
    Example:
        from python_proxy_headers.cloudscraper_proxy import create_scraper
        
        scraper = create_scraper(
            proxy_headers={'X-ProxyMesh-Country': 'US'},
            browser='chrome'
        )
        scraper.proxies = {'https': 'http://proxy:8080'}
        response = scraper.get('https://example.com')
    """
    scraper = ProxyCloudScraper(proxy_headers=proxy_headers, **kwargs)
    
    if sess:
        for attr in ['auth', 'cert', 'cookies', 'headers', 'hooks', 'params', 'proxies', 'data']:
            val = getattr(sess, attr, None)
            if val is not None:
                setattr(scraper, attr, val)
    
    return scraper


# Convenience alias
session = create_scraper
