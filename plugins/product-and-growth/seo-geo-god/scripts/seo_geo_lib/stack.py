"""Read-only stack detection for a repository root (WP01, blueprint §4.3).

Reads only a fixed list of manifest/config files (each ≤1 MB, regular files inside the root,
never symlinks) plus existence checks. Never reads `.env*` files or other secrets; site URLs
held in environment variables are reported by variable name only.
"""
from __future__ import annotations

import json
import os
import re
import stat
from typing import Any, Dict, List, Optional

MAX_READ = 1_048_576
_LOCKFILES = (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lock", "bun"), ("bun.lockb", "bun"),
              ("package-lock.json", "npm"), ("npm-shrinkwrap.json", "npm"))
_JS_EXT = ("js", "mjs", "cjs", "ts", "mts", "cts")
_URL_FIELD = re.compile(r"(?<![A-Za-z0-9_])(site|siteUrl|siteURL|url|baseURL|baseUrl|homepage|hostname|base_url)"
                        r"""\s*[:=]\s*["'`]?(https?://[A-Za-z0-9.-]+(?::\d{1,5})?(?:/[^\s"'`,)}\]]*)?)""")
_ENV_REF = re.compile(r"(?:process\.env\.|import\.meta\.env\.|env\(\s*['\"])([A-Z][A-Z0-9_]{1,63})")
_DOMAIN = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$")
_VITE_META = ("nuxt", "astro", "@sveltejs/kit", "@remix-run/dev", "@react-router/dev", "vitepress", "@docusaurus/core")
RECIPE_ANCHORS = ("nextjs-app-router", "nextjs-pages-router", "nuxt", "astro", "sveltekit", "react-router", "remix",
                  "gatsby", "docusaurus", "vitepress", "angular-ssr", "create-react-app", "vite-spa", "hugo", "jekyll",
                  "eleventy", "wordpress-themes", "shopify-liquid-themes", "django", "rails", "laravel",
                  "plain-static-html")
NOTES = ["Versions are the ranges declared in package.json; check the lockfile for installed versions.",
         "Environment files (.env*) are never read; site URLs from environment variables are named only."]


class _Repo:
    def __init__(self, root: str) -> None:
        real = os.path.realpath(root)
        if not os.path.isdir(real):
            raise ValueError("not a directory: %s" % root)
        self.root = real
        self.skipped: List[Dict[str, str]] = []

    def _path(self, rel: str) -> Optional[str]:
        p = os.path.join(self.root, *rel.split("/"))
        real = os.path.realpath(p)
        if real != p or not (real == self.root or real.startswith(self.root + os.sep)):
            if os.path.lexists(p):
                self.skipped.append({"file": rel, "reason": "symlink or outside root"})
            return None
        return p

    def exists(self, rel: str) -> bool:
        p = self._path(rel)
        return bool(p) and os.path.lexists(p)

    def is_dir(self, rel: str) -> bool:
        p = self._path(rel)
        return bool(p) and os.path.isdir(p)

    def first(self, *rels: str) -> Optional[str]:
        return next((r for r in rels if self.exists(r)), None)

    def read(self, rel: str, limit: int = MAX_READ) -> Optional[str]:
        if os.path.basename(rel).lower().startswith(".env"):
            return None
        p = self._path(rel)
        if not p or not os.path.lexists(p):
            return None
        st = os.lstat(p)
        if not stat.S_ISREG(st.st_mode):
            self.skipped.append({"file": rel, "reason": "not a regular file"})
            return None
        if st.st_size > limit:
            self.skipped.append({"file": rel, "reason": "larger than %d bytes" % limit})
            return None
        with open(p, "rb") as fh:
            return fh.read(limit).decode("utf-8", errors="replace")


def _configs(base: str) -> List[str]:
    return ["%s.%s" % (base, ext) for ext in _JS_EXT]


def _anchor(name: str) -> str:
    assert name in RECIPE_ANCHORS, name
    return "framework-recipes.md#" + name


def _norm_url(url: str) -> str:
    """Bound length and give host-only URLs a trailing slash."""
    url = url[:200]
    return url + "/" if url.count("/") == 2 else url


def detect_stack(root: str) -> Dict[str, Any]:
    """Detect frameworks, package manager, build output, site URL candidates and SEO surfaces.

    Returns the §4.3 dict plus `lockfiles`, `site_url_env_vars`, `skipped` and `notes`.
    Raises ValueError when `root` is not a directory.
    """
    repo = _Repo(root)
    out: Dict[str, Any] = {"frameworks": [], "package_manager": None, "lockfiles": [], "build_script": None,
                           "rendering_hints": [], "build_output_candidates": [], "site_url_candidates": [],
                           "site_url_env_vars": [], "seo_surfaces": {k: [] for k in
                                                                     ("metadata", "sitemap", "robots", "headers",
                                                                      "redirects")},
                           "recipe_anchors": [], "skipped": repo.skipped, "notes": list(NOTES)}
    pkg = _package_json(repo, out)
    deps: Dict[str, str] = {}
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        value = pkg.get(section)
        if isinstance(value, dict):
            deps.update({str(k): str(v)[:60] for k, v in value.items()})
    ctx = _Ctx(repo, out, deps)
    for detector in (_next, _nuxt, _astro, _sveltekit, _remix, _gatsby, _docusaurus, _vitepress, _angular,
                     _vite_spa, _hugo, _jekyll, _eleventy, _wordpress, _shopify, _django, _rails, _laravel):
        detector(ctx)
    if not out["frameworks"] and repo.exists("index.html"):
        ctx.add("static-html", "plain static HTML", None, ["index.html"], "plain-static-html", outputs=["."])
    _common_surfaces(ctx)
    for key in ("rendering_hints", "build_output_candidates", "recipe_anchors", "site_url_env_vars"):
        out[key] = list(dict.fromkeys(out[key]))
    unique: Dict[Any, Dict[str, str]] = {}
    for cand in out["site_url_candidates"]:
        unique.setdefault((cand["value"], cand["source"]), cand)
    out["site_url_candidates"] = list(unique.values())
    out["skipped"] = [dict(t) for t in dict.fromkeys(tuple(sorted(x.items())) for x in repo.skipped)]
    for key in out["seo_surfaces"]:
        out["seo_surfaces"][key] = sorted(set(out["seo_surfaces"][key]))
    return out


class _Ctx:
    def __init__(self, repo: _Repo, out: Dict[str, Any], deps: Dict[str, str]) -> None:
        self.repo, self.out, self.deps = repo, out, deps

    def add(self, name: str, label: str, version: Optional[str], evidence: List[str], anchor: str, *,
            outputs: Optional[List[str]] = None, hints: Optional[List[str]] = None) -> None:
        self.out["frameworks"].append({"name": name, "label": label, "version": version,
                                       "evidence": list(dict.fromkeys(evidence))})
        self.out["recipe_anchors"].append(_anchor(anchor))
        self.out["build_output_candidates"].extend(outputs or [])
        self.out["rendering_hints"].extend(hints or [])

    def scan_config(self, rel: Optional[str]) -> str:
        """Read a config file and collect URL fields and env-variable names."""
        if not rel:
            return ""
        text = self.repo.read(rel) or ""
        for m in _URL_FIELD.finditer(text):
            self.out["site_url_candidates"].append({"value": _norm_url(m.group(2)),
                                                    "source": "%s: %s" % (rel, m.group(1))})
        for name in _ENV_REF.findall(text):
            if any(t in name for t in ("URL", "SITE", "HOST", "DOMAIN", "ORIGIN")):
                self.out["site_url_env_vars"].append(name)
        return text

    def surface(self, kind: str, *rels: str) -> None:
        self.out["seo_surfaces"][kind].extend(r for r in rels if self.repo.exists(r))


def _package_json(repo: _Repo, out: Dict[str, Any]) -> Dict[str, Any]:
    text = repo.read("package.json")
    pkg: Dict[str, Any] = {}
    if text is not None:
        try:
            loaded = json.loads(text)
            pkg = loaded if isinstance(loaded, dict) else {}
        except (ValueError, RecursionError):
            repo.skipped.append({"file": "package.json", "reason": "invalid JSON"})
    locks = [(name, pm) for name, pm in _LOCKFILES if repo.exists(name)]
    out["lockfiles"] = [name for name, _ in locks]
    declared = pkg.get("packageManager")
    if isinstance(declared, str) and re.match(r"^(npm|pnpm|yarn|bun)@", declared):
        out["package_manager"] = declared.split("@", 1)[0]
    elif locks:
        out["package_manager"] = locks[0][1]
    scripts = pkg.get("scripts")
    if isinstance(scripts, dict) and isinstance(scripts.get("build"), str):
        out["build_script"] = scripts["build"][:200]
    home = pkg.get("homepage")
    if isinstance(home, str) and re.match(r"^https?://", home):
        out["site_url_candidates"].append({"value": _norm_url(home), "source": "package.json: homepage"})
    return pkg


def _next(c: _Ctx) -> None:
    cfg = c.repo.first(*_configs("next.config"))
    if "next" not in c.deps and not cfg:
        return
    text = c.scan_config(cfg)
    app = [d for d in ("app", "src/app") if c.repo.is_dir(d)]
    pages = [d for d in ("pages", "src/pages") if c.repo.is_dir(d)]
    evidence = (["package.json"] if "next" in c.deps else []) + ([cfg] if cfg else []) + [d + "/" for d in app + pages]
    export = bool(re.search(r"""output\s*:\s*["'`]export["'`]""", text))
    dist = re.search(r"""distDir\s*:\s*["'`]([A-Za-z0-9._/-]{1,80})["'`]""", text)
    hints = []
    if export:
        outputs = ["out"] + ([dist.group(1)] if dist else [])
        hints.append("next: output 'export' produces static HTML; run the build, then audit-build the export dir")
    else:
        outputs = [dist.group(1) if dist else ".next"]
        hints.append("next: server or hybrid rendering; build, start the production server locally and use "
                     "audit-url --live --allow-local localhost:3000")
    if re.search(r"trailingSlash\s*:\s*true", text):
        hints.append("next: trailingSlash true (directory-style URLs)")
    if re.search(r"""basePath\s*:\s*["'`]/""", text):
        hints.append("next: basePath set; canonical and sitemap URLs must include it")
    routers = (["app router"] if app else []) + (["pages router"] if pages else [])
    label = "Next.js (%s)" % " + ".join(routers) if routers else "Next.js"
    anchor = "nextjs-pages-router" if pages and not app else "nextjs-app-router"
    c.add("next", label, c.deps.get("next"), evidence, anchor, outputs=outputs, hints=hints)
    if app and pages:
        c.out["recipe_anchors"].append(_anchor("nextjs-pages-router"))
    for d in app:
        c.surface("metadata", *["%s/layout.%s" % (d, e) for e in ("tsx", "jsx", "ts", "js")])
        c.surface("sitemap", *["%s/sitemap.%s" % (d, e) for e in ("ts", "js", "xml")])
        c.surface("robots", *["%s/robots.%s" % (d, e) for e in ("ts", "js", "txt")])
    for d in pages:
        c.surface("metadata", *["%s/_app.%s" % (d, e) for e in ("tsx", "jsx", "js")],
                  *["%s/_document.%s" % (d, e) for e in ("tsx", "jsx", "js")])
    c.surface("sitemap", *_configs("next-sitemap.config"))
    c.surface("headers", *(["middleware.ts", "middleware.js", "src/middleware.ts", "src/middleware.js"]))
    if cfg and re.search(r"\bheaders\s*[(:]", text):
        c.out["seo_surfaces"]["headers"].append(cfg)
    if cfg and re.search(r"\bredirects\s*[(:]", text):
        c.out["seo_surfaces"]["redirects"].append(cfg)


def _nuxt(c: _Ctx) -> None:
    cfg = c.repo.first(*_configs("nuxt.config"))
    if "nuxt" not in c.deps and not cfg:
        return
    text = c.scan_config(cfg)
    spa = bool(re.search(r"\bssr\s*:\s*false", text))
    generate = "generate" in (c.out["build_script"] or "")
    hints = ["nuxt: ssr false (client-rendered SPA); check REND001" if spa else
             "nuxt: static generation; audit-build .output/public" if generate else
             "nuxt: server rendering; run the production server locally and use audit-url --allow-local"]
    c.add("nuxt", "Nuxt", c.deps.get("nuxt"), ["package.json"] * ("nuxt" in c.deps) + ([cfg] if cfg else []),
          "nuxt", outputs=[".output/public"], hints=hints)
    c.surface("metadata", "app.vue", "app/app.vue")
    c.surface("robots", "public/robots.txt")


def _astro(c: _Ctx) -> None:
    cfg = c.repo.first(*_configs("astro.config"))
    if "astro" not in c.deps and not cfg:
        return
    text = c.scan_config(cfg)
    mode = re.search(r"""output\s*:\s*["'`](server|hybrid|static)["'`]""", text)
    server = bool(mode and mode.group(1) in ("server", "hybrid"))
    hints = ["astro: output '%s'; prerendered pages land in dist/client, run the server for the rest" % mode.group(1)
             if server else "astro: static output; audit-build dist"]
    if not re.search(r"(?<![A-Za-z0-9_])site\s*:", text):
        hints.append("astro: no site configured; canonical and sitemap URLs need it")
    c.add("astro", "Astro", c.deps.get("astro"), ["package.json"] * ("astro" in c.deps) + ([cfg] if cfg else []),
          "astro", outputs=["dist/client", "dist"] if server else ["dist"], hints=hints)
    if "@astrojs/sitemap" in c.deps:
        c.out["seo_surfaces"]["sitemap"].append(cfg or "package.json")
    c.surface("metadata", "src/layouts")
    c.surface("robots", "public/robots.txt", "src/pages/robots.txt.ts", "src/pages/robots.txt.js")


def _sveltekit(c: _Ctx) -> None:
    cfg = c.repo.first("svelte.config.js", "svelte.config.ts", "svelte.config.mjs")
    if "@sveltejs/kit" not in c.deps:
        return
    text = c.scan_config(cfg)
    static = "@sveltejs/adapter-static" in c.deps or "adapter-static" in text
    c.add("sveltekit", "SvelteKit", c.deps.get("@sveltejs/kit"), ["package.json"] + ([cfg] if cfg else []),
          "sveltekit", outputs=["build"] if static else [".svelte-kit/output"],
          hints=["sveltekit: adapter-static; audit-build build" if static else
                 "sveltekit: server rendering; run the production server locally and use audit-url --allow-local"])
    c.surface("metadata", "src/app.html", "src/routes/+layout.svelte")
    c.surface("sitemap", "src/routes/sitemap.xml/+server.ts", "src/routes/sitemap.xml/+server.js")
    c.surface("robots", "static/robots.txt")


def _remix(c: _Ctx) -> None:
    rr_cfg = c.repo.first(*_configs("react-router.config"))
    remix_cfg = c.repo.first(*_configs("remix.config"))
    if "@react-router/dev" in c.deps or rr_cfg:
        text = c.scan_config(rr_cfg)
        spa = bool(re.search(r"\bssr\s*:\s*false", text))
        c.add("react-router", "React Router (framework mode)", c.deps.get("@react-router/dev"),
              ["package.json"] * ("@react-router/dev" in c.deps) + ([rr_cfg] if rr_cfg else []),
              "react-router", outputs=["build/client"],
              hints=["react-router: ssr false (SPA mode); check REND001" if spa else
                     "react-router: server rendering; run the production server locally and use audit-url --allow-local"])
    elif "@remix-run/react" in c.deps or "@remix-run/dev" in c.deps or remix_cfg:
        c.scan_config(remix_cfg)
        c.add("remix", "Remix", c.deps.get("@remix-run/react") or c.deps.get("@remix-run/dev"),
              ["package.json"] + ([remix_cfg] if remix_cfg else []), "remix",
              outputs=["build/client", "public/build"],
              hints=["remix: server rendering; run the production server locally and use audit-url --allow-local"])
    else:
        return
    c.surface("metadata", "app/root.tsx", "app/root.jsx")


def _gatsby(c: _Ctx) -> None:
    cfg = c.repo.first(*_configs("gatsby-config"))
    if "gatsby" not in c.deps and not cfg:
        return
    c.scan_config(cfg)
    c.add("gatsby", "Gatsby", c.deps.get("gatsby"), ["package.json"] * ("gatsby" in c.deps) + ([cfg] if cfg else []),
          "gatsby", outputs=["public"], hints=["gatsby: static build; audit-build public"])
    c.surface("metadata", "src/components/seo.js", "src/components/seo.tsx")
    c.surface("robots", "static/robots.txt")


def _docusaurus(c: _Ctx) -> None:
    cfg = c.repo.first(*_configs("docusaurus.config"))
    if "@docusaurus/core" not in c.deps and not cfg:
        return
    c.scan_config(cfg)
    c.add("docusaurus", "Docusaurus", c.deps.get("@docusaurus/core"),
          ["package.json"] * ("@docusaurus/core" in c.deps) + ([cfg] if cfg else []), "docusaurus",
          outputs=["build"], hints=["docusaurus: static build; audit-build build"])
    c.surface("robots", "static/robots.txt")


def _vitepress(c: _Ctx) -> None:
    cfg = c.repo.first(*(_configs(".vitepress/config") + _configs("docs/.vitepress/config")))
    if "vitepress" not in c.deps and not cfg:
        return
    c.scan_config(cfg)
    out_dir = cfg.rsplit("/", 1)[0] + "/dist" if cfg else ".vitepress/dist"
    c.add("vitepress", "VitePress", c.deps.get("vitepress"),
          ["package.json"] * ("vitepress" in c.deps) + ([cfg] if cfg else []), "vitepress", outputs=[out_dir],
          hints=["vitepress: static build; audit-build %s" % out_dir])


def _angular(c: _Ctx) -> None:
    if not c.repo.exists("angular.json") and "@angular/core" not in c.deps:
        return
    outputs: List[str] = []
    text = c.repo.read("angular.json")
    try:
        projects = (json.loads(text) if text else {}).get("projects") or {}
    except (ValueError, AttributeError, RecursionError):
        projects = {}
    for name in sorted(projects)[:5] if isinstance(projects, dict) else []:
        proj = projects[name]
        build = ((proj.get("architect") or {}).get("build") or {}) if isinstance(proj, dict) else {}
        opts = build.get("options") if isinstance(build, dict) else None
        path = opts.get("outputPath") if isinstance(opts, dict) else None
        base = path.get("base") if isinstance(path, dict) else path
        if isinstance(base, str):
            outputs += [base.rstrip("/") + "/browser", base.rstrip("/")]
    ssr = "@angular/ssr" in c.deps or "@nguniversal/express-engine" in c.deps
    c.add("angular", "Angular", c.deps.get("@angular/core"), ["angular.json"] * c.repo.exists("angular.json") +
          ["package.json"] * ("@angular/core" in c.deps), "angular-ssr", outputs=outputs or ["dist"],
          hints=["angular: SSR/prerender package present; audit prerendered output or the local server" if ssr else
                 "angular: client-rendered unless SSR or prerendering is enabled; check REND001"])
    c.surface("metadata", "src/index.html")


def _vite_spa(c: _Ctx) -> None:
    if "react-scripts" in c.deps:
        c.add("create-react-app", "Create React App (CSR)", c.deps.get("react-scripts"), ["package.json"],
              "create-react-app", outputs=["build"],
              hints=["create-react-app: client-side rendered SPA; server HTML is an empty shell (REND001)"])
        c.surface("metadata", "public/index.html")
        return
    if "vite" not in c.deps or any(m in c.deps for m in _VITE_META):
        return
    flavor = next((f for f in ("react", "vue", "svelte", "solid-js", "preact", "lit") if f in c.deps), None)
    cfg = c.repo.first(*_configs("vite.config"))
    c.add("vite", "Vite SPA (%s)" % (flavor or "vanilla"), c.deps.get("vite"), ["package.json"] + ([cfg] if cfg else []),
          "vite-spa", outputs=["dist"],
          hints=["vite: client-side rendered SPA unless prerendered; check REND001 and consider SSR or SSG"])
    c.surface("metadata", "index.html")
    c.surface("robots", "public/robots.txt")


def _hugo(c: _Ctx) -> None:
    cfg = c.repo.first("hugo.toml", "hugo.yaml", "hugo.yml", "hugo.json")
    text = c.scan_config(cfg) if cfg else ""
    if not cfg and c.repo.exists("config.toml"):
        raw = c.repo.read("config.toml") or ""
        if re.search(r"(?m)^\s*baseURL\s*=", raw):
            cfg, text = "config.toml", c.scan_config("config.toml")
    if not cfg:
        return
    c.add("hugo", "Hugo", None, [cfg], "hugo", outputs=["public"], hints=["hugo: static build; audit-build public"])
    if text and not re.search(r"(?m)^\s*baseURL\s*[=:]\s*['\"]?https?://", text):
        c.out["rendering_hints"].append("hugo: baseURL missing or not absolute; canonical URLs depend on it")
    c.surface("metadata", "layouts/_default/baseof.html", "layouts/partials/head.html")
    c.surface("robots", "layouts/robots.txt", "static/robots.txt")


def _jekyll(c: _Ctx) -> None:
    gem = c.repo.read("Gemfile") or "" if c.repo.exists("Gemfile") else ""
    if not c.repo.exists("_config.yml") or not (re.search(r"""gem\s+["'](jekyll|github-pages)["']""", gem)
                                                 or not c.repo.exists("package.json")):
        return
    text = c.repo.read("_config.yml") or ""
    m = re.search(r"""(?m)^url\s*:\s*["']?(https?://[^"'\s#]+)""", text)
    if m:
        c.out["site_url_candidates"].append({"value": _norm_url(m.group(1)), "source": "_config.yml: url"})
    c.add("jekyll", "Jekyll", None, ["_config.yml"] + (["Gemfile"] if gem else []), "jekyll", outputs=["_site"],
          hints=["jekyll: static build; audit-build _site"])
    c.surface("metadata", "_includes/head.html", "_layouts/default.html")


def _eleventy(c: _Ctx) -> None:
    cfg = c.repo.first(".eleventy.js", *["eleventy.config.%s" % e for e in ("js", "mjs", "cjs", "ts")])
    if "@11ty/eleventy" not in c.deps and not cfg:
        return
    c.scan_config(cfg)
    c.add("eleventy", "Eleventy", c.deps.get("@11ty/eleventy"),
          ["package.json"] * ("@11ty/eleventy" in c.deps) + ([cfg] if cfg else []), "eleventy", outputs=["_site"],
          hints=["eleventy: static build; audit-build _site"])


def _wordpress(c: _Ctx) -> None:
    css = c.repo.read("style.css", limit=MAX_READ)
    head = (css or "")[:8192]
    name = re.search(r"(?im)^[ \t/*#@]*Theme Name:\s*(.{1,80}?)\s*$", head)
    if not name:
        return
    version = re.search(r"(?im)^[ \t/*#@]*Version:\s*([0-9A-Za-z.+-]{1,40})", head)
    c.add("wordpress-theme", "WordPress theme: %s" % name.group(1), version.group(1) if version else None,
          ["style.css"] + (["functions.php"] if c.repo.exists("functions.php") else []), "wordpress-themes",
          hints=["wordpress: server-rendered PHP; SEO plugins may own titles, canonicals and sitemaps; audit the "
                 "running local site with audit-url --allow-local"])
    c.surface("metadata", "header.php", "functions.php")


def _shopify(c: _Ctx) -> None:
    if not c.repo.exists("layout/theme.liquid"):
        return
    c.add("shopify-theme", "Shopify Liquid theme", None, ["layout/theme.liquid"], "shopify-liquid-themes",
          hints=["shopify: Liquid theme rendered by the platform; audit a preview or the live store you own"])
    c.surface("metadata", "layout/theme.liquid", "snippets/meta-tags.liquid")
    c.surface("robots", "templates/robots.txt.liquid")


def _django(c: _Ctx) -> None:
    if "django" in (c.repo.read("manage.py") or "").lower():
        c.add("django", "Django", None, ["manage.py"], "django",
              hints=["django: server-rendered; run the local server and use audit-url --allow-local"])


def _rails(c: _Ctx) -> None:
    if re.search(r"""gem\s+["']rails["']""", c.repo.read("Gemfile") or ""):
        c.add("rails", "Ruby on Rails", None, ["Gemfile"], "rails",
              hints=["rails: server-rendered; run the local server and use audit-url --allow-local"])
        c.surface("robots", "public/robots.txt")


def _laravel(c: _Ctx) -> None:
    if c.repo.exists("artisan") and "laravel/framework" in (c.repo.read("composer.json") or ""):
        c.add("laravel", "Laravel", None, ["artisan", "composer.json"], "laravel",
              hints=["laravel: server-rendered; run the local server and use audit-url --allow-local"])
        c.surface("robots", "public/robots.txt")


def _common_surfaces(c: _Ctx) -> None:
    c.surface("robots", "robots.txt", "public/robots.txt", "static/robots.txt")
    c.surface("sitemap", "public/sitemap.xml", "static/sitemap.xml", "sitemap.xml")
    c.surface("headers", "_headers", "public/_headers", "static/_headers", "vercel.json", "netlify.toml")
    c.surface("redirects", "_redirects", "public/_redirects", "static/_redirects", "vercel.json", "netlify.toml")
    cname = c.repo.read("CNAME", limit=4096) if c.repo.exists("CNAME") else None
    if cname:
        domain = cname.strip().splitlines()[0].strip() if cname.strip() else ""
        if _DOMAIN.match(domain):
            c.out["site_url_candidates"].append({"value": "https://%s/" % domain.lower(),
                                                 "source": "CNAME (https assumed)"})
