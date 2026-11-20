#!/usr/bin/env python3
"""Decide whether an email found on a public page may be recorded as a creator's contact.

Stdlib only, pure functions, no network and no files. The decision reference is
references/contact-capture-rules.md (from this directory: ../references/contact-capture-rules.md).
Change the rule table below and that reference together.

Sources for the constants:
  * Role mailboxes: RFC 2142 section 4 (abuse, postmaster, webmaster, hostmaster, info,
    marketing, sales, support, noc, security, news, usenet, www, ftp, uucp), plus a short
    list of everyday additions of our own.
  * Deal inboxes: the HypeStake product decision that a deal inbox a creator published on
    their own domain is a business contact. The list is ours.
  * Reserved example names: RFC 2606 (example.com, example.org, example.net and the test,
    example, invalid and localhost top-level names).

Parity: src/contact-rules.ts is a TypeScript port of this module for the HypeStake runtimes.
Both must return the same result for every vector in ../vectors/contact-rules.vectors.json
(see build_vectors.py). Change both, then regenerate and review the vectors.

Registrable domain: this module uses a heuristic. A two-letter country TLD preceded by a
generic second-level label (co, com, org, net, ac, gov, edu) takes three labels, anything
else takes two. It is wrong for many country registries. Production code should use the
Public Suffix List through a vetted library and replace registrable_domain().

Usage, from this directory:
    python3 -I -B contact_rules.py classify partnerships@janedoe.com --site janedoe.com --page sponsor
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import re
from dataclasses import dataclass
from typing import Callable, Iterable

# --- Constants -------------------------------------------------------------------------
# Names are compared after _compact(): lowercase, a +tag removed, separators and trailing
# digits dropped, so "Customer-Service", "sales2" and "support+vip" all match.

RFC2142_ROLES = {
    "ftp", "hostmaster", "info", "marketing", "news", "noc", "postmaster", "sales",
    "support", "usenet", "uucp", "webmaster", "www",
}
EXTRA_ROLES = {
    "accounts", "admin", "billing", "careers", "contact", "customerservice", "editorial",
    "enquiries", "feedback", "general", "hello", "help", "hi", "inquiries", "jobs", "mail",
    "media", "newsroom", "office", "press", "service", "subscribe", "subscriptions", "team",
}
ROLE_LOCALS = RFC2142_ROLES | EXTRA_ROLES

# Addresses that exist for one operational purpose. Outreach there is misuse.
PURPOSE_BOUND_LOCALS = {
    "abuse", "donotreply", "git", "noreply", "security",
}

LEGAL_LOCALS = {
    "compliance", "copyright", "dmca", "dpo", "gdpr", "legal", "privacy", "trust",
}
_DPO_PREFIX = re.compile(r"dpo[-_.]")

DEAL_LOCALS = {
    "ads", "advertise", "advertising", "biz", "booking", "bookings", "brand",
    "brandpartners", "brandpartnerships", "brands", "business", "businessenquiries",
    "businessinquiries", "collab", "collaborations", "collabs", "deals", "management",
    "mgmt", "partners", "partnership", "partnerships", "pr", "sponsor", "sponsors",
    "sponsorship", "sponsorships", "workwithme",
}

PLACEHOLDER_LOCALS = {
    "email", "firstlast", "firstname", "lastname", "name", "someone", "user", "username",
    "you", "youremail", "yourname",
}
RESERVED_TLDS = {
    "example", "invalid", "localhost", "test",
}  # RFC 2606
PLACEHOLDER_DOMAINS = {
    "company.com", "domain.com", "email.com", "example.com", "example.net", "example.org",
    "yourcompany.com", "yourdomain.com", "yoursite.com",
}
# Hosted tooling that stamps addresses into pages: error-tracking keys, site-builder assets.
TOOLING_DOMAINS = {
    "sentry.io", "wixpress.com",
}

ASSET_EXTENSIONS = {
    "avif", "bmp", "css", "gif", "ico", "jpeg", "jpg", "js", "map", "mjs", "mp4", "png",
    "svg", "ttf", "webm", "webp", "woff", "woff2",
}
_DENSITY_LABEL = re.compile(r"\d(\.\d)?x")  # the "2x" of "logo@2x.png"

# Heuristic registrable-domain suffixes (see the module docstring).
GENERIC_SECOND_LEVEL = {"co", "com", "org", "net", "ac", "gov", "edu"}

# Page kinds where an address is incidental rather than a deliberate contact entry.
INCIDENTAL_PAGES = {"legal", "roster", "footer"}
ROSTER_MIN_DOMAINS = 5
SITEWIDE_MIN_PAGES = 3
KEPT_KINDS = {"personal", "business_inbox"}

# --- Extraction ------------------------------------------------------------------------

# Only ASCII whitespace is trimmed, so Python and TypeScript agree on what is stripped.
_ASCII_WS = " \t\n\r\f\v"
# A pinned entity decoder instead of html.unescape, so the TypeScript port can match it exactly.
# The semicolon is required. Unknown names and invalid code points are left as written.
_ENTITY = re.compile(r"&(#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z]{2,8});")
NAMED_ENTITIES = {
    "amp": "&", "apos": "'", "commat": "@", "gt": ">", "lt": "<", "nbsp": "\u00a0",
    "period": ".", "quot": '"',
}
_UNICODE_ESCAPE = re.compile(r"\\u([0-9a-fA-F]{4})")
_WHITESPACE_ESCAPE = re.compile(r"\\[nrt]")
_CANDIDATE = re.compile(
    r"""(?<![A-Za-z0-9._%+\-\x80-\U0010FFFF])   # not after a local-part character (letters, digits, . _ % + -) or any non-ASCII character
        [A-Za-z0-9][A-Za-z0-9._%+-]{0,63}      # local part, at most 64 characters (RFC 5321)
        @
        [A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63}){0,126}\.[A-Za-z]{2,24}   # labels of at most 63 (RFC 1035)
        (?![A-Za-z0-9_-]|\.[A-Za-z0-9]|[^\x00-\x7F])   # the domain really ends here: never cut a longer label short
    """,
    re.VERBOSE,
)


def _code_point(cp: int, original: str) -> str:
    """The character for a decoded escape, or the original text for NUL, surrogates and overflow."""
    if 0 < cp <= 0x10FFFF and not 0xD800 <= cp <= 0xDFFF:
        return chr(cp)
    return original


def _entity(m: re.Match[str]) -> str:
    body = m.group(1)
    if body[0] == "#":
        cp = int(body[2:], 16) if body[1] in "xX" else int(body[1:])
        return _code_point(cp, m.group(0))
    return NAMED_ENTITIES.get(body, m.group(0))


def decode(raw: str | None) -> str:
    """Turn escaped text into plain text. Always run this before extract().

    A literal backslash-t or backslash-n sits in front of the next word as a plain letter.
    Left in place it glues to a local part and yields a believable but wrong address.
    Decodes \\uXXXX escapes (not surrogates), literal \\n \\r \\t, numeric entities and the
    named entities in NAMED_ENTITIES, in that order, each in one pass.
    """
    if raw is None:
        return ""
    if not isinstance(raw, str):
        raise TypeError("decode() takes a string")
    text = _UNICODE_ESCAPE.sub(lambda m: _code_point(int(m.group(1), 16), m.group(0)), raw)
    text = _WHITESPACE_ESCAPE.sub(" ", text)
    return _ENTITY.sub(_entity, text)


def extract(raw: str | None) -> list[str]:
    """Return unique lowercase candidate addresses from raw page or bio text.

    Every quantifier in the pattern is bounded, so the scan is linear in the text length.
    Only ASCII decides the boundaries, so the result does not depend on Unicode tables.
    A domain longer than 253 characters (RFC 1035) is dropped.
    """
    cleaned = (m.rstrip(".,;:)>]'\"").lower() for m in _CANDIDATE.findall(decode(raw)))
    return list(dict.fromkeys(m for m in cleaned if len(m.rpartition("@")[2]) <= MAX_DOMAIN_LENGTH))


# --- Domains ---------------------------------------------------------------------------


_LABEL = re.compile(r"[A-Za-z0-9-]+")
_LOCAL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}")
MAX_DOMAIN_LENGTH = 253
_TLD = re.compile(r"[a-z]{2,24}")


def _is_count(value: object, minimum: int = 0) -> bool:
    """A whole number >= minimum. Booleans are refused; 3.0 counts as 3 so JSON callers agree."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value) and float(value).is_integer() and value >= minimum
    except OverflowError:  # an int too large for a float, such as 10**400
        return False


def registrable_domain(host_or_address: str) -> str | None:
    """Heuristic registrable domain of a host or an address. See the module docstring.

    Pass a host, not a URL: a scheme, path, port or any character outside letters, digits and
    hyphens makes the result None. A bare generic suffix such as co.uk is no one's domain (None).
    """
    if not isinstance(host_or_address, str):
        raise TypeError("registrable_domain() takes a string")
    host = host_or_address.rpartition("@")[2].strip(_ASCII_WS).rstrip(".")
    labels = host.split(".")
    if len(labels) < 2 or not all(_LABEL.fullmatch(label) for label in labels):
        return None
    labels = [label.lower() for label in labels]  # ASCII only after the check above
    if len(labels[-1]) == 2 and labels[-2] in GENERIC_SECOND_LEVEL:
        return ".".join(labels[-3:]) if len(labels) >= 3 else None
    return ".".join(labels[-2:])


def is_roster_page(addresses: list[str], min_domains: int = ROSTER_MIN_DOMAINS) -> bool:
    """True when a page lists addresses on many registrable domains: it names other people."""
    if not _is_count(min_domains, 1):
        raise ValueError("min_domains must be a whole number >= 1")
    if isinstance(addresses, str):
        raise TypeError("addresses must be a list of strings")
    try:
        addresses = list(addresses)  # materialise once, so a generator is not consumed by the check
    except TypeError:
        raise TypeError("addresses must be a list of strings") from None
    if not all(isinstance(a, str) for a in addresses):
        raise TypeError("addresses must be a list of strings")
    domains = {d for d in map(registrable_domain, addresses) if d}
    return len(domains) >= min_domains


# --- Classification --------------------------------------------------------------------


@dataclass(frozen=True)
class Verdict:
    kind: str  # personal | business_inbox | a reject_* kind
    keep: bool
    reason: str


@dataclass(frozen=True)
class Case:
    """Everything a rule may look at, computed once per address."""
    local: str
    domain: str
    tld: str
    registrable: str | None
    name: str  # compacted local part
    own_domain: bool
    page: str
    pages_seen_on: int
    platform_domains: frozenset[str]


def _compact(local: str) -> str:
    base = local.split("+", 1)[0]
    base = re.sub(r"[-_.]", "", base)
    return base.rstrip("0123456789") or base


def _is_malformed(c: Case) -> bool:
    return not c.local or c.registrable is None or not _TLD.fullmatch(c.tld)


def _is_asset(c: Case) -> bool:
    return c.tld in ASSET_EXTENSIONS or bool(_DENSITY_LABEL.fullmatch(c.domain.split(".")[0]))


def _is_placeholder(c: Case) -> bool:
    return (
        c.name in PLACEHOLDER_LOCALS
        or c.registrable in PLACEHOLDER_DOMAINS
        or c.tld in RESERVED_TLDS
    )


def _is_tooling(c: Case) -> bool:
    return c.registrable in TOOLING_DOMAINS


def _is_platform(c: Case) -> bool:
    return c.registrable in c.platform_domains


def _is_purpose_bound(c: Case) -> bool:
    return c.name in PURPOSE_BOUND_LOCALS


def _is_legal(c: Case) -> bool:
    return c.name in LEGAL_LOCALS or bool(_DPO_PREFIX.match(c.local))


def _on_incidental_page(c: Case) -> bool:
    return c.page in INCIDENTAL_PAGES


def _is_sitewide(c: Case) -> bool:
    return c.pages_seen_on >= SITEWIDE_MIN_PAGES


def _is_deal_on_own_domain(c: Case) -> bool:
    return c.name in DEAL_LOCALS and c.own_domain


def _is_deal_elsewhere(c: Case) -> bool:
    return c.name in DEAL_LOCALS


def _is_role(c: Case) -> bool:
    return c.name in ROLE_LOCALS


def _always(_: Case) -> bool:
    return True


# (predicate, kind, reason). Evaluated top to bottom; the first predicate that is true decides.
RULES: tuple[tuple[Callable[[Case], bool], str, str], ...] = (
    (_is_malformed, "reject_junk", "malformed address"),
    (_is_asset, "reject_junk", "asset filename, not an address"),
    (_is_placeholder, "reject_placeholder", "template or reserved example address"),
    (_is_tooling, "reject_placeholder", "address stamped in by error-tracking or site-builder tooling"),
    (_is_platform, "reject_platform", "address on a platform domain belongs to the platform"),
    (_is_purpose_bound, "reject_purpose_bound", "published for another purpose"),
    (_is_legal, "reject_legal", "legal inbox"),
    (_on_incidental_page, "reject_incidental", "found on a page where addresses are incidental"),
    (_is_sitewide, "reject_footer", "repeats across pages: a site-wide entry, not a person"),
    (_is_deal_on_own_domain, "business_inbox", "creator-published deal inbox on their own domain"),
    (_is_deal_elsewhere, "reject_role", "deal-style inbox not on the creator's own domain"),
    (_is_role, "reject_role", "role inbox collapses many people into one"),
    (_always, "personal", "personal-looking address on a deliberate contact surface"),
)


def classify(
    address: str,
    site_domain: str | None = None,
    page: str = "contact",
    pages_seen_on: int = 1,
    platform_domains: Iterable[str] = frozenset(),
) -> Verdict:
    """Classify one address. `site_domain` is the creator's own site host, never an aggregator.

    Raises TypeError or ValueError on invalid arguments. A malformed address is not an error: it
    returns reject_junk. The local part must look like one extract() can produce.
    """
    if not isinstance(address, str):
        raise TypeError("address must be a string")
    if site_domain is not None and not isinstance(site_domain, str):
        raise TypeError("site_domain must be a string or None")
    if not isinstance(page, str):
        raise TypeError("page must be a string")
    if not _is_count(pages_seen_on, 0):
        raise ValueError("pages_seen_on must be a whole number >= 0")
    if isinstance(platform_domains, str):
        raise TypeError("platform_domains must be a collection of strings")
    try:
        platform_domains = frozenset(platform_domains)  # materialise once, so a generator is not consumed
    except TypeError:
        raise TypeError("platform_domains must be a collection of strings") from None
    if not all(isinstance(d, str) for d in platform_domains):
        raise TypeError("platform_domains must be a collection of strings")
    raw_local, _, raw_domain = address.strip(_ASCII_WS).rpartition("@")
    local = raw_local.lower() if _LOCAL.fullmatch(raw_local) else ""
    registrable = registrable_domain(raw_domain)
    domain = raw_domain.lower() if registrable is not None else raw_domain
    case = Case(
        local=local,
        domain=domain,
        tld=domain.rpartition(".")[2],
        registrable=registrable,
        name=_compact(local),
        own_domain=bool(site_domain) and registrable is not None and registrable == registrable_domain(site_domain),
        page=page,
        pages_seen_on=int(pages_seen_on),
        platform_domains=platform_domains,
    )
    for predicate, kind, reason in RULES:
        if predicate(case):
            return Verdict(kind, kind in KEPT_KINDS, reason)
    raise AssertionError("the final rule always matches")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify one address found on a public page.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("classify")
    one.add_argument("address")
    one.add_argument("--site", default=None, help="creator's own site domain")
    one.add_argument("--page", default="contact", help="page kind, e.g. contact, sponsor, legal")
    one.add_argument("--pages-seen-on", type=int, default=1)
    one.add_argument("--platform-domain", action="append", default=[],
                     help="registrable platform domain to reject; repeatable")
    args = parser.parse_args()
    verdict = classify(args.address, args.site, args.page, args.pages_seen_on,
                       frozenset(d.lower() for d in args.platform_domain))
    print(json.dumps(dataclasses.asdict(verdict)))


if __name__ == "__main__":
    main()
