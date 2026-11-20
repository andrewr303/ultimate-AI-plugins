export const VERSION = 1;
export const HOME = 'https://claude.ai/code';
export const HOST = 'com.sessioncontrol.chrome';
export const COLORS = ['peach', 'violet', 'sage', 'blue', 'gold'];
export const STATUSES = { saved: 'Saved', running: 'In progress', attention: 'Needs attention', done: 'Done', paused: 'Paused' };
export const uid = () => crypto.randomUUID();
export const cleanText = (v, max = 160) => typeof v === 'string' ? v.trim().slice(0, max) : '';
export function cloudUrl(value) {
  let u;
  try { u = new URL(value); } catch { throw Error('Paste a complete https://claude.ai/code session URL.'); }
  if (u.protocol !== 'https:' || u.hostname !== 'claude.ai' || u.port || u.username || u.password || !/^\/code(?:\/[A-Za-z0-9_-]+)*\/?$/.test(u.pathname)) {
    throw Error('Use a Claude Code URL beginning with https://claude.ai/code.');
  }
  return `https://claude.ai${u.pathname.replace(/\/$/, '')}`;
}
export function emptyState() {
  return { version: VERSION, accounts: [], workspaces: [{ id: 'personal', name: 'Personal', icon: 'user' }], sessions: [], activity: [], settings: { compact: false } };
}
const idOK = x => typeof x === 'string' && /^[a-zA-Z0-9_-]{1,80}$/.test(x);
export function validateState(raw) {
  if (!raw || raw.version !== VERSION || !Array.isArray(raw.accounts) || !Array.isArray(raw.sessions) || !Array.isArray(raw.workspaces)) throw Error('This is not a supported Session Control backup.');
  if (raw.accounts.length > 100 || raw.sessions.length > 5000 || raw.workspaces.length > 100) throw Error('Backup exceeds the supported size.');
  const ids = new Set();
  const checkId = id => { if (!idOK(id) || ids.has(id)) throw Error('Backup has invalid or duplicate IDs.'); ids.add(id); return id; };
  const accounts = raw.accounts.map(a => {
    if (!a || !['isolated', 'current'].includes(a.mode) || !COLORS.includes(a.color) || !cleanText(a.name)) throw Error('Backup has an invalid account.');
    if (a.mode === 'isolated' && !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(a.profileId || '')) throw Error('Backup has an invalid profile ID.');
    return { id: checkId(a.id), name: cleanText(a.name, 60), email: cleanText(a.email, 120), color: a.color, mode: a.mode, profileId: a.profileId };
  });
  if (accounts.filter(a => a.mode === 'current').length > 1) throw Error('Only one account can use the current Chrome profile.');
  const profileIds = accounts.filter(a => a.mode === 'isolated').map(a => a.profileId);
  if (new Set(profileIds).size !== profileIds.length) throw Error('Isolated accounts must have different profile IDs.');
  const workspaces = raw.workspaces.map(w => { if (!w || !cleanText(w.name)) throw Error('Invalid workspace.'); return { id: checkId(w.id), name: cleanText(w.name, 40), icon: ['user','folder','book','code','gear'].includes(w.icon) ? w.icon : 'folder' }; });
  if (!workspaces.length) throw Error('Keep at least one workspace.');
  const sessions = raw.sessions.map(s => {
    if (!s || !accounts.some(a => a.id === s.accountId) || !workspaces.some(w => w.id === s.workspaceId) || !Object.hasOwn(STATUSES,s.status) || !cleanText(s.title)) throw Error('A session has invalid account, workspace, title or status.');
    return { id: checkId(s.id), accountId: s.accountId, workspaceId: s.workspaceId, title: cleanText(s.title), url: cloudUrl(s.url), notes: cleanText(s.notes, 20000), repository: cleanText(s.repository, 120), branch: cleanText(s.branch, 120), status: s.status, pinned: !!s.pinned, archived: !!s.archived, updatedAt: Number.isFinite(s.updatedAt) ? s.updatedAt : Date.now(), createdAt: Number.isFinite(s.createdAt) ? s.createdAt : Date.now() };
  });
  return { version: VERSION, accounts, workspaces, sessions, activity: Array.isArray(raw.activity) ? raw.activity.slice(0, 100).map(a=>({id:cleanText(a?.id), text:cleanText(a?.text,300), at:Number.isFinite(a?.at)?a.at:Date.now()})) : [], settings: { compact: !!raw.settings?.compact } };
}
export function activity(state, text) {
  state.activity.unshift({ id: uid(), text: cleanText(text, 300), at: Date.now() });
  state.activity = state.activity.slice(0, 100);
}
export function sampleState() {
  const state = emptyState();
  state.workspaces.push({id:'client', name:'Client Work',icon:'folder'}, {id:'research',name:'Research',icon:'book'}, {id:'automation',name:'Automation',icon:'gear'});
  state.accounts = [ ['a1','Personal','personal@example.com','peach'], ['a2','HypeStake','work@example.com','violet'], ['a3','Meridian','team@example.com','sage'] ].map(([id,name,email,color])=>({id,name,email,color,mode:'isolated',profileId:uid()}));
  const data = [
    ['AI assistant desktop/mobile layouts','a2','client','attention','HypeStake / hypestake','cloud / assistant-layouts','Bring the assistant into the brand system.\n\nNext up\n• Review the desktop sidebar and mobile layout\n• Check focus states and keyboard navigation\n• Package the design tokens and README'],
    ['Agent-smith plugin expansion','a1','personal','running','Personal / agent-smith','feature / plugin-expansion','Review the new plugin commands and update the integration guide.'],
    ['Marketing campaign plugin improvements','a2','client','running','HypeStake / campaign-studio','feature / campaign-tools','Validate the new campaign flow and export options.'],
    ['Time blocking in board view','a3','client','done','Meridian / workspace','fix / time-blocking','Ready for review. Check the daily and weekly board layouts.'],
    ['GPT model integration research','a1','research','saved','Personal / experiments','','Compare integration approaches before choosing a direction.'],
    ['Signup page formatting updates','a2','client','paused','HypeStake / web','fix / signup-spacing','Revisit spacing at small viewport sizes.']
  ];
  state.sessions=data.map(([title,accountId,workspaceId,status,repository,branch,notes],i)=>({id:`s${i}`,title,accountId,workspaceId,status,repository,branch,notes,pinned:i===0,archived:false,url:`${HOME}/sample-${i}`,createdAt:Date.now()-86400000,updatedAt:Date.now()-i*3600000}));
  state.activity = [{id:'demo-event',text:'Sample workspace — explore without changing your saved data.',at:Date.now()}];
  return state;
}
