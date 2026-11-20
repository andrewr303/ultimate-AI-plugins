/**
 * Contact rules: decide whether an email found on a public page may be recorded as a creator's contact.
 *
 * TypeScript port of scripts/contact_rules.py, which stays the reference. Both must return the same result for every
 * vector in vectors/contact-rules.vectors.json. Change both, then regenerate and review the vectors.
 *
 * Pure: no I/O, no clock, no Node built-ins, ES2020 library only, no regex lookbehind (older Safari lacks it). Invalid
 * arguments throw TypeError or RangeError; a malformed address is not an error and returns `reject_junk`.
 *
 * The registrable-domain function is a heuristic (see the Python module). In HypeStake, prefer the pinned Public
 * Suffix List snapshot the STAR Finder kernel uses (src/shared/star/finder/domains.ts) and keep this one for parity.
 * Raw addresses are coordinates: hand kept ones only to the contact store the caller owns. Never log or trace them.
 */

export const CONTACT_RULES_VERSION = "contact-rules-v2";

const set = (words: string): ReadonlySet<string> => new Set(words.split(" "));

export const RFC2142_ROLES: ReadonlySet<string> = set("ftp hostmaster info marketing news noc postmaster sales support usenet uucp webmaster www");
export const EXTRA_ROLES: ReadonlySet<string> = set(
  "accounts admin billing careers contact customerservice editorial enquiries feedback general hello help hi inquiries jobs mail media newsroom office press service subscribe subscriptions team",
);
const ROLE_LOCALS: ReadonlySet<string> = new Set([...RFC2142_ROLES, ...EXTRA_ROLES]);
export const PURPOSE_BOUND_LOCALS: ReadonlySet<string> = set("abuse donotreply git noreply security");
export const LEGAL_LOCALS: ReadonlySet<string> = set("compliance copyright dmca dpo gdpr legal privacy trust");
export const DEAL_LOCALS: ReadonlySet<string> = set(
  "ads advertise advertising biz booking bookings brand brandpartners brandpartnerships brands business businessenquiries businessinquiries collab collaborations collabs deals management mgmt partners partnership partnerships pr sponsor sponsors sponsorship sponsorships workwithme",
);
export const PLACEHOLDER_LOCALS: ReadonlySet<string> = set("email firstlast firstname lastname name someone user username you youremail yourname");
export const RESERVED_TLDS: ReadonlySet<string> = set("example invalid localhost test");
export const PLACEHOLDER_DOMAINS: ReadonlySet<string> = set("company.com domain.com email.com example.com example.net example.org yourcompany.com yourdomain.com yoursite.com");
export const TOOLING_DOMAINS: ReadonlySet<string> = set("sentry.io wixpress.com");
export const ASSET_EXTENSIONS: ReadonlySet<string> = set("avif bmp css gif ico jpeg jpg js map mjs mp4 png svg ttf webm webp woff woff2");
export const GENERIC_SECOND_LEVEL: ReadonlySet<string> = set("co com org net ac gov edu");
export const INCIDENTAL_PAGES: ReadonlySet<string> = set("legal roster footer");
export const ROSTER_MIN_DOMAINS = 5;
export const SITEWIDE_MIN_PAGES = 3;
export const NAMED_ENTITIES: Readonly<Record<string, string>> = Object.freeze({
  amp: "&", apos: "'", commat: "@", gt: ">", lt: "<", nbsp: " ", period: ".", quot: '"',
});

export type ContactKind =
  | "personal"
  | "business_inbox"
  | "reject_junk"
  | "reject_placeholder"
  | "reject_platform"
  | "reject_purpose_bound"
  | "reject_legal"
  | "reject_incidental"
  | "reject_footer"
  | "reject_role";

export interface ContactVerdict {
  kind: ContactKind;
  keep: boolean;
  reason: string;
}

export interface ClassifyOptions {
  /** The creator's own site host (never an aggregator or a URL). Null or absent: no own domain to compare against. */
  site_domain?: string | null;
  /** Page kind label, for example contact, sponsor, bio, homepage, legal, roster, footer. Default contact. */
  page?: string;
  /** Number of fetched pages that carried the address. Default 1. */
  pages_seen_on?: number;
  /** Registrable platform domains to refuse, compared exactly (pass them lowercase). */
  platform_domains?: ReadonlyArray<string>;
}

const ASCII_WS_EDGES = /^[ \t\n\r\f\v]+|[ \t\n\r\f\v]+$/g;
const ENTITY = /&(#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z]{2,8});/g;
const UNICODE_ESCAPE = /\\u([0-9a-fA-F]{4})/g;
const WHITESPACE_ESCAPE = /\\[nrt]/g;
// Python uses a negative lookbehind: not after a local-part character (letters, digits, . _ % + -) or any non-ASCII
// character. Here that check is a consumed prefix (group 1), so the pattern runs on engines without lookbehind support.
// Only ASCII decides boundaries (a non-ASCII UTF-16 code unit is always >= 0x80), so the result does not depend on an
// engine's Unicode tables. Every quantifier is bounded (local part 64, labels 63, at most 127 labels), so the scan is
// linear in the text length.
const CANDIDATE = /(^|[^A-Za-z0-9._%+\-\u0080-\uFFFF])([A-Za-z0-9][A-Za-z0-9._%+-]{0,63}@[A-Za-z0-9-]{1,63}(?:\.[A-Za-z0-9-]{1,63}){0,126}\.[A-Za-z]{2,24}(?![A-Za-z0-9_-]|\.[A-Za-z0-9]|[^\x00-\x7F]))/g;
export const MAX_DOMAIN_LENGTH = 253;
const LABEL = /^[A-Za-z0-9-]+$/;
const LOCAL = /^[A-Za-z0-9][A-Za-z0-9._%+-]{0,63}$/;
const TLD = /^[a-z]{2,24}$/;
const DENSITY_LABEL = /^\d(\.\d)?x$/;
const DPO_PREFIX = /^dpo[-_.]/;

const isCount = (v: unknown, min: number): v is number => typeof v === "number" && Number.isFinite(v) && Math.floor(v) === v && v >= min;
const trimAscii = (s: string): string => s.replace(ASCII_WS_EDGES, "");

function codePoint(cp: number, original: string): string {
  return cp > 0 && cp <= 0x10ffff && !(cp >= 0xd800 && cp <= 0xdfff) ? String.fromCodePoint(cp) : original;
}

/** Turn escaped text into plain text. Always run this before extract(). Null or undefined gives "". */
export function decode(raw: string | null | undefined): string {
  if (raw === null || raw === undefined) return "";
  if (typeof raw !== "string") throw new TypeError("decode() takes a string");
  const text = raw.replace(UNICODE_ESCAPE, (m, hex: string) => codePoint(parseInt(hex, 16), m)).replace(WHITESPACE_ESCAPE, " ");
  return text.replace(ENTITY, (m, body: string) => {
    if (body.charAt(0) === "#") {
      const hex = body.charAt(1) === "x" || body.charAt(1) === "X";
      return codePoint(hex ? parseInt(body.slice(2), 16) : parseInt(body.slice(1), 10), m);
    }
    return Object.prototype.hasOwnProperty.call(NAMED_ENTITIES, body) ? (NAMED_ENTITIES[body] as string) : m;
  });
}

/** Unique lowercase candidate addresses from raw page or bio text, in order of first appearance. Linear time. */
export function extract(raw: string | null | undefined): string[] {
  const text = decode(raw);
  const seen = new Set<string>();
  CANDIDATE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = CANDIDATE.exec(text)) !== null) {
    const hit = (m[2] as string).replace(/[.,;:)>\]'"]+$/, "").toLowerCase();
    if (hit.length - hit.lastIndexOf("@") - 1 <= MAX_DOMAIN_LENGTH) seen.add(hit);
  }
  return Array.from(seen);
}

/** Heuristic registrable domain of a host or an address, or null. Pass a host, not a URL. */
export function registrableDomain(hostOrAddress: string): string | null {
  if (typeof hostOrAddress !== "string") throw new TypeError("registrableDomain() takes a string");
  const host = trimAscii(hostOrAddress.slice(hostOrAddress.lastIndexOf("@") + 1)).replace(/\.+$/, "");
  const raw = host.split(".");
  if (raw.length < 2 || !raw.every((label) => LABEL.test(label))) return null;
  const labels = raw.map((label) => label.toLowerCase());
  const last = labels[labels.length - 1] as string;
  const second = labels[labels.length - 2] as string;
  if (last.length === 2 && GENERIC_SECOND_LEVEL.has(second)) return labels.length >= 3 ? labels.slice(-3).join(".") : null;
  return labels.slice(-2).join(".");
}

/** True when a page lists addresses on min_domains or more registrable domains: it names other people. */
export function isRosterPage(addresses: ReadonlyArray<string>, minDomains: number = ROSTER_MIN_DOMAINS): boolean {
  if (!isCount(minDomains, 1)) throw new RangeError("min_domains must be a whole number >= 1");
  if (!Array.isArray(addresses) || !addresses.every((a) => typeof a === "string")) throw new TypeError("addresses must be an array of strings");
  const domains = new Set<string>();
  for (const a of addresses) {
    const d = registrableDomain(a);
    if (d) domains.add(d);
  }
  return domains.size >= minDomains;
}

interface Case {
  local: string;
  domain: string;
  tld: string;
  registrable: string | null;
  name: string;
  ownDomain: boolean;
  page: string;
  pagesSeenOn: number;
  platformDomains: ReadonlySet<string>;
}

function compact(local: string): string {
  const base = (local.split("+")[0] as string).replace(/[-_.]/g, "");
  return base.replace(/[0-9]+$/, "") || base;
}

type Rule = readonly [(c: Case) => boolean, ContactKind, string];

/** Evaluated top to bottom; the first predicate that is true decides. Mirrors RULES in the Python module. */
export const RULES: ReadonlyArray<Rule> = Object.freeze([
  [(c) => !c.local || c.registrable === null || !TLD.test(c.tld), "reject_junk", "malformed address"],
  [(c) => ASSET_EXTENSIONS.has(c.tld) || DENSITY_LABEL.test(c.domain.split(".")[0] as string), "reject_junk", "asset filename, not an address"],
  [(c) => PLACEHOLDER_LOCALS.has(c.name) || (c.registrable !== null && PLACEHOLDER_DOMAINS.has(c.registrable)) || RESERVED_TLDS.has(c.tld), "reject_placeholder", "template or reserved example address"],
  [(c) => c.registrable !== null && TOOLING_DOMAINS.has(c.registrable), "reject_placeholder", "address stamped in by error-tracking or site-builder tooling"],
  [(c) => c.registrable !== null && c.platformDomains.has(c.registrable), "reject_platform", "address on a platform domain belongs to the platform"],
  [(c) => PURPOSE_BOUND_LOCALS.has(c.name), "reject_purpose_bound", "published for another purpose"],
  [(c) => LEGAL_LOCALS.has(c.name) || DPO_PREFIX.test(c.local), "reject_legal", "legal inbox"],
  [(c) => INCIDENTAL_PAGES.has(c.page), "reject_incidental", "found on a page where addresses are incidental"],
  [(c) => c.pagesSeenOn >= SITEWIDE_MIN_PAGES, "reject_footer", "repeats across pages: a site-wide entry, not a person"],
  [(c) => DEAL_LOCALS.has(c.name) && c.ownDomain, "business_inbox", "creator-published deal inbox on their own domain"],
  [(c) => DEAL_LOCALS.has(c.name), "reject_role", "deal-style inbox not on the creator's own domain"],
  [(c) => ROLE_LOCALS.has(c.name), "reject_role", "role inbox collapses many people into one"],
  [() => true, "personal", "personal-looking address on a deliberate contact surface"],
] satisfies Rule[]);

const KEPT: ReadonlySet<ContactKind> = new Set<ContactKind>(["personal", "business_inbox"]);

/** Classify one address found on a public page. */
export function classify(address: string, options: ClassifyOptions = {}): ContactVerdict {
  if (typeof address !== "string") throw new TypeError("address must be a string");
  if (options === null || typeof options !== "object") throw new TypeError("options must be an object");
  const siteDomain = options.site_domain === undefined ? null : options.site_domain;
  const page = options.page === undefined ? "contact" : options.page;
  const pagesSeenOn = options.pages_seen_on === undefined ? 1 : options.pages_seen_on;
  const platformDomains = options.platform_domains === undefined ? [] : options.platform_domains;
  if (siteDomain !== null && typeof siteDomain !== "string") throw new TypeError("site_domain must be a string or null");
  if (typeof page !== "string") throw new TypeError("page must be a string");
  if (typeof pagesSeenOn === "boolean" || !isCount(pagesSeenOn, 0)) throw new RangeError("pages_seen_on must be a whole number >= 0");
  if (!Array.isArray(platformDomains) || !platformDomains.every((d) => typeof d === "string")) throw new TypeError("platform_domains must be an array of strings");

  const trimmed = trimAscii(address);
  const at = trimmed.lastIndexOf("@");
  const rawLocal = at < 0 ? "" : trimmed.slice(0, at);
  const rawDomain = at < 0 ? trimmed : trimmed.slice(at + 1);
  const local = LOCAL.test(rawLocal) ? rawLocal.toLowerCase() : "";
  const registrable = registrableDomain(rawDomain);
  const domain = registrable !== null ? rawDomain.toLowerCase() : rawDomain;
  const c: Case = {
    local,
    domain,
    tld: domain.slice(domain.lastIndexOf(".") + 1),
    registrable,
    name: compact(local),
    ownDomain: !!siteDomain && registrable !== null && registrable === registrableDomain(siteDomain),
    page,
    pagesSeenOn,
    platformDomains: new Set(platformDomains),
  };
  for (const [predicate, kind, reason] of RULES) {
    if (predicate(c)) return { kind, keep: KEPT.has(kind), reason };
  }
  throw new Error("the final rule always matches");
}
