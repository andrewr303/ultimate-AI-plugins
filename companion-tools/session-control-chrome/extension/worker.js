import { HOME, HOST, cloudUrl } from './model.js';
import { readProviderPage } from './vendor/page-reader.js';
import { pageState } from './vendor/page-state.js';
const dashboardUrl = () => chrome.runtime.getURL('dashboard.html');
async function dashboard(capture) {
  if (capture?.url) await chrome.storage.session.set({ capture });
  const tabs = await chrome.runtime.getContexts({contextTypes:['TAB'],documentUrls:[dashboardUrl()]});
  if (tabs.length) { await chrome.tabs.update(tabs[0].tabId, { active: true }); await chrome.windows.update(tabs[0].windowId, { focused: true }); }
  else await chrome.tabs.create({ url: dashboardUrl() });
}
chrome.action.onClicked.addListener(()=>dashboard());
chrome.commands.onCommand.addListener(c=>{if(c==='open-dashboard') dashboard();});
chrome.runtime.onInstalled.addListener(async ()=>{
  await chrome.storage.local.setAccessLevel({ accessLevel: 'TRUSTED_CONTEXTS' });
  chrome.contextMenus.removeAll(()=>chrome.contextMenus.create({id:'save-session',title:'Save to Session Control',contexts:['page'],documentUrlPatterns:['https://claude.ai/code*']}));
});
chrome.contextMenus.onClicked.addListener(async (info,tab)=>{
  if(info.menuItemId !== 'save-session') return;
  try {
    const url=cloudUrl(info.pageUrl);
    let observation=null;
    try {
      const [page]=await chrome.scripting.executeScript({target:{tabId:tab.id},func:readProviderPage});
      observation={state:pageState(page.result).state,at:Date.now()};
    } catch { /* Saving a link still works when the page cannot be read. */ }
    await dashboard({url,title:tab.title || 'Claude Code session',observation});
  } catch { await dashboard(); }
});
function native(message) {
  return new Promise((resolve,reject)=>chrome.runtime.sendNativeMessage(HOST,message,result=>{
    const err=chrome.runtime.lastError;
    if(err) reject(Error('Mac helper unavailable. Open Settings → Mac helper for setup.'));
    else if(!result?.ok) reject(Error(result?.error || 'The Mac helper could not complete this request.'));
    else resolve(result);
  }));
}
chrome.runtime.onMessage.addListener((msg,sender,respond)=>{
  if(sender.id !== chrome.runtime.id || sender.url !== dashboardUrl()) return;
  (async()=>{
    if(msg?.type === 'helper-ping') return native({type:'ping'});
    if(msg?.type === 'open-session') {
      const {state}=await chrome.storage.local.get('state');
      const account=state?.accounts.find(a=>a.id===msg.accountId);
      if(!account) throw Error('Account no longer exists.');
      let url=HOME;
      if(msg.sessionId) {
        const session=state.sessions.find(s=>s.id===msg.sessionId && s.accountId===account.id);
        if(!session) throw Error('Session does not belong to this account.');
        url=cloudUrl(session.url);
      }
      if(account.mode==='current') { await chrome.tabs.create({url}); return {ok:true,mode:'current'}; }
      return native({type:'open',profileId:account.profileId,url});
    }
    throw Error('Unknown dashboard action.');
  })().then(result=>respond({ok:true,result}),e=>respond({ok:false,error:e.message}));
  return true;
});
