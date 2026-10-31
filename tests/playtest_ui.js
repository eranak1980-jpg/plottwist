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
w.fetch=async(url,options={})=>{requests.push({url:String(url),options});return {ok:true,json:async()=>String(url).includes('/api/access')?({paid_games:process.env.MIPO_TEST_PAID?'1':0}):String(url).includes('/api/chat/')?({messages:[]}):({language:'he',copy:{},topics:{}})}};
w.AbortController=AbortController;
class AudioContext{constructor(){this.currentTime=0;this.state='running'}resume(){this.state='running';return Promise.resolve()}suspend(){this.state='suspended';return Promise.resolve()}createOscillator(){return {frequency:{setValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},start(){notes++},stop(){stops++},disconnect(){}}}createGain(){return {gain:{setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},disconnect(){}}}}
w.AudioContext=AudioContext;
function script(source){const el=w.document.createElement('script');el.textContent=source;w.document.body.appendChild(el)}
script(inline);script(fs.readFileSync('static/companion-copy.js','utf8'));script(fs.readFileSync('static/experience.js','utf8'));
function data(round=0){return {code:'TEST1',image_run:1,round,total:8,status:'playing',is_host:true,players:[{id:1,name:'ערן',gender:'male',score:1,active:true,connected:true},{id:2,name:'אבי',score:1,active:true,connected:true}],me:{id:1,score:1,has_photo:false},subject:{id:1,name:'ערן',has_photo:false},topics:[],topics_display:[],spice:1,rounds:8,mode:'duo',language:'he',options:['כן','לא'],question:'בדיקה',answer:'כן',reveal:false,all_guesses:[],waiting_for:[],tiebreak:{},winner_ids:[1,2],history:[],hero_eligible:false,hero_status:'idle',ai_images_ready:false};}
const $=id=>w.document.getElementById(id);
script(fs.readFileSync('static/first-game.js','utf8'));
script(fs.readFileSync('static/playtest.js','utf8'));
(async()=>{
 await new Promise(r=>setImmediate(r));
 assert.equal(w.localStorage.getItem('plot_voice'),null);assert.equal($('voiceToggle').getAttribute('aria-pressed'),'false');
 assert.equal($('quickImages').checked,false,'fast mode is default');
 $('quickAdult').click();assert.equal(w.eval('spice'),3);assert.equal($('adultOptions').open,true);assert.equal($('adultConfirm').checked,false,'do not auto-consent');
 w.eval("audienceType='family'");w.renderAudience();assert($('quickAdult').closest('label').classList.contains('hidden'));assert.notEqual(w.eval('spice'),3);
 w.eval("audienceType='friends'");w.renderAudience();
 $('quickAdult').click();await new Promise(r=>setImmediate(r));assert.equal(w.eval('spice'),3,'adult choice survives details toggle');
 $('quickAdult').click();assert.equal(w.eval('spice'),1);
 await w.req('/api/create',{name:'QA'});assert.equal(JSON.parse(requests.at(-1).options.body).ai_images_enabled,false);
 $('quickImages').click();await w.req('/api/create',{name:'QA'});assert.equal(JSON.parse(requests.at(-1).options.body).ai_images_enabled,true);
 $('advancedSetup').open=false;delete $('advancedSetup').dataset.used;
 w.mode('create');assert($('hostIntro').classList.contains('hidden'));assert(!$('create').classList.contains('hidden'));
 assert.equal($('advancedSetup').open,false);assert.equal(w.eval('rounds'),process.env.MIPO_TEST_PAID?18:8);assert.equal(w.eval('audienceType'),'friends');
 assert($('cname').closest('#quickSetup'));assert($('audienceTypes').closest('#quickSetup'));assert($('topics').closest('#advancedSetup'));
 assert.equal(w.document.querySelectorAll('#cname').length,1);
 const before=requests.length;$('exampleRoundBtn').click();assert(w.document.querySelector('[role="dialog"]'));w.document.querySelector('[data-demo="1"]').click();assert(!w.document.querySelector('.demoAnswer').classList.contains('hidden'));assert.equal(requests.length,before,'demo has no network call or trial consumption');w.document.querySelector('.demoClose').click();
 const lobby={...data(),status:'lobby',photo_count:0,adult_required:false,adults_ready:true};w.render(lobby);assert(!$('lobbyImages').closest('label').classList.contains('hidden'));assert(!$('start').disabled,'two players can start without photos');assert($('photoBox').classList.contains('hidden'));assert(!$('photoToggle').classList.contains('hidden'));$('photoToggle').click();assert(!$('photoBox').classList.contains('hidden'));assert.equal($('photoConsent').checked,false);
 w.render({...lobby,adult_required:true,adults_ready:false});assert($('start').disabled,'adult confirmation still required');
 w.render({...data(),reveal:true,hero_eligible:true,ai_images_ready:true,hero_status:'running'});assert(!$('next').disabled,'image never gates next');assert($('photoToggle').classList.contains('hidden'));
 const final={...data(7),status:'finished',reveal:true,final_image_eligible:false,relationships:[{guesser_id:2,subject_id:1,correct:2,attempts:3}]};w.render({...final,round_insights:[{subject:'ערן',question:'שאלה',answer:'כן',correct:0,attempts:2}]});assert($('playtestHighlights').textContent.includes('0/2'));assert($('revealTalk').classList.contains('hidden'));assert(!$('relationshipCard').classList.contains('hidden'));assert($('relationshipCard').textContent.includes('2/3'));assert(!$('saveResultCard').classList.contains('hidden'));assert($('pilotCostReport').classList.contains('hidden'),'implementation costs not in player flow');
 for(const language of ['en','he','es','pt-BR','fr','ja']){w.document.documentElement.lang=language;await new Promise(r=>setImmediate(r));assert($('createRoomBtn').textContent.length>0);assert($('photoHelp').textContent.length>0)}
 assert.equal(errors.length,0,errors.join('\n'));console.log('PLAYTEST_FAST_IMAGES_VISIBLE_ADULT_GATE_FAMILY_RESET_VOICE_OPT_IN_HIGHLIGHTS_LOCALES_OK');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
