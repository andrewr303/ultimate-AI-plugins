"""SSRF-guarded, bounded HTTP(S) fetching for --live commands (WP01, blueprint §4.4).

Policy summary: http/https only; no userinfo, backslashes, percent signs or `#@` tricks in the
authority; obfuscated IPv4 literals canonicalized; every DNS answer must be public (IPv4-mapped,
NAT64 and 6to4 addresses unwrapped; Teredo refused); the connection is pinned to a checked
address with certificate verification; redirects are followed manually (max 5) with full
re-validation; bodies are capped after decompression. `--allow-local HOST:PORT` permits loopback
and private addresses only for that exact origin, never for redirect hops elsewhere.

Resolver, transport, clock and sleep are injectable so tests never open sockets.
Transport contract: ``transport(TransportRequest) -> response`` where the response has
``status`` (int), ``headers`` (list of (name, value)), ``read(n) -> bytes`` and ``close()``.
"""
from __future__ import annotations

import codecs
import http.client
import ipaddress
import os
import re
import socket
import ssl
import time
import urllib.parse
import zlib
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple, Union

from .rulesdb import loads_json

IPAddress = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
USER_AGENT = "seo-geo-god/1.0 (offline-first SEO/GEO audit CLI; operator-initiated)"
DEFAULT_ACCEPT = "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.8,*/*;q=0.5"
DEFAULT_MAX_BYTES = 5_242_880
MAX_BYTES_LIMIT = 20_971_520
REDIRECT_BODY_CAP = 65_536
MAX_REDIRECTS = 5
CHUNK = 65_536
CRAWL_DEFAULT_PAGES = 50
CRAWL_MAX_PAGES = 500
PROXY_LIMITATION = "target resolved by proxy; DNS pinning not enforced"
ERROR_KINDS = ("url_refused", "dns", "timeout", "tls", "connection", "too_many_redirects", "too_large", "http",
               "decode")
REDIRECT_STATUSES = (301, 302, 303, 307, 308)

_METADATA_NAMES = frozenset({
    "metadata", "metadata.google.internal", "metadata.goog", "metadata.azure.com", "metadata.ec2.internal",
    "metadata.oraclecloud.com", "instance-data", "instance-data.ec2.internal"})
_LOCAL_NAMES = frozenset({"localhost", "ip6-localhost", "ip6-loopback"})
_LOCAL_SUFFIXES = (".localhost", ".local", ".internal")
_IPV4_LIKE = re.compile(r"^(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+)){0,3}$")
_LABEL = re.compile(r"^[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?$")
_SCHEME_AUTH = re.compile(r"^([A-Za-z][A-Za-z0-9+.-]*)://([^/?#]*)")
_SENSITIVE_KEY = re.compile(r"(?i)(token|key|sig|signature|auth|session|password|secret)")
_META_CHARSET = re.compile(rb"""<meta[^>]{0,512}?charset\s*=\s*["']?\s*([A-Za-z0-9_.:-]{1,40})""", re.I)


def _nets(*cidrs: str) -> Tuple[Any, ...]:
    return tuple(ipaddress.ip_network(c) for c in cidrs)


_V4_BLOCKED = _nets("0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12",
                    "192.0.0.0/24", "192.0.2.0/24", "192.88.99.0/24", "192.168.0.0/16", "198.18.0.0/15",
                    "198.51.100.0/24", "203.0.113.0/24", "224.0.0.0/4", "240.0.0.0/4", "255.255.255.255/32")
_V6_BLOCKED = _nets("::/128", "::1/128", "::/96", "64:ff9b:1::/48", "100::/64", "2001::/23", "2001:db8::/32",
                    "3fff::/20", "5f00::/16", "fc00::/7", "fe80::/10", "fec0::/10", "ff00::/8")
_NAT64 = ipaddress.ip_network("64:ff9b::/96")
_TEREDO = ipaddress.ip_network("2001::/32")
_LOCAL_OK = _nets("127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "100.64.0.0/10", "::1/128",
                  "fc00::/7")
_NEVER_LOCAL = frozenset(ipaddress.ip_address(x) for x in ("100.100.100.200", "fd00:ec2::254", "0.0.0.0", "::"))


class FetchRefused(Exception):
    """A URL, address or proxy was refused by policy (`kind` is url_refused or dns)."""

    def __init__(self, reason: str, kind: str = "url_refused") -> None:
        super().__init__(reason)
        self.reason = reason
        self.kind = kind


@dataclass
class FetchResult:
    """Outcome of one fetch. URLs are reported redacted (no userinfo, secret query values masked)."""
    requested_url: str
    url: str
    status: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    text: Optional[str] = None
    content_type: str = ""
    size: int = 0
    too_large: bool = False
    redirect_chain: List[Dict[str, Any]] = field(default_factory=list)
    pinned_ip: Optional[str] = None
    via_proxy: bool = False
    error: Optional[str] = None
    error_kind: Optional[str] = None
    elapsed_ms: int = 0
    raw_headers: List[Tuple[str, str]] = field(default_factory=list)
    encoding: Optional[str] = None
    redirect_target: Optional[str] = None  # recorded, not followed (redirect_policy said no)
    body: Optional[bytes] = field(default=None, repr=False)

    @property
    def ok(self) -> bool:
        """No error and a 2xx status."""
        return self.error is None and self.status is not None and 200 <= self.status < 300

    @property
    def refused(self) -> bool:
        """True when policy refused the URL or a redirect hop."""
        return self.error_kind == "url_refused"

    def json(self) -> Any:
        """Parse the body as JSON with the depth guard (ValueError on failure)."""
        return loads_json(self.text or "")

    def as_record(self) -> Dict[str, Any]:
        """Plain dict for sitescan.site_from_fetches and envelopes (no raw body)."""
        return {"url": self.url, "requested_url": self.requested_url, "status": self.status,
                "headers": dict(self.headers), "text": self.text, "content_type": self.content_type,
                "redirect_chain": [dict(x) for x in self.redirect_chain], "too_large": self.too_large,
                "error": self.error, "error_kind": self.error_kind, "redirect_target": self.redirect_target}


@dataclass
class TransportRequest:
    """What a transport must send. `target` is the request-target; `proxy` = (host, port, ip)."""
    method: str
    url: str
    scheme: str
    host: str
    port: int
    target: str
    headers: Dict[str, str]
    pinned_ip: Optional[str]
    timeout: float
    proxy: Optional[Tuple[str, int, str]] = None


# ----------------------------------------------------------------------------- URL and address policy

def redact_url(url: str) -> str:
    """Drop userinfo and fragment; replace values of secret-looking query keys with REDACTED."""
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return "<unparseable URL>"
    netloc = parts.netloc.rsplit("@", 1)[-1]
    pairs = []
    for pair in parts.query.split("&") if parts.query else []:
        name, sep, _value = pair.partition("=")
        pairs.append(name + "=REDACTED" if sep and _SENSITIVE_KEY.search(urllib.parse.unquote_plus(name)) else pair)
    return urllib.parse.urlunsplit((parts.scheme, netloc, parts.path, "&".join(pairs), ""))


def canonical_host(host: str) -> str:
    """Lower-case, IDNA-encode and strip one trailing dot; canonicalize obfuscated IPv4 literals.

    IPv6 literals (without brackets) return their compressed form. Raises FetchRefused.
    """
    if not isinstance(host, str) or not host:
        raise FetchRefused("empty host")
    if host.startswith("[") and host.endswith("]"):
        host = host[1:-1]
    if ":" in host:
        try:
            ip6 = ipaddress.IPv6Address(host)
        except ValueError:
            raise FetchRefused("malformed IPv6 literal") from None
        return ip6.compressed
    if host.endswith("."):
        host = host[:-1]
    try:
        ascii_host = host.encode("idna").decode("ascii").lower()
    except (UnicodeError, ValueError):
        raise FetchRefused("host is not a valid IDNA name") from None
    if ascii_host.endswith(".") or not ascii_host:
        raise FetchRefused("host has an empty label")
    if _IPV4_LIKE.match(ascii_host):
        try:
            return socket.inet_ntoa(socket.inet_aton(ascii_host))
        except OSError:
            raise FetchRefused("malformed IPv4 literal refused") from None
    labels = ascii_host.split(".")
    if len(ascii_host) > 253 or not all(_LABEL.match(lbl) for lbl in labels):
        raise FetchRefused("host name has an invalid label or is too long")
    if _IPV4_LIKE.match(labels[-1]):
        raise FetchRefused("numeric final label is not a valid IPv4 literal")
    return ascii_host


def _ip_literal(host: str) -> Optional[IPAddress]:
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


def _embedded_v4(ip: ipaddress.IPv6Address) -> Tuple[Optional[ipaddress.IPv4Address], bool]:
    """(embedded IPv4, refuse) for mapped, NAT64 and 6to4 forms; Teredo is always refused."""
    if ip.ipv4_mapped is not None:
        return ip.ipv4_mapped, False
    if ip in _NAT64:
        return ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF), False
    if ip in _TEREDO:
        return None, True
    if ip.sixtofour is not None:
        return ip.sixtofour, False
    return None, False


def is_public_ip(ip: Union[IPAddress, str]) -> bool:
    """True only for globally routable unicast addresses outside every blocked range (§4.4 step 2)."""
    if isinstance(ip, str):
        try:
            ip = ipaddress.ip_address(ip.split("%", 1)[0])
        except ValueError:
            return False
    if ip.version == 6:
        if getattr(ip, "scope_id", None):
            return False
        v4, refuse = _embedded_v4(ip)
        if refuse:
            return False
        if v4 is not None:
            return is_public_ip(v4)
        blocked = _V6_BLOCKED
    else:
        blocked = _V4_BLOCKED
    if any(ip in net for net in blocked):
        return False
    if ip.is_multicast or ip.is_loopback or ip.is_link_local or ip.is_unspecified or ip.is_reserved:
        return False
    return bool(ip.is_global)


def _unwrap(ip: IPAddress) -> IPAddress:
    if ip.version == 6 and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped
    return ip


def _local_ok(ip: IPAddress) -> bool:
    """Allowlistable: loopback, RFC 1918, RFC 6598, IPv6 ULA; never metadata or link-local."""
    ip = _unwrap(ip)
    return ip not in _NEVER_LOCAL and any(ip.version == n.version and ip in n for n in _LOCAL_OK)


def _proxy_ok(ip: IPAddress) -> bool:
    ip = _unwrap(ip)
    return not (ip in _NEVER_LOCAL or ip.is_link_local or ip.is_unspecified or ip.is_multicast or ip.is_reserved)


def _hostport(host: str, port: int) -> str:
    return ("[%s]" % host if ":" in host else host) + ":%d" % port


def parse_allow_local(values: Iterable[str]) -> FrozenSet[str]:
    """Normalize --allow-local HOST:PORT entries (exact match keys); raises ValueError."""
    out = set()
    for raw in values or ():
        m = re.match(r"^(\[[^\]]+\]|[^:\[\]]+):([0-9]{1,5})$", str(raw).strip())
        if not m or not 1 <= int(m.group(2)) <= 65535:
            raise ValueError("--allow-local expects HOST:PORT, got %r" % raw)
        try:
            host = canonical_host(m.group(1))
        except FetchRefused as exc:
            raise ValueError("--allow-local %r: %s" % (raw, exc.reason)) from None
        if host in _METADATA_NAMES or (_ip_literal(host) is not None and _ip_literal(host) in _NEVER_LOCAL):
            raise ValueError("--allow-local %r is never allowlistable" % raw)
        out.add(_hostport(host, int(m.group(2))))
    return frozenset(out)


def _default_port(scheme: str) -> int:
    return 443 if scheme == "https" else 80


def check_url(url: str, *, allow_local: FrozenSet[str] = frozenset()) -> urllib.parse.SplitResult:
    """Syntax and literal-address policy (§4.4 step 1); returns a canonical SplitResult.

    The result has a canonical netloc, a percent-encoded path/query and no fragment.
    Raises FetchRefused. DNS answers are checked later by `resolve_checked`.
    """
    if not isinstance(url, str) or not url:
        raise FetchRefused("empty URL")
    if any(ch.isspace() or ord(ch) < 0x20 or 0x7F <= ord(ch) < 0xA0 or ch in "\u200b\u200c\u200d\u2060\ufeff"
           or 0x202A <= ord(ch) <= 0x202E or 0x2066 <= ord(ch) <= 0x2069 for ch in url):
        raise FetchRefused("URL contains whitespace or control characters")
    if "\\" in url:
        raise FetchRefused("backslash in URL refused")
    low = url.lower()
    if "#@" in low or "%23@" in low:
        raise FetchRefused("fragment/userinfo confusion refused")
    m = _SCHEME_AUTH.match(url)
    if not m:
        raise FetchRefused("only absolute http(s) URLs are allowed")
    scheme, authority = m.group(1).lower(), m.group(2)
    if scheme not in ("http", "https"):
        raise FetchRefused("scheme %s is not allowed" % scheme)
    if "@" in authority:
        raise FetchRefused("userinfo in URL refused")
    if "%" in authority:
        raise FetchRefused("percent-encoding in host refused")
    am = re.match(r"^(\[[0-9A-Fa-f:.]+\]|[^:\[\]]*)(?::([0-9]*))?$", authority)
    if not am or not am.group(1):
        raise FetchRefused("malformed host or port")
    port_text = am.group(2)
    if port_text:
        if len(port_text) > 5 or not 1 <= int(port_text) <= 65535:
            raise FetchRefused("port out of range")
        port = int(port_text)
    else:
        port = _default_port(scheme)
    host = canonical_host(am.group(1))
    key = _hostport(host, port)
    local = key in allow_local
    if host in _METADATA_NAMES:
        raise FetchRefused("cloud metadata host refused")
    if (host in _LOCAL_NAMES or host.endswith(_LOCAL_SUFFIXES)) and not local:
        raise FetchRefused("local host name refused (use --allow-local %s for your own dev server)" % key)
    lit = _ip_literal(host)
    if lit is not None and not (is_public_ip(lit) or (local and _local_ok(lit))):
        raise FetchRefused("non-public address %s refused" % host)
    rest = url[m.end():].split("#", 1)[0]
    path, _, query = rest.partition("?")
    path = urllib.parse.quote(path or "/", safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(query, safe="/%:@!$&'()*+,;=-._~?")
    netloc = (_hostport(host, port) if port_text else ("[%s]" % host if ":" in host else host))
    return urllib.parse.SplitResult(scheme, netloc, path, query, "")


def resolve_checked(host: str, port: int, *, allow_local: FrozenSet[str] = frozenset(),
                    resolver: Optional[Callable[..., Any]] = None, prefer: str = "ipv4") -> List[str]:
    """Resolve and require every address to pass policy; first item is the pin. Fails closed."""
    host = canonical_host(host)
    local = _hostport(host, port) in allow_local
    if host in _METADATA_NAMES:
        raise FetchRefused("cloud metadata host refused")
    lit = _ip_literal(host)
    if lit is not None:
        addrs = [lit]
    else:
        if (host in _LOCAL_NAMES or host.endswith(_LOCAL_SUFFIXES)) and not local:
            raise FetchRefused("local host name refused")
        try:
            infos = (resolver or socket.getaddrinfo)(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        except (OSError, UnicodeError, ValueError) as exc:
            raise FetchRefused("DNS resolution failed for %s: %s" % (host, exc), kind="dns") from None
        addrs = []
        for info in infos or ():
            try:
                ip = ipaddress.ip_address(str(info[4][0]).split("%", 1)[0])
            except (ValueError, IndexError, TypeError):
                raise FetchRefused("resolver returned an unparseable address for %s" % host) from None
            if ip not in addrs:
                addrs.append(ip)
        if not addrs:
            raise FetchRefused("DNS returned no addresses for %s" % host, kind="dns")
    for ip in addrs:
        if not (is_public_ip(ip) or (local and _local_ok(ip))):
            raise FetchRefused("%s resolves to non-public address %s" % (host, ip))
    want = 4 if prefer == "ipv4" else 6
    ordered = [ip for ip in addrs if ip.version == want] + [ip for ip in addrs if ip.version != want]
    return [str(ip) for ip in ordered]


def check_proxy(proxy_url: str, *, resolver: Optional[Callable[..., Any]] = None) -> Tuple[str, int, str]:
    """Validate an HTTP proxy URL; returns (host, port, pinned_ip). Loopback/private proxies are fine;
    link-local, metadata, unspecified, multicast and reserved addresses are refused."""
    raw = proxy_url.strip() if isinstance(proxy_url, str) else ""
    if raw and "://" not in raw:
        raw = "http://" + raw
    m = _SCHEME_AUTH.match(raw)
    if not m or m.group(1).lower() != "http":
        raise FetchRefused("proxy must be an http:// URL")
    authority = m.group(2)
    if any(c in authority for c in "@%\\") or any(ch.isspace() for ch in raw):
        raise FetchRefused("proxy URL with userinfo, percent or backslash refused")
    am = re.match(r"^(\[[0-9A-Fa-f:.]+\]|[^:\[\]]+)(?::([0-9]{1,5}))?$", authority)
    if not am:
        raise FetchRefused("malformed proxy host or port")
    port = int(am.group(2) or 80)
    if not 1 <= port <= 65535:
        raise FetchRefused("proxy port out of range")
    host = canonical_host(am.group(1))
    if host in _METADATA_NAMES:
        raise FetchRefused("metadata proxy host refused")
    lit = _ip_literal(host)
    if lit is not None:
        addrs = [lit]
    else:
        try:
            infos = (resolver or socket.getaddrinfo)(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            addrs = [ipaddress.ip_address(str(i[4][0]).split("%", 1)[0]) for i in infos or ()]
        except (OSError, UnicodeError, ValueError, IndexError, TypeError) as exc:
            raise FetchRefused("proxy DNS resolution failed: %s" % exc, kind="dns") from None
    if not addrs or not all(_proxy_ok(ip) for ip in addrs):
        raise FetchRefused("proxy address refused (link-local, metadata, unspecified, multicast or reserved)")
    return host, port, str(addrs[0])


def _env_proxy(scheme: str) -> Optional[str]:
    names = ("HTTPS_PROXY", "https_proxy") if scheme == "https" else ("HTTP_PROXY", "http_proxy")
    for name in names + ("ALL_PROXY", "all_proxy"):
        if os.environ.get(name):
            return os.environ[name]
    return None


# ----------------------------------------------------------------------------- connections

class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float) -> None:
        super().__init__(host, port, timeout=timeout)
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host: str, port: int, pinned_ip: str, timeout: float, context: ssl.SSLContext) -> None:
        super().__init__(host, port, timeout=timeout, context=context)
        self._pinned_ip = pinned_ip
        self._ctx = context

    def connect(self) -> None:
        self.sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        server_hostname = self.host
        if getattr(self, "_tunnel_host", None):
            self._tunnel()
            server_hostname = self._tunnel_host
        self.sock = self._ctx.wrap_socket(self.sock, server_hostname=server_hostname)


class _Response:
    def __init__(self, resp: http.client.HTTPResponse, conn: http.client.HTTPConnection) -> None:
        self.status = resp.status
        self.headers = resp.getheaders()
        self._resp, self._conn = resp, conn

    def read(self, n: int) -> bytes:
        return self._resp.read(n)

    def close(self) -> None:
        self._resp.close()
        self._conn.close()


def http_transport(req: TransportRequest) -> _Response:
    """Real transport: pinned HTTP(S) connection (TLS verified), or via a validated proxy."""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    if req.proxy is not None:
        phost, pport, pip = req.proxy
        if req.scheme == "https":
            conn: http.client.HTTPConnection = _PinnedHTTPSConnection(phost, pport, pip, req.timeout, ctx)
            conn.set_tunnel(req.host, req.port)
        else:
            conn = _PinnedHTTPConnection(phost, pport, pip, req.timeout)
    elif req.scheme == "https":
        conn = _PinnedHTTPSConnection(req.host, req.port, req.pinned_ip or "", req.timeout, ctx)
    else:
        conn = _PinnedHTTPConnection(req.host, req.port, req.pinned_ip or "", req.timeout)
    try:
        conn.request(req.method, req.target, headers=req.headers)
        return _Response(conn.getresponse(), conn)
    except BaseException:
        conn.close()
        raise


# ----------------------------------------------------------------------------- bodies

class _Decoder:
    """Incremental gzip/deflate decoder whose output per call is bounded (bomb-safe)."""

    def __init__(self, encoding: str) -> None:
        self.kind = encoding
        self._d = zlib.decompressobj(16 + zlib.MAX_WBITS if encoding in ("gzip", "x-gzip") else zlib.MAX_WBITS)
        self._first = encoding == "deflate"
        self.eof = False

    def feed(self, data: bytes, limit: int) -> bytes:
        try:
            out = self._d.decompress(data, limit)
        except zlib.error:
            if not self._first:
                raise
            self._d = zlib.decompressobj(-zlib.MAX_WBITS)  # raw deflate without zlib header
            out = self._d.decompress(data, limit)
        self._first = False
        self.eof = self._d.eof
        return out

    def tail(self, limit: int) -> bytes:
        return self._d.unconsumed_tail and self.feed(self._d.unconsumed_tail, limit) or b""


def _read_capped(resp: Any, cap: int, content_encoding: str) -> Tuple[bytes, bool]:
    """Read and decode the body; stop once decoded (or raw) bytes exceed `cap`."""
    enc = content_encoding.strip().lower()
    if enc in ("", "identity"):
        decoder = None
    elif enc in ("gzip", "x-gzip", "deflate"):
        decoder = _Decoder(enc)
    else:
        raise ValueError("unsupported content-encoding %r" % enc)
    out = bytearray()
    raw_total = 0
    while len(out) <= cap:
        chunk = resp.read(min(CHUNK, cap + 1 - raw_total) if decoder is None else CHUNK)
        if not chunk:
            break
        raw_total += len(chunk)
        if decoder is None:
            out += chunk
        else:
            out += decoder.feed(chunk, cap + 1 - len(out))
            while len(out) <= cap and not decoder.eof:
                more = decoder.tail(cap + 1 - len(out))
                if not more:
                    break
                out += more
            if decoder.eof:
                break
        if raw_total > cap:
            break
    too_large = len(out) > cap or raw_total > cap
    return bytes(out[:cap]), too_large


def _drain(resp: Any, cap: int = REDIRECT_BODY_CAP) -> int:
    """Read at most `cap` bytes of a 3xx body and discard them."""
    seen = 0
    while seen < cap:
        chunk = resp.read(min(CHUNK, cap - seen))
        if not chunk:
            break
        seen += len(chunk)
    return seen


_BINARY_PREFIXES = ("image/", "audio/", "video/", "font/")
_BINARY_TYPES = ("application/pdf", "application/zip", "application/gzip", "application/x-gzip",
                 "application/octet-stream", "application/wasm")


def _charset_from(content_type: str) -> Optional[str]:
    m = re.search(r"charset\s*=\s*[\"']?([A-Za-z0-9_.:-]+)", content_type or "", re.I)
    return m.group(1).lower() if m else None


def _codec(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    try:
        info = codecs.lookup(name)
    except LookupError:
        return None
    return info.name if getattr(info, "_is_text_encoding", True) else None


def decode_bytes(data: bytes, content_type: str = "") -> Tuple[Optional[str], Optional[str]]:
    """(text, encoding): BOM > Content-Type charset > <meta charset> in first 4,096 bytes > UTF-8.

    Unknown or non-text codecs fall back to UTF-8 with replacement. Binary types return (None, None).
    """
    ctype = (content_type or "").split(";", 1)[0].strip().lower()
    if ctype.startswith(_BINARY_PREFIXES) or ctype in _BINARY_TYPES:
        return None, None
    for bom, name in ((codecs.BOM_UTF8, "utf-8"), (codecs.BOM_UTF32_LE, "utf-32-le"),
                      (codecs.BOM_UTF32_BE, "utf-32-be"), (codecs.BOM_UTF16_LE, "utf-16-le"),
                      (codecs.BOM_UTF16_BE, "utf-16-be")):
        if data.startswith(bom):
            return data[len(bom):].decode(name, errors="replace"), name
    enc = _codec(_charset_from(content_type))
    if enc is None and ctype in ("", "text/html", "application/xhtml+xml"):
        m = _META_CHARSET.search(data[:4096])
        enc = _codec(m.group(1).decode("ascii", "replace")) if m else None
    enc = enc or "utf-8"
    try:
        return data.decode(enc, errors="replace"), enc
    except (LookupError, ValueError):
        return data.decode("utf-8", errors="replace"), "utf-8"


# ----------------------------------------------------------------------------- fetch

def _origin(parts: urllib.parse.SplitResult) -> Tuple[str, str, int]:
    return parts.scheme, parts.hostname or "", parts.port or _default_port(parts.scheme)


def _error_kind(exc: BaseException) -> str:
    if isinstance(exc, (socket.timeout, TimeoutError)):
        return "timeout"
    if isinstance(exc, ssl.SSLError):
        return "tls"
    if isinstance(exc, (http.client.HTTPException, ValueError)):
        return "http"
    return "connection"


def _host_header(host: str, port: int, scheme: str) -> str:
    h = "[%s]" % host if ":" in host else host
    return h if port == _default_port(scheme) else "%s:%d" % (h, port)


def fetch(url: str, *, method: str = "GET", accept: str = DEFAULT_ACCEPT, max_bytes: int = DEFAULT_MAX_BYTES,
          timeout: float = 20.0, max_redirects: int = MAX_REDIRECTS, allow_local: FrozenSet[str] = frozenset(),
          via_proxy: bool = False, transport: Optional[Callable[[TransportRequest], Any]] = None,
          resolver: Optional[Callable[..., Any]] = None, clock: Optional[Callable[[], float]] = None,
          redirect_policy: Optional[Callable[[str, str], bool]] = None,
          proxy_url: Optional[str] = None) -> FetchResult:
    """Fetch one URL under the §4.4 policy. Never raises for policy or network problems:
    the result carries `error` and `error_kind` (url_refused, dns, timeout, tls, connection,
    too_many_redirects, too_large, http, decode). ValueError for invalid arguments.

    `redirect_policy(current_url, target_url)` returning False records the target in
    `redirect_target` without fetching it (crawls use this for cross-origin hops).
    """
    return _fetch(url, method=method, accept=accept, max_bytes=max_bytes, timeout=timeout,
                  max_redirects=max_redirects, allow_local=allow_local, via_proxy=via_proxy, transport=transport,
                  resolver=resolver, clock=clock, redirect_policy=redirect_policy, proxy_url=proxy_url)[0]


def _fetch(url: str, *, method: str, accept: str, max_bytes: int, timeout: float, max_redirects: int,
           allow_local: FrozenSet[str], via_proxy: bool, transport: Optional[Callable[[TransportRequest], Any]],
           resolver: Optional[Callable[..., Any]], clock: Optional[Callable[[], float]],
           redirect_policy: Optional[Callable[[str, str], bool]], proxy_url: Optional[str]) -> Tuple[FetchResult, str]:
    if method not in ("GET", "HEAD"):
        raise ValueError("method must be GET or HEAD")
    if not 1 <= max_bytes <= MAX_BYTES_LIMIT:
        raise ValueError("max_bytes must be between 1 and %d" % MAX_BYTES_LIMIT)
    if not 0 <= max_redirects <= MAX_REDIRECTS:
        raise ValueError("max_redirects must be between 0 and %d" % MAX_REDIRECTS)
    allow = parse_allow_local(allow_local)
    clock = clock or time.monotonic
    send = transport or http_transport
    t0 = clock()
    res = FetchResult(requested_url=redact_url(url), url=redact_url(url), via_proxy=False)
    current, start_key, hops = url, None, 0

    def fail(kind: str, message: str) -> Tuple[FetchResult, str]:
        res.error, res.error_kind = message, kind
        res.elapsed_ms = int((clock() - t0) * 1000)
        return res, current

    while True:
        res.url = redact_url(current)
        try:
            parts = check_url(current, allow_local=allow)
        except FetchRefused as exc:
            return fail(exc.kind, ("redirect target refused: " if hops else "") + exc.reason)
        scheme, host, port = _origin(parts)
        key = _hostport(host, port)
        start_key = start_key or key
        hop_allow = allow if (key == start_key and key in allow) else frozenset()
        if hops and key in allow and key != start_key:
            return fail("url_refused", "redirect target refused: --allow-local does not cover %s" % key)
        proxy = None
        pinned: Optional[str] = None
        if via_proxy and key not in hop_allow:
            source = proxy_url or _env_proxy(scheme)
            if not source:
                return fail("connection", "via_proxy requested but no HTTP(S)_PROXY is configured")
            try:
                proxy = check_proxy(source, resolver=resolver)
                resolve_checked(host, port, allow_local=frozenset(), resolver=resolver)
            except FetchRefused as exc:
                if exc.kind != "dns" or proxy is None:
                    return fail(exc.kind, exc.reason)
            res.via_proxy = True
        else:
            try:
                pinned = resolve_checked(host, port, allow_local=hop_allow, resolver=resolver)[0]
            except FetchRefused as exc:
                return fail(exc.kind, ("redirect target refused: " if hops else "") + exc.reason)
        res.pinned_ip = pinned
        target = urllib.parse.urlunsplit(parts) if (proxy and scheme == "http") else (
            parts.path + ("?" + parts.query if parts.query else ""))
        headers = {"Host": _host_header(host, port, scheme), "User-Agent": USER_AGENT, "Accept": accept,
                   "Accept-Encoding": "gzip, deflate", "Connection": "close"}
        req = TransportRequest(method, urllib.parse.urlunsplit(parts), scheme, host, port, target, headers,
                               pinned, timeout, proxy)
        try:
            resp = send(req)
        except (OSError, ssl.SSLError, http.client.HTTPException, ValueError) as exc:
            return fail(_error_kind(exc), "%s: %s" % (type(exc).__name__, exc))
        try:
            status = int(resp.status)
            raw_headers = [(str(k), str(v)) for k, v in resp.headers]
            hdrs: Dict[str, str] = {}
            for k, v in raw_headers:
                hdrs[k.lower()] = hdrs[k.lower()] + ", " + v if k.lower() in hdrs else v
            res.status, res.headers, res.raw_headers = status, hdrs, raw_headers
            res.content_type = hdrs.get("content-type", "")
            location = next((v.strip() for k, v in raw_headers if k.lower() == "location"), "")
            if status in REDIRECT_STATUSES and location:
                _drain(resp)
                res.redirect_chain.append({"url": redact_url(current), "status": status})
                nxt = urllib.parse.urljoin(urllib.parse.urlunsplit(parts), location).split("#", 1)[0]
                if hops >= max_redirects:
                    res.redirect_target = redact_url(nxt)
                    return fail("too_many_redirects", "more than %d redirects" % max_redirects)
                if redirect_policy is not None and not redirect_policy(current, nxt):
                    res.redirect_target = redact_url(nxt)
                    res.elapsed_ms = int((clock() - t0) * 1000)
                    return res, current
                hops += 1
                current = nxt
                continue
            if method == "HEAD":
                body, too_large = b"", False
            else:
                try:
                    body, too_large = _read_capped(resp, max_bytes, hdrs.get("content-encoding", ""))
                except (zlib.error, ValueError) as exc:
                    return fail("decode", "could not decode body: %s" % exc)
            res.body, res.size, res.too_large = body, len(body), too_large
            res.text, res.encoding = decode_bytes(body, res.content_type)
            if too_large:
                return fail("too_large", "body exceeds %d bytes after decompression; truncated" % max_bytes)
            res.elapsed_ms = int((clock() - t0) * 1000)
            return res, current
        except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
            return fail(_error_kind(exc), "%s: %s" % (type(exc).__name__, exc))
        finally:
            resp.close()


def refused_result(url: str, exc: FetchRefused) -> FetchResult:
    """FetchResult for a URL refused before any request."""
    return FetchResult(requested_url=redact_url(url), url=redact_url(url), error=exc.reason, error_kind=exc.kind)


# ----------------------------------------------------------------------------- robots gate and crawl

def robots_gate(start_url: str, *, parse: Callable[[str], Callable[[str], bool]], **fetch_kw: Any
                ) -> Tuple[Callable[[str], bool], Dict[str, Any]]:
    """Our crawler's robots.txt semantics (§4.4 step 11): 2xx → `parse(text)` predicate;
    4xx (not 429) → no restrictions; 5xx, 429 or unreachable → only the start URL.

    `parse(text)` must return a callable taking an absolute URL (cli wires robots.py, token
    `seo-geo-god`). Returns (predicate, info); info is JSON-ready plus `text`.
    """
    start = start_url.split("#", 1)[0]
    try:
        parts = check_url(start, allow_local=parse_allow_local(fetch_kw.get("allow_local", ())))
    except FetchRefused as exc:
        return (lambda _u: False), {"outcome": "refused", "error": exc.reason, "status": None, "text": None}
    robots_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    kw = dict(fetch_kw)
    kw.setdefault("accept", "text/plain,*/*;q=0.1")
    res = fetch(robots_url, **kw)
    info: Dict[str, Any] = {"robots_url": res.requested_url, "status": res.status, "error_kind": res.error_kind,
                            "text": res.text}
    if res.status is not None and 200 <= res.status < 300 and res.error_kind in (None, "too_large"):
        info["outcome"] = "parsed"
        return parse(res.text or ""), info
    if res.error is None and res.status is not None and 400 <= res.status < 500 and res.status != 429:
        info["outcome"] = "no-restrictions"
        return (lambda _u: True), info
    info["outcome"] = "unreachable"
    canonical_start = urllib.parse.urlunsplit(parts)
    return (lambda u: u.split("#", 1)[0] in (start, canonical_start)), info


_ASSET_EXT = re.compile(r"\.(?:css|js|mjs|map|png|jpe?g|gif|webp|avif|svg|ico|bmp|tiff?|pdf|zip|gz|tgz|rar|7z|"
                        r"mp4|webm|mov|mp3|wav|ogg|woff2?|ttf|otf|eot|json|xml|txt|csv|rss|atom|wasm)$", re.I)


def _same_site(a: str, b: str) -> bool:
    ha = (urllib.parse.urlsplit(a).hostname or "").lower()
    hb = (urllib.parse.urlsplit(b).hostname or "").lower()
    strip = (lambda h: h[4:] if h.startswith("www.") else h)
    return bool(ha) and strip(ha) == strip(hb)


def crawl(start_url: str, *, max_pages: int = CRAWL_DEFAULT_PAGES, delay: Optional[float] = None,
          allow_local: FrozenSet[str] = frozenset(), robots_allowed: Optional[Callable[[str], bool]] = None,
          extract_links: Callable[[str, str], List[str]], same_origin: bool = True, deadline_s: float = 600.0,
          max_total_bytes: int = 52_428_800, sleep: Optional[Callable[[float], None]] = None,
          clock: Optional[Callable[[], float]] = None, stats: Optional[Dict[str, Any]] = None,
          **fetch_kw: Any) -> List[FetchResult]:
    """Bounded breadth-first crawl from `start_url` (§4.4 limits).

    `delay` defaults to 1.0 s (0.2 s for an allowlisted local origin); `robots_allowed(url)`
    filters every URL including the start; links come from `extract_links(html, base_url)`
    on 2xx HTML pages only. With `same_origin`, cross-origin links and redirect hops are
    recorded, not fetched; the start URL may move once to the same host (http→https, www).
    `stats` (optional dict) receives skipped URLs and the stop reason.
    """
    if not 1 <= max_pages <= CRAWL_MAX_PAGES:
        raise ValueError("max_pages must be between 1 and %d" % CRAWL_MAX_PAGES)
    allow = parse_allow_local(allow_local)
    clock = clock or time.monotonic
    sleep = sleep or time.sleep
    info = stats if stats is not None else {}
    info.update({"skipped_robots": [], "skipped_cross_origin": [], "skipped_assets": 0, "stopped": None,
                 "total_bytes": 0})
    start = start_url.split("#", 1)[0]
    try:
        parts = check_url(start, allow_local=allow)
    except FetchRefused as exc:
        info["stopped"] = "start URL refused"
        return [refused_result(start, exc)]
    origin = _origin(parts)
    if delay is None:
        delay = 0.2 if _hostport(origin[1], origin[2]) in allow else 1.0
    if delay < 0:
        raise ValueError("delay must be >= 0")
    queue = deque([start])
    seen = {start}
    results: List[FetchResult] = []
    t0 = clock()

    def in_origin(u: str) -> bool:
        try:
            return _origin(urllib.parse.urlsplit(u)) == origin
        except ValueError:
            return False

    while queue and len(results) < max_pages:
        if clock() - t0 > deadline_s:
            info["stopped"] = "deadline"
            break
        if info["total_bytes"] >= max_total_bytes:
            info["stopped"] = "max_total_bytes"
            break
        url = queue.popleft()
        if robots_allowed is not None and not robots_allowed(url):
            info["skipped_robots"].append(redact_url(url))
            continue
        if results and delay:
            sleep(delay)
        first = not results
        if not same_origin:
            policy = None
        elif first:
            policy = (lambda cur, nxt: _same_site(cur, nxt))
        else:
            policy = (lambda cur, nxt: in_origin(nxt))
        res, final_raw = _fetch(url, allow_local=allow, clock=clock, redirect_policy=policy,
                                **_fetch_defaults(fetch_kw))
        results.append(res)
        info["total_bytes"] += res.size
        if res.redirect_target and res.error is None:
            info["skipped_cross_origin"].append(res.redirect_target)
        if first and same_origin and res.error is None:
            try:
                origin = _origin(check_url(final_raw, allow_local=allow))
            except FetchRefused:
                pass
        seen.add(final_raw.split("#", 1)[0])
        ctype = res.content_type.split(";", 1)[0].strip().lower()
        if not (res.ok and res.text and ctype in ("text/html", "application/xhtml+xml", "")):
            continue
        for link in extract_links(res.text, final_raw) or ():
            link = str(link).split("#", 1)[0]
            if not link.lower().startswith(("http://", "https://")) or link in seen:
                continue
            if same_origin and not in_origin(link):
                if len(info["skipped_cross_origin"]) < 200:
                    info["skipped_cross_origin"].append(redact_url(link))
                seen.add(link)
                continue
            if _ASSET_EXT.search(urllib.parse.urlsplit(link).path):
                info["skipped_assets"] += 1
                seen.add(link)
                continue
            if len(seen) < max_pages * 20:
                seen.add(link)
                queue.append(link)
    else:
        if queue and len(results) >= max_pages:
            info["stopped"] = "max_pages"
    info["skipped_cross_origin"] = sorted(set(info["skipped_cross_origin"]))
    return results


def _fetch_defaults(kw: Dict[str, Any]) -> Dict[str, Any]:
    out = {"method": "GET", "accept": DEFAULT_ACCEPT, "max_bytes": DEFAULT_MAX_BYTES, "timeout": 20.0,
           "max_redirects": MAX_REDIRECTS, "via_proxy": False, "transport": None, "resolver": None,
           "proxy_url": None}
    unknown = set(kw) - set(out)
    if unknown:
        raise TypeError("unexpected fetch option(s): %s" % ", ".join(sorted(unknown)))
    out.update(kw)
    return out
