// Fails when a relative Markdown link in the plugin does not resolve to a file.
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const files = [];
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    if (name === "node_modules" || name.startsWith(".")) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (name.endsWith(".md")) files.push(p);
  }
};
walk(root);
const broken = [];
for (const file of files) {
  // Links inside fenced code blocks and inline code are templates, not links.
  const text = readFileSync(file, "utf8").replace(/```[\s\S]*?```/g, "").replace(/`[^`\n]*`/g, "");
  for (const m of text.matchAll(/\]\(([^)\s]+)\)/g)) {
    const target = m[1];
    if (/^[a-z]+:/i.test(target) || target.startsWith("#")) continue;
    const path = resolve(dirname(file), decodeURIComponent(target.split("#")[0]));
    if (!existsSync(path)) broken.push(`${file.slice(root.length)} -> ${target}`);
  }
}
if (broken.length) {
  console.error(broken.join("\n"));
  process.exit(1);
}
console.log(`links check passed (${files.length} Markdown files)`);
