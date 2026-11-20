(function (root) {
  'use strict';

  // A small presentation example. Component semantics and domain work stay with
  // their existing owners; an animation completion never confirms an operation.
  function createMotionPolicy({ mediaQuery, manual = false } = {}) {
    if (typeof manual !== 'boolean') throw new TypeError('manual must be boolean');
    const media = mediaQuery === undefined && typeof root.matchMedia === 'function'
      ? root.matchMedia('(prefers-reduced-motion: reduce)') : mediaQuery;
    let manualReduction = manual;
    let disposed = false;
    const listeners = new Set();
    const read = () => manualReduction || !media || Boolean(media.matches);
    let reduced = read();
    function update() {
      if (disposed) return;
      const next = read();
      if (next === reduced) return;
      reduced = next;
      for (const listener of Array.from(listeners)) listener(reduced);
    }
    if (media && typeof media.addEventListener === 'function') {
      media.addEventListener('change', update);
    } else if (media && typeof media.addListener === 'function') {
      media.addListener(update);
    }
    return {
      get reduced() { return reduced; },
      setManual(value) {
        if (typeof value !== 'boolean') throw new TypeError('manual must be boolean');
        if (disposed) return;
        manualReduction = value;
        update();
      },
      subscribe(listener) {
        if (typeof listener !== 'function') throw new TypeError('listener must be a function');
        if (!disposed) listeners.add(listener);
        return () => listeners.delete(listener);
      },
      dispose() {
        if (disposed) return;
        disposed = true;
        if (media && typeof media.removeEventListener === 'function') {
          media.removeEventListener('change', update);
        } else if (media && typeof media.removeListener === 'function') {
          media.removeListener(update);
        }
        listeners.clear();
      }
    };
  }

  function finite(value, label) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new TypeError(`${label} must be a finite number`);
    }
    return value;
  }

  function createPresentation({ read, write, start, policy, onError } = {}) {
    if (typeof read !== 'function' || typeof write !== 'function') {
      throw new TypeError('read and write must be functions');
    }
    if (start !== undefined && typeof start !== 'function') {
      throw new TypeError('start must be a function when supplied');
    }
    if (onError !== undefined && typeof onError !== 'function') {
      throw new TypeError('onError must be a function when supplied');
    }
    const ownedPolicy = !policy;
    const motionPolicy = policy || createMotionPolicy();
    let target = finite(read(), 'initial presentation');
    let generation = 0;
    let active = null;
    let disposed = false;

    function report(error) {
      try {
        if (onError) onError(error);
        else root.console?.error(error);
      } catch (reportingError) {
        root.console?.error(reportingError);
      }
    }
    function writeTarget() {
      try { write(target); } catch (error) { report(error); }
    }
    function release(record) {
      if (!record || record.released) return;
      record.released = true;
      try { record.handle.cancel(); } catch (error) { report(error); }
    }
    function complete(record, error) {
      if (!disposed && active === record && generation === record.generation) {
        active = null;
        // Preserve a stable base style before removing an effect's fill.
        writeTarget();
      }
      release(record);
      if (error && error.name !== 'AbortError') report(error);
    }
    function settle() {
      if (disposed) return;
      ++generation;
      const previous = active;
      active = null;
      writeTarget();
      release(previous);
    }
    const unsubscribe = motionPolicy.subscribe((reduced) => {
      if (reduced) settle();
    });

    return {
      get target() { return target; },
      get active() { return active !== null; },
      set(nextTarget, { duration = 220 } = {}) {
        finite(nextTarget, 'target');
        finite(duration, 'duration');
        if (duration < 0) throw new RangeError('duration must not be negative');
        if (disposed) return;
        const from = finite(read(), 'current presentation');
        const currentGeneration = ++generation;
        const previous = active;
        active = null;
        target = nextTarget;
        writeTarget();
        // Invalidate first: cancellation handlers may run synchronously.
        release(previous);
        if (disposed || generation !== currentGeneration || motionPolicy.reduced ||
            duration === 0 || !start || from === target) return;

        let record;
        try {
          const handle = start(from, target, { duration });
          record = { handle, generation: currentGeneration, released: false };
          if (!handle || typeof handle.cancel !== 'function' ||
              !handle.finished || typeof handle.finished.then !== 'function') {
            throw new TypeError('start must return a cancelable handle with a finished promise');
          }
          // Attach both outcomes even if startup synchronously replaced this work.
          Promise.resolve(handle.finished).then(
            () => complete(record), (error) => complete(record, error)
          );
          if (disposed || generation !== currentGeneration) release(record);
          else active = record;
        } catch (error) {
          if (record?.handle && typeof record.handle.cancel === 'function') release(record);
          if (!disposed && generation === currentGeneration) writeTarget();
          report(error);
        }
      },
      settle,
      dispose() {
        if (disposed) return;
        disposed = true;
        ++generation;
        const previous = active;
        active = null;
        unsubscribe();
        if (ownedPolicy) motionPolicy.dispose();
        release(previous);
      }
    };
  }

  const api = { createMotionPolicy, createPresentation };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PlatformMotion = api;
})(globalThis);
