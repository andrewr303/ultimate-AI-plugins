'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { createMotionPolicy, createPresentation } = require('../examples/motion-lab/motion-lifecycle.js');

function mediaQuery(matches = false) {
  const listeners = new Set();
  return {
    matches,
    addEventListener(type, listener) { assert.equal(type, 'change'); listeners.add(listener); },
    removeEventListener(type, listener) { assert.equal(type, 'change'); listeners.delete(listener); },
    change(value) { this.matches = value; for (const listener of [...listeners]) listener(); },
    get listenerCount() { return listeners.size; }
  };
}

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

const flush = async () => { await Promise.resolve(); await Promise.resolve(); };

function fixture(options = {}) {
  const media = mediaQuery();
  const policy = createMotionPolicy({ mediaQuery: media });
  let visible = 0;
  const writes = [], effects = [], errors = [];
  const presentation = createPresentation({
    read: () => visible,
    write: (value) => { visible = value; writes.push(value); },
    start: (from, to, timing) => {
      const completion = deferred();
      const effect = { from, to, timing, completion, cancels: 0 };
      effects.push(effect);
      return { finished: completion.promise, cancel() { ++effect.cancels; } };
    },
    policy,
    onError: (error) => errors.push(error),
    ...options
  });
  return { presentation, policy, media, writes, effects, errors,
    sample(value) { visible = value; }, get visible() { return visible; } };
}

test('motion policy follows live system changes and manual reduction never overrides the system', () => {
  const media = mediaQuery();
  const policy = createMotionPolicy({ mediaQuery: media });
  const values = [];
  const unsubscribe = policy.subscribe((value) => values.push(value));
  assert.equal(policy.reduced, false);
  policy.setManual(true);
  media.change(true);
  policy.setManual(false);
  assert.equal(policy.reduced, true);
  media.change(false);
  assert.deepEqual(values, [true, false]);
  unsubscribe();
  policy.setManual(true);
  assert.deepEqual(values, [true, false]);
  policy.dispose();
  policy.dispose();
  assert.equal(media.listenerCount, 0);
  media.change(false);
  assert.equal(policy.reduced, true);
});

test('motion policy defaults to reduced when a browser preference is unavailable', () => {
  const policy = createMotionPolicy({ mediaQuery: null });
  assert.equal(policy.reduced, true);
  policy.setManual(false);
  assert.equal(policy.reduced, true);
  policy.dispose();
});

test('retargeting samples the visible state before removing the old effect', async () => {
  const f = fixture();
  f.presentation.set(1, { duration: 180 });
  f.sample(0.42);
  f.presentation.set(0, { duration: 120 });
  assert.equal(f.effects[0].cancels, 1);
  assert.equal(f.effects[1].from, 0.42);
  assert.equal(f.effects[1].to, 0);
  assert.deepEqual(f.effects[1].timing, { duration: 120 });
  const afterReplacement = [...f.writes];
  f.effects[0].completion.resolve();
  await flush();
  assert.deepEqual(f.writes, afterReplacement);
  assert.equal(f.presentation.active, true);
  f.effects[1].completion.resolve();
  await flush();
  assert.equal(f.presentation.active, false);
  assert.equal(f.presentation.target, 0);
  assert.equal(f.visible, 0);
  assert.deepEqual(f.effects.map((effect) => effect.cancels), [1, 1]);
  f.presentation.dispose();
  f.policy.dispose();
});

test('an obsolete rejected completion cannot settle newer presentation', async () => {
  const f = fixture();
  f.presentation.set(1);
  f.sample(0.5);
  f.presentation.set(0);
  const afterReplacement = [...f.writes];
  f.effects[0].completion.reject(Object.assign(new Error('replaced'), { name: 'AbortError' }));
  await flush();
  assert.deepEqual(f.writes, afterReplacement);
  assert.equal(f.presentation.active, true);
  assert.deepEqual(f.errors, []);
  f.presentation.dispose();
  f.policy.dispose();
});

test('synchronous cancellation callbacks cannot overwrite a newer intent', async () => {
  const policy = createMotionPolicy({ mediaQuery: mediaQuery() });
  let visible = 0;
  const writes = [];
  const completion = deferred();
  let starts = 0, cancels = 0, presentation;
  presentation = createPresentation({
    read: () => visible,
    write: (value) => { visible = value; writes.push(value); },
    policy,
    start: () => {
      ++starts;
      return {
        finished: completion.promise,
        cancel() {
          ++cancels;
          // The replacement's stable base value must exist before removing fill.
          assert.equal(visible, 0);
          presentation.set(0.8, { duration: 0 });
        }
      };
    }
  });
  presentation.set(1);
  visible = 0.4;
  presentation.set(0);
  assert.equal(presentation.target, 0.8);
  assert.equal(visible, 0.8);
  assert.equal(presentation.active, false);
  assert.equal(starts, 1);
  const currentWrites = [...writes];
  completion.resolve();
  await flush();
  assert.deepEqual(writes, currentWrites);
  assert.equal(cancels, 1);
  presentation.dispose();
  policy.dispose();
});

test('live reduced motion settles an active effect to the latest endpoint immediately', async () => {
  const f = fixture();
  f.presentation.set(1);
  assert.equal(f.presentation.active, true);
  f.sample(0.3);
  f.media.change(true);
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.equal(f.effects[0].cancels, 1);
  const settledWrites = [...f.writes];
  f.effects[0].completion.resolve();
  await flush();
  assert.deepEqual(f.writes, settledWrites);
  f.presentation.set(0);
  assert.equal(f.visible, 0);
  assert.equal(f.effects.length, 1);
  f.presentation.dispose();
  f.policy.dispose();
});

test('zero duration and unavailable animation use the same immediate endpoint', () => {
  const f = fixture();
  f.presentation.set(1, { duration: 0 });
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.equal(f.effects.length, 0);
  f.presentation.dispose();
  const fallback = fixture({ start: undefined });
  fallback.presentation.set(1);
  assert.equal(fallback.visible, 1);
  assert.equal(fallback.presentation.active, false);
  fallback.presentation.dispose();
  fallback.policy.dispose();
  f.policy.dispose();
});

test('an externally canceled current effect settles its endpoint without reporting expected cancellation', async () => {
  const f = fixture();
  f.presentation.set(1);
  f.sample(0.2);
  f.effects[0].completion.reject(Object.assign(new Error('canceled'), { name: 'AbortError' }));
  await flush();
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.equal(f.effects[0].cancels, 1);
  assert.deepEqual(f.errors, []);
  f.presentation.dispose();
  f.policy.dispose();
});

test('unexpected animation failure is reported and keeps the correct stable endpoint', async () => {
  const f = fixture();
  const error = new Error('animation driver failed');
  f.presentation.set(1);
  f.sample(0.2);
  f.effects[0].completion.reject(error);
  await flush();
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.deepEqual(f.errors, [error]);
  assert.equal(f.effects[0].cancels, 1);
  f.presentation.dispose();
  f.policy.dispose();
});

test('unexpected stale failures remain visible without mutating the replacement', async () => {
  const f = fixture();
  const error = new Error('old driver failed');
  f.presentation.set(1);
  f.sample(0.4);
  f.presentation.set(0);
  const afterReplacement = [...f.writes];
  f.effects[0].completion.reject(error);
  await flush();
  assert.deepEqual(f.writes, afterReplacement);
  assert.equal(f.presentation.active, true);
  assert.deepEqual(f.errors, [error]);
  f.presentation.dispose();
  f.policy.dispose();
});

test('startup failure falls back without waiting for an animation event', () => {
  const error = new Error('WAAPI unavailable');
  const f = fixture({ start() { throw error; } });
  f.presentation.set(1);
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.deepEqual(f.errors, [error]);
  f.presentation.dispose();
  f.policy.dispose();
});

test('disposal invalidates pending completions, releases once and performs no later DOM writes', async () => {
  const f = fixture();
  f.presentation.set(1);
  f.sample(0.6);
  const beforeDisposal = [...f.writes];
  f.presentation.dispose();
  f.presentation.dispose();
  f.media.change(true);
  f.presentation.set(0);
  f.presentation.settle();
  f.effects[0].completion.resolve();
  await flush();
  assert.deepEqual(f.writes, beforeDisposal);
  assert.equal(f.effects[0].cancels, 1);
  assert.equal(f.presentation.active, false);
  // The caller supplied this shared policy; the presentation does not destroy it.
  assert.equal(f.media.listenerCount, 1);
  f.policy.dispose();
  assert.equal(f.media.listenerCount, 0);
});

test('invalid targets and durations leave the existing interaction untouched', () => {
  const f = fixture();
  f.presentation.set(1);
  const writes = [...f.writes];
  for (const value of [NaN, Infinity, '1', null]) {
    assert.throws(() => f.presentation.set(value), /finite number/);
  }
  for (const value of [NaN, Infinity, '1']) {
    assert.throws(() => f.presentation.set(0, { duration: value }), /finite number/);
  }
  assert.throws(() => f.presentation.set(0, { duration: -1 }), /negative/);
  assert.deepEqual(f.writes, writes);
  assert.equal(f.effects[0].cancels, 0);
  assert.equal(f.presentation.target, 1);
  f.presentation.dispose();
  f.policy.dispose();
});

test('settling and later promise delivery release an effect only once', async () => {
  const f = fixture();
  f.presentation.set(1);
  f.presentation.settle();
  f.presentation.settle();
  f.effects[0].completion.resolve();
  await flush();
  assert.equal(f.visible, 1);
  assert.equal(f.effects[0].cancels, 1);
  f.presentation.dispose();
  f.policy.dispose();
});

test('invalid animation handle is released and reported with a usable endpoint', () => {
  let cancels = 0;
  const f = fixture({ start: () => ({ cancel() { ++cancels; } }) });
  f.presentation.set(1);
  assert.equal(f.visible, 1);
  assert.equal(f.presentation.active, false);
  assert.equal(cancels, 1);
  assert.equal(f.errors.length, 1);
  assert.match(f.errors[0].message, /finished promise/);
  f.presentation.dispose();
  f.policy.dispose();
});
