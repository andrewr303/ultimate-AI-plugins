export function add(a, b) {
  if (!Number.isFinite(a) || !Number.isFinite(b)) throw new TypeError('Expected numbers');
  return a + b;
}
