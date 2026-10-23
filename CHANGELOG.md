# Changelog

## Unreleased

### httpx 1.0

- Importing `python_proxy_headers.httpx_proxy` no longer raises `ImportError: cannot import name AsyncHTTPTransport` when httpx 1.x is installed.
- httpx 1.0.dev6 (2026-08-31) is a rewrite without httpcore, without `HTTPTransport` / `AsyncHTTPTransport`, and without proxy support ([encode/httpx#947](https://github.com/encode/httpx/issues/947)). The module warns at import time and raises `UnsupportedHttpxVersion` if you call it.
- The `[httpx]` extra is `httpx>=0.28,<1`. There is no 1.0 adapter in this change. Options are documented in `docs/httpx.rst`: stay on 0.28, wait for a public CONNECT hook, or add a small backend after `NetworkBackend` can take an existing tunnel. Vendoring httpcore is not one of them.

### Tests

- Contract checks and a local CONNECT mock (`tests/mock_connect_proxy.py`, no proxy credentials) exercise the private hooks in `urllib3_proxy_manager.py` (`_prepare_proxy`, `_tunnel`, `http.client._read_headers`), `httpx_proxy` (copied httpcore `handle_request` / `handle_async_request`), and `aiohttp_proxy.py` (copied `_create_proxy_connection`). They name the upstream symbol when it moves.

### Packaging

- Keywords, trove classifiers, and optional extras: `[urllib3]`, `[requests]`, `[httpx]`, `[aiohttp]`, `[pycurl]`, `[cloudscraper]`, `[autoscraper]`.
- `requires-python` is `>=3.10`. urllib3 2.8, requests 2.34, and aiohttp 3.14 all require 3.10+, and the httpx adapter already uses `str | None`.
- The changelog URL points at this file.

## 0.2.3

CONNECT header injection hardening and safer merging of proxy response headers. See the [GitHub release](https://github.com/proxymesh/python-proxy-headers/releases/tag/v0.2.3).

## Earlier

[GitHub Releases](https://github.com/proxymesh/python-proxy-headers/releases).
