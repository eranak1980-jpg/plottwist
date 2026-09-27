const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('static/experience.js','utf8');
let now=1000,notes=0,click,interval,stored={},button;
const status={classList:{contains:()=>false},querySelector:()=>null};
const doc={hidden:false,documentElement:{lang:'he'},getElementById:()=>status,
 querySelector:()=>({appendChild:b=>button=b}),
 createElement:()=>({setAttribute(k,v){this[k]=v}}),addEventListener:(kind,fn)=>click=fn};
class AudioContext{constructor(){this.currentTime=0;this.state='running'}createOscillator(){return {frequency:{setValueAtTime(){}},connect(){},start(){notes++},stop(){},disconnect(){}}}createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},disconnect(){}}}}
const win={AudioContext,req:async()=>({ok:true}),render(){},setImageGate(){}};
const env={window:win,document:doc,localStorage:{getItem:k=>stored[k],setItem:(k,v)=>stored[k]=v},Date:{now:()=>now},MutationObserver:class{observe(){}},setInterval:fn=>interval=fn};
vm.createContext(env);vm.runInContext(source,env);
assert.equal(notes,0,'no autoplay');assert.equal(button['aria-label'],'השתק צלילים');
click({target:{closest:()=>({disabled:false})}});assert.equal(notes,1);
button.onclick();assert.equal(stored.plot_sound,'off');now+=100;
click({target:{closest:()=>({disabled:false})}});assert.equal(notes,1,'muted clicks silent');
button.onclick();assert.equal(stored.plot_sound,'on');assert.equal(notes,2);
(async()=>{now+=100;assert.deepEqual(await win.req('/api/X/guess',{guess:'yes'}),{ok:true});assert.equal(notes,4);
now+=100;win.setImageGate({code:'X',image_run:1,round:0},false,'pending');win.setImageGate({code:'X',image_run:1,round:0},false,'ready');assert.equal(notes,6);
now+=100;win.setImageGate({code:'X',image_run:1,round:0},false,'ready');assert.equal(notes,6,'polling never repeats chime');
doc.hidden=true;now+=100;click({target:{closest:()=>({disabled:false})}});assert.equal(notes,6,'background silent');
console.log('SOUND_GESTURE_MUTE_PERSISTENCE_SAVE_IMAGE_DEDUP_HIDDEN_OK');
})().catch(e=>{console.error(e);process.exitCode=1});
