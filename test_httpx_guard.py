#!/usr/bin/env python3
"""httpx >= 1 must not crash import of the httpx adapter."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class HttpxGuardTests(unittest.TestCase):
    def test_version_major(self) -> None:
        from python_proxy_headers.httpx_proxy import httpx_major

        self.assertEqual(httpx_major("0.28.1"), 0)
        self.assertEqual(httpx_major("1.0.dev6"), 1)
        self.assertEqual(httpx_major("1.0.0rc1"), 1)
        self.assertIsNone(httpx_major(None))
        self.assertIsNone(httpx_major(""))

    def test_httpx_extra_is_pinned_below_1(self) -> None:
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('httpx = ["httpx>=0.28,<1"]', text)

    def test_supported_httpx_keeps_real_transport(self) -> None:
        import httpx
        from httpcore._sync.http_proxy import TunnelHTTPConnection

        from python_proxy_headers.httpx_proxy import (
            HTTPProxyTransport,
            ProxyTunnelHTTPConnection,
            httpx_major,
        )

        if httpx_major(getattr(httpx, "__version__", None)) != 0:
            self.skipTest(f"httpx {httpx.__version__} is not the 0.28 line")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.reload(importlib.import_module("python_proxy_headers.httpx_proxy"))
        self.assertFalse([item for item in caught if issubclass(item.category, UserWarning)])
        self.assertTrue(issubclass(ProxyTunnelHTTPConnection, TunnelHTTPConnection))
        self.assertIsInstance(
            HTTPProxyTransport(proxy="http://127.0.0.1:9"), httpx.HTTPTransport
        )

    def test_httpx_1_dev6_warns_and_raises(self) -> None:
        fake = Path(tempfile.mkdtemp())
        package = fake / "httpx"
        package.mkdir()
        (package / "__init__.py").write_text('__version__ = "1.0.dev6"\n', encoding="utf-8")
        code = textwrap.dedent(
            """
            import sys
            import warnings
            warnings.simplefilter("always")
            import python_proxy_headers.httpx_proxy as proxy

            print("HTTPCORE", "httpcore" in sys.modules)
            calls = (
                ("get", lambda: proxy.get("https://example.invalid")),
                ("transport", lambda: proxy.HTTPProxyTransport(proxy="http://127.0.0.1:9")),
                ("async", lambda: proxy.AsyncHTTPProxyTransport(proxy="http://127.0.0.1:9")),
                ("stream", lambda: proxy.stream("GET", "https://example.invalid")),
            )
            for label, call in calls:
                try:
                    call()
                except proxy.UnsupportedHttpxVersion as exc:
                    text = str(exc)
                    ok = "1.0.dev6" in text and "httpx>=0.28,<1" in text
                    print("RAISED", label, ok)
            """
        )
        script = Path(tempfile.mkdtemp()) / "check_httpx_import.py"
        script.write_text(code, encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [str(fake), str(ROOT), env.get("PYTHONPATH", "")]
        )
        completed = subprocess.run(
            [sys.executable, str(script)],
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("HTTPCORE False", completed.stdout)
        self.assertNotIn("ImportError", completed.stderr)
        self.assertIn("UserWarning", completed.stderr)
        self.assertIn("1.0.dev6", completed.stderr)
        for label in ("get", "transport", "async", "stream"):
            self.assertIn(f"RAISED {label} True", completed.stdout)


if __name__ == "__main__":
    unittest.main()
