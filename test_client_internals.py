#!/usr/bin/env python3
"""Exercise private client hooks against a local CONNECT proxy.

urllib3, httpx/httpcore, and aiohttp adapters override or copy private
methods. These tests call those paths and fail with the upstream symbol name
when a release moves them. No PROXY_URL or network access is required.

httpx 1.x has no adapter. Importing ``httpx_proxy`` must not raise, and using
it must raise UnsupportedHttpxVersion.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import os
import socket
import ssl
import subprocess
import sys
import tempfile
import textwrap
import threading
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
MOCK_PROXY = ROOT / "tests" / "mock_connect_proxy.py"
FAKE_IP = "203.0.113.7"
SEND_HEADER = {"X-ProxyMesh-Country": "US"}


def _runtime() -> str:
    """Describe the interpreters and client versions under test."""
    parts = [f"Python {sys.version.split()[0]}"]
    for name in ("urllib3", "requests", "httpx", "httpcore", "aiohttp"):
        try:
            module = importlib.import_module(name)
        except ImportError:
            parts.append(f"{name} not-installed")
        else:
            parts.append(f"{name} {getattr(module, '__version__', '?')}")
    return ", ".join(parts)


def _param_names(func: Any) -> List[str]:
    return list(inspect.signature(func).parameters)


def _header(headers: Any, name: str) -> Optional[str]:
    if headers is None:
        return None
    value = headers.get(name)
    if value is None:
        value = headers.get(name.lower())
    if isinstance(value, bytes):
        return value.decode("latin-1")
    if value is None:
        return None
    return str(value)


class HttpxGuardTests(unittest.TestCase):
    """httpx 1.x must not crash the import, and the extra must stay on 0.28."""

    def test_version_major(self) -> None:
        from python_proxy_headers.httpx_support import httpx_major

        self.assertEqual(httpx_major("0.28.1"), 0)
        self.assertEqual(httpx_major("1.0.dev6"), 1)
        self.assertEqual(httpx_major("1.0.0rc1"), 1)
        self.assertIsNone(httpx_major(None))
        self.assertIsNone(httpx_major(""))

    def test_classify_without_probing(self) -> None:
        from python_proxy_headers.httpx_support import classify_httpx

        self.assertEqual(classify_httpx("0.28.1").kind, "supported")
        self.assertEqual(classify_httpx("1.0.dev6").kind, "unsupported")
        self.assertEqual(classify_httpx(probe=False).kind, "missing")

    def test_imported_version_wins_when_major_disagrees(self) -> None:
        from unittest import mock

        from python_proxy_headers.httpx_support import classify_httpx

        with mock.patch(
            "python_proxy_headers.httpx_support._imported_version",
            return_value="1.0.dev6",
        ), mock.patch(
            "python_proxy_headers.httpx_support._metadata_version",
            return_value="0.28.1",
        ):
            status = classify_httpx()
        self.assertEqual(status.kind, "unsupported")
        self.assertEqual(status.version, "1.0.dev6")

    def test_unsupported_message_names_issue_and_extra(self) -> None:
        from python_proxy_headers.httpx_support import (
            HttpxStatus,
            install_message,
        )

        text = install_message(HttpxStatus("unsupported", "1.0.dev6"))
        self.assertIn("1.0.dev6", text)
        self.assertIn("947", text)
        self.assertIn("httpx>=0.28,<1", text)
        self.assertIn("AsyncHTTPTransport", text)
        missing = install_message(HttpxStatus("missing", None))
        self.assertIn("python-proxy-headers[httpx]", missing)

    def test_pyproject_pins_httpx_extra_and_changelog(self) -> None:
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('httpx = ["httpx>=0.28,<1"]', text)
        self.assertIn(
            'Changelog = "https://github.com/proxymesh/python-proxy-headers/blob/main/CHANGELOG.md"',
            text,
        )
        self.assertNotIn("commits/main", text)
        for keyword in ("proxy-headers", "https-proxy", "proxymesh"):
            self.assertIn(f'"{keyword}"', text)
        self.assertIn("Topic :: Internet :: Proxy Servers", text)
        self.assertIn('requires-python = ">=3.10"', text)

    def test_import_matches_installed_httpx(self) -> None:
        """Importing httpx_proxy succeeds for both 0.28.x and 1.x."""
        code = textwrap.dedent(
            """
            import warnings
            warnings.simplefilter("always")
            import python_proxy_headers.httpx_proxy as proxy

            print("STATUS", proxy.HTTPX_STATUS.kind, proxy.HTTPX_STATUS.version or "-")
            if proxy.HTTPX_STATUS.kind == "supported":
                print("READY", callable(proxy.get))
            else:
                try:
                    proxy.get("https://example.invalid", proxy="http://127.0.0.1:9")
                    print("NO_RAISE")
                except proxy.UnsupportedHttpxVersion as exc:
                    text = str(exc)
                    print("RAISED")
                    print("HAS947", "947" in text)
                    print("HAS_EXTRA", "python-proxy-headers[httpx]" in text)
            """
        )
        completed = _run_python(code, extra_pythonpath=[])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("ImportError", completed.stderr)
        kind = _status_kind(completed.stdout)
        if kind == "supported":
            self.assertIn("READY True", completed.stdout)
            self.assertNotIn("drops httpcore", completed.stderr)
        elif kind == "unsupported":
            self.assertIn("RAISED", completed.stdout)
            self.assertIn("HAS947 True", completed.stdout)
            self.assertIn("947", completed.stderr)
            self.assertIn("UserWarning", completed.stderr)
        elif kind == "missing":
            self.assertIn("RAISED", completed.stdout)
            self.assertIn("HAS_EXTRA True", completed.stdout)
            self.assertNotIn("UserWarning", completed.stderr)
        else:
            self.fail(f"unexpected httpx status {kind}\n{completed.stdout}\n{completed.stderr}")

    def test_shadowed_httpx_1_dev6_does_not_crash_on_import(self) -> None:
        """A 1.0.dev6 module earlier on sys.path must not raise ImportError."""
        fake = Path(tempfile.mkdtemp())
        package = fake / "httpx"
        package.mkdir()
        (package / "__init__.py").write_text('__version__ = "1.0.dev6"\n', encoding="utf-8")
        code = textwrap.dedent(
            """
            import warnings
            warnings.simplefilter("always")
            import python_proxy_headers.httpx_proxy as proxy

            print("STATUS", proxy.HTTPX_STATUS.kind, proxy.HTTPX_STATUS.version or "-")
            for label, call in (
                ("get", lambda: proxy.get("https://example.invalid", proxy="http://127.0.0.1:9")),
                ("transport", lambda: proxy.HTTPProxyTransport(proxy="http://127.0.0.1:9")),
                ("async-transport", lambda: proxy.AsyncHTTPProxyTransport(proxy="http://127.0.0.1:9")),
                ("stream", lambda: proxy.stream("GET", "https://example.invalid", proxy="http://127.0.0.1:9")),
            ):
                try:
                    call()
                    print("NO_RAISE", label)
                except proxy.UnsupportedHttpxVersion:
                    print("RAISED", label)
            """
        )
        completed = _run_python(code, extra_pythonpath=[fake])
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("STATUS unsupported 1.0.dev6", completed.stdout)
        for label in ("get", "transport", "async-transport", "stream"):
            self.assertIn(f"RAISED {label}", completed.stdout)
        self.assertNotIn("NO_RAISE", completed.stdout)
        self.assertNotIn("ImportError", completed.stderr)
        self.assertIn("1.0.dev6", completed.stderr)
        self.assertIn("947", completed.stderr)


class Urllib3ContractTests(unittest.TestCase):
    def test_prepare_proxy_signature_still_matches(self) -> None:
        import urllib3
        from urllib3.connectionpool import HTTPSConnectionPool

        from python_proxy_headers.urllib3_proxy_manager import HTTPSProxyConnectionPool

        base = _param_names(HTTPSConnectionPool._prepare_proxy)
        ours = _param_names(HTTPSProxyConnectionPool._prepare_proxy)
        self.assertIsNot(
            HTTPSProxyConnectionPool._prepare_proxy,
            HTTPSConnectionPool._prepare_proxy,
        )
        if base != ours:
            self.fail(
                "urllib3 HTTPSConnectionPool._prepare_proxy signature changed. "
                f"python_proxy_headers override parameters are {ours}; "
                f"upstream parameters are now {base}. urllib3 {urllib3.__version__}. "
                "HTTPSProxyConnectionPool._prepare_proxy in urllib3_proxy_manager.py "
                "needs an update before CONNECT header capture keeps working."
            )

    def test_tunnel_and_read_headers_hooks(self) -> None:
        import http.client
        import urllib3
        from python_proxy_headers.urllib3_proxy_manager import HTTPSProxyConnection

        if not hasattr(http.client, "_read_headers"):
            self.fail(
                "http.client._read_headers is gone. urllib3_proxy_manager.py "
                "imports it at module level (and the <3.12 _tunnel copy calls it). "
                f"{_runtime()}."
            )
        if sys.version_info < (3, 12):
            if "_tunnel" not in HTTPSProxyConnection.__dict__:
                self.fail(
                    "HTTPSProxyConnection._tunnel is not defined on Python "
                    f"{sys.version.split()[0]}. The <3.12 branch copies "
                    "HTTPConnection._tunnel and reads headers with "
                    f"http.client._read_headers. urllib3 {urllib3.__version__}."
                )
            if "get_proxy_response_headers" not in HTTPSProxyConnection.__dict__:
                self.fail(
                    "HTTPSProxyConnection.get_proxy_response_headers is missing "
                    "on Python < 3.12, so _prepare_proxy cannot read CONNECT headers."
                )
        else:
            if not hasattr(http.client.HTTPConnection, "get_proxy_response_headers"):
                self.fail(
                    "HTTPConnection.get_proxy_response_headers is missing. On "
                    "Python 3.12+, HTTPSProxyConnectionPool._prepare_proxy reads "
                    "CONNECT headers through that stdlib method. "
                    f"{_runtime()}."
                )
            if not hasattr(http.client.HTTPConnection, "_tunnel"):
                self.fail(
                    "HTTPConnection._tunnel is missing. urllib3 still opens the "
                    f"CONNECT tunnel through it. {_runtime()}."
                )


class HttpxContractTests(unittest.TestCase):
    def test_copied_handle_request_still_matches_httpcore(self) -> None:
        self._require_httpx_0()
        import httpcore
        import httpx
        from httpcore._async.http_proxy import AsyncHTTPProxy, AsyncTunnelHTTPConnection
        from httpcore._sync.http_proxy import HTTPProxy, TunnelHTTPConnection, merge_headers

        from python_proxy_headers.httpx_proxy import (
            AsyncHTTPProxyHeaders,
            AsyncProxyTunnelHTTPConnection,
            HTTPProxyHeaders,
            ProxyTunnelHTTPConnection,
        )

        required = (
            "proxy_origin",
            "remote_origin",
            "ssl_context",
            "proxy_ssl_context",
            "proxy_headers",
            "keepalive_expiry",
            "http1",
            "http2",
            "network_backend",
        )
        params = inspect.signature(TunnelHTTPConnection.__init__).parameters
        missing = [name for name in required if name not in params]
        if missing or not hasattr(TunnelHTTPConnection, "handle_request"):
            self.fail(
                "httpcore TunnelHTTPConnection no longer matches the copied "
                "ProxyTunnelHTTPConnection.handle_request. Missing "
                f"{missing or ['handle_request']}. httpcore {httpcore.__version__}, "
                f"httpx {httpx.__version__}."
            )
        if not hasattr(AsyncTunnelHTTPConnection, "handle_async_request"):
            self.fail(
                "httpcore AsyncTunnelHTTPConnection.handle_async_request is gone. "
                f"httpcore {httpcore.__version__}."
            )
        self.assertTrue(callable(merge_headers))
        self.assertTrue(hasattr(HTTPProxy, "create_connection"))
        self.assertTrue(hasattr(AsyncHTTPProxy, "create_connection"))
        self.assertIsNot(
            ProxyTunnelHTTPConnection.handle_request,
            TunnelHTTPConnection.handle_request,
        )
        self.assertIsNot(
            AsyncProxyTunnelHTTPConnection.handle_async_request,
            AsyncTunnelHTTPConnection.handle_async_request,
        )
        self.assertIsNot(HTTPProxyHeaders.create_connection, HTTPProxy.create_connection)
        self.assertIsNot(
            AsyncHTTPProxyHeaders.create_connection,
            AsyncHTTPProxy.create_connection,
        )

    def _require_httpx_0(self) -> None:
        from python_proxy_headers.httpx_proxy import HTTPX_STATUS

        if HTTPX_STATUS.kind != "supported":
            self.skipTest(
                "httpcore handle_request checks need httpx 0.28.x; "
                f"found {HTTPX_STATUS.kind} {HTTPX_STATUS.version}. "
                "httpx 1.x has no CONNECT adapter (encode/httpx#947)."
            )


class AiohttpContractTests(unittest.TestCase):
    def test_create_proxy_connection_signature_and_helpers(self) -> None:
        import aiohttp
        from aiohttp.connector import TCPConnector

        from python_proxy_headers.aiohttp_proxy import ProxyTCPConnector

        base = _param_names(TCPConnector._create_proxy_connection)
        ours = _param_names(ProxyTCPConnector._create_proxy_connection)
        if base != ours:
            self.fail(
                "aiohttp TCPConnector._create_proxy_connection signature changed. "
                f"ProxyTCPConnector copy parameters are {ours}; upstream parameters "
                f"are now {base}. aiohttp {aiohttp.__version__}. The copy in "
                "aiohttp_proxy.py has to be updated or CONNECT headers will not "
                "be captured."
            )
        required = (
            "_fail_on_no_start_tls",
            "_loop_supports_start_tls",
            "_create_direct_connection",
            "_warn_about_tls_in_tls",
            "_get_ssl_context",
            "_wrap_existing_connection",
            "_start_tls_connection",
        )
        missing = [name for name in required if not hasattr(TCPConnector, name)]
        if missing:
            self.fail(
                "aiohttp TCPConnector dropped helpers used by the copied "
                f"_create_proxy_connection: {', '.join(missing)}. "
                f"aiohttp {aiohttp.__version__}."
            )

        async def _instance_attrs() -> List[str]:
            connector = ProxyTCPConnector()
            try:
                return [
                    name
                    for name in ("_timeout_ceil_threshold", "_factory")
                    if not hasattr(connector, name)
                ]
            finally:
                await connector.close()

        absent = asyncio.run(_instance_attrs())
        if absent:
            self.fail(
                "ProxyTCPConnector instances no longer have "
                f"{', '.join(absent)}, which the copied _create_proxy_connection "
                f"reads. aiohttp {aiohttp.__version__}."
            )


class _LocalTunnel:
    """TLS origin plus tests/mock_connect_proxy.py on 127.0.0.1."""

    def __init__(self) -> None:
        self.proxy_port = 0
        self.origin_port = 0
        self.logs: List[str] = []
        self._proc: Optional[subprocess.Popen[str]] = None
        self._origin: Optional[socket.socket] = None
        self._stop = threading.Event()
        self._tmpdir = tempfile.mkdtemp()

    @property
    def proxy_url(self) -> str:
        return f"http://127.0.0.1:{self.proxy_port}"

    @property
    def origin_url(self) -> str:
        return f"https://127.0.0.1:{self.origin_port}/"

    def start(self) -> None:
        key = os.path.join(self._tmpdir, "key.pem")
        cert = os.path.join(self._tmpdir, "cert.pem")
        subprocess.check_call(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                key,
                "-out",
                cert,
                "-days",
                "1",
                "-nodes",
                "-subj",
                "/CN=127.0.0.1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        origin = socket.socket()
        origin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        origin.bind(("127.0.0.1", 0))
        origin.listen(16)
        self._origin = origin
        self.origin_port = origin.getsockname()[1]
        threading.Thread(
            target=self._serve_origin, args=(context,), daemon=True
        ).start()

        self._proc = subprocess.Popen(
            [sys.executable, str(MOCK_PROXY), "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert self._proc.stdout is not None
        assert self._proc.stderr is not None
        threading.Thread(target=self._read_logs, args=(self._proc.stderr,), daemon=True).start()
        line = self._proc.stdout.readline().strip()
        if not line.startswith("PORT "):
            self.stop()
            raise RuntimeError(
                "mock_connect_proxy did not report a port "
                f"({line!r}). logs={''.join(self.logs)!r}"
            )
        self.proxy_port = int(line.split()[1])

    def stop(self) -> None:
        self._stop.set()
        if self._origin is not None:
            try:
                self._origin.close()
            except OSError:
                pass
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()

    def _read_logs(self, stream: Any) -> None:
        for line in stream:
            self.logs.append(line)

    def _serve_origin(self, context: ssl.SSLContext) -> None:
        assert self._origin is not None
        self._origin.settimeout(0.5)
        while not self._stop.is_set():
            try:
                conn, _addr = self._origin.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            threading.Thread(
                target=self._handle_origin, args=(context, conn), daemon=True
            ).start()

    def _handle_origin(self, context: ssl.SSLContext, conn: socket.socket) -> None:
        try:
            tls = context.wrap_socket(conn, server_side=True)
            tls.settimeout(5)
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = tls.recv(4096)
                if not chunk:
                    break
                data += chunk
            body = b"origin-body"
            tls.sendall(
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: text/plain\r\n"
                b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                b"Connection: close\r\n\r\n" + body
            )
            try:
                tls.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            tls.close()
        except Exception:
            try:
                conn.close()
            except OSError:
                pass


class MockProxyFunctionalTests(unittest.TestCase):
    """End-to-end CONNECT through the private hooks. Fails if they drift."""

    tunnel: _LocalTunnel

    @classmethod
    def setUpClass(cls) -> None:
        import urllib3

        urllib3.disable_warnings()
        cls.tunnel = _LocalTunnel()
        cls.tunnel.start()

    @classmethod
    def tearDownClass(cls) -> None:
        tunnel = getattr(cls, "tunnel", None)
        if tunnel is not None:
            tunnel.stop()

    def test_urllib3_prepare_proxy_reads_connect_headers(self) -> None:
        import urllib3
        from python_proxy_headers.urllib3_proxy_manager import proxy_from_url

        context = ssl._create_unverified_context()
        try:
            with proxy_from_url(
                self.tunnel.proxy_url,
                proxy_headers=SEND_HEADER,
                ssl_context=context,
                retries=False,
            ) as manager:
                response = manager.request("GET", self.tunnel.origin_url, timeout=8.0)
        except Exception as exc:
            self.fail(self._hook("urllib3", "HTTPSProxyConnectionPool._prepare_proxy and HTTPConnection._tunnel / http.client._read_headers", exc))
        self.assertEqual(response.status, 200, _runtime())
        self.assertEqual(response.data, b"origin-body")
        self._assert_merged(
            response.headers,
            "urllib3",
            "HTTPSProxyConnectionPool._prepare_proxy",
            urllib3.__version__,
        )

    def test_httpx_handle_request_merges_connect_headers(self) -> None:
        self._require_httpx_0()
        import httpcore
        import httpx
        from python_proxy_headers.httpx_proxy import (
            AsyncHTTPProxyTransport,
            HTTPProxyTransport,
        )

        proxy = httpx.Proxy(self.tunnel.proxy_url, headers=SEND_HEADER)
        try:
            transport = HTTPProxyTransport(proxy=proxy, verify=False)
            with httpx.Client(
                mounts={"https://": transport},
                verify=False,
                timeout=8.0,
            ) as client:
                response = client.get(self.tunnel.origin_url)
        except Exception as exc:
            self.fail(
                self._hook(
                    "httpx",
                    "ProxyTunnelHTTPConnection.handle_request (copy of httpcore TunnelHTTPConnection.handle_request)",
                    exc,
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "origin-body")
        self._assert_merged(
            response.headers,
            "httpx",
            "ProxyTunnelHTTPConnection.handle_request",
            f"httpx {httpx.__version__} / httpcore {httpcore.__version__}",
        )

        async def _async_get() -> Any:
            async_proxy = httpx.Proxy(self.tunnel.proxy_url, headers=SEND_HEADER)
            async_transport = AsyncHTTPProxyTransport(proxy=async_proxy, verify=False)
            async with httpx.AsyncClient(
                mounts={"https://": async_transport},
                verify=False,
                timeout=8.0,
            ) as client:
                return await client.get(self.tunnel.origin_url)

        try:
            async_response = asyncio.run(_async_get())
        except Exception as exc:
            self.fail(
                self._hook(
                    "httpx",
                    "AsyncProxyTunnelHTTPConnection.handle_async_request",
                    exc,
                )
            )
        self._assert_merged(
            async_response.headers,
            "httpx",
            "AsyncProxyTunnelHTTPConnection.handle_async_request",
            f"httpx {httpx.__version__} / httpcore {httpcore.__version__}",
        )

    def test_aiohttp_create_proxy_connection_reads_connect_headers(self) -> None:
        import aiohttp
        from python_proxy_headers.aiohttp_proxy import ProxyClientSession

        async def _get() -> Dict[str, Optional[str]]:
            timeout = aiohttp.ClientTimeout(total=8)
            async with ProxyClientSession(timeout=timeout) as session:
                async with session.get(
                    self.tunnel.origin_url,
                    proxy=self.tunnel.proxy_url,
                    proxy_headers=SEND_HEADER,
                    ssl=False,
                ) as response:
                    body = await response.text()
                    return {
                        "status": str(response.status),
                        "body": body,
                        "ip": _header(response.headers, "X-ProxyMesh-IP"),
                        "echo": _header(response.headers, "X-ProxyMesh-Country-Echo"),
                    }

        try:
            result = asyncio.run(_get())
        except Exception as exc:
            self.fail(
                self._hook(
                    "aiohttp",
                    "ProxyTCPConnector._create_proxy_connection (copy of TCPConnector._create_proxy_connection)",
                    exc,
                )
            )
        self.assertEqual(result["status"], "200")
        self.assertEqual(result["body"], "origin-body")
        self.assertEqual(
            result["ip"],
            FAKE_IP,
            "aiohttp copied _create_proxy_connection did not surface "
            f"X-ProxyMesh-IP. aiohttp {aiohttp.__version__}. {_runtime()}. "
            f"proxy log: {''.join(self.tunnel.logs)!r}",
        )
        self.assertEqual(result["echo"], "US")

    def _require_httpx_0(self) -> None:
        from python_proxy_headers.httpx_proxy import HTTPX_STATUS

        if HTTPX_STATUS.kind != "supported":
            self.skipTest(
                "httpx CONNECT checks need httpx 0.28.x; "
                f"found {HTTPX_STATUS.kind} {HTTPX_STATUS.version}."
            )

    def _hook(self, library: str, hook: str, exc: BaseException) -> str:
        return (
            f"{library} private hook failed ({hook}). A method this package "
            f"overrides or copies no longer matches the installed release: "
            f"{type(exc).__name__}: {exc}. {_runtime()}. "
            f"proxy log: {''.join(self.tunnel.logs)!r}"
        )

    def _assert_merged(self, headers: Any, library: str, hook: str, version: str) -> None:
        ip = _header(headers, "X-ProxyMesh-IP")
        echo = _header(headers, "X-ProxyMesh-Country-Echo")
        self.assertEqual(
            ip,
            FAKE_IP,
            f"{library} {hook} did not merge X-ProxyMesh-IP from the CONNECT "
            f"response ({version}). {_runtime()}. "
            f"proxy log: {''.join(self.tunnel.logs)!r}",
        )
        self.assertEqual(
            echo,
            "US",
            f"{library} {hook} did not echo X-ProxyMesh-Country onto the "
            f"CONNECT response ({version}). The request header never reached "
            f"the proxy, or the response header was dropped. {_runtime()}.",
        )


class OptionalClientImportTests(unittest.TestCase):
    """Import adapters for clients that are installed. Skip when they are not."""

    def test_pycurl_module_imports(self) -> None:
        self._import_pair("pycurl", "python_proxy_headers.pycurl_proxy")

    def test_cloudscraper_module_imports(self) -> None:
        self._import_pair("cloudscraper", "python_proxy_headers.cloudscraper_proxy")

    def test_autoscraper_module_imports(self) -> None:
        self._import_pair("autoscraper", "python_proxy_headers.autoscraper_proxy")

    def _import_pair(self, distribution: str, module_name: str) -> None:
        try:
            importlib.import_module(distribution)
        except ImportError:
            self.skipTest(f"{distribution} is not installed")
        importlib.import_module(module_name)


def _run_python(code: str, extra_pythonpath: List[Path]) -> subprocess.CompletedProcess[str]:
    script = Path(tempfile.mkdtemp()) / "check_httpx_import.py"
    script.write_text(code, encoding="utf-8")
    parts = [str(path) for path in extra_pythonpath]
    parts.append(str(ROOT))
    existing = os.environ.get("PYTHONPATH")
    if existing:
        parts.append(existing)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return subprocess.run(
        [sys.executable, str(script)],
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def _status_kind(stdout: str) -> str:
    for line in stdout.splitlines():
        if line.startswith("STATUS "):
            return line.split()[1]
    return ""


if __name__ == "__main__":
    unittest.main()
