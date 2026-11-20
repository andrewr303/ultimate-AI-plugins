'use strict';

// Semantic changes belong to the controls below. Presentation owns decoration only.
(() => {
  const byId = (id) => document.getElementById(id);
  const root = document.documentElement;
  const systemMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const reduce = byId('reduce');
  const fill = byId('detailFill');
  const detail = byId('detail');
  const dialogTrigger = byId('openDialog');
  const detailsTrigger = byId('toggleDetails');
  const detailsPanel = byId('detailsPanel');
  let policy;
  let illustration;
  let dialogEntry;
  let unsubscribePolicy;
  let mounted = false;
  let expanded = false;

  function animate(element, keyframes, duration) {
    return element.animate(keyframes, {
      duration, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'both'
    });
  }

  function syncMotion() {
    root.dataset.reduce = String(policy.reduced);
    byId('motionStatus').textContent = systemMotion.matches
      ? 'No motion · system preference'
      : policy.reduced ? 'No motion · comparison setting'
        : 'Restrained motion · system allows motion';
  }

  function mountPresentation() {
    if (mounted) return;
    mounted = true;
    policy = PlatformMotion.createMotionPolicy({
      mediaQuery: systemMotion, manual: reduce.checked
    });
    unsubscribePolicy = policy.subscribe(syncMotion);
    illustration = PlatformMotion.createPresentation({
      policy,
      read: () => {
        const matrix = new DOMMatrixReadOnly(getComputedStyle(fill).transform);
        return matrix.a;
      },
      write: (target) => { fill.style.transform = 'scaleX(' + target + ')'; },
      start: (from, to, options) => animate(fill, [
        { transform: 'scaleX(' + from + ')' },
        { transform: 'scaleX(' + to + ')' }
      ], options.duration),
      onError: (error) => console.error(error)
    });
    dialogEntry = PlatformMotion.createPresentation({
      policy,
      read: () => Number(getComputedStyle(detail).opacity),
      write: (target) => { detail.style.opacity = String(target); },
      start: (from, to, options) => animate(detail, [
        { opacity: from, transform: 'translateY(' + ((1 - from) * 8) + 'px)' },
        { opacity: to, transform: 'translateY(' + ((1 - to) * 8) + 'px)' }
      ], options.duration),
      onError: (error) => console.error(error)
    });
    illustration.set(expanded ? 1 : 0, { duration: 0 });
    dialogEntry.set(1, { duration: 0 });
    syncMotion();
  }

  // An unavailable animation API selects the same stable endpoint immediately.
  function effectDuration(element, duration) {
    return typeof element.animate === 'function' ? duration : 0;
  }

  mountPresentation();
  reduce.addEventListener('change', () => policy.setManual(reduce.checked));
  for (const [id, token, output] of [
    ['smallDuration', '--small', 'smallValue'],
    ['detailDuration', null, 'detailValue']
  ]) {
    byId(id).addEventListener('input', (event) => {
      const value = Number(event.currentTarget.value);
      if (token) root.style.setProperty(token, value + 'ms');
      byId(output).textContent = value + ' ms';
    });
  }
  byId('favorite').addEventListener('click', (event) => {
    const button = event.currentTarget;
    const selected = button.getAttribute('aria-pressed') !== 'true';
    button.setAttribute('aria-pressed', String(selected));
    button.querySelector('span').textContent = selected ? 'Saved example' : 'Save example';
    byId('pressStatus').textContent = selected
      ? 'Saved in this local example.' : 'This example is not saved.';
  });

  function setExpanded(value) {
    expanded = value;
    // Move focus before hiding its owner. Never defer this to a visual completion.
    if (!expanded && detailsPanel.contains(document.activeElement)) detailsTrigger.focus();
    detailsTrigger.setAttribute('aria-expanded', String(expanded));
    detailsTrigger.querySelector('span').textContent = expanded ? 'Hide details' : 'Show details';
    detailsPanel.inert = !expanded;
    detailsPanel.hidden = !expanded;
    byId('detailState').textContent = expanded ? 'Details expanded.' : 'Details collapsed.';
    illustration.set(expanded ? 1 : 0, {
      duration: effectDuration(fill, Number(byId('detailDuration').value))
    });
  }
  detailsTrigger.addEventListener('click', () => setExpanded(!expanded));
  byId('closeDetails').addEventListener('click', () => setExpanded(false));

  function openDialog() {
    if (typeof detail.showModal !== 'function') {
      byId('dialogStatus').textContent = 'Native modal dialogs are unavailable in this browser.';
      return;
    }
    if (detail.open) return;
    dialogEntry.set(0, { duration: 0 });
    detail.showModal();
    dialogEntry.set(1, { duration: effectDuration(detail, 220) });
  }

  function closeDialog() {
    detail.close();
    dialogEntry.settle();
  }

  dialogTrigger.addEventListener('click', openDialog);
  byId('closeDialog').addEventListener('click', closeDialog);
  byId('replayDialog').addEventListener('click', () => {
    closeDialog();
    openDialog();
  });
  detail.addEventListener('cancel', () => dialogEntry.settle());
  detail.addEventListener('close', () => {
    // A queued close event from before replay cannot move focus out of a reopened dialog.
    if (!detail.open) {
      dialogEntry.settle();
      if (dialogTrigger.isConnected) dialogTrigger.focus();
    }
  });

  // Delivery is independent of current intent. Old responses are intentionally retained.
  const maxQueued = 8;
  const maxLog = 6;
  const queue = [];
  let generation = 0;
  let currentId = null;
  let received = 0;
  let ignored = 0;

  function renderQueue() {
    const pending = currentId !== null;
    byId('run').disabled = queue.length >= maxQueued;
    byId('run').setAttribute('aria-disabled', String(queue.length >= maxQueued));
    byId('run').querySelector('span').textContent = pending
      ? 'Start newer simulation' : 'Run simulation';
    byId('cancel').disabled = !pending;
    byId('asyncRegion').setAttribute('aria-busy', String(pending));
    byId('deliverOldest').disabled = queue.length === 0;
    byId('deliverLatest').disabled = queue.length === 0;
    byId('queueCount').textContent = String(queue.length);
    byId('receivedCount').textContent = String(received);
    byId('ignoredCount').textContent = String(ignored);
  }

  function logDelivery(message) {
    const item = document.createElement('li');
    item.textContent = message;
    byId('responseLog').prepend(item);
    while (byId('responseLog').children.length > maxLog) byId('responseLog').lastChild.remove();
  }

  byId('run').addEventListener('click', () => {
    if (queue.length >= maxQueued) return;
    currentId = ++generation;
    queue.push({ id: currentId, outcome: byId('outcome').value });
    byId('asyncStatus').textContent = 'Simulation ' + currentId
      + ' pending. Deliver a response or start a newer simulation.';
    renderQueue();
  });

  byId('cancel').addEventListener('click', () => {
    if (currentId === null) return;
    const canceledId = currentId;
    currentId = null;
    byId('asyncStatus').textContent = 'Simulation ' + canceledId
      + ' canceled locally. Its queued response may still arrive.';
    renderQueue();
    byId('run').focus();
  });

  function deliver(latest) {
    if (!queue.length) return;
    const response = latest ? queue.pop() : queue.shift();
    received += 1;
    if (response.id !== currentId) {
      ignored += 1;
      logDelivery('Received ' + response.id + ': ignored because its intent is no longer current.');
    } else {
      currentId = null;
      byId('asyncStatus').textContent = response.outcome === 'success'
        ? 'Simulation ' + response.id + ' succeeded. No real data was saved.'
        : 'Simulation ' + response.id + ' failed. Change the result and retry.';
      logDelivery('Received ' + response.id + ': accepted ' + response.outcome + '.');
    }
    renderQueue();
  }
  byId('deliverOldest').addEventListener('click', () => deliver(false));
  byId('deliverLatest').addEventListener('click', () => deliver(true));

  window.addEventListener('pagehide', () => {
    if (!mounted) return;
    // Release only this example's effects/subscriptions and local delivery fixture.
    illustration.dispose();
    dialogEntry.dispose();
    unsubscribePolicy();
    policy.dispose();
    mounted = false;
    queue.length = 0;
    if (currentId !== null) {
      currentId = null;
      byId('asyncStatus').textContent = 'Simulation canceled when leaving this example.';
    }
    renderQueue();
  });
  window.addEventListener('pageshow', mountPresentation);
})();
