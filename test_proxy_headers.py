#!/usr/bin/env python3
"""
Test harness for python-proxy-headers extensions.

This script tests each module's ability to:
1. Make a request through a proxy
2. Receive and capture proxy response headers
3. Extract the specified header (default: X-ProxyMesh-IP)

Configuration via environment variables:
    PROXY_URL       - Proxy URL (e.g., http://user:pass@proxy.example.com:8080)
    HTTPS_PROXY     - Fallback if PROXY_URL not set
    TEST_URL        - URL to request (default: https://httpbin.org/ip)
    PROXY_HEADER    - Header to check for (default: X-ProxyMesh-IP)

Usage:
    python test_proxy_headers.py [module1] [module2] ...
    
    # Test all modules
    python test_proxy_headers.py
    
    # Test specific modules
    python test_proxy_headers.py requests httpx
    
    # With custom header
    PROXY_HEADER=X-Custom-Header python test_proxy_headers.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import os
import sys
import importlib
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List, Type
from urllib.parse import urlparse


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class TestConfig:
    """Test configuration from environment variables."""
    proxy_url: str
    test_url: str
    proxy_header: str
    
    @classmethod
    def from_env(cls) -> 'TestConfig':
        """Load configuration from environment variables."""
        proxy_url = os.environ.get('PROXY_URL') or os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
        if not proxy_url:
            raise EnvironmentError(
                "No proxy URL configured. Set PROXY_URL or HTTPS_PROXY environment variable."
            )
        
        test_url = os.environ.get('TEST_URL', 'https://httpbin.org/ip')
        proxy_header = os.environ.get('PROXY_HEADER', 'X-ProxyMesh-IP')
        
        return cls(
            proxy_url=proxy_url,
            test_url=test_url,
            proxy_header=proxy_header
        )


# =============================================================================
# Test Result
# =============================================================================

@dataclass
class TestResult:
    """Result of a single module test."""
    module_name: str
    success: bool
    header_value: Optional[str] = None
    error: Optional[str] = None
    response_status: Optional[int] = None
    
    def __str__(self) -> str:
        if self.success:
            return f"[PASS] {self.module_name}: {self.header_value}"
        else:
            return f"[FAIL] {self.module_name}: {self.error}"


# =============================================================================
# Base Test Class
# =============================================================================

class ModuleTest(ABC):
    """Base class for module tests."""
    
    name: str = "base"
    
    @abstractmethod
    def test(self, config: TestConfig) -> TestResult:
        """
        Run the test for this module.
        
        Args:
            config: Test configuration
            
        Returns:
            TestResult with success/failure and header value or error
        """
        pass
    
    def _check_header(self, headers: Dict[str, str], header_name: str) -> Optional[str]:
        """
        Check for header in response (case-insensitive).
        
        Args:
            headers: Response headers dict
            header_name: Header name to look for
            
        Returns:
            Header value if found, None otherwise
        """
        # Case-insensitive header lookup
        header_lower = header_name.lower()
        for key, value in headers.items():
            if key.lower() == header_lower:
                return value
        return None


# =============================================================================
# urllib3 Test
# =============================================================================

class Urllib3Test(ModuleTest):
    """Test for urllib3 extension."""
    
    name = "urllib3"
    
    def test(self, config: TestConfig) -> TestResult:
        try:
            from python_proxy_headers.urllib3_proxy_manager import proxy_from_url
            
            # Create proxy manager (ProxyHeaderManager)
            manager = proxy_from_url(config.proxy_url)
            
            # Make request
            # The extension merges proxy CONNECT headers into response.headers
            response = manager.request('GET', config.test_url)
            
            # Check for proxy header in merged response headers
            header_value = self._check_header(dict(response.headers), config.proxy_header)
            
            if header_value:
                return TestResult(
                    module_name=self.name,
                    success=True,
                    header_value=header_value,
                    response_status=response.status
                )
            else:
                return TestResult(
                    module_name=self.name,
                    success=False,
                    error=f"Header '{config.proxy_header}' not found in response",
                    response_status=response.status
                )
                
        except ImportError as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"Import error: {e}"
            )
        except Exception as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"{type(e).__name__}: {e}"
            )


# =============================================================================
# requests Test
# =============================================================================

class RequestsTest(ModuleTest):
    """Test for requests extension."""
    
    name = "requests"
    
    def test(self, config: TestConfig) -> TestResult:
        try:
            from python_proxy_headers.requests_adapter import ProxySession
            
            # Create session with proxy headers
            with ProxySession() as session:
                session.proxies = {
                    'http': config.proxy_url,
                    'https': config.proxy_url
                }
                
                # Make request
                response = session.get(config.test_url)
                
                # Check for proxy header in response
                header_value = self._check_header(dict(response.headers), config.proxy_header)
                
                if header_value:
                    return TestResult(
                        module_name=self.name,
                        success=True,
                        header_value=header_value,
                        response_status=response.status_code
                    )
                else:
                    return TestResult(
                        module_name=self.name,
                        success=False,
                        error=f"Header '{config.proxy_header}' not found in response",
                        response_status=response.status_code
                    )
                    
        except ImportError as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"Import error: {e}"
            )
        except Exception as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"{type(e).__name__}: {e}"
            )


# =============================================================================
# aiohttp Test
# =============================================================================

class AiohttpTest(ModuleTest):
    """Test for aiohttp extension."""
    
    name = "aiohttp"
    
    def test(self, config: TestConfig) -> TestResult:
        try:
            import asyncio
            from python_proxy_headers.aiohttp_proxy import ProxyClientSession
            
            async def _test_async():
                # ProxyClientSession automatically includes ProxyTCPConnector
                # and merges proxy headers into response.headers
                async with ProxyClientSession() as session:
                    async with session.get(config.test_url, proxy=config.proxy_url) as response:
                        # The extension merges proxy headers into response.headers
                        header_value = self._check_header(dict(response.headers), config.proxy_header)
                        status = response.status
                        
                        return header_value, status
            
            # Run async test
            header_value, status = asyncio.run(_test_async())
            
            if header_value:
                return TestResult(
                    module_name=self.name,
                    success=True,
                    header_value=header_value,
                    response_status=status
                )
            else:
                return TestResult(
                    module_name=self.name,
                    success=False,
                    error=f"Header '{config.proxy_header}' not found in response",
                    response_status=status
                )
                
        except ImportError as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"Import error: {e}"
            )
        except Exception as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"{type(e).__name__}: {e}"
            )


# =============================================================================
# httpx Test
# =============================================================================

class HttpxTest(ModuleTest):
    """Test for httpx extension."""
    
    name = "httpx"
    
    def test(self, config: TestConfig) -> TestResult:
        try:
            from python_proxy_headers.httpx_proxy import HTTPProxyTransport
            import httpx
            
            # Create transport with proxy
            transport = HTTPProxyTransport(proxy=config.proxy_url)
            
            # Create client with custom transport mounted for both http and https
            with httpx.Client(mounts={'http://': transport, 'https://': transport}) as client:
                response = client.get(config.test_url)
                
                # The extension merges proxy CONNECT headers into response.headers
                header_value = self._check_header(dict(response.headers), config.proxy_header)
                
                if header_value:
                    return TestResult(
                        module_name=self.name,
                        success=True,
                        header_value=header_value,
                        response_status=response.status_code
                    )
                else:
                    return TestResult(
                        module_name=self.name,
                        success=False,
                        error=f"Header '{config.proxy_header}' not found in response",
                        response_status=response.status_code
                    )
                    
        except ImportError as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"Import error: {e}"
            )
        except Exception as e:
            return TestResult(
                module_name=self.name,
                success=False,
                error=f"{type(e).__name__}: {e}"
            )


# =============================================================================
# Test Registry
# =============================================================================

# Register all available tests
AVAILABLE_TESTS: Dict[str, Type[ModuleTest]] = {
    'urllib3': Urllib3Test,
    'requests': RequestsTest,
    'aiohttp': AiohttpTest,
    'httpx': HttpxTest,
}


def get_test(name: str) -> Optional[ModuleTest]:
    """Get a test instance by name."""
    test_class = AVAILABLE_TESTS.get(name.lower())
    if test_class:
        return test_class()
    return None


def list_available_tests() -> List[str]:
    """List all available test names."""
    return list(AVAILABLE_TESTS.keys())


# =============================================================================
# Main Runner
# =============================================================================

def run_tests(test_names: Optional[List[str]] = None, config: Optional[TestConfig] = None) -> List[TestResult]:
    """
    Run tests for specified modules.
    
    Args:
        test_names: List of module names to test (None = all)
        config: Test configuration (None = load from env)
        
    Returns:
        List of TestResult objects
    """
    if config is None:
        config = TestConfig.from_env()
    
    if test_names is None or len(test_names) == 0:
        test_names = list_available_tests()
    
    results = []
    
    print(f"\n{'='*60}")
    print("Python Proxy Headers - Test Harness")
    print(f"{'='*60}")
    print(f"Proxy URL:     {_mask_password(config.proxy_url)}")
    print(f"Test URL:      {config.test_url}")
    print(f"Header:        {config.proxy_header}")
    print(f"Modules:       {', '.join(test_names)}")
    print(f"{'='*60}\n")
    
    for name in test_names:
        test = get_test(name)
        if test is None:
            result = TestResult(
                module_name=name,
                success=False,
                error=f"Unknown module. Available: {', '.join(list_available_tests())}"
            )
        else:
            print(f"Testing {name}...", end=" ", flush=True)
            result = test.test(config)
            print("OK" if result.success else "FAILED")
        
        results.append(result)
    
    return results


def _mask_password(url: str) -> str:
    """Mask password in URL for display."""
    parsed = urlparse(url)
    if parsed.password:
        masked = url.replace(f":{parsed.password}@", ":****@")
        return masked
    return url


def print_results(results: List[TestResult]) -> bool:
    """
    Print test results summary.
    
    Args:
        results: List of test results
        
    Returns:
        True if all tests passed, False otherwise
    """
    print(f"\n{'='*60}")
    print("Results")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for result in results:
        print(result)
        if result.success:
            passed += 1
        else:
            failed += 1
    
    print(f"{'='*60}")
    print(f"Passed: {passed}/{len(results)}")
    
    if failed > 0:
        print(f"Failed: {failed}/{len(results)}")
        return False
    
    print("All tests passed!")
    return True


def main():
    """Main entry point."""
    # Parse command line arguments
    test_names = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Handle --help
    if test_names and test_names[0] in ['--help', '-h']:
        print(__doc__)
        print(f"\nAvailable modules: {', '.join(list_available_tests())}")
        sys.exit(0)
    
    # Handle --list
    if test_names and test_names[0] in ['--list', '-l']:
        print("Available modules:")
        for name in list_available_tests():
            print(f"  - {name}")
        sys.exit(0)
    
    try:
        config = TestConfig.from_env()
    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nSet environment variables:", file=sys.stderr)
        print("  export PROXY_URL='http://user:pass@proxy.example.com:8080'", file=sys.stderr)
        print("  export TEST_URL='https://httpbin.org/ip'  # optional", file=sys.stderr)
        print("  export PROXY_HEADER='X-ProxyMesh-IP'  # optional", file=sys.stderr)
        sys.exit(1)
    
    try:
        results = run_tests(test_names, config)
        all_passed = print_results(results)
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
