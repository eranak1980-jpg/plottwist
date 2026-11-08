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
script(inline);script(fs.readFileSync('static/companion-copy.js','utf8'));script(fs.readFileSync('static/mascot.js','utf8'));script(fs.readFileSync('static/experience.js','utf8'));
function data(round=0){return {code:'TEST1',image_run:1,round,total:8,status:'playing',is_host:true,players:[{id:1,name:'ערן',gender:'male',score:1,active:true,connected:true},{id:2,name:'אבי',score:1,active:true,connected:true}],me:{id:1,score:1,has_photo:false},subject:{id:1,name:'ערן',has_photo:false},topics:[],topics_display:[],spice:1,rounds:8,mode:'duo',language:'he',options:['כן','לא'],question:'בדיקה',answer:'כן',reveal:false,all_guesses:[],waiting_for:[],tiebreak:{},winner_ids:[1,2],history:[],hero_eligible:false,hero_status:'idle',ai_images_ready:false};}
const $=id=>w.document.getElementById(id);
script(fs.readFileSync('static/first-game.js','utf8'));
script(fs.readFileSync('static/playtest.js','utf8'));
(async()=>{
 await new Promise(r=>setImmediate(r));
 assert.equal(w.localStorage.getItem('plot_voice'),null);assert.equal($('voiceToggle').getAttribute('aria-pressed'),'false');
 assert.equal($('quickImages').checked,false,'fast mode is default');
 assert($('groupPromise').textContent.includes('One payment'));
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
 const reveal={...data(1),reveal:true,answered:true,answer:'האמת הסודית',all_guesses:[{player_id:2,name:'אבי',guess:'ניחוש בלבד',correct:false}]};
 w.render(reveal);assert(w.document.body.classList.contains('reveal-paused'));assert($('revealPrelude').textContent.includes('ניחוש בלבד'));assert(!$('revealPrelude').textContent.includes('האמת הסודית'));assert.equal(w.lastState.answer,null);
 w.render(reveal);await new Promise(r=>setTimeout(r,1100));assert(!w.document.body.classList.contains('reveal-paused'));assert($('reveal').textContent.includes('האמת הסודית'));
 w.render(reveal);assert(!w.document.body.classList.contains('reveal-paused'),'polling cannot replay the reveal');
 assert($('revealInsight').textContent.includes('0 of 1'));
 assert($('answerOwner').textContent.includes('ערן'));
 w.eval("s.host='host-key'");const feedbackButton=$('questionFeedback').querySelector('[data-reason=weak_question]');await feedbackButton.onclick();assert(feedbackButton.disabled);const report=requests.find(r=>r.url.includes('/question-feedback'));assert(report);assert.equal(JSON.parse(report.options.body).round,1);assert.equal(JSON.parse(report.options.body).host,'host-key');
 const count=requests.length;await feedbackButton.onclick();assert.equal(requests.length,count,'no duplicate report');
 w.render({...reveal,round:2});assert(w.document.body.classList.contains('reveal-paused'));w.render({...data(3),is_host:false});assert(!w.document.body.classList.contains('reveal-paused'));assert($('questionFeedback').classList.contains('hidden'));await new Promise(r=>setTimeout(r,1100));assert.equal(w.lastState.round,3,'old reveal timer cannot roll back a later round');
 const final={...data(7),status:'finished',reveal:true,final_image_eligible:false,relationships:[{guesser_id:2,subject_id:1,correct:2,attempts:3}]};w.render({...final,round_insights:[{subject:'ערן',question:'שאלה',answer:'כן',correct:0,attempts:2}]});assert($('playtestHighlights').textContent.includes('0/2'));assert($('revealTalk').classList.contains('hidden'));assert(!$('relationshipCard').classList.contains('hidden'));assert($('relationshipCard').textContent.includes('2/3'));assert(!$('saveResultCard').classList.contains('hidden'));assert($('pilotCostReport').classList.contains('hidden'),'implementation costs not in player flow');
 assert($('playtestHighlights').textContent.includes('Who read you best?'));
 assert($('replayBtn').textContent.includes('Play again with this group'));
 w.render({...final,relationships:[{guesser_id:2,subject_id:1,correct:0,attempts:3}],round_insights:[]});assert($('playtestHighlights').classList.contains('hidden'),'do not call zero correct guesses best');
 w.render({...final,players:[...final.players,{id:3,name:'שגית',score:2}],relationships:[{guesser_id:1,subject_id:2,correct:4,attempts:4},{guesser_id:2,subject_id:1,correct:2,attempts:3},{guesser_id:3,subject_id:1,correct:4,attempts:6}]});
 assert($('playtestHighlights').textContent.includes('Tied: '));assert($('playtestHighlights').textContent.includes('שגית'));assert(!$('playtestHighlights').textContent.includes('4/4'),'personal recap prioritizes who guessed about me');
 // Exercise the real Create handlers and middleware with the capacity response seen in production.
 const originalFetch=w.fetch,createBodies=[];
 w.fetch=async(url,options={})=>{
  if(url==='/api/create'){
   const body=JSON.parse(options.body);createBodies.push(body);
   return {ok:body.allow_ai_fallback===true,json:async()=>body.allow_ai_fallback===true?{code:'SAFE1',host:'host-secret',token:'player-secret',name:body.name,language:'en',ai_fallback_used:true}:{error:'pilot_limit'}};
  }
  if(String(url).includes('/api/state/SAFE1'))return {ok:true,json:async()=>({...data(),code:'SAFE1',status:'lobby',language:'en',photo_count:0,adult_required:false,ai_images_enabled:false})};
  return originalFetch(url,options);
 };
 w.mode('create');$('cname').value='Host';$('quickImages').checked=true;
 await w.createGame();
 assert(!$('createError').classList.contains('hidden'),'capacity failure is visible next to Create');
 assert($('createError').textContent.includes('AI'));
 assert.equal(createBodies.length,1,'do not create a fallback room without an explicit choice');
 await $('createError').querySelector('button').onclick();
 await new Promise(r=>setImmediate(r));await new Promise(r=>setImmediate(r));
 assert.equal(createBodies.length,2);assert.equal(createBodies[1].allow_ai_fallback,true);
 assert.equal(w.eval('s.code'),'SAFE1');assert.equal($('lobbyImages').checked,false);
 assert(!$('inviteCard').classList.contains('hidden'));assert(!$('inviteCard').querySelector('.inviteAiNotice').classList.contains('hidden'));
 const invite=$('inviteCard'),shareButton=invite.querySelector('button'),fallback=invite.querySelector('.inviteFallback');
 const shared=[];w.navigator.share=async payload=>{shared.push(payload)};
 await shareButton.onclick();
 assert.equal(shared.length,1);assert.equal(shared[0].url,'https://plot.test/?code=SAFE1');
 assert(!JSON.stringify(shared[0]).includes('host-secret'),'invite never exposes host rights');
 assert(fallback.classList.contains('hidden'),'native sharing is the first action');
 w.navigator.share=async()=>{throw Object.assign(new Error('cancelled'),{name:'AbortError'})};
 await shareButton.onclick();assert(fallback.classList.contains('hidden'),'cancellation does not force a second action');
 w.navigator.share=async()=>{throw Object.assign(new Error('blocked'),{name:'NotAllowedError'})};
 await shareButton.onclick();assert(!fallback.classList.contains('hidden'),'blocked native share offers another way to invite');
 assert.equal(new URL(fallback.querySelector('a').href).searchParams.get('text').endsWith('https://plot.test/?code=SAFE1'),true);
 let copied='';Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async value=>{copied=value}},configurable:true});
 await fallback.querySelector('button').onclick();assert.equal(copied,'https://plot.test/?code=SAFE1');
 delete w.navigator.share;fallback.classList.add('hidden');await shareButton.onclick();assert(!fallback.classList.contains('hidden'));
 w.fetch=originalFetch;
 for(const language of ['en','he','es','pt-BR','fr','ja']){w.document.documentElement.lang=language;await new Promise(r=>setImmediate(r));assert($('createRoomBtn').textContent.length>0);assert($('photoHelp').textContent.length>0)}
 assert.equal(errors.length,0,errors.join('\n'));console.log('PLAYTEST_FAST_IMAGES_VISIBLE_ADULT_GATE_FAMILY_RESET_VOICE_OPT_IN_HIGHLIGHTS_LOCALES_OK');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
