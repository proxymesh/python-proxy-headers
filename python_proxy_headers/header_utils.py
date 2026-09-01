"""Validation and safe merging for proxy CONNECT headers.

CONNECT requests are raw HTTP and must not interpolate CR, LF, or NUL.
CONNECT response headers are not origin HTTPS headers and must not overwrite
them; only X-ProxyMesh-* values are copied onto the origin response.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union

RawHeaders = Union[Mapping[Any, Any], Sequence[Tuple[Any, Any]], None]

# ProxyMesh response headers that callers read from response.headers.
SAFE_PROXY_HEADER_PREFIX = "x-proxymesh-"

# Never copy these from a CONNECT response onto the origin response.
BLOCKED_PROXY_RESPONSE_HEADERS = frozenset({
	"age",
	"authorization",
	"cache-control",
	"clear-site-data",
	"connection",
	"content-disposition",
	"content-encoding",
	"content-language",
	"content-length",
	"content-location",
	"content-range",
	"content-security-policy",
	"content-security-policy-report-only",
	"content-type",
	"cookie",
	"date",
	"etag",
	"expires",
	"host",
	"keep-alive",
	"last-modified",
	"link",
	"location",
	"pragma",
	"proxy-authenticate",
	"proxy-authorization",
	"refresh",
	"server",
	"set-cookie",
	"set-cookie2",
	"strict-transport-security",
	"te",
	"trailer",
	"transfer-encoding",
	"upgrade",
	"vary",
	"via",
	"warning",
	"www-authenticate",
	"x-content-type-options",
	"x-frame-options",
	"x-xss-protection",
})


def _as_str(value: Any) -> str:
	if isinstance(value, bytes):
		return value.decode("latin-1")
	return str(value)


def validate_header_name(name: Any) -> str:
	"""Return a header name, or raise ValueError if it is not a single token."""
	name_s = _as_str(name)
	if not name_s:
		raise ValueError("Header name must not be empty")
	for char in name_s:
		code = ord(char)
		if char in "()<>@,;:\\\"/[]?={} \t:" or code <= 32 or code == 127:
			raise ValueError(f"Invalid header name {name_s!r}")
	return name_s


def validate_header_value(value: Any) -> str:
	"""Return a header value, or raise ValueError if it contains CR, LF, or NUL."""
	value_s = _as_str(value)
	if any(char in value_s for char in "\r\n\x00"):
		raise ValueError(f"Invalid header value {value_s!r}")
	return value_s


def validate_headers(headers: Optional[Mapping[Any, Any]]) -> Dict[str, str]:
	"""Validate a mapping of CONNECT request headers.

	Raises:
		ValueError: If any name or value contains CR, LF, NUL, or other
			characters illegal in a single CONNECT header line.
	"""
	if not headers:
		return {}
	validated: Dict[str, str] = {}
	for name, value in headers.items():
		validated[validate_header_name(name)] = validate_header_value(value)
	return validated


def _header_items(headers: RawHeaders) -> List[Tuple[Any, Any]]:
	if not headers:
		return []
	if isinstance(headers, (list, tuple)):
		return list(headers)
	if hasattr(headers, "items"):
		return list(headers.items())
	return []


def origin_has_header(origin_headers: RawHeaders, name: str) -> bool:
	"""Return True if origin_headers already contains ``name`` (case-insensitive)."""
	lowered = _as_str(name).lower()
	for key, _value in _header_items(origin_headers):
		if _as_str(key).lower() == lowered:
			return True
	return False


def is_mergeable_proxy_header(name: Any) -> bool:
	"""Return True if a CONNECT response header may be copied onto origin headers."""
	lowered = _as_str(name).lower()
	if lowered in BLOCKED_PROXY_RESPONSE_HEADERS:
		return False
	if lowered.startswith("access-control-"):
		return False
	return lowered.startswith(SAFE_PROXY_HEADER_PREFIX)


def snapshot_headers(headers: RawHeaders) -> Dict[str, str]:
	"""Copy headers into a plain dict of strings."""
	snapshot: Dict[str, str] = {}
	for name, value in _header_items(headers):
		snapshot[_as_str(name)] = _as_str(value)
	return snapshot


def merge_proxy_response_headers(
	origin_headers: MutableMapping[Any, Any],
	proxy_headers: RawHeaders,
) -> None:
	"""Copy allowlisted CONNECT headers onto origin headers without overwriting."""
	for name, value in _header_items(proxy_headers):
		name_s = _as_str(name)
		if not is_mergeable_proxy_header(name_s):
			continue
		if origin_has_header(origin_headers, name_s):
			continue
		origin_headers[name_s] = _as_str(value)


def filter_connect_headers(
	origin_headers: RawHeaders,
	connect_headers: RawHeaders,
) -> List[Tuple[Any, Any]]:
	"""Return CONNECT header pairs that are safe to merge into origin headers."""
	extra: List[Tuple[Any, Any]] = []
	for name, value in _header_items(connect_headers):
		if is_mergeable_proxy_header(name) and not origin_has_header(origin_headers, name):
			extra.append((name, value))
	return extra
