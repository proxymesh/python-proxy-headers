"""Detect whether the installed httpx can load the CONNECT adapter.

httpx 0.28.x (httpcore) is supported. httpx 1.0 is a rewrite without httpcore,
without ``HTTPTransport`` / ``AsyncHTTPTransport``, and without proxy support
(https://github.com/encode/httpx/issues/947).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

# Kept in sync with [project.optional-dependencies] httpx in pyproject.toml.
SUPPORTED_HTTPX_SPEC = "httpx>=0.28,<1"
HTTPX_PROXY_ISSUE = "https://github.com/encode/httpx/issues/947"

BACKEND_EXPORTS = (
	"ProxyTunnelHTTPConnection",
	"AsyncProxyTunnelHTTPConnection",
	"HTTPProxyHeaders",
	"AsyncHTTPProxyHeaders",
	"HTTPProxyTransport",
	"AsyncHTTPProxyTransport",
	"request",
	"get",
	"options",
	"head",
	"post",
	"put",
	"patch",
	"delete",
	"stream",
)

_MISSING = object()


class UnsupportedHttpxVersion(RuntimeError):
	"""Raised when httpx cannot send or read CONNECT proxy headers.

	httpx 1.x is installed, httpx is missing, or the httpcore backend failed
	to import. The message names the installed version and the supported range.
	"""


@dataclass(frozen=True)
class HttpxStatus:
	"""What ``classify_httpx`` decided about the environment.

	``kind`` is ``supported`` (httpx 0.x), ``unsupported`` (httpx 1 or newer),
	``missing`` (httpx is not installed), or ``broken`` (version looks like
	0.x but the httpcore backend did not import).
	"""

	kind: str
	version: Optional[str] = None
	detail: Optional[str] = None


def httpx_major(version: Optional[str]) -> Optional[int]:
	"""Return the numeric major of an httpx version string.

	``1.0.dev6`` is major 1 and ``0.28.1`` is major 0. Returns None when
	``version`` is empty or does not start with a number.
	"""
	if not version:
		return None
	token = version.strip().split(".", 1)[0]
	digits = []
	for char in token:
		if char.isdigit():
			digits.append(char)
		else:
			break
	if not digits:
		return None
	return int("".join(digits))


def _imported_version() -> Optional[str]:
	try:
		import httpx
	except ImportError:
		return None
	version = getattr(httpx, "__version__", None)
	if isinstance(version, str) and version:
		return version
	return None


def _metadata_version() -> Optional[str]:
	try:
		from importlib.metadata import PackageNotFoundError, version
	except ImportError:  # pragma: no cover - importlib.metadata is stdlib on 3.10+
		return None
	try:
		return version("httpx")
	except PackageNotFoundError:
		return None


def probe_installed_version() -> Optional[str]:
	"""Return the httpx version that ``import httpx`` will actually use.

	Distribution metadata can disagree with a module earlier on ``sys.path``
	(for example a shadowed 1.0 build while metadata still says 0.28). When
	the majors differ, the imported module wins.
	"""
	imported = _imported_version()
	meta = _metadata_version()
	if imported and meta and httpx_major(imported) != httpx_major(meta):
		return imported
	return imported or meta


def classify_httpx(version: Any = _MISSING, *, probe: bool = True) -> HttpxStatus:
	"""Classify an httpx version string, or the version installed in this process.

	Pass ``probe=False`` and no version to classify a missing install without
	touching the environment.
	"""
	if version is _MISSING:
		version = probe_installed_version() if probe else None
	if version is None:
		return HttpxStatus("missing", None)
	if not isinstance(version, str):
		version = str(version)
	major = httpx_major(version)
	if major == 0:
		return HttpxStatus("supported", version)
	return HttpxStatus("unsupported", version)


def install_message(status: HttpxStatus) -> str:
	"""Explain why the httpx helpers cannot run, including the 1.0 plan pointer."""
	spec = SUPPORTED_HTTPX_SPEC
	if status.kind == "missing":
		return (
			"httpx is not installed. python-proxy-headers supports the httpx "
			f"0.28 line only ({spec}). Install it with "
			"`pip install 'python-proxy-headers[httpx]'`."
		)
	if status.kind == "broken":
		detail = f" ({status.detail})" if status.detail else ""
		found = f"httpx {status.version}" if status.version else "httpx 0.x"
		return (
			f"{found} looks like a supported 0.x release, but the httpcore "
			f"CONNECT adapter failed to import{detail}. Reinstall with "
			"`pip install 'python-proxy-headers[httpx]'` "
			f"({spec})."
		)
	found = f"httpx {status.version}" if status.version else "httpx 1.x"
	return (
		f"{found} is installed, but python-proxy-headers only supports the "
		f"httpx 0.28 line ({spec}). httpx 1.0 is a rewrite that drops httpcore "
		"and does not support proxies "
		f"({HTTPX_PROXY_ISSUE}); AsyncHTTPTransport and HTTPTransport are gone, "
		"so the 0.x adapter is not loaded. Importing this module succeeds, and "
		"calling the helpers raises UnsupportedHttpxVersion. "
		"Install a compatible release with "
		"`pip install 'python-proxy-headers[httpx]'`. "
		"A 1.0 adapter is not included; see the httpx documentation for the "
		"support options (stay on 0.28, wait for a public CONNECT hook, or add "
		"a small backend once NetworkBackend can take an existing tunnel)."
	)


def load_backend() -> Dict[str, Any]:
	"""Import the httpcore implementation.

	Raises:
		ImportError: httpx 0.x symbols or httpcore are not importable.
	"""
	from httpx import AsyncHTTPTransport, HTTPTransport  # noqa: F401
	import httpcore  # noqa: F401
	from . import _httpx_httpcore as backend

	namespace: Dict[str, Any] = {}
	for name in BACKEND_EXPORTS:
		namespace[name] = getattr(backend, name)
	return namespace


def _make_raiser(message: str) -> Callable[..., Any]:
	def _raise(*_args: Any, **_kwargs: Any) -> Any:
		raise UnsupportedHttpxVersion(message)

	return _raise


def unavailable_namespace(message: str) -> Dict[str, Any]:
	"""Build stand-ins that raise ``UnsupportedHttpxVersion`` when used.

	The public names still import. Nothing here touches httpcore.
	"""
	namespace: Dict[str, Any] = {}
	for name in BACKEND_EXPORTS:
		if name[:1].isupper():
			raiser = _make_raiser(message)

			def _init(self: Any, *args: Any, _raiser: Callable[..., Any] = raiser, **kwargs: Any) -> None:
				_raiser(*args, **kwargs)

			cls = type(name, (), {"__init__": _init, "__doc__": message})
			cls.__module__ = "python_proxy_headers.httpx_proxy"
			namespace[name] = cls
		else:
			fn = _make_raiser(message)
			fn.__name__ = name
			fn.__doc__ = message
			fn.__module__ = "python_proxy_headers.httpx_proxy"
			namespace[name] = fn
	return namespace
