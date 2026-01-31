"""
AutoScraper extension for sending and receiving proxy headers.

This module provides an AutoScraper subclass that enables:
1. Sending custom headers to proxy servers during CONNECT
2. Using our ProxySession for all HTTP requests

Example usage:
    from python_proxy_headers.autoscraper_proxy import ProxyAutoScraper

    scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
    
    # Build with proxy
    result = scraper.build(
        url='https://example.com',
        wanted_list=['Example Domain'],
        request_args={'proxies': {'https': 'http://proxy:8080'}}
    )
    
    # Get results with proxy
    result = scraper.get_result_similar(
        url='https://other-example.com',
        request_args={'proxies': {'https': 'http://proxy:8080'}}
    )
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

try:
    from autoscraper import AutoScraper
except ImportError:
    raise ImportError(
        "autoscraper is required for this module. "
        "Install it with: pip install autoscraper"
    )

from .requests_adapter import ProxySession


class ProxyAutoScraper(AutoScraper):
    """
    AutoScraper with proxy header support.
    
    This class extends AutoScraper to use our ProxySession for HTTP requests,
    enabling custom proxy headers to be sent during CONNECT tunneling.
    
    Args:
        proxy_headers: Dict of headers to send to proxy servers
        stack_list: Initial stack list (rules) for the scraper
    
    Example:
        scraper = ProxyAutoScraper(proxy_headers={'X-ProxyMesh-Country': 'US'})
        
        result = scraper.build(
            url='https://finance.yahoo.com/quote/AAPL/',
            wanted_list=['Apple Inc.'],
            request_args={'proxies': {'https': 'http://proxy:8080'}}
        )
        
        # Use the learned rules on another page
        result = scraper.get_result_similar(
            url='https://finance.yahoo.com/quote/GOOG/',
            request_args={'proxies': {'https': 'http://proxy:8080'}}
        )
    """
    
    def __init__(
        self,
        proxy_headers: Optional[Dict[str, str]] = None,
        stack_list: Optional[List] = None
    ):
        super().__init__(stack_list=stack_list)
        self._proxy_headers = proxy_headers or {}
        self._session: Optional[ProxySession] = None
    
    def _get_session(self) -> ProxySession:
        """Get or create the ProxySession."""
        if self._session is None:
            self._session = ProxySession(proxy_headers=self._proxy_headers)
        return self._session
    
    def set_proxy_headers(self, proxy_headers: Dict[str, str]):
        """
        Update the proxy headers.
        
        This will close the current session and create a new one with
        the updated headers on the next request.
        
        Args:
            proxy_headers: New proxy headers to use
        """
        self._proxy_headers = proxy_headers
        if self._session is not None:
            self._session.close()
            self._session = None
    
    def close(self):
        """Close the underlying session."""
        if self._session is not None:
            self._session.close()
            self._session = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    @classmethod
    def _fetch_html(cls, url, request_args=None):
        """
        Fetch HTML from URL using the standard requests.
        
        Note: This is the class method from parent. For proxy header support,
        use instance methods which use the ProxySession.
        """
        # Fall back to parent implementation for class method calls
        return super()._fetch_html(url, request_args)
    
    def _fetch_html_with_proxy(self, url: str, request_args: Optional[Dict] = None) -> str:
        """
        Fetch HTML from URL using ProxySession with proxy header support.
        
        Args:
            url: URL to fetch
            request_args: Additional request arguments (proxies, headers, etc.)
            
        Returns:
            HTML content as string
        """
        request_args = request_args or {}
        
        # Build headers
        headers = dict(self.request_headers)
        if url:
            headers["Host"] = urlparse(url).netloc
        
        user_headers = request_args.pop("headers", {})
        headers.update(user_headers)
        
        # Use our ProxySession
        session = self._get_session()
        
        # Copy session-level settings if not in request_args
        if 'proxies' in request_args:
            session.proxies.update(request_args.pop('proxies'))
        
        res = session.get(url, headers=headers, **request_args)
        
        # Handle encoding
        if res.encoding == "ISO-8859-1" and "ISO-8859-1" not in res.headers.get(
            "Content-Type", ""
        ):
            res.encoding = res.apparent_encoding
        
        return res.text
    
    def _get_soup_with_proxy(self, url=None, html=None, request_args=None):
        """
        Get BeautifulSoup object using ProxySession.
        
        Args:
            url: URL to fetch (optional if html is provided)
            html: HTML string (optional if url is provided)
            request_args: Additional request arguments
            
        Returns:
            BeautifulSoup object
        """
        from html import unescape
        from bs4 import BeautifulSoup
        from autoscraper.utils import normalize
        
        if html:
            html = normalize(unescape(html))
            return BeautifulSoup(html, "lxml")
        
        html = self._fetch_html_with_proxy(url, request_args)
        html = normalize(unescape(html))
        
        return BeautifulSoup(html, "lxml")
    
    def build(
        self,
        url: Optional[str] = None,
        wanted_list: Optional[List] = None,
        wanted_dict: Optional[Dict] = None,
        html: Optional[str] = None,
        request_args: Optional[Dict] = None,
        update: bool = False,
        text_fuzz_ratio: float = 1.0,
    ) -> List:
        """
        Build scraping rules with proxy header support.
        
        Same as AutoScraper.build() but uses ProxySession for requests.
        
        Parameters:
            url: URL of the target web page
            wanted_list: List of needed contents to be scraped
            wanted_dict: Dict of needed contents (keys are aliases)
            html: HTML string (alternative to URL)
            request_args: Request arguments including proxies
            update: If True, add to existing rules
            text_fuzz_ratio: Fuzziness ratio for matching
            
        Returns:
            List of similar results
        """
        from html import unescape
        from autoscraper.utils import normalize, unique_hashable, unique_stack_list
        
        if not wanted_list and not (wanted_dict and any(wanted_dict.values())):
            raise ValueError("No targets were supplied")
        
        # Use our proxy-aware soup getter
        soup = self._get_soup_with_proxy(url=url, html=html, request_args=request_args)
        
        result_list = []
        
        if update is False:
            self.stack_list = []
        
        if wanted_list:
            wanted_dict = {"": wanted_list}
        
        wanted_list = []
        
        for alias, wanted_items in wanted_dict.items():
            wanted_items = [normalize(w) for w in wanted_items]
            wanted_list += wanted_items
            
            for wanted in wanted_items:
                children = self._get_children(soup, wanted, url, text_fuzz_ratio)
                
                for child in children:
                    result, stack = self._get_result_for_child(child, soup, url)
                    stack["alias"] = alias
                    result_list += result
                    self.stack_list.append(stack)
        
        result_list = [item.text for item in result_list]
        result_list = unique_hashable(result_list)
        
        self.stack_list = unique_stack_list(self.stack_list)
        return result_list
    
    def get_result_similar(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        soup=None,
        request_args: Optional[Dict] = None,
        grouped: bool = False,
        group_by_alias: bool = False,
        unique: Optional[bool] = None,
        attr_fuzz_ratio: float = 1.0,
        keep_blank: bool = False,
        keep_order: bool = False,
        contain_sibling_leaves: bool = False,
    ):
        """
        Get similar results with proxy header support.
        
        Same as AutoScraper.get_result_similar() but uses ProxySession.
        """
        if soup is None and url is not None:
            soup = self._get_soup_with_proxy(url=url, html=html, request_args=request_args)
        
        return super().get_result_similar(
            url=url,
            html=html,
            soup=soup,
            request_args=None,  # Already fetched
            grouped=grouped,
            group_by_alias=group_by_alias,
            unique=unique,
            attr_fuzz_ratio=attr_fuzz_ratio,
            keep_blank=keep_blank,
            keep_order=keep_order,
            contain_sibling_leaves=contain_sibling_leaves,
        )
    
    def get_result_exact(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        soup=None,
        request_args: Optional[Dict] = None,
        grouped: bool = False,
        group_by_alias: bool = False,
        unique: Optional[bool] = None,
        attr_fuzz_ratio: float = 1.0,
        keep_blank: bool = False,
    ):
        """
        Get exact results with proxy header support.
        
        Same as AutoScraper.get_result_exact() but uses ProxySession.
        """
        if soup is None and url is not None:
            soup = self._get_soup_with_proxy(url=url, html=html, request_args=request_args)
        
        return super().get_result_exact(
            url=url,
            html=html,
            soup=soup,
            request_args=None,  # Already fetched
            grouped=grouped,
            group_by_alias=group_by_alias,
            unique=unique,
            attr_fuzz_ratio=attr_fuzz_ratio,
            keep_blank=keep_blank,
        )
    
    def get_result(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        request_args: Optional[Dict] = None,
        grouped: bool = False,
        group_by_alias: bool = False,
        unique: Optional[bool] = None,
        attr_fuzz_ratio: float = 1.0,
    ):
        """
        Get similar and exact results with proxy header support.
        
        Same as AutoScraper.get_result() but uses ProxySession.
        """
        soup = self._get_soup_with_proxy(url=url, html=html, request_args=request_args)
        
        args = dict(
            url=url,
            soup=soup,
            grouped=grouped,
            group_by_alias=group_by_alias,
            unique=unique,
            attr_fuzz_ratio=attr_fuzz_ratio,
        )
        similar = self.get_result_similar(**args)
        exact = self.get_result_exact(**args)
        return similar, exact
