#!/usr/bin/env python3
"""Unit tests for CONNECT header validation and safe origin-header merging."""

from __future__ import annotations

import os
import socket
import ssl
import subprocess
import tempfile
import threading
import time
import unittest

from python_proxy_headers.header_utils import (
    filter_connect_headers,
    is_mergeable_proxy_header,
    merge_proxy_response_headers,
    validate_header_name,
    validate_header_value,
    validate_headers,
)


class ValidateHeadersTests(unittest.TestCase):
    def test_accepts_normal_proxy_header(self) -> None:
        self.assertEqual(
            validate_headers({"X-ProxyMesh-Country": "US"}),
            {"X-ProxyMesh-Country": "US"},
        )

    def test_rejects_crlf_in_value(self) -> None:
        with self.assertRaises(ValueError):
            validate_header_value("US\r\nX-Injected: pwned")

    def test_rejects_crlf_in_name(self) -> None:
        with self.assertRaises(ValueError):
            validate_header_name("X-Foo: bar\r\nX-Injected")

    def test_rejects_nul(self) -> None:
        with self.assertRaises(ValueError):
            validate_headers({"X-ProxyMesh-Country": "US\x00evil"})

    def test_proxy_from_url_rejects_crlf(self) -> None:
        from python_proxy_headers.urllib3_proxy_manager import proxy_from_url

        with self.assertRaises(ValueError):
            proxy_from_url(
                "http://127.0.0.1:9",
                proxy_headers={
                    "X-ProxyMesh-Country": "US\r\nProxy-Authorization: Basic ZXZpbDpldmls"
                },
            )

    def test_requests_adapter_rejects_crlf(self) -> None:
        from python_proxy_headers.requests_adapter import ProxySession

        with self.assertRaises(ValueError):
            ProxySession(proxy_headers={"X-ProxyMesh-Country": "US\r\nX-Injected: pwned"})

    def test_pycurl_rejects_crlf(self) -> None:
        try:
            import pycurl
            from python_proxy_headers.pycurl_proxy import set_proxy_headers
        except ImportError:
            self.skipTest("pycurl is not installed")
        curl = pycurl.Curl()
        try:
            with self.assertRaises(ValueError):
                set_proxy_headers(
                    curl, {"X-ProxyMesh-Country": "US\r\nX-Injected: pwned"}
                )
        finally:
            curl.close()


class MergeProxyHeadersTests(unittest.TestCase):
    def test_merges_custom_proxy_header(self) -> None:
        origin = {"Content-Type": "text/plain"}
        merge_proxy_response_headers(origin, {"X-Custom-Exit-IP": "203.0.113.10"})
        self.assertEqual(origin["X-Custom-Exit-IP"], "203.0.113.10")
        self.assertEqual(origin["Content-Type"], "text/plain")

    def test_does_not_overwrite_origin(self) -> None:
        origin = {"X-Custom-Exit-IP": "origin-value"}
        merge_proxy_response_headers(origin, {"X-Custom-Exit-IP": "proxy-value"})
        self.assertEqual(origin["X-Custom-Exit-IP"], "origin-value")

    def test_blocks_set_cookie_and_location(self) -> None:
        origin = {"Content-Type": "text/plain"}
        merge_proxy_response_headers(
            origin,
            {
                "Set-Cookie": "session=attacker",
                "Location": "https://evil.example/",
                "Content-Type": "text/html",
                "Proxy-Connection": "Keep-Alive",
                "X-Custom-Exit-IP": "203.0.113.10",
            },
        )
        self.assertEqual(origin["Content-Type"], "text/plain")
        self.assertNotIn("Set-Cookie", origin)
        self.assertNotIn("Location", origin)
        self.assertNotIn("Proxy-Connection", origin)
        self.assertEqual(origin["X-Custom-Exit-IP"], "203.0.113.10")

    def test_is_mergeable_skips_sensitive_headers(self) -> None:
        self.assertTrue(is_mergeable_proxy_header("X-Custom-Exit-IP"))
        self.assertTrue(is_mergeable_proxy_header("X-ProxyMesh-IP"))
        self.assertFalse(is_mergeable_proxy_header("Set-Cookie"))
        self.assertFalse(is_mergeable_proxy_header("Location"))
        self.assertFalse(is_mergeable_proxy_header("Proxy-Connection"))

    def test_filter_connect_headers_preserves_bytes(self) -> None:
        origin = [(b"content-type", b"text/plain")]
        connect = [
            (b"set-cookie", b"session=attacker"),
            (b"x-custom-exit-ip", b"203.0.113.10"),
        ]
        extra = filter_connect_headers(origin, connect)
        self.assertEqual(extra, [(b"x-custom-exit-ip", b"203.0.113.10")])


class _LocalHttpsProxy:
    """Minimal CONNECT proxy plus TLS origin for merge/injection tests."""

    def __init__(self, connect_headers: bytes) -> None:
        self.connect_headers = connect_headers
        self.captured_connect = b""
        self._tmpdir = tempfile.mkdtemp()
        self._key = os.path.join(self._tmpdir, "key.pem")
        self._cert = os.path.join(self._tmpdir, "cert.pem")
        subprocess.check_call(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                self._key,
                "-out",
                self._cert,
                "-days",
                "1",
                "-nodes",
                "-subj",
                "/CN=127.0.0.1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self._ctx.load_cert_chain(self._cert, self._key)
        self._origin = socket.socket()
        self._origin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._origin.bind(("127.0.0.1", 0))
        self.origin_port = self._origin.getsockname()[1]
        self._proxy = socket.socket()
        self._proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._proxy.bind(("127.0.0.1", 0))
        self.proxy_port = self._proxy.getsockname()[1]
        self._threads = [
            threading.Thread(target=self._run_origin, daemon=True),
            threading.Thread(target=self._run_proxy, daemon=True),
        ]

    def start(self) -> None:
        for thread in self._threads:
            thread.start()
        time.sleep(0.05)

    def close(self) -> None:
        for sock in (self._origin, self._proxy):
            try:
                sock.close()
            except OSError:
                pass

    def _run_origin(self) -> None:
        self._origin.listen(5)
        self._origin.settimeout(8)
        try:
            conn, _ = self._origin.accept()
        except (socket.timeout, OSError):
            return
        try:
            tls = self._ctx.wrap_socket(conn, server_side=True)
            tls.settimeout(3)
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
                b"Set-Cookie: origin=safe\r\n"
                b"X-Origin: real\r\n"
                b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                b"\r\n" + body
            )
            tls.close()
        except Exception:
            try:
                conn.close()
            except OSError:
                pass

    def _run_proxy(self) -> None:
        self._proxy.listen(5)
        self._proxy.settimeout(8)
        try:
            conn, _ = self._proxy.accept()
        except (socket.timeout, OSError):
            return
        conn.settimeout(5)
        data = b""
        try:
            while b"\r\n\r\n" not in data:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
        except OSError:
            pass
        self.captured_connect = data
        try:
            conn.sendall(b"HTTP/1.1 200 Connection Established\r\n" + self.connect_headers + b"\r\n")
        except OSError:
            conn.close()
            return
        try:
            origin = socket.create_connection(("127.0.0.1", self.origin_port), timeout=5)
        except OSError:
            conn.close()
            return
        conn.setblocking(False)
        origin.setblocking(False)
        deadline = time.time() + 4
        while time.time() < deadline:
            moved = False
            for src, dst in ((conn, origin), (origin, conn)):
                try:
                    chunk = src.recv(8192)
                except BlockingIOError:
                    chunk = None
                except OSError:
                    chunk = b""
                if chunk:
                    try:
                        dst.sendall(chunk)
                        moved = True
                    except OSError:
                        deadline = 0
                        break
                elif chunk == b"":
                    deadline = 0
                    break
            if not moved:
                time.sleep(0.01)
        for sock in (conn, origin):
            try:
                sock.close()
            except OSError:
                pass


class ConnectMergeIntegrationTests(unittest.TestCase):
    def test_urllib3_does_not_copy_hostile_connect_headers(self) -> None:
        import urllib3
        from python_proxy_headers.requests_adapter import ProxySession

        urllib3.disable_warnings()
        helper = _LocalHttpsProxy(
            b"Set-Cookie: session=attacker\r\n"
            b"Location: https://evil.example/\r\n"
            b"Content-Type: text/html\r\n"
            b"X-Origin: spoofed\r\n"
            b"X-Custom-Exit-IP: 203.0.113.10\r\n"
        )
        helper.start()
        try:
            with ProxySession() as session:
                session.verify = False
                session.proxies = {"https": f"http://127.0.0.1:{helper.proxy_port}"}
                response = session.get(
                    f"https://127.0.0.1:{helper.origin_port}/", timeout=5
                )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "origin-body")
            self.assertEqual(response.headers.get("Content-Type"), "text/plain")
            self.assertEqual(response.headers.get("X-Origin"), "real")
            self.assertNotEqual(response.headers.get("Location"), "https://evil.example/")
            self.assertNotIn("session=attacker", response.headers.get("Set-Cookie", ""))
            self.assertEqual(response.headers.get("X-Custom-Exit-IP"), "203.0.113.10")
            self.assertEqual(response.cookies.get("origin"), "safe")
            self.assertNotIn("session", response.cookies)
            proxy_headers = {k.lower(): v for k, v in (response.proxy_headers or {}).items()}
            self.assertEqual(proxy_headers.get("x-custom-exit-ip"), "203.0.113.10")
            self.assertEqual(proxy_headers.get("set-cookie"), "session=attacker")
        finally:
            helper.close()

    def test_urllib3_does_not_send_injected_connect_header(self) -> None:
        from python_proxy_headers.urllib3_proxy_manager import proxy_from_url

        helper = _LocalHttpsProxy(b"")
        helper.start()
        try:
            with self.assertRaises(ValueError):
                proxy_from_url(
                    f"http://127.0.0.1:{helper.proxy_port}",
                    proxy_headers={"X-ProxyMesh-Country": "US\r\nX-Injected: pwned"},
                    timeout=2.0,
                    retries=False,
                )
            self.assertEqual(helper.captured_connect, b"")
        finally:
            helper.close()


if __name__ == "__main__":
    unittest.main()
