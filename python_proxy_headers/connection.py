import http, sys
from http.client import _read_headers
from urllib3.connection import HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.poolmanager import ProxyManager

if sys.version_info < (3, 12, 0):
	#####################################
	### copied from python3.12 source ###
	#####################################
	import email.parser
	import email.message

	class HTTPMessage(email.message.Message):
		# XXX The only usage of this method is in
		# http.server.CGIHTTPRequestHandler.  Maybe move the code there so
		# that it doesn't need to be part of the public API.  The API has
		# never been defined so this could cause backwards compatibility
		# issues.

		def getallmatchingheaders(self, name):
			"""Find all header lines matching a given header name.

			Look through the list of headers and find all lines matching a given
			header name (and their continuation lines).  A list of the lines is
			returned, without interpretation.  If the header does not occur, an
			empty list is returned.  If the header occurs multiple times, all
			occurrences are returned.  Case is not important in the header name.

			"""
			name = name.lower() + ':'
			n = len(name)
			lst = []
			hit = 0
			for line in self.keys():
				if line[:n].lower() == name:
					hit = 1
				elif not line[:1].isspace():
					hit = 0
				if hit:
					lst.append(line)
			return lst

	def _parse_header_lines(header_lines, _class=HTTPMessage):
		"""
		Parses only RFC2822 headers from header lines.

		email Parser wants to see strings rather than bytes.
		But a TextIOWrapper around self.rfile would buffer too many bytes
		from the stream, bytes which we later need to read as bytes.
		So we read the correct bytes here, as bytes, for email Parser
		to parse.

		"""
		hstring = b''.join(header_lines).decode('iso-8859-1')
		return email.parser.Parser(_class=_class).parsestr(hstring)
else:
	from http.client import _parse_header_lines

class HTTPSProxyConnection(HTTPSConnection):
	if sys.version_info < (3, 12, 0):
		#####################################
		### copied from python3.12 source ###
		#####################################

		def _wrap_ipv6(self, ip):
			if b':' in ip and ip[0] != b'['[0]:
				return b"[" + ip + b"]"
			return ip
		
		def _tunnel(self):
			connect = b"CONNECT %s:%d %s\r\n" % (
				self._wrap_ipv6(self._tunnel_host.encode("idna")),
				self._tunnel_port,
				self._http_vsn_str.encode("ascii"))
			headers = [connect]
			for header, value in self._tunnel_headers.items():
				headers.append(f"{header}: {value}\r\n".encode("latin-1"))
			headers.append(b"\r\n")
			# Making a single send() call instead of one per line encourages
			# the host OS to use a more optimal packet size instead of
			# potentially emitting a series of small packets.
			self.send(b"".join(headers))
			del headers

			response = self.response_class(self.sock, method=self._method)
			try:
				(version, code, message) = response._read_status()

				self._raw_proxy_headers = _read_headers(response.fp)

				if self.debuglevel > 0:
					for header in self._raw_proxy_headers:
						print('header:', header.decode())

				if code != http.HTTPStatus.OK:
					self.close()
					raise OSError(f"Tunnel connection failed: {code} {message.strip()}")

			finally:
				response.close()

		def get_proxy_response_headers(self):
			"""
			Returns a dictionary with the headers of the response
			received from the proxy server to the CONNECT request
			sent to set the tunnel.

			If the CONNECT request was not sent, the method returns None.
			"""
			return (
				_parse_header_lines(self._raw_proxy_headers)
				if self._raw_proxy_headers is not None
				else None
			)

class HTTPSProxyConnectionPool(HTTPSConnectionPool):
	ConnectionCls = HTTPSProxyConnection

	def _prepare_proxy(self, conn):
		super()._prepare_proxy(conn)
		self._proxy_response_headers = conn.get_proxy_response_headers()
	
	def urlopen(self, *args, **kwargs):
		response = super().urlopen(*args, **kwargs)
		response.headers.update(self._proxy_response_headers)
		return response

class ProxyHeaderManager(ProxyManager):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.pool_classes_by_scheme = {"http": HTTPConnectionPool, "https": HTTPSProxyConnectionPool}

def proxy_from_url(url, **kwargs):
    return ProxyHeaderManager(proxy_url=url, **kwargs)