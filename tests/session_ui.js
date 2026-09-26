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
