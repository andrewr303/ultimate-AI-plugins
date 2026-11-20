// Fails when a kernel under src/ uses an API or syntax above HypeStake's runtime floor (ES2020 library, browsers
// without regex lookbehind, Deno and Node without Node built-ins). The ES2020 lib in tsconfig.json catches most
// library calls; this catches the rest by text.
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

const root = new URL("../src/", import.meta.url).pathname;
const forbidden = ["Object.hasOwn", ".at(", "findLast", "structuredClone", "node:", "process.", "enum ", "namespace ", "replaceAll", "(?<=", "(?<!", "require(", "Deno.", "window.", "document."];
const failures = [];
for (const name of readdirSync(root)) {
  if (!name.endsWith(".ts")) continue;
  const text = readFileSync(join(root, name), "utf8");
  for (const token of forbidden) if (text.includes(token)) failures.push(`${name}: ${token}`);
  for (const m of text.matchAll(/from\s+"([^"]+)"/g)) {
    if (!m[1].startsWith("./") || !m[1].endsWith(".ts")) failures.push(`${name}: import ${m[1]} must be relative with a .ts extension`);
  }
}
if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log("kernel floor check passed");
