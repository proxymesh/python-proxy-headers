"""Send and read CONNECT proxy headers with httpx 0.28.x.

httpx 1.0 removes httpcore and proxy support, so this module does not import
httpcore when httpx>=1 is installed. Importing still succeeds: it warns, and
the helpers raise :class:`UnsupportedHttpxVersion`.

The ``[httpx]`` extra is ``httpx>=0.28,<1``.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict

from .httpx_support import (
	HttpxStatus,
	UnsupportedHttpxVersion,
	classify_httpx,
	install_message,
	load_backend,
	unavailable_namespace,
	BACKEND_EXPORTS,
)

__all__ = [
	"AsyncHTTPProxyHeaders",
	"AsyncHTTPProxyTransport",
	"AsyncProxyTunnelHTTPConnection",
	"HTTPProxyHeaders",
	"HTTPProxyTransport",
	"HTTPX_STATUS",
	"HttpxStatus",
	"ProxyTunnelHTTPConnection",
	"UnsupportedHttpxVersion",
	"delete",
	"get",
	"head",
	"options",
	"patch",
	"post",
	"put",
	"request",
	"stream",
]


def _export(namespace: Dict[str, Any]) -> None:
	for name in BACKEND_EXPORTS:
		globals()[name] = namespace[name]


def _activate() -> HttpxStatus:
	"""Bind the real backend or the raising stand-ins. Never raises ImportError."""
	status = classify_httpx()
	if status.kind == "supported":
		try:
			namespace = load_backend()
		except ImportError as exc:
			status = HttpxStatus("broken", status.version, detail=str(exc))
			message = install_message(status)
			warnings.warn(message, UserWarning, stacklevel=3)
			namespace = unavailable_namespace(message)
		_export(namespace)
		return status

	message = install_message(status)
	if status.kind == "unsupported":
		warnings.warn(message, UserWarning, stacklevel=3)
	_export(unavailable_namespace(message))
	return status


HTTPX_STATUS = _activate()
