"""WP01 fetch tests: every §4.4 vector, address policy, allowlist, redirects, caps, decoding, proxy, crawl.

No test opens a socket: the network sentinel is active and resolver/transport/clock are fakes.
"""
from __future__ import annotations

import http.client
import ipaddress
import os
import socket
import ssl
import sys
import unittest
import zlib
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # works for discover and tests.test_fetch
import helpers  # noqa: E402
from seo_geo_lib import fetch  # noqa: E402
from seo_geo_lib.fetch import FetchRefused, check_url, is_public_ip  # noqa: E402


def setUpModule() -> None:
    helpers.block_network()


PUBLIC = "93.184.215.14"
HTML = {"Content-Type": "text/html; charset=utf-8"}

BLOCKED_VECTORS = [
    "http://127.0.0.1/", "http://2130706433/", "http://0x7f000001/", "http://017700000001/", "http://127.1/",
    "http://[::1]/", "http://[::ffff:127.0.0.1]/", "http://[64:ff9b::a9fe:a9fe]/", "http://[2002:a9fe:a9fe::]/",
    "http://169.254.169.254/", "http://100.64.0.1/", "http://224.0.0.1/", "http://0.0.0.0/",
    "http://metadata.google.internal/", "http://foo.localhost/", "https://user:pass@example.com/",
    "http://127.0.0.1:6666\\@1.1.1.1/", "https://127.0.0.1#@example.com/", "https://example.com%5c@1.1.1.1/",
    "file:///etc/passwd", "ftp://example.com/", "http://example.com:99999/",
]
EXTRA_BLOCKED = [
    "", " http://example.com/", "http://exa mple.com/", "http://example.com/\x00", "http://example.com/\u202e",
    "https://169.254.169.254\\@example.com/", "https://metadata.google.internal%2e/", "http://127.0.0.1%2e/",
    "http://localhost/", "http://LOCALHOST./", "http://printer.local/", "http://db.internal/", "http://metadata/",
    "http://instance-data/", "http://metadata.azure.com/", "http://metadata.goog/", "http://ip6-localhost/",
    "http://0177.0.0.1/", "http://0x7f.0x0.0x0.0x1/", "http://127.0.0.001/", "http://10.1/", "http://3232235777/",
    "http://[fe80::1]/", "http://[fd00:ec2::254]/", "http://[::]/", "http://[2001:db8::1]/", "http://[2001::1]/",
    "http://[64:ff9b:1::1]/", "http://192.0.2.10/", "http://198.18.0.1/", "http://203.0.113.5/", "http://240.0.0.1/",
    "http://255.255.255.255/", "http://08.1.1.1/", "http://1.2.3.4.5/", "http://example.123/", "http://a.0x10/",
    "http://[::127.0.0.1]/",
    "http://example.com:0/", "http://example.com:+80/", "http://example.com:80a/", "http:example.com/",
    "javascript:alert(1)", "data:text/html,hi", "//example.com/", "http:///path", "http://a..b/",
    "http://" + "a" * 64 + ".example/", "http://" + ".".join(["abcdefgh"] * 32) + "/", "http://１２７.０.０.１/",
    "http://127。0。0。1/",
]


class FetchTestBase(unittest.TestCase):
    expect_network = False

    def setUp(self) -> None:
        self._attempts = len(helpers.network_attempts())

    def tearDown(self) -> None:
        if not self.expect_network:
            self.assertEqual(helpers.network_attempts()[self._attempts:], [], "test touched the network sentinel")

    def resolver(self, extra=None):
        mapping = {"example.com": [PUBLIC], "www.example.com": [PUBLIC], "example.org": ["93.184.215.15"]}
        mapping.update(extra or {})
        return helpers.FakeResolver(mapping)

    def get(self, url, transport, resolver=None, **kw):
        return fetch.fetch(url, transport=transport, resolver=resolver or self.resolver(), clock=helpers.FakeClock(),
                           **kw)


class VectorTest(FetchTestBase):
    def test_blueprint_vectors_refused_by_check_url(self) -> None:
        for url in BLOCKED_VECTORS:
            with self.subTest(url=url), self.assertRaises(FetchRefused):
                check_url(url)

    def test_blueprint_vectors_refused_by_fetch_without_requests(self) -> None:
        transport, resolver = helpers.FakeTransport(default=(200, HTML, b"ok")), helpers.FakeResolver({})
        for url in BLOCKED_VECTORS:
            with self.subTest(url=url):
                res = fetch.fetch(url, transport=transport, resolver=resolver)
                self.assertEqual(res.error_kind, "url_refused")
                self.assertTrue(res.refused)
                self.assertIsNone(res.status)
        self.assertEqual(transport.calls, [])
        self.assertEqual(resolver.calls, [])

    def test_extra_vectors_refused(self) -> None:
        for url in EXTRA_BLOCKED:
            with self.subTest(url=url), self.assertRaises(FetchRefused):
                check_url(url)

    def test_refused_userinfo_never_echoed(self) -> None:
        res = fetch.fetch("https://user:pass@example.com/", transport=helpers.FakeTransport())
        self.assertNotIn("pass", res.requested_url + res.url + (res.error or ""))

    def test_allowed_literals_and_names(self) -> None:
        for url, host in (("http://8.8.8.8/", "8.8.8.8"), ("https://[2606:4700:4700::1111]/", "2606:4700:4700::1111"),
                          ("https://EXAMPLE.com./aé?q=ü", "example.com"), ("https://bücher.example/", None),
                          ("http://example.com:8080/", "example.com"), ("https://100.128.0.1/", "100.128.0.1")):
            with self.subTest(url=url):
                parts = check_url(url)
                if host:
                    self.assertEqual(parts.hostname, host)
        parts = check_url("https://EXAMPLE.com./aé?q=ü#frag")
        self.assertEqual((parts.netloc, parts.path, parts.query, parts.fragment),
                         ("example.com", "/a%C3%A9", "q=%C3%BC", ""))
        self.assertEqual(check_url("https://bücher.example/").hostname, "xn--bcher-kva.example")
        self.assertEqual(check_url("http://example.com:8080").netloc, "example.com:8080")
        self.assertEqual(check_url("http://example.com:8080").path, "/")

    def test_canonical_host(self) -> None:
        self.assertEqual(fetch.canonical_host("Example.COM."), "example.com")
        self.assertEqual(fetch.canonical_host("2130706433"), "127.0.0.1")
        self.assertEqual(fetch.canonical_host("0x7f.1"), "127.0.0.1")
        self.assertEqual(ipaddress.ip_address(fetch.canonical_host("[::FFFF:7f00:1]")),
                         ipaddress.ip_address("::ffff:127.0.0.1"))  # text form differs across Python versions
        self.assertEqual(fetch.canonical_host("１２７.０.０.１"), "127.0.0.1")
        for bad in ("", "a..b", "example.com..", "-bad.example", "x" * 64, "08.0.0.1", "[::g]"):
            with self.subTest(host=bad), self.assertRaises(FetchRefused):
                fetch.canonical_host(bad)

    def test_random_encodings_of_private_addresses(self) -> None:
        rnd = helpers.seeded_random()
        nets = [ipaddress.ip_network(n) for n in ("127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
                                                  "169.254.0.0/16", "100.64.0.0/10", "0.0.0.0/8", "224.0.0.0/4")]
        for _ in range(200):
            net = rnd.choice(nets)
            ip = ipaddress.IPv4Address(int(net.network_address) + rnd.randrange(net.num_addresses))
            n, octets = int(ip), [int(x) for x in str(ip).split(".")]
            form = rnd.randrange(8)
            host = [str(n), hex(n), "0%o" % n, ".".join("0%o" % o for o in octets),
                    ".".join(hex(o) for o in octets), "%d.%d" % (octets[0], n & 0xFFFFFF),
                    "%d.%d.%d" % (octets[0], octets[1], n & 0xFFFF), "[::ffff:%s]" % ip][form]
            if rnd.random() < 0.3:
                host = host.upper()
            url = "%s://%s%s/" % (rnd.choice(["http", "https", "HTTP"]), host, rnd.choice(["", ":80", ":8443", "."]))
            with self.subTest(url=url), self.assertRaises(FetchRefused):
                check_url(url)


class AddressPolicyTest(FetchTestBase):
    def test_public_table(self) -> None:
        for ip in ("8.8.8.8", "1.1.1.1", "100.128.0.1", "93.184.215.14", "::ffff:8.8.8.8", "2606:4700:4700::1111",
                   "2002:808:808::1", "64:ff9b::808:808"):
            with self.subTest(ip=ip):
                self.assertTrue(is_public_ip(ipaddress.ip_address(ip)))
        for ip in ("10.0.0.1", "172.16.0.1", "172.31.255.255", "192.168.1.1", "100.64.0.1", "100.100.100.200",
                   "127.0.0.1", "169.254.169.254", "192.0.0.8", "192.0.2.1", "192.88.99.1", "198.18.0.1",
                   "198.51.100.1", "203.0.113.1", "224.0.0.1", "240.0.0.1", "255.255.255.255", "0.0.0.0",
                   "::", "::1", "fd00::1", "fd00:ec2::254", "fe80::1", "fec0::1", "ff02::1", "100::1", "2001:db8::1",
                   "2001::1", "2001:10::1", "3fff::1", "5f00::1", "64:ff9b:1::1", "64:ff9b::a00:1", "::ffff:10.0.0.1",
                   "2002:a9fe:a9fe::", "2002:7f00:1::", "::7f00:1", "4000::1"):
            with self.subTest(ip=ip):
                self.assertFalse(is_public_ip(ipaddress.ip_address(ip)))
        self.assertFalse(is_public_ip("fe80::1%eth0"))
        self.assertFalse(is_public_ip("not-an-ip"))
        self.assertTrue(is_public_ip("8.8.4.4"))

    def test_resolution_requires_every_answer_public(self) -> None:
        mixed = helpers.FakeResolver({"mixed.example.com": [PUBLIC, "10.0.0.5"]})
        with self.assertRaises(FetchRefused) as ctx:
            fetch.resolve_checked("mixed.example.com", 443, resolver=mixed)
        self.assertEqual(ctx.exception.kind, "url_refused")
        v6private = helpers.FakeResolver({"v6.example.com": [PUBLIC, "fd12::1"]})
        with self.assertRaises(FetchRefused):
            fetch.resolve_checked("v6.example.com", 443, resolver=v6private)
        transport = helpers.FakeTransport(default=(200, HTML, b"x"))
        res = self.get("https://mixed.example.com/", transport, resolver=mixed)
        self.assertEqual(res.error_kind, "url_refused")
        self.assertEqual(transport.calls, [])

    def test_resolution_failures_fail_closed(self) -> None:
        with self.assertRaises(FetchRefused) as ctx:
            fetch.resolve_checked("missing.example.com", 443, resolver=helpers.FakeResolver({}))
        self.assertEqual(ctx.exception.kind, "dns")
        empty = helpers.FakeResolver({"empty.example.com": []})
        with self.assertRaises(FetchRefused) as ctx:
            fetch.resolve_checked("empty.example.com", 443, resolver=empty)
        self.assertEqual(ctx.exception.kind, "dns")
        transport = helpers.FakeTransport()
        res = self.get("https://missing.example.com/", transport, resolver=helpers.FakeResolver({}))
        self.assertEqual(res.error_kind, "dns")
        self.assertEqual(transport.calls, [])

    def test_pin_prefers_ipv4_and_supports_ipv6_only(self) -> None:
        both = helpers.FakeResolver({"dual.example.com": ["2606:4700:4700::1111", PUBLIC]})
        self.assertEqual(fetch.resolve_checked("dual.example.com", 443, resolver=both),
                         [PUBLIC, "2606:4700:4700::1111"])
        self.assertEqual(fetch.resolve_checked("dual.example.com", 443, resolver=both, prefer="ipv6")[0],
                         "2606:4700:4700::1111")
        v6 = helpers.FakeResolver({"v6only.example.com": ["2606:4700:4700::1111"]})
        transport = helpers.FakeTransport({"https://v6only.example.com/": (200, HTML, b"ok")})
        res = self.get("https://v6only.example.com/", transport, resolver=v6)
        self.assertEqual((res.status, res.pinned_ip), (200, "2606:4700:4700::1111"))

    def test_literal_skips_resolver(self) -> None:
        resolver = helpers.FakeResolver({})
        transport = helpers.FakeTransport({"http://8.8.8.8/": (200, HTML, b"ok")})
        res = self.get("http://8.8.8.8/", transport, resolver=resolver)
        self.assertEqual((res.status, res.pinned_ip, resolver.calls), (200, "8.8.8.8", []))

    def test_successful_fetch_request_shape(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/a?x=1": (200, HTML, b"<p>hello</p>")})
        res = self.get("https://example.com/a?x=1#frag", transport)
        self.assertTrue(res.ok)
        self.assertEqual((res.text, res.encoding, res.size, res.pinned_ip), ("<p>hello</p>", "utf-8", 12, PUBLIC))
        req = transport.calls[0]
        self.assertEqual((req.method, req.host, req.port, req.target, req.pinned_ip, req.proxy),
                         ("GET", "example.com", 443, "/a?x=1", PUBLIC, None))
        self.assertEqual(req.headers["User-Agent"], fetch.USER_AGENT)
        self.assertEqual(req.headers["Accept"], fetch.DEFAULT_ACCEPT)
        self.assertEqual(req.headers["Accept-Encoding"], "gzip, deflate")
        self.assertEqual(req.headers["Host"], "example.com")
        self.assertNotIn("Accept-Language", req.headers)
        self.assertNotIn("Cookie", req.headers)
        self.assertEqual(req.timeout, 20.0)
        self.assertEqual(res.as_record()["status"], 200)
        port = helpers.FakeTransport({"http://example.com:8080/": (204, {}, b"")})
        self.assertEqual(self.get("http://example.com:8080/", port).status, 204)
        self.assertEqual(port.calls[0].headers["Host"], "example.com:8080")

    def test_head_and_argument_validation(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (200, HTML, b"body")})
        res = self.get("https://example.com/", transport, method="HEAD")
        self.assertEqual((res.status, res.size, transport.responses[0].bytes_read), (200, 0, 0))
        for kw in ({"method": "POST"}, {"max_bytes": 20_971_521}, {"max_bytes": 0}, {"max_redirects": 6}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                self.get("https://example.com/", transport, **kw)

    def test_error_kinds(self) -> None:
        for exc, kind in ((socket.timeout("timed out"), "timeout"), (TimeoutError("t"), "timeout"),
                          (ssl.SSLCertVerificationError("bad cert"), "tls"), (ConnectionResetError("reset"), "connection"),
                          (http.client.BadStatusLine("junk"), "http"), (OSError("unreachable"), "connection")):
            with self.subTest(kind=kind):
                res = self.get("https://example.com/", helpers.FakeTransport({"https://example.com/": (200, {}, exc)}))
                self.assertEqual(res.error_kind, kind)
        self.assertTrue(set(fetch.ERROR_KINDS) >= {"url_refused", "dns", "timeout", "tls", "connection",
                                                   "too_many_redirects", "too_large", "http", "decode"})


class SentinelTest(FetchTestBase):
    expect_network = True

    def test_default_resolver_and_transport_hit_sentinel(self) -> None:
        with self.assertRaises(helpers.NetworkBlocked):
            fetch.fetch("https://example.com/", transport=helpers.FakeTransport())
        req = fetch.TransportRequest("GET", "https://example.com/", "https", "example.com", 443, "/", {},
                                     PUBLIC, 1.0)
        with self.assertRaises(helpers.NetworkBlocked):
            fetch.http_transport(req)
        attempts = helpers.network_attempts()[self._attempts:]
        self.assertTrue(attempts[0].startswith("socket.getaddrinfo"))
        self.assertIn(PUBLIC, attempts[1])  # pinned connection: create_connection((pinned_ip, port))
        self.assertEqual(len(attempts), 2)
        helpers.reset_network_attempts(self._attempts)  # drop only these deliberate attempts


class AllowLocalTest(FetchTestBase):
    def test_parse_allow_local(self) -> None:
        self.assertEqual(fetch.parse_allow_local(["LOCALHOST:3000", "127.0.0.1:4321", "[::1]:8080"]),
                         frozenset({"localhost:3000", "127.0.0.1:4321", "[::1]:8080"}))
        for bad in ("localhost", "localhost:0", "localhost:70000", ":3000", "metadata.google.internal:80",
                    "100.100.100.200:80", "0.0.0.0:3000", "[::]:3000", "local host:80", "http://localhost:3000"):
            with self.subTest(entry=bad), self.assertRaises(ValueError):
                fetch.parse_allow_local([bad])

    def test_exact_host_port_semantics(self) -> None:
        allow = fetch.parse_allow_local(["localhost:3000", "127.0.0.1:4321", "10.0.0.8:8080"])
        for url in ("http://localhost:3000/", "https://localhost:3000/x", "http://127.0.0.1:4321/",
                    "http://10.0.0.8:8080/"):
            with self.subTest(url=url):
                check_url(url, allow_local=allow)
        for url in ("http://localhost:3001/", "http://localhost/", "http://127.0.0.1:3000/", "http://127.0.0.2:4321/",
                    "http://[::1]:3000/", "http://10.0.0.8/", "http://dev.localhost:3000/"):
            with self.subTest(url=url), self.assertRaises(FetchRefused):
                check_url(url, allow_local=allow)

    def test_never_allowlistable_addresses(self) -> None:
        allow = frozenset({"169.254.169.254:80", "[fe80::1]:3000", "224.0.0.1:80", "192.0.2.1:80"})
        for url in ("http://169.254.169.254/", "http://[fe80::1]:3000/", "http://224.0.0.1/", "http://192.0.2.1/"):
            with self.subTest(url=url), self.assertRaises(FetchRefused):
                check_url(url, allow_local=allow)
        allow = fetch.parse_allow_local(["localhost:3000"])
        bad_dns = helpers.FakeResolver({"localhost": ["169.254.10.10"]})
        with self.assertRaises(FetchRefused):
            fetch.resolve_checked("localhost", 3000, allow_local=allow, resolver=bad_dns)
        alibaba = helpers.FakeResolver({"localhost": ["100.100.100.200"]})
        with self.assertRaises(FetchRefused):
            fetch.resolve_checked("localhost", 3000, allow_local=allow, resolver=alibaba)

    def test_local_fetch_pins_loopback(self) -> None:
        resolver = helpers.FakeResolver({"localhost": ["127.0.0.1", "::1"]})
        transport = helpers.FakeTransport({"http://localhost:3000/": (200, HTML, b"<h1>dev</h1>")})
        res = fetch.fetch("http://localhost:3000/", allow_local=["localhost:3000"], transport=transport,
                          resolver=resolver)
        self.assertEqual((res.status, res.pinned_ip), (200, "127.0.0.1"))
        refused = fetch.fetch("http://localhost:3000/", transport=transport, resolver=resolver)
        self.assertEqual(refused.error_kind, "url_refused")
        self.assertIn("--allow-local localhost:3000", refused.error)

    def test_allowlist_not_applied_to_other_port_redirect(self) -> None:
        resolver = helpers.FakeResolver({"localhost": ["127.0.0.1"]})
        for allow in (["localhost:3000"], ["localhost:3000", "localhost:3001"]):
            with self.subTest(allow=allow):
                transport = helpers.FakeTransport({
                    "http://localhost:3000/": (302, {"Location": "http://localhost:3001/admin"}, b""),
                    "http://localhost:3001/admin": (200, HTML, b"secret")})
                res = fetch.fetch("http://localhost:3000/", allow_local=allow, transport=transport, resolver=resolver)
                self.assertEqual(res.error_kind, "url_refused")
                self.assertEqual(transport.urls, ["http://localhost:3000/"])

    def test_same_origin_local_redirect_followed(self) -> None:
        resolver = helpers.FakeResolver({"localhost": ["127.0.0.1"]})
        transport = helpers.FakeTransport({"http://localhost:3000/": (308, {"Location": "/en/"}, b""),
                                           "http://localhost:3000/en/": (200, HTML, b"ok")})
        res = fetch.fetch("http://localhost:3000/", allow_local=["localhost:3000"], transport=transport,
                          resolver=resolver)
        self.assertEqual((res.status, res.url), (200, "http://localhost:3000/en/"))
        self.assertEqual(res.redirect_chain, [{"url": "http://localhost:3000/", "status": 308}])

    def test_public_redirect_into_allowlisted_origin_refused(self) -> None:
        resolver = self.resolver({"localhost": ["127.0.0.1"]})
        transport = helpers.FakeTransport({"https://example.com/": (302, {"Location": "http://localhost:3000/"}, b"")})
        res = self.get("https://example.com/", transport, resolver=resolver, allow_local=["localhost:3000"])
        self.assertEqual(res.error_kind, "url_refused")
        self.assertEqual(len(transport.calls), 1)


class RedirectTest(FetchTestBase):
    def test_redirect_to_loopback_refused_after_one_fetch(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (301, {"Location": "http://127.0.0.1/"}, b""),
                                           "http://127.0.0.1/": (200, HTML, b"internal")})
        res = self.get("https://example.com/", transport)
        self.assertEqual(res.error_kind, "url_refused")
        self.assertIn("redirect target refused", res.error)
        self.assertEqual(transport.urls, ["https://example.com/"])
        self.assertEqual(res.redirect_chain, [{"url": "https://example.com/", "status": 301}])
        self.assertEqual(res.status, 301)

    def test_redirect_revalidates_dns_and_scheme(self) -> None:
        resolver = self.resolver({"internal.example.com": ["10.1.2.3"]})
        for location in ("https://internal.example.com/", "file:///etc/passwd", "ftp://example.com/",
                         "http://[::ffff:169.254.169.254]/", "https://user:pw@example.org/", "http://2130706433/"):
            with self.subTest(location=location):
                transport = helpers.FakeTransport({"https://example.com/": (302, {"Location": location}, b"")})
                res = self.get("https://example.com/", transport, resolver=resolver)
                self.assertEqual(res.error_kind, "url_refused")
                self.assertEqual(len(transport.calls), 1)

    def test_relative_location_and_chain(self) -> None:
        transport = helpers.FakeTransport({
            "https://example.com/a": (301, {"Location": "b?session=s3cret"}, b""),
            "https://example.com/b?session=s3cret": (307, {"Location": "https://www.example.com/c#top"}, b""),
            "https://www.example.com/c": (200, HTML, b"final")})
        res = self.get("https://example.com/a", transport)
        self.assertEqual((res.status, res.text, res.url), (200, "final", "https://www.example.com/c"))
        self.assertEqual(res.redirect_chain, [{"url": "https://example.com/a", "status": 301},
                                              {"url": "https://example.com/b?session=REDACTED", "status": 307}])

    def test_five_hop_cap(self) -> None:
        def chain(n):
            routes = {"https://example.com/r%d" % i: (302, {"Location": "/r%d" % (i + 1)}, b"") for i in range(n)}
            routes["https://example.com/r%d" % n] = (200, HTML, b"end")
            return helpers.FakeTransport(routes)
        ok = chain(5)
        res = self.get("https://example.com/r0", ok)
        self.assertEqual((res.status, len(ok.calls), len(res.redirect_chain)), (200, 6, 5))
        too_many = chain(6)
        res = self.get("https://example.com/r0", too_many)
        self.assertEqual((res.error_kind, len(too_many.calls)), ("too_many_redirects", 6))
        self.assertEqual(res.redirect_target, "https://example.com/r6")
        zero = chain(1)
        self.assertEqual(self.get("https://example.com/r0", zero, max_redirects=0).error_kind, "too_many_redirects")

    def test_redirect_body_capped_at_64k(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (302, {"Location": "/next"}, b"x" * 10_000_000),
                                           "https://example.com/next": (200, HTML, b"ok")})
        res = self.get("https://example.com/", transport)
        self.assertEqual(res.status, 200)
        self.assertLessEqual(transport.responses[0].bytes_read, fetch.REDIRECT_BODY_CAP)
        self.assertEqual(transport.responses[0].bytes_read, 65_536)
        self.assertTrue(transport.responses[0].closed)

    def test_redirect_policy_records_without_following(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (301, {"Location": "https://example.org/"}, b"")})
        res = self.get("https://example.com/", transport, redirect_policy=lambda cur, nxt: False)
        self.assertIsNone(res.error)
        self.assertEqual((res.status, res.redirect_target, len(transport.calls)), (301, "https://example.org/", 1))

    def test_redirect_without_location_is_final(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (302, {}, b"moved")})
        res = self.get("https://example.com/", transport)
        self.assertEqual((res.status, res.text, res.redirect_chain), (302, "moved", []))


class BodyLimitTest(FetchTestBase):
    @staticmethod
    def bomb(total: int, wbits: int) -> bytes:
        comp = zlib.compressobj(9, zlib.DEFLATED, wbits)
        block = b"\0" * 1_048_576
        return b"".join(comp.compress(block) for _ in range(total // len(block))) + comp.flush()

    def test_gzip_bomb_aborted_at_cap(self) -> None:
        body = self.bomb(128 * 1_048_576, 16 + zlib.MAX_WBITS)  # 128 MiB of zeros, about 130 KB compressed
        self.assertLess(len(body), 200_000)
        transport = helpers.FakeTransport({"https://example.com/": (200, dict(HTML, **{"Content-Encoding": "gzip"}),
                                                                   body)})
        res = self.get("https://example.com/", transport, max_bytes=1_048_576)
        self.assertEqual((res.error_kind, res.too_large, res.size), ("too_large", True, 1_048_576))
        self.assertLessEqual(transport.responses[0].bytes_read, 2 * fetch.CHUNK)
        self.assertLess(transport.responses[0].bytes_read, len(body))
        self.assertLessEqual(len(res.body), 1_048_576)

    def test_deflate_variants_and_cap_boundary(self) -> None:
        payload = b"<p>" + b"a" * 5000 + b"</p>"
        for encoding, data in (("deflate", zlib.compress(payload)), ("deflate", self.raw_deflate(payload)),
                               ("gzip", helpers.gzip_bytes(payload)), ("identity", payload), ("", payload)):
            with self.subTest(encoding=encoding):
                transport = helpers.FakeTransport({"https://example.com/": (200, {"Content-Encoding": encoding,
                                                                                   "Content-Type": "text/html"}, data)})
                res = self.get("https://example.com/", transport)
                self.assertEqual((res.error, res.text), (None, payload.decode()))
        exact = helpers.FakeTransport({"https://example.com/": (200, HTML, payload)})
        self.assertFalse(self.get("https://example.com/", exact, max_bytes=len(payload)).too_large)
        over = helpers.FakeTransport({"https://example.com/": (200, HTML, payload)})
        res = self.get("https://example.com/", over, max_bytes=len(payload) - 1)
        self.assertEqual((res.too_large, res.size, res.error_kind), (True, len(payload) - 1, "too_large"))
        self.assertLessEqual(over.responses[0].bytes_read, len(payload))

    @staticmethod
    def raw_deflate(data: bytes) -> bytes:
        comp = zlib.compressobj(6, zlib.DEFLATED, -zlib.MAX_WBITS)
        return comp.compress(data) + comp.flush()

    def test_decode_errors(self) -> None:
        for encoding, body in (("br", b"\x1b\x00"), ("gzip", b"not gzip at all"), ("gzip, gzip", b"x")):
            with self.subTest(encoding=encoding):
                transport = helpers.FakeTransport({"https://example.com/": (200, {"Content-Encoding": encoding}, body)})
                self.assertEqual(self.get("https://example.com/", transport).error_kind, "decode")


class DecodingTest(FetchTestBase):
    def test_charset_order(self) -> None:
        meta_utf8 = b'<meta charset="utf-8">'
        cases = [
            (b"\xef\xbb\xbfcaf\xc3\xa9", "text/html; charset=iso-8859-1", "café", "utf-8"),           # BOM wins
            (b"\xff\xfec\x00a\x00f\x00\xe9\x00", "text/html; charset=utf-8", "café", "utf-16-le"),
            (meta_utf8 + b"caf\xe9", "text/html; charset=ISO-8859-1", meta_utf8.decode() + "café", "iso8859-1"),
            (b'<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">\x93hi\x94', "text/html",
             None, "cp1252"),
            (b"\x93x\x94", "text/plain", "\ufffdx\ufffd", "utf-8"),
            (b"caf\xc3\xa9", "", "café", "utf-8"),
            (b"x" * 5000 + b'<meta charset="iso-8859-1">\xe9', "text/html", None, "utf-8"),        # beyond 4,096 bytes
            (b"caf\xc3\xa9", "text/html; charset=x-unknown", "café", "utf-8"),
            (b"caf\xc3\xa9", "text/html; charset=base64", "café", "utf-8"),
            (b"caf\xc3\xa9", "text/html; charset=rot13", "café", "utf-8"),
        ]
        for data, ctype, text, enc in cases:
            with self.subTest(ctype=ctype, data=data[:20]):
                got_text, got_enc = fetch.decode_bytes(data, ctype)
                self.assertEqual(got_enc, enc)
                if text is not None:
                    self.assertEqual(got_text, text)
        self.assertEqual(fetch.decode_bytes(b"\x89PNG", "image/png"), (None, None))
        self.assertEqual(fetch.decode_bytes(b"\x1f\x8b", "application/gzip"), (None, None))

    def test_fetch_reports_encoding_and_json(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/data.json": (200, {"Content-Type": "application/json"},
                                                                            b'{"ok": true}')})
        res = self.get("https://example.com/data.json", transport)
        self.assertEqual((res.encoding, res.json()), ("utf-8", {"ok": True}))
        deep = helpers.FakeTransport({"https://example.com/d": (200, {"Content-Type": "application/json"},
                                                               b"[" * 300 + b"]" * 300)})
        with self.assertRaises(ValueError):
            self.get("https://example.com/d", deep).json()


class RedactionTest(FetchTestBase):
    def test_redact_url(self) -> None:
        self.assertEqual(
            fetch.redact_url("https://user:pw@example.com/p?token=abc&x=1&api_key=k&X-Amz-Signature=s&sessionid=9&q=a#f"),
            "https://example.com/p?token=REDACTED&x=1&api_key=REDACTED&X-Amz-Signature=REDACTED&sessionid=REDACTED&q=a")
        self.assertEqual(fetch.redact_url("https://example.com/?auth&password=&page=2"),
                         "https://example.com/?auth&password=REDACTED&page=2")
        self.assertEqual(fetch.redact_url("http://[::1"), "<unparseable URL>")

    def test_fetch_reports_redacted_but_requests_real(self) -> None:
        url = "https://example.com/feed?access_token=abc123&page=2"
        transport = helpers.FakeTransport({url: (200, HTML, b"ok")})
        res = self.get(url, transport)
        self.assertEqual(res.requested_url, "https://example.com/feed?access_token=REDACTED&page=2")
        self.assertEqual(res.url, res.requested_url)
        self.assertEqual(transport.calls[0].url, url)
        self.assertNotIn("abc123", repr(res.as_record()))


class ProxyTest(FetchTestBase):
    def test_check_proxy(self) -> None:
        self.assertEqual(fetch.check_proxy("http://127.0.0.1:3128"), ("127.0.0.1", 3128, "127.0.0.1"))
        self.assertEqual(fetch.check_proxy("10.0.0.2:8080")[2], "10.0.0.2")
        resolver = helpers.FakeResolver({"proxy.example.com": ["10.20.0.1"], "bad.example.com": ["169.254.0.9"]})
        self.assertEqual(fetch.check_proxy("http://proxy.example.com:3128", resolver=resolver),
                         ("proxy.example.com", 3128, "10.20.0.1"))
        for bad in ("http://169.254.169.254:3128", "http://[fe80::1]:3128", "http://metadata.google.internal:80",
                    "http://0.0.0.0:3128", "http://224.0.0.1:3128", "http://100.100.100.200:80", "http://240.0.0.1:1",
                    "http://user:pw@proxy.example.com:3128", "socks5://127.0.0.1:1080", "https://127.0.0.1:3128",
                    "http://bad.example.com:3128", "http://127.0.0.1:99999", "", "http://%31:80"):
            with self.subTest(proxy=bad), self.assertRaises(FetchRefused):
                fetch.check_proxy(bad, resolver=resolver)

    def test_metadata_proxy_from_environment_refused(self) -> None:
        transport = helpers.FakeTransport(default=(200, HTML, b"x"))
        with mock.patch.dict(os.environ, {"HTTPS_PROXY": "http://169.254.169.254:3128"}):
            res = self.get("https://example.com/", transport, via_proxy=True)
        self.assertEqual(res.error_kind, "url_refused")
        self.assertEqual(transport.calls, [])

    def test_proxy_mode_requests(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/x": (200, HTML, b"ok"),
                                           "http://example.org/y": (200, HTML, b"ok")})
        no_dns = helpers.FakeResolver({})
        env = {"HTTPS_PROXY": "http://127.0.0.1:3128", "HTTP_PROXY": "http://127.0.0.1:3129"}
        with mock.patch.dict(os.environ, env):
            res = self.get("https://example.com/x", transport, resolver=no_dns, via_proxy=True)
            plain = self.get("http://example.org/y", transport, resolver=no_dns, via_proxy=True)
        self.assertEqual((res.status, res.via_proxy, res.pinned_ip), (200, True, None))
        req = transport.calls[0]
        self.assertEqual((req.proxy, req.target, req.host), (("127.0.0.1", 3128, "127.0.0.1"), "/x", "example.com"))
        self.assertEqual((transport.calls[1].proxy[1], transport.calls[1].target), (3129, "http://example.org/y"))
        self.assertTrue(plain.via_proxy)

    def test_proxy_mode_still_checks_target(self) -> None:
        transport = helpers.FakeTransport(default=(200, HTML, b"x"))
        private = helpers.FakeResolver({"intra.example.com": ["10.9.9.9"]})
        res = self.get("https://intra.example.com/", transport, resolver=private, via_proxy=True,
                       proxy_url="http://127.0.0.1:3128")
        self.assertEqual(res.error_kind, "url_refused")
        self.assertEqual(self.get("http://127.0.0.1/", transport, via_proxy=True,
                                  proxy_url="http://127.0.0.1:3128").error_kind, "url_refused")
        self.assertEqual(transport.calls, [])
        with mock.patch.dict(os.environ, {}, clear=True):
            missing = self.get("https://example.com/", transport, via_proxy=True)
        self.assertEqual(missing.error_kind, "connection")

    def test_local_targets_bypass_proxy(self) -> None:
        transport = helpers.FakeTransport({"http://localhost:3000/": (200, HTML, b"dev")})
        res = fetch.fetch("http://localhost:3000/", allow_local=["localhost:3000"], via_proxy=True,
                          proxy_url="http://10.0.0.2:3128", transport=transport,
                          resolver=helpers.FakeResolver({"localhost": ["127.0.0.1"]}))
        self.assertEqual((res.status, res.via_proxy, res.pinned_ip, transport.calls[0].proxy),
                         (200, False, "127.0.0.1", None))


def site(pages):
    """FakeTransport for a small synthetic site: {path: (status, links)}."""
    routes = {}
    for path, (status, links) in pages.items():
        body = "".join('<a href="%s">x</a>' % link for link in links).encode()
        routes["https://example.com" + path] = (status, HTML, body)
    return helpers.FakeTransport(routes)


def links_of(html, base):
    import re
    import urllib.parse
    return [urllib.parse.urljoin(base, h) for h in re.findall(r'href="([^"]+)"', html)]


class CrawlTest(FetchTestBase):
    def crawl(self, transport, start="https://example.com/", **kw):
        clock = kw.pop("clock", helpers.FakeClock())
        stats = {}
        results = fetch.crawl(start, extract_links=kw.pop("extract_links", links_of), transport=transport,
                              resolver=kw.pop("resolver", self.resolver()), clock=clock, sleep=clock.sleep,
                              stats=stats, **kw)
        return results, stats, clock

    def test_robots_predicate_same_origin_and_assets(self) -> None:
        transport = site({"/": (200, ["/a", "/private/x", "https://example.org/ext", "/logo.png", "/a#frag", "mailto:x"]),
                          "/a": (200, ["/", "/b"]), "/b": (200, []), "/private/x": (200, [])})
        results, stats, clock = self.crawl(transport, robots_allowed=lambda u: "/private/" not in u)
        self.assertEqual([r.url for r in results], ["https://example.com/", "https://example.com/a",
                                                    "https://example.com/b"])
        self.assertEqual(stats["skipped_robots"], ["https://example.com/private/x"])
        self.assertEqual(stats["skipped_cross_origin"], ["https://example.org/ext"])
        self.assertEqual(stats["skipped_assets"], 1)
        self.assertNotIn("https://example.org/ext", transport.urls)
        self.assertEqual(clock.sleeps, [1.0, 1.0])

    def test_max_pages_deadline_and_bytes(self) -> None:
        many = {"/": (200, ["/p%d" % i for i in range(20)])}
        many.update({"/p%d" % i: (200, []) for i in range(20)})
        results, stats, _ = self.crawl(site(many), max_pages=3)
        self.assertEqual((len(results), stats["stopped"]), (3, "max_pages"))
        results, stats, _ = self.crawl(site(many), max_pages=50, deadline_s=1.5)
        self.assertEqual((len(results), stats["stopped"]), (3, "deadline"))
        results, stats, _ = self.crawl(site(many), max_pages=50, delay=0.0, max_total_bytes=100)
        self.assertEqual(stats["stopped"], "max_total_bytes")
        self.assertLess(len(results), 21)
        for bad in (0, 501):
            with self.assertRaises(ValueError):
                self.crawl(site(many), max_pages=bad)
        with self.assertRaises(ValueError):
            self.crawl(site(many), delay=-1)
        with self.assertRaises(TypeError):
            self.crawl(site(many), colour="red")

    def test_delays(self) -> None:
        transport = site({"/": (200, ["/a", "/b"]), "/a": (200, []), "/b": (200, [])})
        _, _, clock = self.crawl(transport, delay=0.5)
        self.assertEqual(clock.sleeps, [0.5, 0.5])
        local = helpers.FakeTransport({"http://localhost:3000/": (200, HTML, b'<a href="/a">a</a>'),
                                       "http://localhost:3000/a": (200, HTML, b"")})
        results, _, clock = self.crawl(local, start="http://localhost:3000/", allow_local=["localhost:3000"],
                                       resolver=helpers.FakeResolver({"localhost": ["127.0.0.1"]}))
        self.assertEqual((len(results), clock.sleeps), (2, [0.2]))

    def test_start_refused_and_non_html_pages(self) -> None:
        results, stats, _ = self.crawl(helpers.FakeTransport(), start="http://127.0.0.1/")
        self.assertEqual((len(results), results[0].error_kind, stats["stopped"]),
                         (1, "url_refused", "start URL refused"))
        calls = []
        transport = helpers.FakeTransport({"https://example.com/": (404, HTML, b'<a href="/x">x</a>')})
        results, _, _ = self.crawl(transport, extract_links=lambda h, b: calls.append(b) or [])
        self.assertEqual((len(results), calls), (1, []))

    def test_start_redirect_moves_origin_once(self) -> None:
        transport = helpers.FakeTransport({
            "http://example.com/": (301, {"Location": "https://www.example.com/"}, b""),
            "https://www.example.com/": (200, HTML, b'<a href="/a">a</a><a href="http://example.com/b">b</a>'),
            "https://www.example.com/a": (302, {"Location": "https://example.org/elsewhere"}, b"")})
        results, stats, _ = self.crawl(transport, start="http://example.com/")
        self.assertEqual([r.url for r in results], ["https://www.example.com/", "https://www.example.com/a"])
        self.assertEqual(results[1].redirect_target, "https://example.org/elsewhere")
        self.assertIn("https://example.org/elsewhere", stats["skipped_cross_origin"])
        self.assertIn("http://example.com/b", stats["skipped_cross_origin"])
        self.assertNotIn("https://example.org/elsewhere", transport.urls)

    def test_start_redirect_to_other_site_not_followed(self) -> None:
        transport = helpers.FakeTransport({"https://example.com/": (301, {"Location": "https://example.org/"}, b"")})
        results, stats, _ = self.crawl(transport)
        self.assertEqual((len(results), results[0].redirect_target), (1, "https://example.org/"))
        self.assertEqual(transport.urls, ["https://example.com/"])

    def test_refused_links_and_redirects_are_recorded_not_fatal(self) -> None:
        transport = site({"/": (200, ["/a b", "/go", "/ok"]), "/ok": (200, [])})
        transport.add("https://example.com/go", 302, {"Location": "http://127.0.0.1/"})
        results, stats, _ = self.crawl(transport)
        by_url = {r.url: r for r in results}
        self.assertEqual(by_url["https://example.com/a b"].error_kind, "url_refused")
        self.assertIsNone(by_url["https://example.com/go"].error)
        self.assertEqual(by_url["https://example.com/go"].redirect_target, "http://127.0.0.1/")
        self.assertIn("http://127.0.0.1/", stats["skipped_cross_origin"])
        self.assertIsNone(by_url["https://example.com/ok"].error)
        self.assertNotIn("http://127.0.0.1/", transport.urls)


class RobotsGateTest(FetchTestBase):
    def gate(self, routes, start="https://example.com/start"):
        parsed = []

        def parse(text):
            parsed.append(text)
            return lambda url: "/blocked" not in url
        pred, info = fetch.robots_gate(start, parse=parse, transport=helpers.FakeTransport(routes),
                                       resolver=self.resolver(), clock=helpers.FakeClock())
        return pred, info, parsed

    def test_outcomes(self) -> None:
        pred, info, parsed = self.gate({"https://example.com/robots.txt": (200, {"Content-Type": "text/plain"},
                                                                          b"User-agent: *\nDisallow: /blocked\n")})
        self.assertEqual((info["outcome"], info["status"]), ("parsed", 200))
        self.assertIn("Disallow: /blocked", parsed[0])
        self.assertTrue(pred("https://example.com/a") and not pred("https://example.com/blocked"))
        pred, info, parsed = self.gate({"https://example.com/robots.txt": (404, HTML, b"nope")})
        self.assertEqual((info["outcome"], parsed), ("no-restrictions", []))
        self.assertTrue(pred("https://example.com/blocked"))
        for status in (500, 503, 429):
            with self.subTest(status=status):
                pred, info, _ = self.gate({"https://example.com/robots.txt": (status, HTML, b"err")})
                self.assertEqual(info["outcome"], "unreachable")
                self.assertTrue(pred("https://example.com/start"))
                self.assertTrue(pred("https://example.com/start#x"))
                self.assertFalse(pred("https://example.com/other"))
        pred, info, _ = self.gate({})
        self.assertEqual((info["outcome"], info["error_kind"]), ("unreachable", "connection"))
        pred, info, _ = self.gate({}, start="http://127.0.0.1/")
        self.assertEqual(info["outcome"], "refused")
        self.assertFalse(pred("http://127.0.0.1/"))


if __name__ == "__main__":
    unittest.main()
