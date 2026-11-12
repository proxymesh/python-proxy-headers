"""httpx >= 1 must raise ImportError when the httpx adapter is imported."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class HttpxGuardTests(unittest.TestCase):
    def test_httpx_1_dev6_raises_import_error(self) -> None:
        fake = Path(tempfile.mkdtemp())
        package = fake / "httpx"
        package.mkdir()
        (package / "__init__.py").write_text(
            '__version__ = "1.0.dev6"\n', encoding="utf-8"
        )
        env = os.environ.copy()
        prior = env.get("PYTHONPATH")
        parts = [str(fake), str(ROOT)]
        if prior:
            parts.append(prior)
        env["PYTHONPATH"] = os.pathsep.join(parts)
        completed = subprocess.run(
            [sys.executable, "-c", "import python_proxy_headers.httpx_proxy"],
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("ImportError", completed.stderr)
        self.assertIn("1.0.dev6", completed.stderr)
        self.assertIn("python-proxy-headers[httpx]", completed.stderr)


if __name__ == "__main__":
    unittest.main()
