#!/usr/bin/env python3
"""design-variations helper. Python 3.8+, standard library only.

Commands
  init     DIR --title T [--mode redesign|new] [--w 1440 --h 900] [--theme light|dark]   start a workspace (never overwrites)
  next     DIR [--count 10]                                         print the next round number and option IDs
  build    DIR [--out index.html] [--standalone]                    assemble the gallery; --standalone also writes variants-standalone/
           DIR --standalone-dir OUTDIR                              write only the standalone pages, to OUTDIR (relative to the current
                                                                    folder, outside the workspace); index.html is not rebuilt
  check    DIR [--strict]                                           validate ledger, variants, spread, quality rules and that index.html boots
  novelty  DIR [--round N]                                          compare a round's ideas (and passed options' signatures) with earlier rounds
  lint-dc  PATH                                                     static checks for Claude Design .dc.html files / canvas.json

Workspace layout (see references/host-html.md):
  DIR/design-variations.json   the round ledger (assets/ledger.schema.json)
  DIR/kit/kit.html             shared tokens, fonts, data and helpers injected into every prototype
  DIR/kit/round-<n>.html       optional additions for round n only, injected after kit.html into that round's frames
  DIR/variants/<id>.html       one prototype per option: <style>, markup, <script>
  DIR/index.html               built gallery (do not hand-edit; rebuild)

Exit codes: 0 ok, 1 errors found, 2 usage problem.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
TEMPLATE = SKILL / "assets" / "gallery-template.html"
LEDGER = "design-variations.json"
SCHEMA_ID = "design-variations/1"
ID_RE = re.compile(r"^(\d{1,3})([a-z])$")
LETTERS = "abcdefghijklmnopqrstuvwxyz"
REDESIGN_BANDS = {"refine": (1, 3), "evolve": (4, 6), "rethink": (7, 8), "reinvent": (9, 10)}
NEW_BANDS = {"proven": (1, 3), "fresh": (4, 6), "novel": (7, 8), "experimental": (9, 10)}
ALL_BANDS = dict(REDESIGN_BANDS, **NEW_BANDS)
KINDS = {"explore", "more", "like", "combine", "refine", "feedback", "scope", "chosen", "edit"}
FIXED_KINDS = {"chosen", "edit"}
DISTRIBUTIONS = {"default", "closer", "bolder", "only-radical", "only-small"}
AXES = {"layout-paradigm", "information-architecture", "density", "visual-hierarchy", "typography", "colour-stance",
        "shape-and-depth", "imagery-and-icons", "motion", "interaction-model", "navigation-model", "content-and-voice",
        "progressive-disclosure", "data-representation", "input-and-controls", "feedback-and-state",
        "automation-and-guidance"}
# Inspiration libraries hold other products' screens; design-context servers hold the user's own design. Only
# libraries must yield references, and a round with no library connected needs a degraded line. Unknown providers
# are treated as libraries.
DESIGN_CONTEXT = {"figma", "dembrandt", "shadcn", "storybook", "penpot", "webflow", "framer", "canva"}
GENERIC_NAME = re.compile(r"^(option|variant|variation|design|version|concept|idea|layout)\s*[-#:]?\s*([a-z]|\d+)?$", re.I)
PLACEHOLDER = re.compile(r"lorem ipsum|dolor sit amet|\bjohn doe\b|\bjane doe\b|\bfoo bar\b|\bplaceholder text\b|\basdf\b", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF]")
INTERACTIVE = re.compile(r"<(button|input|select|textarea|details|summary)\b|<a\s[^>]*href=|tabindex=|contenteditable", re.I)
BEHAVIOUR = re.compile(r"addEventListener|onclick=|onsubmit=|oninput=|onchange=|<details\b", re.I)
EXTERNAL = re.compile(r"""(?:src|href)\s*=\s*["'](https?:)?//([^/"']+)""", re.I)
ALLOWED_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com", "cdnjs.cloudflare.com", "cdn.jsdelivr.net", "unpkg.com")
PLANES = {"surface": (1, 3), "skeleton": (3, 5), "structure": (6, 8), "scope": (9, 10)}
ROLES = {"refine": "Refine", "push": "Push", "crossover": "Crossover", "secondary": "Secondary axis", "wildcard": "Wildcard"}
ROLE_KINDS = {"like", "combine", "refine"}
TRAIT_KEYS = ("skeleton", "device", "interaction", "moment")
CONN_STATUS = {"used", "connected-unused", "needs-signin", "failed", "absent"}
WORKING = {"used", "connected-unused"}
REF_USES = {"seed", "corroborating"}
ROUND_KIT = re.compile(r"^round-([1-9]\d{0,2})\.html$")
ROUND_KIT_LOOSE = re.compile(r"^round-(\d{1,3})\.html$")
SCRIPT_TAG = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.S | re.I)
ABBREV = {"e.g", "i.e", "etc", "vs", "approx", "inc", "co", "ltd", "no", "mr", "mrs", "ms", "dr", "st", "cf", "fig"}
SENTENCE_END = re.compile(r"""(?:([.!?])["'”’)\]]*\s+|([。！？])\s*)(?=\S)""")


class Report:
    def __init__(self):
        self.errors, self.warnings, self.notes = [], [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.notes.append(m)

    def emit(self, title):
        print(title)
        for label, items in (("ERROR", self.errors), ("WARN", self.warnings), ("NOTE", self.notes)):
            for m in items:
                print(f"  {label}: {m}")
        print(f"  {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return 1 if self.errors else 0


def load_ledger(d):
    p = Path(d) / LEDGER
    if not p.is_file():
        raise SystemExit(f"No {LEDGER} in {d}. Run: dv.py init {d} --title \"...\"")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"{p}: invalid JSON ({e})")


def band_for(rung, mode):
    bands = NEW_BANDS if mode == "new" else REDESIGN_BANDS
    for name, (lo, hi) in bands.items():
        if lo <= rung <= hi:
            return name
    return None


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "design"


# ---------------------------------------------------------------- init / next

def cmd_init(a):
    d = Path(a.dir)
    if d.exists() and any(d.iterdir()):
        if (d / LEDGER).is_file():
            print(f"{d} already holds a variations workspace; continuing it. Use `next` for the next round.")
            return 0
        print(f"Refusing to write into non-empty {d}. Pick a new folder so nothing existing is touched.")
        return 2
    (d / "variants").mkdir(parents=True, exist_ok=True)
    (d / "kit").mkdir(exist_ok=True)
    ledger = {
        "schema": SCHEMA_ID,
        "title": a.title,
        "slug": slugify(a.title),
        "mode": a.mode,
        "host": "html",
        "created": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "subject": {"kind": "screen", "archetype": "", "platform": "web", "source": [], "summary": ""},
        "theme": {"source": "", "summary": ""},
        "round_label": "Turn",
        "chrome": {"theme": a.theme, "tokens": {}},
        "contract": {"must_keep": [], "may_change": [], "lifted": [], "constraints": []},
        "frame": {"w": a.w, "h": a.h},
        "rounds": [],
    }
    (d / LEDGER).write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    (d / "kit" / "kit.html").write_text(
        "<!-- Shared by every prototype: product tokens, fonts, base styles, realistic data and small helpers.\n"
        "     Load only the fonts the product itself loads, so the Now frame looks like the real page. -->\n"
        "<style>\n  :root {\n    /* product tokens go here */\n  }\n  *, *::before, *::after { box-sizing: border-box; }\n"
        "  body { margin: 0; }\n"
        "  /* Hidden means hidden, even when a component's own rule sets display. */\n"
        "  [hidden] { display: none !important; }\n"
        "  /* Visually hidden but announced; clip-based, so it never causes sideways scrolling. */\n"
        "  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; border: 0; }\n"
        "</style>\n<script>\n  window.KIT = {\n    /* shared data (include stress rows: a very long name, many items, an empty optional field) and helpers */\n  };\n</script>\n",
        encoding="utf-8")
    print(f"Created {d} with {LEDGER}, kit/kit.html and variants/. Next: fill the contract, then `dv.py next {d}`.\n"
          f"Later rounds that need new shared helpers or CSS put them in kit/round-<n>.html, so earlier rounds' files stay unchanged.")
    return 0


def cmd_next(a):
    led = load_ledger(a.dir)
    n = max([r.get("n", 0) for r in led.get("rounds", [])] or [0]) + 1
    ids = [f"{n}{LETTERS[i]}" for i in range(min(a.count, 26))]
    print(json.dumps({"round": n, "ids": ids}))
    return 0


# ---------------------------------------------------------------- build

def esc(s):
    return html.escape(str(s or ""), quote=True)


def link_ids(text, known):
    out = esc(text)
    return re.sub(r"\b(\d{1,3}[a-z])\b", lambda m: f'<a href="#{m.group(1)}">{m.group(1)}</a>' if m.group(1) in known else m.group(1), out)


def option_html(o, refs, known):
    oid = o["id"]
    attrs = [f'id="{esc(oid)}"']
    for k in ("rung", "band", "axis"):
        if o.get(k) not in (None, ""):
            attrs.append(f'data-{k}="{esc(o[k])}"')
    for k in ("w", "h"):
        if o.get(k):
            attrs.append(f'data-{k}="{int(o[k])}"')
    if o.get("states"):
        attrs.append(f'data-states="{esc(",".join(str(s) for s in o["states"]))}"')
    role = o.get("role") if isinstance(o.get("role"), str) and o["role"] in ROLES else None
    if role:
        attrs.append(f'data-role="{esc(role)}"')
    meta = []
    if o.get("keeps"):
        meta.append(f"<span><b>Keeps</b> {esc(o['keeps'])}</span>")
    if o.get("changes"):
        meta.append(f"<span><b>Changes</b> {esc(o['changes'])}</span>")
    if o.get("switch_back"):
        meta.append(f"<span><b>Switch back</b> {esc(o['switch_back'])}</span>")
    if o.get("solves"):
        meta.append(f"<span><b>Solves</b> {esc(o['solves'])}</span>")
    if o.get("parents"):
        meta.append("<span><b>From</b> " + ", ".join(link_ids(p, known) for p in o["parents"]) + "</span>")
    seeds, seen_in = [], []
    for rid in o.get("refs", []):
        r = refs.get(rid)
        if not r:
            continue
        label = esc(r.get("title") or r.get("provider") or rid)
        strength = f' <span class="dv-strength">({esc(r["strength"])})</span>' if r.get("strength") else ""
        link = f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{label}</a>{strength}' if r.get("url") else label + strength
        # A reference found after the option was planned corroborates it; it is never shown as the idea's source.
        (seen_in if r.get("use") == "corroborating" else seeds).append(link)
    if seeds:
        meta.append("<span><b>Inspired by</b> " + ", ".join(seeds) + "</span>")
    if seen_in:
        meta.append("<span><b>Also seen in</b> " + ", ".join(seen_in) + "</span>")
    meta_html = f'\n        <p class="dv-meta">{"".join(meta)}</p>' if meta else ""
    desc = o.get("description", "")
    extra = unsaid_cost(desc, o["cost"]) if o.get("cost") else ""
    if extra:
        desc = (desc + " " + extra).strip()
    cls = "dv-option dv-baseline" if o.get("baseline") else "dv-option"
    chip = "Now" if o.get("baseline") else oid
    role_html = f'\n          <span class="dv-role" title="Its role in this round">{esc(ROLES[role])}</span>' if role else ""
    return (
        f'      <article class="{cls}" {" ".join(attrs)} aria-labelledby="{esc(oid)}-name">\n'
        f'        <div class="dv-option-head">\n'
        f'          <span class="dv-chip">{esc(chip)}</span>{role_html}\n'
        f'          <h3 class="dv-name" id="{esc(oid)}-name">{esc(o.get("name", oid))}</h3>\n'
        f'          <p class="dv-desc">{esc(desc)}</p>\n'
        f'        </div>{meta_html}\n'
        f'        <div class="dv-frame"></div>\n'
        f'      </article>\n')


def round_html(r, led, known, newest=False):
    n = r["n"]
    frame = led.get("frame", {})
    w = int(r.get("w") or frame.get("w") or 1440)
    h = int(r.get("h") or frame.get("h") or 900)
    kind = r.get("kind", "explore")
    word = led.get("round_label") or "Turn"
    eyebrow = {"chosen": f"{word} {n} · Chosen", "edit": f"{word} {n} · Edit"}.get(kind, f"{word} {n} · {r.get('topic') or led.get('title', '')}")
    refs = {x.get("id"): x for x in r.get("references", []) if x.get("id")}
    for prev in led.get("rounds", []):
        for x in prev.get("references", []):
            refs.setdefault(x.get("id"), x)
    chosen = ""
    if r.get("degraded"):
        chosen += f'\n      <p class="dv-degraded">{esc(r["degraded"])}</p>'
    if r.get("chosen"):
        chosen += '\n      <p class="dv-chosen-line">Chosen: ' + ", ".join(link_ids(c, known) for c in r["chosen"]) + "</p>"
    opts = "".join(option_html(o, refs, known) for o in r.get("options", []))
    base = led.get("baseline")
    if newest and base and r.get("kind") not in FIXED_KINDS:
        b = {"id": "today", "baseline": True, "band": "today", "name": base.get("name", "Today"),
             "description": base.get("description", "The current design, unchanged, for comparison."),
             "w": base.get("w"), "h": base.get("h"), "states": base.get("states")}
        opts = option_html(b, refs, known) + opts
    return (
        f'  <section class="dv-round" id="round-{n}" data-round="{n}" data-kind="{esc(kind)}" data-w="{w}" data-h="{h}" aria-labelledby="round-{n}-title">\n'
        f'    <div class="dv-round-head">\n'
        f'      <p class="dv-eyebrow">{esc(eyebrow)}</p>\n'
        f'      <h2 id="round-{n}-title">{esc(r.get("title", ""))}</h2>\n'
        f'      <p class="dv-summary">{link_ids(r.get("summary", ""), known)}</p>{chosen}\n'
        f'    </div>\n'
        f'    <div class="dv-options">\n{opts}    </div>\n'
        f'  </section>\n')


def replace_region(text, start, end, new):
    i, j = text.find(start), text.find(end)
    if i < 0 or j < 0 or j < i:
        raise SystemExit(f"Template is missing the {start} … {end} region.")
    return text[: i + len(start)] + "\n" + new + text[j:]


def round_of(oid):
    m = ID_RE.match(str(oid or ""))
    return int(m.group(1)) if m else None


def round_kits(d, rep=None):
    """kit/round-<n>.html files: additions that only round n's frames load, after kit/kit.html. Only the name without
    leading zeros counts; another spelling (round-02.html) is reported and ignored."""
    out = {}
    kd = Path(d) / "kit"
    if kd.is_dir():
        for p in sorted(kd.iterdir()):
            if not p.is_file():
                continue
            m = ROUND_KIT.match(p.name)
            if m:
                out[int(m.group(1))] = p
            elif ROUND_KIT_LOOSE.match(p.name):
                msg = f"kit/{p.name} is ignored; name a round kit kit/round-<n>.html with no leading zeros (kit/round-{int(ROUND_KIT_LOOSE.match(p.name).group(1))}.html)"
                if rep is not None:
                    rep.warn(msg)
                else:
                    print("  WARN: " + msg)
    return out


def write_standalone(sd, variants, kit, rkits, led):
    lang = esc(led.get("lang", "en"))
    for v in variants:
        vid = re.search(r'id="variant-([^"]+)"', v).group(1)
        body = v.split(">", 1)[1].rsplit("</template>", 1)[0]
        extra = rkits.get(round_of(vid), "")
        (sd / f"{vid}.html").write_text(
            f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(vid)} · {esc(led.get("title", ""))}</title>\n{kit}\n{extra}\n</head><body>{body}</body></html>\n', encoding="utf-8")


def cmd_build(a):
    d = Path(a.dir)
    led = load_ledger(d)
    tpl = TEMPLATE.read_text(encoding="utf-8")
    rounds = sorted(led.get("rounds", []), key=lambda r: r.get("n", 0), reverse=True)
    if not rounds:
        print("Ledger has no rounds yet; nothing to build.")
        return 1
    standalone_only = bool(getattr(a, "standalone_dir", None))
    if standalone_only:
        sd = Path(a.standalone_dir).expanduser()
        if sd.exists() and not sd.is_dir():
            print(f"--standalone-dir names a folder for the option pages; {sd} is a file.")
            return 2
        sdr, dr = sd.resolve(), d.resolve()
        if sdr == dr or dr in sdr.parents:
            print(f"Refusing to write standalone pages inside the workspace ({d}); --standalone-dir is for a folder outside it. "
                  f"Use `dv.py build {d} --standalone` for variants-standalone/ inside the workspace.")
            return 2
    known = {o["id"] for r in rounds for o in r.get("options", []) if o.get("id")}
    missing = []
    variants = []
    for r in rounds:
        for o in r.get("options", []):
            p = d / "variants" / f"{o['id']}.html"
            if not p.is_file():
                missing.append(o["id"])
                continue
            body = p.read_text(encoding="utf-8")
            if "</template>" in body.lower():
                raise SystemExit(f"{p} contains </template>; remove it (variants are wrapped in a template).")
            variants.append(f'<template id="variant-{o["id"]}">\n{body.rstrip()}\n</template>\n')
    if led.get("baseline"):
        bp = d / "variants" / "today.html"
        if bp.is_file():
            variants.append(f'<template id="variant-today">\n{bp.read_text(encoding="utf-8").rstrip()}\n</template>\n')
        else:
            missing.append("today")
    kit_p = d / "kit" / "kit.html"
    kit = kit_p.read_text(encoding="utf-8") if kit_p.is_file() else ""
    if "</template>" in kit.lower():
        raise SystemExit(f"{kit_p} contains </template>; remove it.")
    round_ns = {r.get("n") for r in rounds}
    rkits = {}
    for n, p in round_kits(d).items():
        t = p.read_text(encoding="utf-8")
        if "</template>" in t.lower():
            raise SystemExit(f"{p} contains </template>; remove it.")
        if n not in round_ns:
            print(f"  WARN: {p.name} matches no round in the ledger; skipped.")
            continue
        rkits[n] = t
    if standalone_only:
        sd.mkdir(parents=True, exist_ok=True)
        write_standalone(sd, variants, kit, rkits, led)
        print(f"Wrote {len(variants)} standalone page(s) to {sd}. The workspace was not touched; "
              f"run `dv.py build {d}` to rebuild index.html.")
        if missing:
            print("  Missing prototypes: " + ", ".join(missing))
            return 1
        return 0
    out = tpl.replace("__DV_TITLE__", esc(led.get("title", "Design"))).replace("__DV_KEY__", esc(led.get("slug") or slugify(led.get("title", "design"))))
    chrome = led.get("chrome", {})
    theme = chrome.get("theme", "dark")
    out = out.replace('<html lang="en" data-theme="dark">', f'<html lang="{esc(led.get("lang", "en"))}" data-theme="{esc(theme)}">', 1)
    toks = chrome.get("tokens", {})
    lines = "".join(f"  {k}: {v};\n" for k, v in toks.items() if re.match(r"^--dv-[a-z0-9-]+$", k) and not re.search(r"[;{}<>]", str(v)))
    if "/* DV:OVERRIDES */" in out:
        out = out.replace("/* DV:OVERRIDES */", lines or "/* none */")
    elif lines:
        i = out.find("/* DV:TOKENS:END */")
        out = out[:i] + lines + "  " + out[i:]
    out = replace_region(out, "<!-- DV:ROUNDS:START -->", "<!-- DV:ROUNDS:END -->", "".join(round_html(r, led, known, i == 0) for i, r in enumerate(rounds)))
    kit_region = f'<template id="dv-kit">\n{kit.rstrip()}\n</template>\n'
    kit_region += "".join(f'<template id="dv-kit-round-{n}">\n{t.rstrip()}\n</template>\n' for n, t in sorted(rkits.items()))
    out = replace_region(out, "<!-- DV:KIT:START -->", "<!-- DV:KIT:END -->", kit_region)
    out = replace_region(out, "<!-- DV:VARIANTS:START -->", "<!-- DV:VARIANTS:END -->", "".join(variants))
    embedded = json.dumps(led, ensure_ascii=False).replace("</", "<\\/")
    cut = out.rfind("</body>")
    out = out[:cut] + f'<script type="application/json" id="dv-ledger">{embedded}</script>\n' + out[cut:]
    target = d / (a.out or "index.html")
    target.write_text(out, encoding="utf-8")
    if getattr(a, "standalone", False):
        sd = d / "variants-standalone"; sd.mkdir(exist_ok=True)
        write_standalone(sd, variants, kit, rkits, led)
        print(f"  Wrote {len(variants)} standalone page(s) to {sd}")
    size = target.stat().st_size
    print(f"Built {target} ({size/1024:.0f} KB): {len(rounds)} round(s), {len(variants)} prototype(s).")
    if rkits:
        print("  Round kits: " + ", ".join(f"kit/round-{n}.html → round {n} frames only" for n in sorted(rkits)))
    if missing:
        print("  Missing prototypes (their frames will say so): " + ", ".join(missing))
        return 1
    if size > 15 * 1024 * 1024:
        print("  WARN: over 15 MB; artifact hosts cap pages near 16 MB.")
    return 0


# ---------------------------------------------------------------- check

def check_round_spread(r, mode, rep):
    opts = r.get("options", [])
    n = r.get("n")
    kind = r.get("kind", "explore")
    dist = r.get("distribution", "default")
    count = len(opts)
    rungs = [o.get("rung") for o in opts]
    strict = kind in ("explore", "more")
    say = rep.err if strict else rep.warn
    if dist not in DISTRIBUTIONS:
        rep.warn(f"round {n}: distribution {dist!r} is not one of {sorted(DISTRIBUTIONS)}")
    if any(not isinstance(x, int) or not 1 <= x <= 10 for x in rungs):
        rep.err(f"round {n}: every option needs an integer rung 1–10")
        return
    if rungs != sorted(rungs):
        say(f"round {n}: order options a→j from the smallest change to the most radical (rungs {rungs})")
    bands = NEW_BANDS if mode == "new" else REDESIGN_BANDS
    if strict and dist == "default" and count >= 4:
        for name, (lo, hi) in bands.items():
            if not any(lo <= x <= hi for x in rungs):
                say(f"round {n}: no option in the {name} band (rungs {lo}–{hi}); the spread must run from small tweaks to radical")
    if strict and dist == "default" and count >= 2 and (min(rungs) > 3 or max(rungs) < 9):
        say(f"round {n}: rungs span {min(rungs)}–{max(rungs)}; include at least one rung ≤3 and one ≥9")
    if strict and dist == "closer" and min(rungs) > 3:
        say(f"round {n}: a 'closer' round still needs refinements (rung ≤3)")
    if strict and dist == "bolder" and max(rungs) < 9:
        say(f"round {n}: a 'bolder' round needs at least one option at rung 9 or 10")
    pairs = [(o.get("rung"), norm_axis(o.get("axis"))) for o in opts]
    dup = {p for p in pairs if pairs.count(p) > 1 and p[1]}
    if dup:
        say(f"round {n}: options share the same rung and primary axis {sorted(dup)}; give each a different position")
    axes = {norm_axis(o.get("axis")) for o in opts if o.get("axis")}
    from collections import Counter
    for ax, k in Counter(norm_axis(o.get("axis")) for o in opts if o.get("axis")).items():
        if k > 1 and kind not in ("refine",):
            same = [o for o in opts if norm_axis(o.get("axis")) == ax]
            pars = {(o.get("paradigm") or "").lower() for o in same}
            if len(pars) < len(same):
                rep.warn(f"round {n}: {k} options lead on {ax} with the same paradigm; make them differ or replace one")
            elif not r.get("degraded"):
                rep.note(f"round {n}: {k} options lead on {ax}; note the overlap in the degraded line and the reply")
    need_axes = min(6, max(1, round(count * 0.6)))
    if kind not in ("refine",) and len(axes) < need_axes:
        rep.warn(f"round {n}: only {len(axes)} distinct primary axes across {count} options (aim for {need_axes}); options may read as tints of one idea")
    paradigms = {(o.get("paradigm") or "").strip().lower() for o in opts if (o.get("rung") or 0) >= 4 and o.get("paradigm")}
    need_par = min(3, count // 3)
    if strict and dist in ("default", "bolder", "only-radical") and need_par and len(paradigms) < need_par:
        rep.warn(f"round {n}: only {len(paradigms)} distinct paradigms among Evolve-and-above options (aim for {need_par})")
    for o in opts:
        b = o.get("band")
        if b and b in ALL_BANDS and isinstance(o.get("rung"), int):
            lo, hi = ALL_BANDS[b]
            if not lo <= o["rung"] <= hi:
                rep.warn(f"{o['id']}: band {b} does not match rung {o['rung']}")


def norm_axis(a):
    return re.sub(r"[\s_]+", "-", (a or "").strip().lower()).replace("color", "colour")


def calls_kit_helper(text, kit_text=""):
    """True when the fragment calls a kit helper: KIT.x(…), or an alias such as `const K = KIT, R = K.r2; R.wire(…)`."""
    names = {"KIT"}
    grew = True
    while grew:
        grew = False
        for m in re.finditer(r"\b([A-Za-z_$][\w$]*)\s*=\s*(?:window\.)?([A-Za-z_$][\w$]*)\b", text):
            if m.group(2) in names and m.group(1) not in names:
                names.add(m.group(1)); grew = True
        for m in re.finditer(r"\{([^{}]*)\}\s*=\s*(?:window\.)?([A-Za-z_$][\w$]*)\b", text):
            if m.group(2) in names:
                for part in m.group(1).split(","):
                    nm = part.split("=")[0].split(":")[-1].strip()
                    if re.match(r"^[A-Za-z_$][\w$]*$", nm) and nm not in names:
                        names.add(nm); grew = True
    alt = "|".join(re.escape(x) for x in sorted(names, key=len, reverse=True))
    wiring = kit_wiring_names(kit_text)
    wires = lambda nm: bool(WIRING_NAME.match(nm)) or nm in wiring
    for m in re.finditer(rf"(?<![\w$.])(?:{alt})((?:\.[A-Za-z_$][\w$]*)+)\s*\(", text):
        if wires(m.group(1).rsplit(".", 1)[-1]):
            return True
    plain = [x for x in names if x != "KIT" and wires(x)]
    return bool(plain) and bool(re.search(rf"(?<![\w$.])(?:{'|'.join(re.escape(x) for x in plain)})\s*\(", text))


WIRING_NAME = re.compile(r"^(wire|bind|on[A-Z_]|on$|listen|attach|mount|init|setup|hook|delegate|enhance|handle)", re.I)


def kit_wiring_names(kit_text):
    """Helper names the kit defines in a function that wires events (addEventListener, on… handlers)."""
    out = set()
    defs = list(re.finditer(r"(?:\.|\b)([A-Za-z_$][\w$]*)\s*[:=]\s*(?:function\b|\([^)]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)|\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", kit_text or ""))
    for i, m in enumerate(defs):
        end = defs[i + 1].start() if i + 1 < len(defs) else len(kit_text)
        if re.search(r"addEventListener|\.on[a-z]+\s*=", kit_text[m.end(): min(end, m.end() + 4000)]):
            out.add(m.group(1) or m.group(2))
    return out


def check_variant_file(oid, p, rep, kit_text=""):
    text = p.read_text(encoding="utf-8")
    low = text.lower()
    if len(text.strip()) < 400:
        rep.warn(f"{oid}: prototype is very small ({len(text)} chars); is it a real, full surface?")
    if not INTERACTIVE.search(text):
        rep.err(f"{oid}: no interactive elements (button, input, select, link, tabindex); prototypes must be interactive")
    # Handlers wired by a shared kit helper count: the skill asks builders to put shared components in the kit.
    if not BEHAVIOUR.search(text) and not (BEHAVIOUR.search(kit_text) and calls_kit_helper(text, kit_text)):
        rep.warn(f"{oid}: no event handlers found; controls may look interactive but do nothing")
    m = PLACEHOLDER.search(text)
    if m:
        rep.err(f"{oid}: placeholder content ({m.group(0)!r}); use realistic content")
    if EMOJI.search(text):
        rep.warn(f"{oid}: emoji found; use the product's icons or inline SVG unless the brand uses emoji")
    for host in {h.lower() for _, h in EXTERNAL.findall(text)}:
        if not host.endswith(ALLOWED_HOSTS):
            rep.warn(f"{oid}: loads from {host}; prototypes should work offline (allowed CDNs: {', '.join(ALLOWED_HOSTS)})")
    if "</template>" in low:
        rep.err(f"{oid}: contains </template>")
    if re.search(r"<!doctype|<html\b|<head\b|<body\b", low):
        rep.warn(f"{oid}: variant files are fragments; drop <!doctype>/<html>/<head>/<body> (the gallery adds them)")
    if re.search(r"\bdocument\.write\(|\btop\.|\bparent\.(?!postMessage)", text):
        rep.warn(f"{oid}: reaches outside its frame (document.write/top/parent); keep prototypes self-contained")


def inventory(insp, n, rep):
    """Connected and troubled providers, from the legacy lists and inspiration.connections.

    A provider counts as connected when any of its connections is used or connected-unused, so a copy that needs
    sign-in beside a working copy is not a degradation."""
    by = {}
    for i, c in enumerate(insp.get("connections") or []):
        if not isinstance(c, dict) or not c.get("provider"):
            rep.warn(f"round {n}: inspiration.connections[{i}] needs provider, via and status")
            continue
        if not c.get("via"):
            rep.warn(f"round {n}: connection {c['provider']} has no 'via'; say how it was reached (claude.ai connector, plugin server …) so two copies can be told apart")
        st = c.get("status")
        if not isinstance(st, str) or st not in CONN_STATUS:
            rep.warn(f"round {n}: connection {c['provider']} via {c.get('via') or '?'} has status {st!r}; use one of {', '.join(sorted(CONN_STATUS))}")
            st = None
        by.setdefault(str(c["provider"]).lower(), set()).add(st)
    listed = lambda k: {str(x).lower() for x in (insp.get(k) or [])}
    connected = listed("connected") | {p for p, ss in by.items() if ss & WORKING}
    troubled = (listed("needs_signin") | listed("failed") | {p for p, ss in by.items() if ss & {"needs-signin", "failed"}}) - connected
    # Searched, answered, nothing fit: recorded honestly, so it needs a degraded line rather than a forced reference.
    # The connections record wins over the older `connected` list, which cannot say whether a provider was used.
    unused = {p for p, ss in by.items() if "connected-unused" in ss and "used" not in ss}
    return connected, troubled, by, unused


def check_index_boot(idx, rep):
    """The gallery boots only when its runtime script is intact and the ledger JSON sits after it, once."""
    text = idx.read_text(encoding="utf-8", errors="replace")
    scripts = [(m.start(), m.end(), m.group(1), m.group(2)) for m in SCRIPT_TAG.finditer(text)]
    ledgers = [s for s in scripts if re.search(r"""\bid\s*=\s*["']?dv-ledger\b""", s[2])]
    runtimes = [s for s in scripts if "application/json" not in s[2].lower() and re.search(r"window\.DV_GALLERY\s*=", s[3])]
    starts = {s[0] for s in scripts}
    nested = [m.start() for m in re.finditer(r"""<script\b[^>]*\bid\s*=\s*["']?dv-ledger\b""", text, re.I) if m.start() not in starts]
    if nested:
        rep.err("index.html: the dv-ledger JSON was written inside another script, which cuts the gallery runtime short so it cannot boot; rebuild with `dv.py build` and never hand-patch it")
    if not runtimes:
        rep.err("index.html: the gallery runtime is broken or missing (no script defines window.DV_GALLERY), so the gallery cannot boot; rebuild with `dv.py build` and never hand-patch it")
    if nested:
        return
    if len(ledgers) != 1:
        rep.err(f"index.html: {len(ledgers)} dv-ledger JSON scripts (exactly one belongs after the gallery runtime); rebuild with `dv.py build`")
    elif runtimes and ledgers[0][0] < runtimes[-1][1]:
        rep.err("index.html: the dv-ledger JSON sits before or inside the gallery runtime script; rebuild with `dv.py build`")
    else:
        try:
            json.loads(ledgers[0][3])
        except json.JSONDecodeError as e:
            rep.err(f"index.html: the dv-ledger script is not valid JSON ({e}); rebuild with `dv.py build`")


def norm_trait(v):
    return re.sub(r"\s+", " ", str(v or "")).strip().lower()


def cmd_check(a):
    d = Path(a.dir)
    rep = Report()
    led = load_ledger(d)
    if led.get("schema") != SCHEMA_ID:
        rep.err(f"schema must be {SCHEMA_ID!r}")
    mode = led.get("mode")
    if mode not in ("redesign", "new"):
        rep.err("mode must be 'redesign' or 'new'")
    if not led.get("title"):
        rep.err("title is empty")
    c = led.get("contract", {})
    if mode == "redesign" and not c.get("must_keep"):
        rep.err("redesign without contract.must_keep; list the functions, data and brand elements every option keeps")
    rounds = led.get("rounds", [])
    host = led.get("host", "html")
    files_here = host == "html"
    if not rounds:
        rep.warn("no rounds yet")
    ns = sorted(r.get("n") for r in rounds if isinstance(r.get("n"), int))
    newest_n = ns[-1] if ns else None
    kit_p = d / "kit" / "kit.html"
    kit_text = kit_p.read_text(encoding="utf-8") if kit_p.is_file() else ""
    rkit_text = {}
    for k, p in round_kits(d, rep).items():
        rkit_text[k] = p.read_text(encoding="utf-8")
        if k not in ns:
            rep.warn(f"kit/{p.name} matches no round in the ledger; the build skips it")
        if "</template>" in rkit_text[k].lower():
            rep.err(f"kit/{p.name} contains </template>")
    kit_for = lambda oid: kit_text + "\n" + rkit_text.get(round_of(oid), "")
    if mode == "redesign" and not led.get("baseline"):
        rep.warn("no baseline: redesigns show today's design as the Now frame (\"baseline\": {\"name\": \"Today\"} and variants/today.html)")
    if files_here and led.get("baseline") and not (d / "variants" / "today.html").is_file():
        rep.err("baseline declared but variants/today.html is missing")
    if files_here and led.get("baseline") and (d / "variants" / "today.html").is_file():
        check_variant_file("today", d / "variants" / "today.html", rep, kit_text)
    for i, pref in enumerate(led.get("preferences", [])):
        if not isinstance(pref, dict) or not pref.get("trait") or pref.get("kind") not in ("like", "dislike", "constraint"):
            rep.warn(f"preferences[{i}]: needs kind (like, dislike or constraint) and trait")
    seen_ids, seen_n = set(), set()
    must_keep = c.get("must_keep", [])
    all_opts = {o.get("id"): o for rr in rounds for o in rr.get("options", []) if o.get("id")}
    for r in rounds:
        kind = r.get("kind", "explore")
        n = r.get("n")
        live = kind not in FIXED_KINDS
        newest = n == newest_n
        gaps = Counter()

        # Field rules added after a round was shown apply to the newest round only; older rounds get one note.
        def soft(msg, field, k=1):
            if newest:
                rep.warn(msg)
            else:
                gaps[field] += k

        def hard(msg, field, k=1):
            if newest:
                rep.err(msg)
            else:
                gaps[field] += k

        insp = r.get("inspiration")
        refs = r.get("references", [])
        if live:
            connected, troubled = set(), set()
            if not isinstance(insp, dict):
                rep.warn(f"round {n}: record the inspiration inventory (connected, needs_signin, absent, queries)")
            else:
                connected, troubled, by, unused = inventory(insp, n, rep)
                used = {str(x.get("provider") or "").lower() for x in refs}
                libs = connected - DESIGN_CONTEXT
                if libs and not (used & libs):
                    if libs - unused:
                        rep.err(f"round {n}: {', '.join(sorted(libs - unused))} connected but no reference comes from it; the inspiration step is required when a library is connected")
                    elif not r.get("degraded"):
                        soft(f"round {n}: {', '.join(sorted(libs & unused))} answered but gave nothing this round used; say so in a degraded line", "degraded line")
                for p, ss in sorted(by.items()):
                    if "used" in ss and p not in used:
                        rep.warn(f"round {n}: {p} is marked used but no reference comes from it")
                for x in refs:
                    p = (x.get("provider") or "").lower()
                    if p in by and p not in connected:
                        rep.warn(f"round {n}: reference {x.get('id')} comes from {p}, but no connection to {p} is recorded as used; record the one that answered")
            if not refs:
                rep.warn(f"round {n}: no references recorded; say which fallback was used")
            if isinstance(insp, dict) and not (connected - DESIGN_CONTEXT) and not r.get("degraded"):
                soft(f"round {n}: no inspiration library was connected (design-context servers such as Figma do not count); add a degraded line saying which fallback the references came from", "degraded line")
            elif (troubled - DESIGN_CONTEXT) and not r.get("degraded"):
                soft(f"round {n}: {', '.join(sorted(troubled - DESIGN_CONTEXT))} needed sign-in or failed and no working copy is recorded; add a degraded line", "degraded line")
            elif refs and all((x.get("provider") or "") == "knowledge" for x in refs):
                rep.note(f"round {n}: every reference is model knowledge; label it so in the reply")
        if not isinstance(n, int) or n in seen_n:
            rep.err(f"round number {n!r} missing or repeated")
        seen_n.add(n)
        if r.get("kind", "explore") not in KINDS:
            rep.err(f"round {n}: kind must be one of {sorted(KINDS)}")
        for k in ("title", "summary"):
            if not r.get(k):
                rep.err(f"round {n}: {k} is empty")
        if kind == "edit" and (len(r.get("options", [])) != 1 or r.get("chosen")):
            rep.err(f"round {n}: an edit round holds exactly one option and never sets chosen")
        if r.get("kind") in ("like", "combine", "refine", "feedback", "scope", "edit") and not (r.get("basis") or r.get("feedback")):
            rep.warn(f"round {n}: record the user's feedback or the basis options this round builds on")
        opts = r.get("options", [])
        if not opts:
            rep.err(f"round {n}: no options")
        known_refs = {x.get("id"): x for x in refs if x.get("id")}
        for rr in rounds:
            for x in rr.get("references", []):
                known_refs.setdefault(x.get("id"), x)
        letters, no_plane, no_traits, multi, no_role = [], [], [], [], []
        for o in opts:
            oid = o.get("id", "")
            rung = o.get("rung") if isinstance(o.get("rung"), int) else 0
            m = ID_RE.match(oid)
            if not m or int(m.group(1)) != n:
                rep.err(f"round {n}: option id {oid!r} must be the round number plus a letter (e.g. {n}a)")
            else:
                letters.append(m.group(2))
            if oid in seen_ids:
                rep.err(f"{oid}: id reused; ids are permanent across rounds")
            seen_ids.add(oid)
            name = (o.get("name") or "").strip()
            if not name or GENERIC_NAME.match(name):
                rep.err(f"{oid}: name {name!r} must say the idea in 2–4 words, never 'Option C'")
            elif len(name.split()) > 6:
                rep.warn(f"{oid}: name is long ({len(name.split())} words); aim for 2–4")
            if not o.get("description"):
                rep.err(f"{oid}: description is empty (one plain sentence about what the option is; the cost goes in 'cost')")
            elif sentence_count(o["description"]) > 1:
                multi.append(oid)
            if o.get("cost") and o.get("description") and unsaid_cost(o["description"], o["cost"]) != o["cost"].strip():
                soft(f"{oid}: the description repeats (part of) the cost; keep the cost only in 'cost' (the build leaves out what the description already says)", "cost repeated in description")
            if not o.get("axis") and live:
                rep.warn(f"{oid}: no primary axis recorded")
            elif o.get("axis") and norm_axis(o["axis"]) not in AXES:
                rep.warn(f"{oid}: axis {o['axis']!r} is not one of the canonical slugs in variation-axes.md")
            if live and rung >= 7 and not o.get("solves"):
                soft(f"{oid}: Rethink and Reinvent options state the user problem they solve ('solves')", "solves")
            seeds = [x for x in o.get("refs", []) if (known_refs.get(x) or {}).get("use") != "corroborating"]
            if live and rung >= 7 and not seeds:
                why = "; corroborating references do not count as seeds" if o.get("refs") else ""
                rep.warn(f"{oid}: a Rethink or Reinvent option with no reference seed; record what it borrows, or label it exploratory{why}")
            plane = o.get("plane")
            if plane:
                if not isinstance(plane, str) or plane not in PLANES:
                    rep.warn(f"{oid}: plane {plane!r} is not one of {', '.join(PLANES)}")
                elif rung and not PLANES[plane][0] <= rung <= PLANES[plane][1]:
                    lo, hi = PLANES[plane]
                    rep.err(f"{oid}: rung {rung} is outside the {plane} plane (rungs {lo}–{hi}); re-place the option by the plane test or replace it, never relabel it to fill a slot")
            elif live and mode == "redesign" and rung >= 4:
                no_plane.append(oid)
            if live and rung >= 9 and not o.get("switch_back"):
                if mode == "redesign":
                    hard(f"{oid}: rung {rung} needs a way back to the familiar view inside the prototype; build it and say how in 'switch_back'", "switch_back")
                else:
                    soft(f"{oid}: rung {rung} with no 'switch_back'; offer one click to a plain view of the same facts", "switch_back")
            tr = o.get("traits")
            if live and rung >= 7 and not (isinstance(tr, dict) and all(norm_trait(tr.get(k)) for k in TRAIT_KEYS)):
                no_traits.append(oid)
            if o.get("role") and (not isinstance(o["role"], str) or o["role"] not in ROLES):
                rep.warn(f"{oid}: role {o['role']!r} is not one of {', '.join(ROLES)}")
            if kind in ROLE_KINDS and not o.get("role"):
                no_role.append(oid)
            if mode == "redesign" and live and rung >= 4 and must_keep:
                mapped = o.get("contract")
                if not isinstance(mapped, list):
                    rep.err(f"{oid}: map every must-keep item to where it lives in this option (option.contract)")
                else:
                    have = {str(mp.get("item")).strip().lower() for mp in mapped if isinstance(mp, dict)}
                    missing = [] if "*" in have else [k for i, k in enumerate(must_keep) if str(i) not in have and str(k).strip().lower() not in have]
                    if missing:
                        rep.err(f"{oid}: contract items not mapped: {missing[:3]}{' …' if len(missing) > 3 else ''}")
            if live and not o.get("cost") and not re.search(r"\bcost|\bloses?\b|\bfewer\b|\bless\b|\bslower\b|\bneeds?\b|\btakes?\b", o.get("description", ""), re.I):
                rep.warn(f"{oid}: no cost stated (put it in 'cost'; build appends it to the description)")
            if mode == "redesign" and live and not (o.get("keeps") and o.get("changes")):
                rep.warn(f"{oid}: record keeps and changes so the contract check is visible")
            for p in o.get("parents", []):
                if p not in seen_ids and p not in all_opts:
                    rep.err(f"{oid}: parent {p} does not exist")
            if files_here and not o.get("file"):
                vp = d / "variants" / f"{oid}.html"
                if not vp.is_file():
                    rep.err(f"{oid}: missing variants/{oid}.html")
                else:
                    check_variant_file(oid, vp, rep, kit_for(oid))
            elif o.get("file") and not (d / o["file"]).exists():
                rep.warn(f"{oid}: file {o['file']} not found relative to the ledger")
        if letters and letters != [LETTERS[i] for i in range(len(letters))]:
            rep.err(f"round {n}: letters must run a, b, c … in order (got {''.join(letters)})")
        if no_plane:
            soft(f"round {n}: no plane on {', '.join(no_plane)}; record the deepest plane each option touches (surface, skeleton, structure or scope) so its rung can be checked", "plane", len(no_plane))
        if no_traits:
            soft(f"round {n}: no traits (skeleton, device, interaction, moment) on {', '.join(no_traits)}; record them so the shared-traits cap can be checked", "traits", len(no_traits))
        if multi:
            soft(f"round {n}: descriptions of {', '.join(multi)} run past one sentence; say what the option is in one sentence and keep the cost in 'cost'", "one-sentence description", len(multi))
        if no_role:
            soft(f"round {n}: no role on {', '.join(no_role)}; record refine, push, crossover, secondary or wildcard so the gallery shows it", "role", len(no_role))
        if kind == "like" and len(opts) >= 5 and not any(o.get("role") == "wildcard" for o in opts):
            hard(f"round {n}: a like round of {len(opts)} options needs at least one wildcard (role 'wildcard') so the exploration does not converge too early", "wildcard")
        if live:
            bold = [o for o in opts if isinstance(o.get("rung"), int) and o["rung"] >= 7 and isinstance(o.get("traits"), dict)]
            for i, x in enumerate(bold):
                for y in bold[i + 1:]:
                    same = [k for k in TRAIT_KEYS if norm_trait(x["traits"].get(k)) and norm_trait(x["traits"].get(k)) == norm_trait(y["traits"].get(k))]
                    if len(same) > 1:
                        soft(f"{x.get('id')} and {y.get('id')} share {len(same)} traits ({', '.join(same)}); Rethink and Reinvent options share at most one of skeleton, device, interaction and moment", "shared traits")
        unsigned = []
        for pid in r.get("passed") or []:
            if pid not in all_opts:
                rep.warn(f"round {n}: passed option {pid} does not exist")
            elif not all_opts[pid].get("signature"):
                unsigned.append(pid)
        if unsigned:
            soft(f"round {n}: passed option(s) {', '.join(unsigned)} have no 'signature'; name each one's signature device in a line so later rounds (and dv.py novelty) can avoid it", "signature", len(unsigned))
        if live:
            check_round_spread(r, mode, rep)
            if len(opts) != r.get("count", 10) and not r.get("count"):
                rep.note(f"round {n}: {len(opts)} options (default is 10; record 'count' when the user asked for another number)")
        for ref in r.get("references", []):
            if not ref.get("url") and ref.get("provider") not in ("user", "knowledge", "screenshot", "capture"):
                rep.warn(f"round {n}: reference {ref.get('id')} has no link to cite")
            if ref.get("provider") == "knowledge" and ref.get("url"):
                rep.err(f"round {n}: reference {ref.get('id')} is model knowledge but carries a link; knowledge references never get links")
            if ref.get("strength") and ref["strength"] not in ("precedent", "example", "craft judgement", "exploratory"):
                rep.warn(f"round {n}: reference {ref.get('id')} strength should be precedent, example, craft judgement or exploratory")
            if ref.get("use") and (not isinstance(ref["use"], str) or ref["use"] not in REF_USES):
                rep.warn(f"round {n}: reference {ref.get('id')} use should be seed or corroborating")
        if gaps:
            said = ", ".join(f"{k} ×{v}" if v > 1 else k for k, v in gaps.items())
            rep.note(f"round {n}: newer field rules apply to round {newest_n} only, so these gaps are not reported ({said}). "
                     f"Ledger metadata may be backfilled; shown variant files never change.")
    idx = d / "index.html"
    if not files_here:
        pass
    elif idx.is_file():
        newest_src = max([p.stat().st_mtime for p in [d / LEDGER, *(d / "variants").glob("*.html"), *(d / "kit").glob("*")] if p.exists()] or [0])
        if idx.stat().st_mtime < newest_src:
            rep.warn("index.html is older than its sources; run `dv.py build`")
        check_index_boot(idx, rep)
    else:
        rep.note("no index.html yet; run `dv.py build`")
    if not files_here:
        rep.note(f"host is {host}: prototype files are checked by lint-dc or the project's own tools, not here")
    code = rep.emit(f"check {d}")
    if a.strict and rep.warnings:
        return 1
    return code


# ---------------------------------------------------------------- novelty

WORD = re.compile(r"[a-z0-9]+")
STOP = set("a an the and or of to in on for with by at from as is are be this that it its into over under same new more less one two".split())


def toks(s):
    return {w for w in WORD.findall((s or "").lower()) if w not in STOP and len(w) > 2}


def jacc(x, y):
    return len(x & y) / len(x | y) if x and y else 0.0


FUNCTION_WORDS = STOP | set("about all also any but can each every has have just not only onto our per than their them then they very via was what when where which while who will with you your".split())


def stem(w):
    """A deliberately small stemmer: reminders/reminder/remind and leading/lead compare equal."""
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    for suf in ("ing", "ed", "er", "e"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def content_words(s):
    return {stem(w) for w in WORD.findall((s or "").lower()) if w not in FUNCTION_WORDS and len(w) > 2}


def coverage(of, by):
    """Share of the content words of `of` that also appear in `by`."""
    a = content_words(of)
    return len(a & content_words(by)) / len(a) if a else 0.0


def dice(a, b):
    return 2 * len(a & b) / (len(a) + len(b)) if a and b else 0.0


def split_sentences(s):
    """Sentences in s. After . ! ? a new sentence starts with a capital letter in any script, a digit or a currency
    sign; a CJK full stop always ends one."""
    s = (s or "").strip()
    out, start = [], 0
    for m in SENTENCE_END.finditer(s):
        if m.group(1):
            nxt = s[m.end():].lstrip("\"'“‘([")[:1]
            caseless = nxt.isalpha() and not nxt.islower() and not nxt.isupper()  # e.g. CJK
            if not (nxt.isupper() or caseless or nxt.isdigit() or (nxt and nxt in "£$€")):
                continue
            prev = re.search(r"(\S+)$", s[: m.start(1)])
            word = prev.group(1).lower().lstrip("(\"'") if prev else ""
            if m.group(1) == "." and (word in ABBREV or re.fullmatch(r"[a-z]", word)):
                continue
            out.append(s[start: m.end(1)])
        else:
            out.append(s[start: m.end(2)])
        start = m.end()
    out.append(s[start:])
    return [x for x in out if x.strip()]


def sentence_count(s):
    return len(split_sentences(s))


def restates(desc, cost):
    """True when the description already says this cost: as whole words, or with nearly all its content words."""
    core = (cost or "").strip().rstrip(". ").lower()
    if not core:
        return False
    if re.search(r"(?<!\w)" + re.escape(core) + r"(?!\w)", (desc or "").lower()) or coverage(cost, desc) >= 0.75:
        return True
    cw = content_words(cost)
    return any(dice(cw, content_words(x)) >= 0.55 for x in split_sentences(desc))


def cost_clauses(cost):
    return [c.strip() for c in re.split(r";\s*|(?<=[.!?])\s+", (cost or "").strip()) if c.strip()]


def unsaid_cost(desc, cost):
    """The part of the cost the description does not already say: all of it, some clauses, or nothing."""
    clauses = cost_clauses(cost)
    keep = [c for c in clauses if not restates(desc, c)]
    if len(keep) == len(clauses):
        return (cost or "").strip()
    if not keep:
        return ""
    text = "; ".join(c.rstrip(".;").strip() for c in keep) + "."
    return text[0].upper() + text[1:]


def cmd_novelty(a):
    led = load_ledger(a.dir)
    rounds = sorted(led.get("rounds", []), key=lambda r: r.get("n", 0))
    if not rounds:
        print("no rounds")
        return 1
    target = next((r for r in rounds if r.get("n") == a.round), rounds[-1]) if a.round else rounds[-1]
    prior = [o for r in rounds if r.get("n", 0) < target.get("n", 0) for o in r.get("options") or []]
    passed = {pid for r in rounds for pid in r.get("passed") or []}
    rep = Report()
    unsigned = sorted(p["id"] for p in prior if p.get("id") in passed and not p.get("signature"))
    if unsigned:
        rep.note(f"passed option(s) {', '.join(unsigned)} have no signature; only their labels were compared")
    for o in target.get("options") or []:
        t_name, t_idea = toks(o.get("name")), toks(" ".join([o.get("idea") or "", o.get("description") or "", o.get("paradigm") or ""]))
        tags = {x.lower() for x in o.get("tags") or []}
        own = " ".join([o.get("idea") or "", o.get("description") or "", o.get("signature") or ""])
        for p in prior:
            if p.get("id") in (o.get("parents") or []):
                continue
            if p.get("id") in passed and p.get("signature"):
                share = coverage(p["signature"], own)
                if share >= 0.6:
                    rep.warn(f"{o['id']} repeats the signature of {p['id']} ({p.get('name')}), which the user passed on: "
                             f"{share:.0%} of '{p['signature']}'; drop that device, or say why the user asked for it back")
            same_shape = (o.get("paradigm") and o.get("paradigm") == p.get("paradigm") and (o.get("axis") or "") == (p.get("axis") or ""))
            sim = max(jacc(t_name, toks(p.get("name"))), jacc(t_idea, toks(" ".join([p.get("idea") or "", p.get("description") or "", p.get("paradigm") or ""]))))
            tag_overlap = jacc(tags, {x.lower() for x in p.get("tags") or []}) if tags else 0
            if same_shape or sim >= 0.5 or tag_overlap >= 0.75:
                why = "same paradigm and axis" if same_shape else (f"text overlap {sim:.2f}" if sim >= 0.5 else f"tag overlap {tag_overlap:.2f}")
                if p.get("id") in passed:
                    rep.err(f"{o['id']} resembles {p['id']} ({p.get('name')}), which the user passed on: {why}")
                else:
                    (rep.err if target.get("kind") == "more" else rep.warn)(f"{o['id']} resembles {p['id']} ({p.get('name')}): {why}")
    if target.get("kind") == "more":
        rep.note("kind 'more' asks for directions unlike anything shown so far; resemblances are errors")
    return rep.emit(f"novelty round {target.get('n')} vs {len(prior)} earlier option(s)")


# ---------------------------------------------------------------- lint-dc

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HOLE = re.compile(r"\{\{(.*?)\}\}", re.S)
PATH_OK = re.compile(r"^\s*(?:[A-Za-z_$][\w$]*(?:\.[\w$]+)*|true|false|null|-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\")\s*$")


class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        if tag in ("dc-import", "x-import", "sc-if", "sc-for", "div", "span"):
            self.problems.append(f"line {self.getpos()[0]}: <{tag} … /> is self-closed; write <{tag} …></{tag}>")

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for t, ln in self.stack[i + 1:]:
                    self.problems.append(f"line {ln}: <{t}> is never closed")
                del self.stack[i:]
                return
        self.problems.append(f"line {self.getpos()[0]}: stray </{tag}>")


def lint_dc_file(p, rep, root):
    raw = p.read_text(encoding="utf-8")
    name = str(p.relative_to(root)) if root in p.parents else p.name
    if '<script src="./support.js"></script>' not in raw and not re.search(r'<script src="(\.\./)+support\.js"></script>', raw):
        rep.err(f'{name}: the head line <script src="./support.js"></script> is missing or altered')
    if raw.count("<x-dc>") != 1 or raw.count("</x-dc>") != 1:
        rep.err(f"{name}: needs exactly one <x-dc> … </x-dc>")
    sm = re.search(r"<script type=\"text/x-dc\" data-dc-script([^>]*)>(.*?)</script>", raw, re.S)
    if not sm:
        rep.err(f'{name}: missing <script type="text/x-dc" data-dc-script> block')
        logic, attrs = "", ""
    else:
        attrs, logic = sm.group(1), sm.group(2)
        if "class Component extends DCLogic" not in logic:
            rep.err(f"{name}: logic must define class Component extends DCLogic")
        if re.search(r"^\s*(import|export)\s", logic, re.M):
            rep.err(f"{name}: no import/export in the logic block (classic JS only)")
        for bad in ("innerHTML", "appendChild", "document.createElement", "insertAdjacentHTML"):
            if bad in logic:
                rep.err(f"{name}: {bad} in logic; all UI is <x-dc> markup, never script-built")
        if re.search(r"(window|document)\.addEventListener\(\s*['\"]key(down|up|press)", logic):
            rep.err(f"{name}: global keyboard handler; bind keys on elements instead")
        if re.search(r"\brender\s*\(\s*\)\s*\{", logic):
            rep.warn(f"{name}: defines render(); DCLogic uses renderVals()")
        pm = re.search(r"data-props='(.*?)'", attrs, re.S)
        if not pm and 'data-props="' in attrs:
            rep.warn(f"{name}: single-quote the data-props attribute (double quotes change which characters need escaping)")
            pm = re.search(r'data-props="(.*?)"', attrs, re.S)
        if pm:
            try:
                props = json.loads(html.unescape(pm.group(1)))
                pv = props.get("$preview")
                if not (isinstance(pv, dict) and isinstance(pv.get("width"), (int, float)) and isinstance(pv.get("height"), (int, float))):
                    rep.warn(f"{name}: data-props has no $preview {{width, height}}")
                for k, v in props.items():
                    if k.startswith("$"):
                        continue
                    if not isinstance(v, dict) or "editor" not in v:
                        rep.err(f"{name}: prop {k} needs an 'editor' key (use null for objects/callbacks)")
                    elif v.get("editor") == "enum" and not v.get("options"):
                        rep.err(f"{name}: enum prop {k} needs options")
            except json.JSONDecodeError as e:
                rep.err(f"{name}: data-props is not valid JSON after entity decoding ({e})")
    body = raw.split("<x-dc>", 1)[-1].split("</x-dc>", 1)[0] if "<x-dc>" in raw else raw
    for m in HOLE.finditer(body):
        if not PATH_OK.match(m.group(1)):
            line = body[: m.start()].count("\n") + 1
            rep.err(f"{name}: hole {{{{{m.group(1).strip()}}}}} is an expression; compute it in renderVals() (x-dc line {line})")
    for tag in ("iframe", "object", "embed"):
        if re.search(rf"<{tag}\b", body, re.I):
            rep.err(f"{name}: <{tag}> is not allowed on a canvas")
    for m in re.finditer(r"<([A-Z][A-Za-z0-9]*)[\s>/]", body):
        rep.err(f"{name}: capitalised tag <{m.group(1)}>; mount children with <dc-import name=\"…\">")
    for m in re.finditer(r"<dc-import\b([^>]*)>", body):
        nm = re.search(r'\bname="([^"]+)"', m.group(1))
        if not nm:
            rep.err(f"{name}: <dc-import> without name")
        elif not (p.parent / f"{nm.group(1)}.dc.html").is_file():
            rep.warn(f"{name}: dc-import name=\"{nm.group(1)}\" has no sibling file '{nm.group(1)}.dc.html'")
    for m in re.finditer(r"<[a-zA-Z][\w-]*\s[^<>]*?\s[\w:-]+=(?![\"'{])[^\s>]+", body):
        rep.err(f"{name}: unquoted attribute in {m.group(0)[:60]!r}")
        break
    if EMOJI.search(body):
        rep.warn(f"{name}: emoji in markup; use inline stroke SVG or the design system's icons")
    tc = TagChecker()
    try:
        tc.feed(re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", body, flags=re.S | re.I))
        tc.close()
    except Exception as e:  # html.parser is lenient; report rather than crash
        rep.warn(f"{name}: could not parse markup fully ({e})")
    for t, ln in tc.stack:
        if t not in ("helmet",):
            tc.problems.append(f"line {ln}: <{t}> is never closed")
    for prob in tc.problems[:8]:
        rep.err(f"{name}: {prob} (x-dc fragment)")
    return raw


def cmd_lint_dc(a):
    target = Path(a.path)
    rep = Report()
    files = [target] if target.is_file() else sorted(p for p in target.rglob("*.dc.html") if "/ds/" not in str(p).replace("\\", "/"))
    if not files:
        print(f"no .dc.html files under {target}")
        return 2
    root = target if target.is_dir() else target.parent
    srcs = {p: lint_dc_file(p, rep, root) for p in files}
    canvas = None
    for cand in (root / "canvas.json", root / "project" / "canvas.json", root.parent / "canvas.json"):
        if cand.is_file():
            canvas = cand
            break
    if canvas:
        try:
            idx = json.loads(canvas.read_text(encoding="utf-8"))
            base = canvas.parent
            boards = idx.get("boards", {})
            order = idx.get("order", [])
            if set(order) != set(boards):
                rep.err("canvas.json: order and boards must list the same files")
            for path, b in boards.items():
                if not (base / path).is_file():
                    rep.err(f"canvas.json: board {path} has no file")
                for k in ("x", "y", "w", "h"):
                    if not isinstance(b.get(k), (int, float)):
                        rep.err(f"canvas.json: board {path} needs numeric {k}")
                if isinstance(b.get("w"), (int, float)) and not 40 <= b["w"] <= 8000:
                    rep.err(f"canvas.json: board {path} width out of 40–8000")
                src = srcs.get(base / path)
                if src and re.search(r"on[A-Z][a-z]+=\"\{\{", src) and not b.get("is_interactive"):
                    rep.warn(f"canvas.json: {path} has working controls; set is_interactive: true")
            listed = {str((base / p).resolve()) for p in boards}
            for p in files:
                if str(p.resolve()) not in listed and canvas.parent in p.parents:
                    rep.warn(f"canvas.json: {p.relative_to(base)} is not listed in boards (every .dc.html shows)")
        except json.JSONDecodeError as e:
            rep.err(f"{canvas}: invalid JSON ({e})")
    else:
        rep.note("no canvas.json found next to the files; checked artboards only")
    return rep.emit(f"lint-dc {target} ({len(files)} file(s))")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dv.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("dir"); p.add_argument("--title", required=True)
    p.add_argument("--mode", choices=["redesign", "new"], default="redesign"); p.add_argument("--w", type=int, default=1440); p.add_argument("--h", type=int, default=900)
    p.add_argument("--theme", choices=["light", "dark"], default="light", help="gallery chrome theme; match the product")
    p = sub.add_parser("next"); p.add_argument("dir"); p.add_argument("--count", type=int, default=10)
    p = sub.add_parser("build"); p.add_argument("dir"); p.add_argument("--out"); p.add_argument("--standalone", action="store_true")
    p.add_argument("--standalone-dir", help="write only the standalone pages to this folder (relative to the current folder, outside the workspace)")
    p = sub.add_parser("check"); p.add_argument("dir"); p.add_argument("--strict", action="store_true")
    p = sub.add_parser("novelty"); p.add_argument("dir"); p.add_argument("--round", type=int)
    p = sub.add_parser("lint-dc"); p.add_argument("path")
    a = ap.parse_args(argv)
    return {"init": cmd_init, "next": cmd_next, "build": cmd_build, "check": cmd_check, "novelty": cmd_novelty, "lint-dc": cmd_lint_dc}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
