const {test}=require('node:test');
const assert=require('node:assert/strict');
const model=import('../extension/model.js');
test('only HTTPS Claude Code paths are accepted and tracking data is stripped',async()=>{
  const {cloudUrl}=await model;
  assert.equal(cloudUrl('https://claude.ai/code/session_123/?utm_source=test#x'),'https://claude.ai/code/session_123');
  for(const url of ['javascript:alert(1)','https://evil.test/code/a','https://claude.ai.evil.test/code/a','http://claude.ai/code/a','https://user:pass@claude.ai/code','https://claude.ai:8080/code','https://claude.ai/chat/abc','https://claude.ai/code/%2e%2e/settings'])assert.throws(()=>cloudUrl(url));
});
test('a valid workspace roundtrips without turning notes into markup',async()=>{
  const {sampleState,validateState}=await model;const s=sampleState();s.sessions[0].notes='<script>alert(1)</script>';
  assert.deepEqual(validateState(JSON.parse(JSON.stringify(s))),s);
});
test('backups reject duplicate profiles and dangling account/workspace references',async()=>{
  const {sampleState,validateState}=await model;
  let s=sampleState();s.accounts[1].profileId=s.accounts[0].profileId;assert.throws(()=>validateState(s),/different profile/);
  s=sampleState();s.sessions[0].accountId='missing';assert.throws(()=>validateState(s),/invalid account/);
  s=sampleState();s.sessions[0].workspaceId='missing';assert.throws(()=>validateState(s),/invalid account/);
  s=sampleState();s.sessions[0].id=s.accounts[0].id;assert.throws(()=>validateState(s),/duplicate/);
  s=sampleState();s.accounts[0].mode=s.accounts[1].mode='current';assert.throws(()=>validateState(s),/Only one/);
  s=sampleState();s.sessions[0].status='completed-by-silence';assert.throws(()=>validateState(s),/invalid/);
  s=sampleState();s.sessions[0].status='toString';assert.throws(()=>validateState(s),/invalid/);
});
test('starter status normalizer preserves unknown and never infers completion from silence',async()=>{
  const {pageState}=await import('../extension/vendor/page-state.js');
  assert.equal(pageState({}).state,'unknown');assert.equal(pageState({stop:true}).state,'running');
  assert.equal(pageState({terminal:'completed'}).state,'turn_complete');assert.equal(pageState({login:true}).rawState,'login_required');
});
