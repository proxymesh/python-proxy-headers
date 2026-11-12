"""The private hooks this package overrides are still present upstream."""

import http.client
import inspect
import sys
import unittest

from aiohttp.connector import TCPConnector
from httpcore._async.http_proxy import AsyncHTTPProxy, AsyncTunnelHTTPConnection
from httpcore._sync.http_proxy import HTTPProxy, TunnelHTTPConnection
from urllib3.connectionpool import HTTPSConnectionPool

from python_proxy_headers.aiohttp_proxy import ProxyTCPConnector
from python_proxy_headers.httpx_proxy import (
    AsyncHTTPProxyHeaders,
    AsyncProxyTunnelHTTPConnection,
    HTTPProxyHeaders,
    ProxyTunnelHTTPConnection,
)
from python_proxy_headers.urllib3_proxy_manager import (
    HTTPSProxyConnection,
    HTTPSProxyConnectionPool,
)


class HookTests(unittest.TestCase):
    def test_urllib3_prepare_proxy(self) -> None:
        self.assertIsNot(
            HTTPSProxyConnectionPool._prepare_proxy,
            HTTPSConnectionPool._prepare_proxy,
        )
        self.assertEqual(
            list(inspect.signature(HTTPSProxyConnectionPool._prepare_proxy).parameters),
            list(inspect.signature(HTTPSConnectionPool._prepare_proxy).parameters),
        )
        self.assertTrue(callable(http.client._read_headers))
        if sys.version_info < (3, 12):
            self.assertTrue(callable(HTTPSProxyConnection._tunnel))
        else:
            self.assertTrue(callable(http.client.HTTPConnection._tunnel))
            self.assertTrue(
                callable(http.client.HTTPConnection.get_proxy_response_headers)
            )

    def test_httpx_handle_request(self) -> None:
        self.assertIsNot(
            ProxyTunnelHTTPConnection.handle_request,
            TunnelHTTPConnection.handle_request,
        )
        self.assertIsNot(
            AsyncProxyTunnelHTTPConnection.handle_async_request,
            AsyncTunnelHTTPConnection.handle_async_request,
        )
        self.assertIsNot(
            HTTPProxyHeaders.create_connection,
            HTTPProxy.create_connection,
        )
        self.assertIsNot(
            AsyncHTTPProxyHeaders.create_connection,
            AsyncHTTPProxy.create_connection,
        )
        params = inspect.signature(TunnelHTTPConnection.__init__).parameters
        for name in (
            "proxy_origin",
            "remote_origin",
            "ssl_context",
            "proxy_ssl_context",
            "proxy_headers",
            "keepalive_expiry",
            "http1",
            "http2",
            "network_backend",
        ):
            self.assertIn(name, params)

    def test_aiohttp_create_proxy_connection(self) -> None:
        self.assertEqual(
            list(
                inspect.signature(ProxyTCPConnector._create_proxy_connection).parameters
            ),
            list(inspect.signature(TCPConnector._create_proxy_connection).parameters),
        )


if __name__ == "__main__":
    unittest.main()
