// Execute production boot/session helpers against browser storage scenarios.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const page=fs.readFileSync('static/kyc.html','utf8');
const boot=page.slice(page.indexOf('function readStored('),page.indexOf('let deviceId='));
const old={code:'ROOMA',token:'a',host:'host-a',name:'Host'};
function run(search,stored){const data=new Map(Object.entries(stored));const ctx={URLSearchParams,location:{search,pathname:'/'},history:{replaceState(){}},localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)}};vm.createContext(ctx);vm.runInContext(boot,ctx);return {value:JSON.parse(vm.runInContext('JSON.stringify(s)',ctx)),ctx,data};}
let r=run('?new=1',{kyc:JSON.stringify(old)});assert.deepEqual(r.value,{});assert.deepEqual(JSON.parse(r.data.get('kyc')),{});assert.equal(JSON.parse(r.data.get('plot_rooms')).ROOMA.host,'host-a');
r=run('?code=ROOMA',{kyc:JSON.stringify({code:'ROOMB',token:'b'}),plot_rooms:JSON.stringify({ROOMA:old})});assert.equal(r.value.host,'host-a');
r=run('?code=NEW12',{kyc:JSON.stringify(old)});assert.deepEqual(r.value,{});assert.equal(JSON.parse(r.data.get('plot_rooms')).ROOMA.token,'a');
r=run('',{kyc:'malformed'});assert.deepEqual(r.value,{});
r=run('',{kyc:JSON.stringify(old)});assert.equal(r.value.code,'ROOMA');
console.log('SESSION_NEW_GAME_ROOM_SWITCH_REOPEN_CORRUPT_STORAGE_OK');

// A save completing during a poll must refresh immediately when that poll settles.
const loadSource=page.slice(page.indexOf('async function load('),page.indexOf('function maybeScoreboard'));
(async()=>{
 const requests=[],rendered=[],element={classList:{add(){},remove(){}},textContent:''};
 const ctx={s:{code:'ROOMA'},loading:false,refreshAfterLoad:false,connectionFailures:0,stateSig:'',uiLang:'en',copy:{},document:{hidden:false},window:{lastState:{}},$:()=>element,req:()=>new Promise(resolve=>requests.push(resolve)),render:d=>rendered.push(d.round)};
 vm.createContext(ctx);vm.runInContext(loadSource,ctx);
 const first=ctx.load(false);await ctx.load();assert.equal(requests.length,1,'no overlapping polls');
 requests[0]({code:'ROOMA',round:0});await new Promise(setImmediate);
 assert.equal(requests.length,2,'pending action triggers immediate follow-up');
 requests[1]({code:'ROOMA',round:1});await first;
 assert.deepEqual(rendered,[0,1]);assert.equal(ctx.loading,false);
 console.log('ACTION_REFRESH_DURING_POLL_OK');
})().catch(e=>{console.error(e);process.exitCode=1});
