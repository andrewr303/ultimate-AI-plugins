// Accessible, visible UI signals only. Exact controls, no hidden APIs or full-page scraping.
function pageState(x) {
  if (x.login)
    return {
      state: "waiting_permission",
      rawState: "login_required",
      text: "Sign in to this account in its isolated provider window.",
    };
  if (x.permission)
    return {
      state: "waiting_permission",
      rawState: "visible_permission",
      text: x.permission,
    };
  if (x.question)
    return {
      state: "waiting_answer",
      rawState: "visible_question",
      text: x.question,
    };
  if (x.terminal) {
    const state = {
      completed: "turn_complete",
      failed: "failed",
      cancelled: "idle",
      paused: "idle",
      auth_expired: "waiting_permission",
      process_exit: "disconnected",
    }[x.terminal];
    if (state)
      return {
        state,
        rawState: "visible_task_status:" + x.terminal,
        text: "",
        stopReason:
          { completed: "turn_complete", failed: "failed" }[x.terminal] ||
          x.terminal,
      };
  }
  if (x.stop || x.waitingTool)
    return { state: "running", rawState: "visible_stop_control", text: "" };
  return {
    state: "unknown",
    rawState: x.challenge ? "provider_challenge" : "no_reliable_state",
    text: x.challenge
      ? "Provider browser verification requires attention."
      : "",
  };
}
export { pageState };
