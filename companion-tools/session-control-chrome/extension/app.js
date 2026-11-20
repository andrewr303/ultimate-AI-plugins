import { HOME, COLORS, STATUSES, uid, cleanText, cloudUrl, emptyState, validateState, sampleState, activity } from './model.js';
const $ = s => document.querySelector(s);
const esc = x => String(x ?? '').replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const paths = {
  star:'M12 2v20M2 12h20M5 5l14 14M5 19 19 5M8 2l8 20M2 8l20 8M2 16l20-8M8 22l8-20',
  home:'m3 11 9-8 9 8M5 10v10h5v-6h4v6h5V10',user:'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0ZM4 21v-2a8 8 0 0 1 16 0v2Z',
  users:'M15 21v-2a6 6 0 0 0-12 0v2M13 3a4 4 0 0 1 0 8M21 21v-2a6 6 0 0 0-4-5M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  code:'m8 6-6 6 6 6m8-12 6 6-6 6m-3-15-2 18',folder:'M3 7V4h6l3 3h9v13H3Z',
  layers:'m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 16l10 5 10-5',activity:'M2 12h5l3-8 4 16 3-8h5',
  gear:'m9 3 6 0 1 3 3 1 2 5-2 2v3l-5 4-3-2-3 1-5-4 1-3-1-3 4-5Zm6 9a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  plus:'M12 5v14M5 12h14',arrow:'M5 12h14m-6-6 6 6-6 6',external:'M14 3h7v7m-11 4L21 3M10 3H3v18h18v-7',
  search:'M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Zm-2 5 6 6',cloud:'M6 18a5 5 0 0 1 0-10 6 6 0 0 1 11-2 6 6 0 0 1 1 12Z',
  book:'M12 5v16M12 5C9 2 4 3 2 4v15c4-2 7-1 10 2 3-3 6-4 10-2V4c-2-1-7-2-10 1Z',
  close:'m6 6 12 12M6 18 18 6',check:'m5 12 4 4L19 6',pin:'m9 3 9 9m-5-7-6 6 6 6 6-6M3 21l7-7M6 10l8 8',
  edit:'m4 16 12-12 4 4L8 20H4ZM14 6l4 4',trash:'M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7',
  branch:'M6 5v14m0-7c8 0 12-1 12-7M8 3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Zm0 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM20 3a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z',
  note:'M4 3h11l5 5v13H4ZM14 3v6h6M8 13h8m-8 4h5',download:'M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5',
  upload:'M12 16V4m-5 5 5-5 5 5M4 16v5h16v-5',lock:'M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5Zm7 4v3',
  monitor:'M2 3h20v14H2Zm10 14v4m-5 0h10',info:'M12 11v6m0-10v.1M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',archive:'M3 3h18v5H3Zm2 5v13h14V8m-10 4h6',copy:'M8 8h13v13H8ZM3 16V3h13'
};
const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${paths[name] || paths.folder}"/></svg>`;
const avatar = a => `<span class="avatar ${a.color}">${esc(a.name.slice(0,1).toUpperCase())}</span>`;
const time = ts => new Date(ts).toLocaleString(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
const ago = ts => { const m=Math.max(0,Math.floor((Date.now()-ts)/60000)); return m<1?'Just now':m<60?`${m}m ago`:m<1440?`${Math.floor(m/60)}h ago`:`${Math.floor(m/1440)}d ago`; };
let state, realState, demo=false, view='sessions', workspace='all', accountFilter='all', statusFilter='all', search='', selectedId=null, showArchived=false, helper='unknown', capture=null, busy=false;
let toastTimer;
function toast(message) { $('#toast').textContent=message; $('#toast').classList.add('show'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),5000); }
document.defaultView.addEventListener('pagehide',()=>clearTimeout(toastTimer));
async function message(data) { const r=await chrome.runtime.sendMessage(data); if(!r?.ok) throw Error(r?.error || 'The extension did not respond. Please reload it in chrome://extensions.'); return r.result; }
async function commit(change) {
  if(busy) throw Error('A save is in progress. Please try again.');
  busy=true;
  try {
    const next=structuredClone(state); change(next); const valid=validateState(next);
    if(!demo) await chrome.storage.local.set({state:valid});
    state=valid;
    if(!demo) realState=state;
  } finally { busy=false; }
}
const account = id => state.accounts.find(a=>a.id===id);
function visibleSessions() {
  return state.sessions.filter(s=>s.archived===showArchived && (workspace==='all'||s.workspaceId===workspace) && (accountFilter==='all'||s.accountId===accountFilter) && (statusFilter==='all'||s.status===statusFilter) && `${s.title} ${s.notes} ${s.repository} ${s.branch} ${account(s.accountId)?.name}`.toLowerCase().includes(search.toLowerCase())).sort((a,b)=>Number(b.pinned)-Number(a.pinned)||b.updatedAt-a.updatedAt);
}
function header(title,subtitle,action='new-session',label='Save session',eyebrow='YOUR CLOUD WORKBENCH') {
  return `<header class="page-header"><div class="heading-copy"><div class="eyebrow">${eyebrow}</div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div>${action?`<button class="btn primary" data-action="${action}">${icon('plus')}${label}</button>`:''}</header>`;
}
function render() {
  const live=state.sessions.filter(s=>!s.archived);
  const nav=[['overview','home','Overview'],['sessions','code','Sessions'],['accounts','users','Accounts'],['workspaces','layers','Workspaces'],['activity','activity','Activity'],['settings','gear','Settings']];
  $('#app').innerHTML=`<div class="shell ${state.settings.compact?'compact':''}">
    <header class="brand"><span class="brand-mark">${icon('star')}</span><div><div class="brand-title">Claude Code</div><div class="brand-subtitle">Session Control <span class="muted">/ independent companion</span></div></div><div class="brand-right"><span class="brand-subtitle">A little less tab chaos.</span><span class="local-pill">${icon('lock')} Saved on this Mac</span><button class="icon-btn" data-action="settings" aria-label="Open settings">${icon('gear')}</button></div></header>
    <aside class="sidebar" aria-label="Main navigation"><nav class="nav">${nav.map(([id,ic,label])=>`<button data-action="nav" data-id="${id}" class="${view===id?'active':''}" ${view===id?'aria-current="page"':''} title="${label}">${icon(ic)}<span class="nav-label">${label}</span>${id==='sessions'?`<span class="count">${live.length}</span>`:''}</button>`).join('')}</nav>
    <div><div class="sidebar-label">Your accounts</div>${state.accounts.map(a=>`<button class="account-nav ${a.color}" data-action="filter-account" data-id="${a.id}"><span class="dot"></span><span>${esc(a.name)}</span><span class="count">${live.filter(s=>s.accountId===a.id).length}</span></button>`).join('')}${!state.accounts.length?'<div class="sidebar-label muted">No accounts yet</div>':''}</div>
    <div class="sidebar-bottom"><strong>${icon('cloud')} Your accounts, together</strong><p>One dashboard.<br>Separate, persistent logins.</p><button data-action="new-account">＋ Add an account</button></div></aside>
    <div class="main-wrap"><nav class="workspace-bar" aria-label="Workspace filter"><button class="workspace ${workspace==='all'?'selected':''}" data-action="workspace" data-id="all">${icon('layers')}All sessions</button>${state.workspaces.map(w=>`<button class="workspace ${workspace===w.id?'selected':''}" data-action="workspace" data-id="${w.id}">${icon(w.icon)}${esc(w.name)}</button>`).join('')}<span class="workspace-spacer"></span><button class="icon-btn" data-action="new-workspace" aria-label="Add workspace">${icon('plus')}</button></nav>
    <main id="main" class="workbench" tabindex="-1">${demo?`<div class="hint-bar demo-bar">${icon('info')}<p>Sample workspace · Fictional sessions. Your saved data is separate.</p><button data-action="exit-demo">Exit preview</button></div>`:!state.accounts.length?'':helper!=='ready'&&state.accounts.some(a=>a.mode==='isolated')?`<div class="hint-bar">${icon('lock')}<p>Finish Mac helper setup to open accounts in their own Chrome profiles.</p><button data-action="settings">Set up helper</button></div>`:''}${renderPage()}</main></div></div>`;
}
function renderPage() {
  if(view==='sessions') return renderSessions();
  if(view==='accounts') return renderAccounts();
  if(view==='workspaces') return renderWorkspaces();
  if(view==='activity') return `${header('Activity','A local history of changes made in this dashboard.',null)}<div class="content-pad">${state.activity.length?state.activity.map(a=>`<div class="activity-row"><span class="dot"></span><div><p>${esc(a.text)}</p><small>${time(a.at)}</small></div></div>`).join(''):'<div class="empty-small">Your activity will appear here as you organize sessions.</div>'}</div>`;
  if(view==='settings') return renderSettings();
  return renderOverview();
}
function onboarding() { return `<div class="empty-state"><div class="large-icon">${icon('code')}</div><div class="eyebrow">MAKE ROOM TO FOCUS</div><h2>One place. Every account.</h2><p>Bring your Claude Code cloud sessions together. Keep personal work and client projects close, with each account’s login safely in its own Chrome profile.</p><div class="empty-actions"><button class="btn primary" data-action="new-account">${icon('plus')}Add your first account</button><button class="btn" data-action="demo">Explore a sample workspace ${icon('arrow')}</button></div></div><div class="onboarding"><article><div class="step-number">01</div><h3>Add your accounts</h3><p>Give each account a name and a color. Choose an isolated Chrome profile.</p></article><article><div class="step-number">02</div><h3>Sign in once</h3><p>Install the small Mac helper, open an account, and sign in normally.</p></article><article><div class="step-number">03</div><h3>Keep sessions in reach</h3><p>Save session links, add notes, and pick up where you left off.</p></article></div>`; }
function renderSessions() {
  const title=workspace==='all'?'Your sessions':state.workspaces.find(w=>w.id===workspace)?.name || 'Your sessions';
  let out=header(title,'A calmer home for everything you’re working on.');
  if(!state.accounts.length) return out+onboarding();
  const sessions=visibleSessions();
  if(!sessions.some(s=>s.id===selectedId)) selectedId=sessions[0]?.id || null;
  out+=`<div class="toolbar"><label class="search">${icon('search')}<input id="search" type="search" aria-label="Search sessions" placeholder="Search sessions, notes, repositories…" value="${esc(search)}"><span class="kbd">⌘ K</span></label><select class="filter" id="account-filter" aria-label="Filter by account"><option value="all">All accounts</option>${state.accounts.map(a=>`<option value="${a.id}" ${accountFilter===a.id?'selected':''}>${esc(a.name)}</option>`).join('')}</select><select class="filter" id="status-filter" aria-label="Filter by status"><option value="all">All labels</option>${Object.entries(STATUSES).map(([v,n])=>`<option value="${v}" ${statusFilter===v?'selected':''}>${n}</option>`).join('')}</select><label class="archive-toggle"><input type="checkbox" id="show-archived" ${showArchived?'checked':''}>Archived</label></div>`;
  if(!sessions.length) return out+`<div class="empty-state"><div class="large-icon">${icon(search||statusFilter!=='all'?'search':'note')}</div><h2>${search||accountFilter!=='all'||statusFilter!=='all'?'No matches here':'A fresh space to work'}</h2><p>${search||accountFilter!=='all'||statusFilter!=='all'?'Try another search or clear your filters.':'Save a Claude Code session link and keep its context, notes, and account together.'}</p><div class="empty-actions"><button class="btn primary" data-action="new-session">${icon('plus')}Save a session</button><button class="btn" data-action="clear-filters">Clear filters</button></div></div>`;
  const s=sessions.find(s=>s.id===selectedId), a=account(s.accountId);
  out+=`<div class="session-layout"><section class="session-list" aria-label="Saved sessions">${state.accounts.map(acc=>{
    const group=sessions.filter(s=>s.accountId===acc.id); if(!group.length)return '';
    return `<div class="group-label ${acc.color}"><span class="dot"></span>${esc(acc.name)} <span class="muted">/ ${group.length}</span></div>${group.map(s=>`<button class="session-item ${s.id===selectedId?'selected':''}" data-action="select-session" data-id="${s.id}" aria-pressed="${s.id===selectedId}">${icon('code')}<span><span class="session-item-title">${esc(s.title)}</span><span class="session-item-meta"><span class="status-dot ${s.status}"></span>${STATUSES[s.status]}<span>·</span>${ago(s.updatedAt)}</span></span>${s.pinned?`<span class="pin">${icon('pin')}</span>`:''}</button>`).join('')}`;
  }).join('')}</section><article class="session-detail" aria-label="Session details"><div class="detail-top"><span class="status-pill ${s.status}"><span class="status-dot ${s.status}"></span>${STATUSES[s.status]}</span><small>Personal label</small><button class="icon-btn" data-action="pin-session" data-id="${s.id}" aria-label="${s.pinned?'Unpin':'Pin'} session" title="${s.pinned?'Unpin':'Pin'} session">${icon('pin')}</button><button class="icon-btn" data-action="edit-session" data-id="${s.id}" aria-label="Edit session">${icon('edit')}</button></div><h2>${esc(s.title)}</h2><div class="detail-sub">${avatar(a)}${esc(a.name)}<span class="muted">/</span>${esc(state.workspaces.find(w=>w.id===s.workspaceId)?.name)}</div><div class="detail-actions"><button class="btn primary" data-action="open-session" data-id="${s.id}">Open in ${esc(a.name)} ${icon('external')}</button><button class="btn" data-action="copy-session" data-id="${s.id}">${icon('copy')}Copy link</button></div><div class="section-label">${icon('note')}Your session notes</div><div class="notes ${s.notes?'':'empty'}">${s.notes?esc(s.notes):'Keep your next steps, decisions, or a handoff here.'}</div><button class="text-button" style="align-self:flex-start;margin:14px 0 28px" data-action="edit-session" data-id="${s.id}">${s.notes?'Edit notes':'Add a note'} →</button><footer class="detail-footer"><span>Saved ${time(s.createdAt)}</span><span>Updated ${ago(s.updatedAt)}</span></footer></article>
  <aside class="context" aria-label="Session context"><div class="context-section"><h3>Environment</h3><div class="context-row">${icon('cloud')}<div>${esc(a.name)}<small>${a.mode==='isolated'?'Isolated Chrome profile':'This Chrome profile'}</small></div></div><div class="context-row">${icon('folder')}<div>${s.repository?esc(s.repository):'No repository added'}<small>Repository · set by you</small></div></div><div class="context-row">${icon('branch')}<div>${s.branch?esc(s.branch):'No branch added'}<small>Branch · set by you</small></div></div><p class="context-note">Account labels are chosen by you. Sign in to the matching account in its Chrome window.</p></div><div class="context-section"><h3>Keep it organized</h3><label class="section-label" for="session-status">Session label</label><select id="session-status" class="filter">${Object.entries(STATUSES).map(([v,n])=>`<option value="${v}" ${s.status===v?'selected':''}>${n}</option>`).join('')}</select><p class="context-note">These labels are set by you. Live task status is not monitored.</p><button class="context-link" data-action="archive-session" data-id="${s.id}">${icon('archive')}${s.archived?'Restore session':'Archive session'}</button></div><div class="context-section"><h3>Back to the real thing</h3><p class="context-note">Conversations, files, permissions, and prompts stay in Claude. This is your launchpad.</p><button class="context-link" data-action="open-account" data-id="${a.id}">Open account home ${icon('external')}</button></div></aside></div>`;
  return out;
}
function renderAccounts() {
  return header('Your accounts','Separate logins. A shared place to find your work.','new-account','Add account')+(!state.accounts.length?onboarding():`<div class="content-pad"><div class="cards">${state.accounts.map(a=>`<article class="card"><div class="card-top">${avatar(a)}<div><h3>${esc(a.name)}</h3><small>${esc(a.email||'No email label')}</small></div></div><span class="status-pill">${icon('lock')}${a.mode==='isolated'?'Isolated Chrome profile':'This Chrome profile'}</span><div class="card-stat">${state.sessions.filter(s=>s.accountId===a.id&&!s.archived).length} saved sessions</div><p class="card-description">${a.mode==='isolated'?'The Mac helper keeps this account in a dedicated Chrome profile. Sign in once; Chrome retains the login.':'Uses the login already active in this Chrome profile. Only one account can use this mode.'}</p><div class="card-actions"><button class="btn primary" data-action="open-account" data-id="${a.id}">Open account ${icon('external')}</button><button class="btn" data-action="edit-account" data-id="${a.id}">Edit</button><button class="icon-btn" data-action="delete-account" data-id="${a.id}" aria-label="Remove ${esc(a.name)}">${icon('trash')}</button></div></article>`).join('')}</div><p class="context-note" style="margin-top:22px">Login state stays inside Chrome. Session Control does not read passwords or cookies. Account names and emails are labels, not verified identities.</p></div>`);
}
function renderWorkspaces() {
  return header('Workspaces','A little structure for your different kinds of work.','new-workspace','New workspace')+`<div class="content-pad"><div class="cards">${state.workspaces.map(w=>`<article class="card"><div class="card-top"><span style="color:var(--peach)">${icon(w.icon)}</span><h3>${esc(w.name)}</h3></div><div class="card-stat">${state.sessions.filter(s=>s.workspaceId===w.id&&!s.archived).length} saved sessions</div><div class="card-actions"><button class="btn" data-action="workspace" data-id="${w.id}">View sessions ${icon('arrow')}</button><button class="icon-btn" data-action="edit-workspace" data-id="${w.id}" aria-label="Edit ${esc(w.name)}">${icon('edit')}</button><button class="icon-btn" data-action="delete-workspace" data-id="${w.id}" aria-label="Remove ${esc(w.name)}" ${state.workspaces.length===1?'disabled':''}>${icon('trash')}</button></div></article>`).join('')}</div></div>`;
}
function renderOverview() {
  if(!state.accounts.length) return header('Welcome to your workbench','A home for your Claude Code cloud sessions.')+onboarding();
  const sessions=state.sessions.filter(s=>!s.archived), attention=sessions.filter(s=>s.status==='attention');
  return header('Room to focus','Every account, project, and next step within reach.')+`<div class="content-pad"><div class="stats"><div class="stat"><span>Saved sessions</span><strong>${sessions.length}</strong></div><div class="stat"><span>Accounts</span><strong>${state.accounts.length}</strong></div><div class="stat"><span>Labeled for attention</span><strong>${attention.length}</strong></div></div><div class="overview-grid"><section><div class="subheading"><h3>Pick up where you left off</h3><button class="text-button" data-action="nav" data-id="sessions">View all →</button></div>${sessions.sort((a,b)=>b.updatedAt-a.updatedAt).slice(0,6).map(s=>`<button class="recent-row" data-action="jump-session" data-id="${s.id}">${icon('code')}<span>${esc(s.title)}<small>${esc(account(s.accountId).name)} · ${STATUSES[s.status]}</small></span>${icon('arrow')}</button>`).join('')||'<p class="empty-small">Save your first session to get started.</p>'}</section><section><h3>A note for your future self</h3><article class="card"><span style="color:var(--peach)">${icon('note')}</span><p class="card-description">A session link gets you back to the conversation. A few notes get you back into the work.</p><p class="card-description">Add the next step, a decision to revisit, or the branch you’re working on.</p><button class="text-button" data-action="new-session">Save a session →</button></article></section></div></div>`;
}
function renderSettings() {
  const extid=chrome.runtime.id;
  return header('Make yourself at home','Your data stays local. Your logins stay in Chrome.',null)+`<div class="content-pad"><section class="settings-section"><div class="subheading"><h2>Mac helper</h2><span class="status-pill">${helper==='ready'?'Connected':helper==='checking'?'Checking…':'Not connected'}</span></div><p>Chrome tabs in one profile share a login. The helper opens a separate, persistent Chrome profile for each isolated account. It uses Chrome’s own profile storage and never copies credentials.</p><ol class="install-steps"><li><span>Install <strong>Google Chrome</strong> and <strong>Node.js 22 or newer</strong> on your Mac.</span></li><li><span>In the downloaded package, open <code>mac-helper/Install Mac Helper.command</code>. If needed, run it in Terminal with <code>bash</code>.</span></li><li><span>When asked, paste this extension ID:<br><code id="extension-id">${esc(extid)}</code> <button class="text-button" data-action="copy-id">Copy</button></span></li><li><span>Click <strong>Check connection</strong>, then open an account from Accounts and sign in to Claude.</span></li></ol><div class="settings-actions"><button class="btn primary" data-action="check-helper" ${helper==='checking'?'disabled':''}>${icon('check')}Check connection</button><button class="btn" data-action="copy-id">${icon('copy')}Copy extension ID</button></div><p class="context-note">The helper is for macOS only. It does not run a web server, install a background daemon, or change your existing browser profiles. Keep the unpacked extension folder at the same location so its ID stays stable.</p></section>
  <section class="settings-section"><h2>Workspace backup</h2><p>Export your account labels, profile IDs, session links, and notes as JSON. Logins and cookies are not included. A backup can contain private project names and notes.</p><div class="settings-actions"><button class="btn" data-action="export">${icon('download')}Export backup</button><button class="btn" data-action="import">${icon('upload')}Import backup</button></div><input type="file" id="backup-file" accept="application/json,.json" hidden></section>
  <section class="settings-section"><h2>Your preferences</h2><label class="settings-row"><span>Compact session list<small>Fit a few more sessions in the sidebar.</small></span><input id="compact-setting" type="checkbox" ${state.settings.compact?'checked':''}></label></section>
  <section class="settings-section"><h2>Save a session from Claude</h2><p>In this Chrome profile, right-click a Claude Code page and choose <strong>Save to Session Control</strong>. Review the account before saving. For isolated account windows, copy the session URL and use <strong>Save session</strong> here.</p><p>Live monitoring across accounts, in-tab embedded Claude, automatic replies, and subscription usage are not provided. Status, repository, and branch fields are your own labels.</p></section><section class="settings-section"><h2>Session Control <small>0.5.0</small></h2><p>Built from your Session Control Native 0.4.2 source, with a Chrome-first dashboard inspired by your screenshot. Independent companion; not affiliated with Anthropic.</p><button class="btn" data-action="demo">Explore sample workspace ${icon('arrow')}</button></section></div>`;
}
function modal(title,intro,fields,onSubmit,button='Save') {
  const d=$('#modal');
  d.innerHTML=`<form id="editor"><div class="modal-heading"><h2 id="modal-title">${esc(title)}</h2><button type="button" class="icon-btn" data-action="close-modal" aria-label="Close dialog">${icon('close')}</button></div><p class="modal-intro">${intro}</p>${fields}<p class="form-error" id="form-error" role="alert"></p><div class="form-actions"><button type="button" class="btn" data-action="close-modal">Cancel</button><button type="submit" class="btn primary">${button}${icon('check')}</button></div></form>`;
  d.showModal();
  $('#editor').addEventListener('submit',async e=>{
    e.preventDefault(); const b=e.submitter;b.disabled=true;$('#form-error').textContent='';
    try { await onSubmit(new FormData(e.target)); d.close(); render(); } catch(err) { $('#form-error').textContent=err.message; } finally { b.disabled=false; }
  });
}
function accountEditor(id) {
  const a=account(id), isEdit=!!a;
  modal(a?'Edit account':'Add an account','Give this login a name you’ll recognize. You’ll sign in directly in Chrome.',`
  <label for="account-name">Account name <span class="field-required">*</span></label><input id="account-name" name="name" required maxlength="60" placeholder="e.g. Personal, Client Work" value="${esc(a?.name||'')}">
  <label for="account-email">Email label <span class="muted">(optional)</span></label><input id="account-email" name="email" type="email" maxlength="120" placeholder="you@example.com" value="${esc(a?.email||'')}">
  <div class="form-grid"><div><label for="account-color">Account color</label><select id="account-color" name="color">${COLORS.map(c=>`<option value="${c}" ${a?.color===c?'selected':''}>${c[0].toUpperCase()+c.slice(1)}</option>`).join('')}</select></div><div><label for="account-mode">Login location</label><select id="account-mode" name="mode" ${isEdit?'disabled':''}><option value="isolated" ${a?.mode==='isolated'?'selected':''}>Isolated Chrome profile</option><option value="current" ${a?.mode==='current'?'selected':''}>This Chrome profile</option></select></div></div>
  <p class="form-warning">An isolated profile keeps this account signed in separately and requires the Mac helper. “This Chrome profile” uses the login already active here and is limited to one account.</p>${isEdit?'<p class="form-help">Login location stays fixed to preserve account isolation. Add a separate account to use another location.</p>':''}`,async fd=>{
    const name=cleanText(fd.get('name'),60), mode=a?.mode||fd.get('mode');
    if(!name) throw Error('Enter an account name.');
    if(mode==='current'&&state.accounts.some(x=>x.mode==='current'&&x.id!==id)) throw Error('This Chrome profile already has an account. Choose an isolated profile for another login.');
    await commit(s=>{ if(a) Object.assign(s.accounts.find(x=>x.id===id),{name,email:cleanText(fd.get('email'),120),color:fd.get('color')}); else s.accounts.push({id:uid(),name,email:cleanText(fd.get('email'),120),color:fd.get('color'),mode,profileId:uid()}); activity(s,`${a?'Updated':'Added'} account “${name}”.`); });
    toast(a?'Account updated.':'Account added. Open it from Accounts to sign in.');
  },a?'Save changes':'Add account');
}
function sessionEditor(id, seed) {
  if(!state.accounts.length) { toast('Add an account first so this session opens in the right place.'); accountEditor(); return; }
  const s=state.sessions.find(s=>s.id===id);
  const c=seed||{};
  modal(s?'Edit session':'Save a session',`Keep a link to the real conversation, plus the context you’ll want later.${c.observation?`<br><span class="muted">Visible page signal at capture: ${esc(c.observation.state)}. This is a one-time observation; the saved label starts as “Saved”.</span>`:''}`,`
  <label for="session-title">Session name <span class="field-required">*</span></label><input id="session-title" name="title" required maxlength="160" placeholder="What are you working on?" value="${esc(s?.title||c.title||'')}">
  <label for="session-url">Claude Code URL <span class="field-required">*</span></label><input id="session-url" name="url" type="url" required maxlength="2000" placeholder="https://claude.ai/code/session_…" value="${esc(s?.url||c.url||'')}"><p class="form-help">Paste the session’s address from Claude Code. The home URL opens a new session.</p>
  <div class="form-grid"><div><label for="session-account">Account <span class="field-required">*</span></label><select id="session-account" name="accountId">${state.accounts.map(a=>`<option value="${a.id}" ${(s?.accountId||accountFilter)===a.id?'selected':''}>${esc(a.name)}</option>`).join('')}</select></div><div><label for="session-workspace">Workspace</label><select id="session-workspace" name="workspaceId">${state.workspaces.map(w=>`<option value="${w.id}" ${(s?.workspaceId||workspace)===w.id?'selected':''}>${esc(w.name)}</option>`).join('')}</select></div></div>
  <div class="form-grid"><div><label for="session-repo">Repository <span class="muted">(optional)</span></label><input id="session-repo" name="repository" maxlength="120" placeholder="owner / repository" value="${esc(s?.repository||'')}"></div><div><label for="session-branch">Branch <span class="muted">(optional)</span></label><input id="session-branch" name="branch" maxlength="120" placeholder="feature / your-branch" value="${esc(s?.branch||'')}"></div></div>
  <label for="session-notes">Notes & next steps</label><textarea id="session-notes" name="notes" maxlength="20000" rows="5" placeholder="Where did you leave off?">${esc(s?.notes||'')}</textarea><p class="form-warning">Check the account before saving. The account label routes this link; it does not verify the identity logged in to Claude.</p>`,async fd=>{
    const title=cleanText(fd.get('title')),url=cloudUrl(fd.get('url')),accountId=fd.get('accountId'),workspaceId=fd.get('workspaceId');
    if(!title) throw Error('Enter a session name.');
    if(state.sessions.some(x=>x.id!==id&&x.accountId===accountId&&x.url===url&&!x.archived)) throw Error('This link is already saved for that account. Edit the existing session instead.');
    const values={title,url,accountId,workspaceId,notes:cleanText(fd.get('notes'),20000),repository:cleanText(fd.get('repository'),120),branch:cleanText(fd.get('branch'),120),updatedAt:Date.now()};
    const newId=id||uid();
    await commit(st=>{if(s) Object.assign(st.sessions.find(x=>x.id===id),values); else st.sessions.unshift({...values,id:newId,createdAt:Date.now(),status:'saved',pinned:false,archived:false});activity(st,`${s?'Updated':'Saved'} “${title}” in ${account(accountId).name}.`);});
    selectedId=newId;view='sessions';workspace='all';accountFilter='all';statusFilter='all';search='';showArchived=!!s?.archived;
    toast(s?'Session updated.':'Session saved.');
  },s?'Save changes':'Save session');
}
function workspaceEditor(id) {
  const w=state.workspaces.find(w=>w.id===id);
  modal(w?'Edit workspace':'New workspace','Group your work in a way that makes sense to you.',`<label for="workspace-name">Workspace name</label><input id="workspace-name" name="name" maxlength="40" required value="${esc(w?.name||'')}" placeholder="e.g. Client Work"><label for="workspace-icon">Icon</label><select id="workspace-icon" name="icon">${['folder','user','book','code','gear'].map(ic=>`<option value="${ic}" ${w?.icon===ic?'selected':''}>${({folder:'Folder',user:'Personal',book:'Research',code:'Code',gear:'Automation'})[ic]}</option>`).join('')}</select>`,async fd=>{
    const name=cleanText(fd.get('name'),40);if(!name)throw Error('Enter a workspace name.');
    await commit(st=>{if(w)Object.assign(st.workspaces.find(x=>x.id===id),{name,icon:fd.get('icon')});else st.workspaces.push({id:uid(),name,icon:fd.get('icon')});activity(st,`${w?'Updated':'Created'} workspace “${name}”.`);});toast('Workspace saved.');
  });
}
async function open(accountId,sessionId) {
  if(demo) { toast('Sample links don’t open real sessions. Exit preview to add your accounts.'); return; }
  const a=account(accountId);
  if(a.mode==='isolated'&&helper!=='ready') {
    try { await message({type:'helper-ping'});helper='ready'; } catch { view='settings';render();toast('Install the Mac helper to open isolated account profiles.');return; }
  }
  await message({type:'open-session',accountId,sessionId});
  await commit(s=>activity(s,`Sent ${sessionId?'session':'account home'} to ${a.name} in Chrome.`));
  toast(`Sent to ${a.name} in Chrome. Sign in there if needed.`);render();
}
async function checkHelper() {
  helper='checking';render();
  try { await message({type:'helper-ping'});helper='ready';toast('Mac helper connected. Your isolated accounts are ready to open.'); }
  catch(e) {helper='missing';toast(e.message);}
  render();
}
async function confirmAction(title,intro,fn,button='Remove') {
  modal(title,esc(intro),'',fn,button);
}
const actions = {
  nav:id=>{view=id;render();},settings:()=>{view='settings';render();},
  workspace:id=>{workspace=id;view='sessions';accountFilter='all';search='';statusFilter='all';render();},
  'filter-account':id=>{accountFilter=id;view='sessions';workspace='all';render();},
  'clear-filters':()=>{search='';accountFilter='all';statusFilter='all';render();},
  'select-session':id=>{selectedId=id;render();},
  'jump-session':id=>{selectedId=id;workspace='all';accountFilter='all';statusFilter='all';search='';showArchived=false;view='sessions';render();},
  'new-account':()=>accountEditor(), 'edit-account':id=>accountEditor(id),
  'new-session':()=>sessionEditor(), 'edit-session':id=>sessionEditor(id),
  'new-workspace':()=>workspaceEditor(), 'edit-workspace':id=>workspaceEditor(id),
  'close-modal':()=>$('#modal').close(),
  'open-account':id=>open(id), 'open-session':id=>{const s=state.sessions.find(s=>s.id===id);return open(s.accountId,id);},
  'copy-session':async id=>{await navigator.clipboard.writeText(state.sessions.find(s=>s.id===id).url);toast('Session link copied.');},
  'pin-session':async id=>{await commit(st=>{const s=st.sessions.find(s=>s.id===id);s.pinned=!s.pinned;});render();},
  'archive-session':async id=>{await commit(st=>{const s=st.sessions.find(s=>s.id===id);s.archived=!s.archived;s.updatedAt=Date.now();activity(st,`${s.archived?'Archived':'Restored'} “${s.title}”.`);});render();toast('Session moved. Use the Archived checkbox to view archived sessions.');},
  'delete-account':id=>{const a=account(id),n=state.sessions.filter(s=>s.accountId===id).length;return confirmAction('Remove account?',`Remove “${a.name}” and its ${n} saved session links from this dashboard? Chrome profiles, logins, and conversations will be kept. Export a backup in Settings if you want to restore these links later.`,async()=>{await commit(st=>{st.accounts=st.accounts.filter(a=>a.id!==id);st.sessions=st.sessions.filter(s=>s.accountId!==id);activity(st,`Removed account “${a.name}” from dashboard.`);});if(accountFilter===id)accountFilter='all';toast('Account removed from dashboard. Its Chrome profile is kept.');});},
  'delete-workspace':id=>{const w=state.workspaces.find(w=>w.id===id);return confirmAction('Remove workspace?',`Remove “${w.name}”? Its sessions will move to the first remaining workspace.`,async()=>{await commit(st=>{if(st.workspaces.length===1)throw Error('Keep at least one workspace.');st.workspaces=st.workspaces.filter(w=>w.id!==id);st.sessions.forEach(s=>{if(s.workspaceId===id)s.workspaceId=st.workspaces[0].id;});activity(st,`Removed workspace “${w.name}”.`);});if(workspace===id)workspace='all';toast('Workspace removed. Sessions kept.');});},
  'check-helper':checkHelper,
  'copy-id':async()=>{await navigator.clipboard.writeText(chrome.runtime.id);toast('Extension ID copied.');},
  demo:()=>{if(demo){toast('You’re already exploring the sample workspace.');return;}realState=state;state=sampleState();demo=true;workspace='all';accountFilter='all';statusFilter='all';search='';selectedId='s0';view='sessions';showArchived=false;render();},
  'exit-demo':()=>{state=realState;demo=false;workspace='all';accountFilter='all';statusFilter='all';search='';selectedId=null;showArchived=false;render();},
  export:()=>{const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`session-control${demo?'-sample':''}-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('Backup exported. It contains metadata and notes, not logins.');},
  import:()=>$('#backup-file').click()
};
document.addEventListener('click',e=>{
  const el=e.target.closest('[data-action]');if(!el||el.disabled)return;
  const action=actions[el.dataset.action];if(!action)return;
  Promise.resolve().then(()=>action(el.dataset.id)).catch(err=>toast(err.message));
});
document.addEventListener('input',e=>{
  if(e.target.id==='search') {const start=e.target.selectionStart;search=e.target.value;render();const input=$('#search');input.focus();input.setSelectionRange?.(start,start);}
});
document.addEventListener('change',async e=>{
  try {
    if(e.target.id==='account-filter'){accountFilter=e.target.value;render();}
    if(e.target.id==='status-filter'){statusFilter=e.target.value;render();}
    if(e.target.id==='show-archived'){showArchived=e.target.checked;render();}
    if(e.target.id==='session-status'){const val=e.target.value;await commit(st=>{const s=st.sessions.find(s=>s.id===selectedId);s.status=val;s.updatedAt=Date.now();activity(st,`Labeled “${s.title}” as ${STATUSES[val]}.`);});render();}
    if(e.target.id==='compact-setting'){const compact=e.target.checked;await commit(st=>{st.settings.compact=compact;});render();}
    if(e.target.id==='backup-file'){
      const file=e.target.files[0];if(!file)return;
      e.target.value='';if(file.size>5*1024*1024)throw Error('Choose a backup smaller than 5 MB.');
      const imported=validateState(JSON.parse(await file.text()));
      confirmAction('Replace dashboard data?',`This backup contains ${imported.accounts.length} accounts and ${imported.sessions.length} sessions. It will replace ${demo?'this sample workspace':'your saved dashboard metadata'}. Export your current data first if you want to keep it. Chrome logins are unchanged.`,async()=>{
        if(!demo)await chrome.storage.local.set({state:imported});state=imported;if(!demo)realState=state;workspace='all';accountFilter='all';statusFilter='all';search='';selectedId=null;toast('Backup imported. Isolated profiles retain their logins only on the original Mac.');
      },'Replace data');
    }
  }catch(err){toast(err.message);}
});
document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'&&!$('#modal').open){e.preventDefault();view='sessions';render();$('#search')?.focus();}
});
async function pendingCapture() {
  const result=await chrome.storage.session.get('capture');
  if(!result.capture)return;
  capture=result.capture;await chrome.storage.session.remove('capture');
  if(demo){state=realState;demo=false;render();}
  if(!state.accounts.length){toast('Add an account first. Then right-click the Claude session again to save it.');accountEditor();return;}
  sessionEditor(null,capture);capture=null;
}
chrome.storage.onChanged.addListener((changes,area)=>{if(area==='session'&&changes.capture?.newValue&&!$('#modal').open)pendingCapture().catch(e=>toast(e.message));});
try {
  const saved=await chrome.storage.local.get('state');
  state=saved.state?validateState(saved.state):emptyState();realState=state;render();
  await pendingCapture();
}catch(err){
  $('#app').innerHTML=`<main class="empty-state"><h1>We couldn’t load your workspace</h1><p>${esc(err.message)}</p><p>Your stored data has not been replaced. Try reloading the extension, or export the raw storage from Chrome’s extension inspector before resetting it.</p></main>`;
}
