// Shared visible-page reader. It never reads cookies, storage, inputs, or private APIs.
function readProviderPage() {
  const visible = (e) => !!e && e.getClientRects().length > 0;
  const buttons = [...document.querySelectorAll("button")].filter(visible);
  const dialog = [...document.querySelectorAll("[role=dialog]")].find(visible);
  const title = document.title;
  const taskStatus = [
    ...document.querySelectorAll(
      '[data-testid="task-status"], [data-session-status]',
    ),
  ].find(visible);
  const status =
    taskStatus?.getAttribute("data-session-status") ||
    taskStatus?.getAttribute("data-state") ||
    taskStatus?.innerText.trim().toLowerCase();
  return {
    title,
    terminal: [
      "completed",
      "failed",
      "cancelled",
      "paused",
      "auth_expired",
      "process_exit",
    ].includes(status)
      ? status
      : null,
    waitingTool:
      !!taskStatus &&
      /^(running|executing|waiting for tool|waiting for network)$/.test(
        status || "",
      ),
    messages: [
      ...document.querySelectorAll(
        '[data-message-author-role="assistant"], [data-testid="assistant-message"], .font-claude-response',
      ),
    ]
      .filter(visible)
      .slice(-12)
      .map((e, i) => ({
        id: e.getAttribute("data-message-id") || e.id || String(i),
        text: e.innerText.slice(-4000),
      })),
    login:
      [
        ...document.querySelectorAll("input[type=email],input[type=password]"),
      ].some(visible) ||
      buttons.some((e) =>
        /^(log in|sign in|continue with google|continue with apple)$/i.test(
          e.innerText.trim(),
        ),
      ),
    challenge: /just a moment|verify you are human|access denied/i.test(title),
    stop: buttons.some((e) =>
      /^(stop|stop generating|stop response)$/i.test(
        e.getAttribute("aria-label") || e.innerText.trim(),
      ),
    ),
    permission:
      dialog && /allow|approve|permission/i.test(dialog.innerText)
        ? dialog.innerText.slice(0, 3000)
        : null,
    question:
      dialog &&
      dialog.querySelector("input,textarea") &&
      !dialog.querySelector("input[type=password],input[type=email]")
        ? dialog.innerText.slice(0, 3000)
        : null,
    links: [...document.querySelectorAll("a[href]")]
      .filter(visible)
      .slice(0, 150)
      .map((a) => ({ url: a.href, title: a.innerText.slice(0, 150) })),
  };
}
export { readProviderPage };
