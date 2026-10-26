// Execute the actual app scripts against a DOM, storage, timers and mocked transport/audio.
const assert=require('node:assert/strict'),fs=require('node:fs');
const {JSDOM}=require(process.env.PLOT_JSDOM||'jsdom');
const page=fs.readFileSync('static/kyc.html','utf8'),inline=page.split('<script>',2)[1].split('</script>',1)[0],experienceCss=fs.readFileSync('static/experience.css','utf8');
const markup=page.replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,'');
const dom=new JSDOM(markup,{url:'https://plot.test/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window,errors=[],requests=[];w.addEventListener('error',e=>errors.push(e.message));
let clock=10000,notes=0,stops=0,intervals=[];w.Date.now=()=>clock;
w.setInterval=fn=>{intervals.push(fn);return intervals.length};
w.HTMLElement.prototype.scrollIntoView=function(){};
w.fetch=async(url,options={})=>{requests.push({url:String(url),options});return {ok:true,json:async()=>String(url).includes('/api/chat/')?({messages:[]}):({language:'he',copy:{},topics:{}})}};
w.AbortController=AbortController;
class AudioContext{constructor(){this.currentTime=0;this.state='running'}resume(){this.state='running';return Promise.resolve()}suspend(){this.state='suspended';return Promise.resolve()}createOscillator(){return {frequency:{setValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},start(){notes++},stop(){stops++},disconnect(){}}}createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},disconnect(){}}}}
w.AudioContext=AudioContext;
function script(source){const el=w.document.createElement('script');el.textContent=source;w.document.body.appendChild(el)}
script(inline);script(fs.readFileSync('static/companion-copy.js','utf8'));script(fs.readFileSync('static/experience.js','utf8'));
function data(round=0){return {code:'TEST1',image_run:1,round,total:8,status:'playing',is_host:true,players:[{id:1,name:'ערן',gender:'male',score:1,active:true,connected:true},{id:2,name:'אבי',score:1,active:true,connected:true}],me:{id:1,score:1,has_photo:false},subject:{id:1,name:'ערן',has_photo:false},topics:[],topics_display:[],spice:1,rounds:8,mode:'duo',language:'he',options:['כן','לא'],question:'בדיקה',answer:'כן',reveal:false,all_guesses:[],waiting_for:[],tiebreak:{},winner_ids:[1,2],history:[],hero_eligible:false,hero_status:'idle',ai_images_ready:false};}
const $=id=>w.document.getElementById(id);
script(fs.readFileSync('static/first-game.js','utf8'));
(async()=>{
 await new Promise(r=>setImmediate(r));
 w.mode('create');assert($('hostIntro').classList.contains('hidden'));assert(!$('create').classList.contains('hidden'));
 assert.equal($('advancedSetup').open,false);assert.equal(w.eval('rounds'),8);assert.equal(w.eval('audienceType'),'friends');
 assert($('cname').closest('#quickSetup'));assert($('audienceTypes').closest('#quickSetup'));assert($('topics').closest('#advancedSetup'));
 assert.equal(w.document.querySelectorAll('#cname').length,1);
 const before=requests.length;$('exampleRoundBtn').click();assert(w.document.querySelector('[role="dialog"]'));w.document.querySelector('[data-demo="1"]').click();assert(!w.document.querySelector('.demoAnswer').classList.contains('hidden'));assert.equal(requests.length,before,'demo has no network call or trial consumption');w.document.querySelector('.demoClose').click();
 const lobby={...data(),status:'lobby',photo_count:0,adult_required:false,adults_ready:true};w.render(lobby);assert(!$('start').disabled,'two players can start without photos');assert($('photoBox').classList.contains('hidden'));assert(!$('photoToggle').classList.contains('hidden'));$('photoToggle').click();assert(!$('photoBox').classList.contains('hidden'));assert.equal($('photoConsent').checked,false);
 w.render({...lobby,adult_required:true,adults_ready:false});assert($('start').disabled,'adult confirmation still required');
 w.render({...data(),reveal:true,hero_eligible:true,ai_images_ready:true,hero_status:'running'});assert(!$('next').disabled,'image never gates next');assert($('photoToggle').classList.contains('hidden'));
 const final={...data(7),status:'finished',reveal:true,final_image_eligible:false,relationships:[{guesser_id:2,subject_id:1,correct:2,attempts:3}]};w.render(final);assert(!$('relationshipCard').classList.contains('hidden'));assert($('relationshipCard').textContent.includes('2/3'));assert(!$('saveResultCard').classList.contains('hidden'));assert($('pilotCostReport').classList.contains('hidden'),'implementation costs not in player flow');
 for(const language of ['en','he','es','pt-BR','fr','ja']){w.document.documentElement.lang=language;await new Promise(r=>setImmediate(r));assert($('createRoomBtn').textContent.length>0);assert($('photoHelp').textContent.length>0)}
 assert.equal(errors.length,0,errors.join('\n'));console.log('FIRST_GAME_QUICK_SETUP_DEMO_OPTIONAL_PHOTOS_ADULT_GATE_IMAGES_RELATIONSHIPS_LOCALES_OK');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
