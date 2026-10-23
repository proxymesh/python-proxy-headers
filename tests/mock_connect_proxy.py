#!/usr/bin/env python3
"""Minimal CONNECT proxy for local adapter tests. No credentials.

Replies to CONNECT with ``HTTP/1.1 200 Connection established``,
``X-ProxyMesh-IP``, and an echo of each ``X-ProxyMesh-*`` request header,
then pipes bytes. Plain HTTP absolute-URI requests are forwarded with
``X-ProxyMesh-IP`` added.

Usage:
    python3 tests/mock_connect_proxy.py [port]

``port`` defaults to 18080. Use ``0`` to bind an ephemeral port. The chosen
port is written to stdout as ``PORT <n>`` before the accept loop starts.
"""

from __future__ import annotations

import select
import socket
import sys
import threading

FAKE_IP = "203.0.113.7"

def pipe(a, b, label=""):
    socks = [a, b]
    n = [0, 0]
    try:
        while True:
            r, _, _ = select.select(socks, [], [], 60)
            if not r:
                return
            for s in r:
                data = s.recv(65536)
                if not data:
                    return
                n[0 if s is a else 1] += len(data)
                (b if s is a else a).sendall(data)
    except OSError:
        pass
    finally:
        sys.stderr.write(f"[proxy] tunnel {label} closed: client->up {n[0]}B, up->client {n[1]}B\n")
        a.close(); b.close()

def read_head(c):
    buf = b""
    while b"\r\n\r\n" not in buf:
        d = c.recv(4096)
        if not d:
            break
        buf += d
    head, _, rest = buf.partition(b"\r\n\r\n")
    return head, rest

def handle(c):
    try:
        head, rest = read_head(c)
        lines = head.decode("latin-1").split("\r\n")
        method, target, _ = lines[0].split(" ", 2)
        hdrs = [l.split(":", 1) for l in lines[1:] if ":" in l]
        echo = "".join(f"{k.strip()}-Echo: {v.strip()}\r\n" for k, v in hdrs if k.lower().startswith("x-proxymesh"))
        sys.stderr.write(f"[proxy] {method} {target} hdrs={[k for k,_ in hdrs]}\n")
        if method == "CONNECT":
            host, port = target.rsplit(":", 1)
            up = socket.create_connection((host, int(port)), timeout=20)
            c.sendall(("HTTP/1.1 200 Connection established\r\n"
                       f"X-ProxyMesh-IP: {FAKE_IP}\r\n{echo}\r\n").encode())
            if rest:
                up.sendall(rest)
            pipe(c, up, target)
        else:
            from urllib.parse import urlsplit
            u = urlsplit(target)
            up = socket.create_connection((u.hostname, u.port or 80), timeout=20)
            path = (u.path or "/") + (("?" + u.query) if u.query else "")
            out = [f"{method} {path} HTTP/1.1"] + [f"{k}:{v}" for k, v in hdrs if not k.lower().startswith("proxy-") and k.lower() != "connection"] + ["Connection: close"]
            up.sendall(("\r\n".join(out) + "\r\n\r\n").encode("latin-1") + rest)
            resp = b""
            while True:
                d = up.recv(65536)
                if not d: break
                resp += d
            h, _, body = resp.partition(b"\r\n\r\n")
            c.sendall(h + f"\r\nX-ProxyMesh-IP: {FAKE_IP}".encode() + b"\r\n\r\n" + body)
            c.close(); up.close()
    except Exception as e:
        sys.stderr.write(f"[proxy] error {e!r}\n")
        try: c.close()
        except OSError: pass

def serve(port: int = 18080) -> None:
    """Bind ``127.0.0.1:port`` and serve until the process is killed."""
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", port))
    bound = listener.getsockname()[1]
    listener.listen(128)
    sys.stdout.write(f"PORT {bound}\n")
    sys.stdout.flush()
    sys.stderr.write(f"[proxy] listening on 127.0.0.1:{bound}\n")
    while True:
        client, _addr = listener.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


def main(argv: list[str] | None = None) -> None:
    """Parse ``argv`` and run :func:`serve`."""
    args = list(sys.argv[1:] if argv is None else argv)
    port = int(args[0]) if args else 18080
    serve(port)


if __name__ == "__main__":
    main()
