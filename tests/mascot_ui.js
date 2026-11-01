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
script(inline);script(fs.readFileSync('static/companion-copy.js','utf8'));script(fs.readFileSync('static/mascot.js','utf8'));script(fs.readFileSync('static/experience.js','utf8'));
function data(round=0){return {code:'TEST1',image_run:1,round,total:8,status:'playing',is_host:true,players:[{id:1,name:'ערן',gender:'male',score:1,active:true,connected:true},{id:2,name:'אבי',score:1,active:true,connected:true}],me:{id:1,score:1,has_photo:false},subject:{id:1,name:'ערן',has_photo:false},topics:[],topics_display:[],spice:1,rounds:8,mode:'duo',language:'he',options:['כן','לא'],question:'בדיקה',answer:'כן',reveal:false,all_guesses:[],waiting_for:[],tiebreak:{},winner_ids:[1,2],history:[],hero_eligible:false,hero_status:'idle',ai_images_ready:false};}
const $=id=>w.document.getElementById(id);
(async()=>{
 await new Promise(r=>setImmediate(r));
 assert.equal(w.MipoMascot.expression('win'),'celebrate');assert.equal(w.MipoMascot.expression('suspicious'),'suspicious');
 assert(!w.MipoMascot.html('<script>').includes('<script>'),'only approved mood keys in markup');
 assert(page.indexOf('/static/mascot.js')<page.indexOf('/static/experience.js'),'load the shared renderer first');
 function transition(round,guesses){const d={...data(round),answered:true,guess_need:guesses.length,guess_count:guesses.length};w.render(d);w.render({...d,reveal:true,all_guesses:guesses})}
 const guess=(id,choice,correct=false)=>({player_id:id,name:'Player '+id,guess:choice,correct});
 transition(0,[guess(2,'A'),guess(3,'A')]);assert.equal($('companionMoment').querySelector('[data-expression]').dataset.expression,'suspicious','same wrong guess beats a score tie');
 transition(1,[guess(2,'A'),guess(3,'B')]);assert.equal($('companionMoment').querySelector('[data-expression]').dataset.expression,'surprise');
 transition(2,[guess(2,'A',true),guess(3,'B')]);assert.equal($('companionMoment').querySelector('[data-expression]').dataset.expression,'wink');assert($('companionMoment').textContent.includes('Player 2'));
 const actor=$('companionMoment').querySelector('img');actor.dispatchEvent(new w.Event('error'));assert.equal(actor.closest('.mipoComic').style.visibility,'hidden');assert(!$('next').disabled,'missing art never blocks the next question');
 const waiting={...data(3),answered:true,guess_count:0,guess_need:1};w.render(waiting);assert.equal($('waiting').querySelector('[data-expression]').dataset.expression,'smirk');
 const final={...data(7),status:'finished',reveal:true,final_image_eligible:false};w.render(final);const winner=$('finishMascot').querySelector('img');assert(winner.src.includes('celebrate.webp'));w.render(final);assert.equal($('finishMascot').querySelector('img'),winner,'polling does not restart victory animation');
 assert.equal($('finishMascot').querySelectorAll('img').length,1);assert.equal(notes,0,'no unrequested speech or audio');
 assert(fs.readFileSync('static/mascot.css','utf8').includes('@media(prefers-reduced-motion:reduce)'));
 for(const pose of ['smirk','surprise','suspicious','wink','celebrate'])assert(fs.statSync('static/mascot/'+pose+'.webp').size<70000);
 assert.equal(errors.length,0,errors.join('\n'));console.log('COMIC_MASCOT_REAL_EVENT_MOODS_POLL_STABILITY_QUIET_WAITING_ACCESSIBILITY_ART_FAILURE_NONBLOCKING_OK');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
