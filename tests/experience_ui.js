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
(async()=>{
 await new Promise(r=>setImmediate(r));
 w.document.documentElement.lang='he';
 assert.equal(notes,0,'no audio before gesture');
 w.renderCreateTopics();w.renderAudience();
 assert(!$('adultOptions').open,'adult categories opt in');
 w.mode('create');assert(!$('hostIntro').classList.contains('hidden'));assert(!$('hostIntroAge').checked,'intro never prechecks age');
 $('hostIntroAge').checked=true;$('hostIntroAge').dispatchEvent(new w.Event('change'));
 assert($('adultConfirm').checked,'explicit intro consent is retained in setup');
 $('hostIntroContinue').click();assert($('adultOptions').open);assert(!$('adultBox').classList.contains('hidden'),'age confirmation visible before choosing a topic');
 assert.equal(w.document.querySelector('#adultOptions [data-topic="דייטים"]').textContent.length>0,true);
 $('adultOptions').open=true;$('adultOptions').dispatchEvent(new w.Event('toggle'));
 w.document.querySelector('#adultOptions [data-topic="דייטים"]').click();
 assert(!$('adultBox').classList.contains('hidden'),'dating reveals age consent at medium/chill level');
 w.renderCreateTopics();assert.equal(w.document.querySelectorAll('#topics [data-topic="דייטים"]').length,1,'rerender does not duplicate adult topics');
 w.document.querySelector('[data-audience="family"]').click();assert($('adultOptions').classList.contains('hidden'));assert(!w.document.querySelector('#adultOptions [data-topic="דייטים"]').classList.contains('on'));
 assert(!$('adultConfirm').checked);assert(!$('hostIntroAge').checked);
 let lobby={...data(),status:'lobby',adult_required:true,adults_ready:false,me:{id:1,has_photo:false,adult_confirmed:false}};
 w.render(lobby);assert($('start').disabled);assert(!$('playerAge').classList.contains('hidden'));assert(!$('photoBox').classList.contains('hidden'));
 assert(!$('shareBtn').classList.contains('hidden'));
 assert($('photoBox').compareDocumentPosition($('sharedSetup'))&w.Node.DOCUMENT_POSITION_FOLLOWING,'photo step before settings');
 assert.equal(w.document.querySelector('.photoPick').htmlFor,'photoInput');
 assert(experienceCss.includes('#photoBox #photoInput{position:absolute!important'),'native photo input is visually hidden behind one large picker');
 assert(!$('howAge').classList.contains('hidden'));assert(!$('howAgeCheck').checked);
 $('howAgeCheck').checked=true;$('howAgeCheck').dispatchEvent(new w.Event('change'));assert($('playerAgeCheck').checked);
 w.render({...lobby,code:'NEXT1',is_host:false});assert(!$('howAgeCheck').checked,'consent is never carried into a different room');assert(!$('playerAgeCheck').checked);
 assert($('shareBtn').classList.contains('hidden'),'guests cannot see share link');
 w.navigator.clipboard={writeText(){throw Error('guest must not share')}};await w.share();
 const readyLobby={...lobby,code:'READY',adult_required:false,adults_ready:true,is_host:true,me:{id:1,has_photo:true,adult_confirmed:true},players:[{id:1,name:'ערן',gender:'male',score:0,active:true,connected:true,has_photo:true,photo_url:'/photo/1'},{id:2,name:'אבי',score:0,active:true,connected:true,has_photo:true,photo_url:'/photo/2'}],photo_count:2};
 w.render(readyLobby);assert(!$('photoReadyCard').classList.contains('hidden'),'saved photo confirmation remains visible');assert($('savedPhotoThumb').src.includes('/photo/1'));assert($('photoInput').offsetParent===null||w.getComputedStyle($('photoInput')).clip!=='auto');

 assert.equal(new Set(Object.values(w.PlotLines.he).flat()).size,80);
 w.eval("s={code:'TEST1',token:'test-token',host:'test-host'}");let d=data();w.render(d);assert(!$('scoreDock').classList.contains('hidden'));assert($('scoreBar').textContent.includes('אבי'));assert(w.document.querySelector('.nextDock').classList.contains('hidden'));assert(!$('gameChat').classList.contains('hidden'));
 assert($('chatFab').getAttribute('aria-label'));assert([...w.document.querySelectorAll('[data-reaction]')].every(b=>b.getAttribute('aria-label')&&b.title),'emoji reactions have accessible labels');
 $('chatFab').click();assert(!$('chatSheet').classList.contains('hidden'));w.document.querySelectorAll('#chatSheet [data-reaction]')[1].click();await new Promise(r=>setImmediate(r));assert(requests.some(r=>r.url.endsWith('/api/TEST1/chat')&&JSON.parse(r.options.body).body==='😂'),'quick reaction posts to room chat');$('chatClose').click();assert($('chatSheet').classList.contains('hidden'));
 $('scoreBar').click();assert.equal($('scoreBar').getAttribute('aria-expanded'),'true');assert(notes>0,'gesture activates audio');
 $('closeScores').click();assert.equal($('scoreBar').getAttribute('aria-expanded'),'false');
 clock+=1000;d={...data(1),reveal:true,interactive_match:{ready:false,participants:[],answers:[]},all_guesses:[{player_id:2,name:'אבי',gender:'male',guess:'כן',correct:true}]};w.render(d);
 assert.equal($('scoreBar').getAttribute('aria-expanded'),'true','scoreboard after two rounds');
 assert(!w.document.querySelector('.nextDock').classList.contains('hidden'));
 assert($('interactiveTwist').classList.contains('hidden'),'legacy secret Match Twist is removed');assert(!$('next').classList.contains('hidden'),'legacy Match Twist never blocks next');
 assert(w.document.body.classList.contains('hasNextDock'),'chat button clears the host reveal CTA');assert(experienceCss.includes('.hasScoreDock.hasNextDock .chatFab'));
 assert(!$('revealReactions').classList.contains('hidden'));assert(w.document.querySelector('.emphasizedGuess .guessChoice').textContent.includes('כן'));assert(w.document.querySelector('.emphasizedGuess').textContent.includes('ניחש'));
 assert(w.document.querySelector('.emphasizedGuess .genderBadge'),'reveal guess keeps gender badge');
 w.openNewGameOptions();assert(!$('newGameOverlay').classList.contains('hidden'));assert(!$('keepGameBtn').classList.contains('hidden'));$('newGameCancel').click();
 let confirmText='';w.confirm=text=>{confirmText=text;return false};await w.dropPlayer(2);assert(confirmText.includes('אבי'),'drop asks for named confirmation');
 const atReveal=notes;w.render(d);assert.equal(notes,atReveal,'poll does not repeat sounds');
 w.render(data(2));assert(w.document.querySelector('.nextDock').classList.contains('hidden'),'no stale next button on question');assert(!w.document.body.classList.contains('hasNextDock'));
 clock+=1000;$('soundToggle').click();assert.equal(w.localStorage.getItem('plot_sound'),'off');let muted=notes;clock+=2000;$('scoreBar').click();assert.equal(notes,muted);
 clock+=1000;$('soundToggle').click();assert.equal(w.localStorage.getItem('plot_sound'),'on');assert(notes>muted);
 // Repeated loading updates must preserve the line; time-based changes draw without replacement.
 d={...data(3),reveal:true,hero_eligible:true,ai_images_ready:true,hero_status:'running',subject:{id:1,name:'ערן',photo_url:'/test.jpg'}};
 w.render(d);const first=w.document.querySelector('.loadingJoke').textContent;w.render(d);assert.equal(w.document.querySelector('.loadingJoke').textContent,first);
 let seen=new Set([first]);for(let i=0;i<20;i++){clock+=12000;intervals.at(-1)();const line=w.document.querySelector('.loadingJoke').textContent;assert(!seen.has(line));seen.add(line)}
 $('soundToggle').click();muted=notes;clock+=12000;intervals.at(-1)();assert.equal(notes,muted,'muted companion stays silent');
 const final={...data(7),status:'finished',reveal:true,prize:'שמלה חדשה',can_tiebreak:true,final_image_eligible:false};w.render(final);
 assert.equal($('finishTitle').textContent,'יש לנו 2 מנצחים!');assert.equal(($('scores').textContent.match(/🏆/g)||[]).length,2);assert($('finalPrize').textContent.includes('לכל זוכה'));assert(!$('tieChoice').classList.contains('hidden'));
 assert($('replayBtn').textContent.includes('אותם אנשים'),'end screen exposes a direct same-group new game action');assert(experienceCss.includes('body.finalImagePending #finalHeroStatus'),'final winner wait owns the screen');
 w.render({...final,is_host:false});assert($('tieChoice').classList.contains('hidden'),'host-only tie action');
 w.render({...final,can_tiebreak:false});assert($('tieChoice').classList.contains('hidden'),'bounded tie action');
 assert.equal($('scoreDock').classList.contains('hidden'),true);
 const session={code:'REOPN',token:'opaque-player-token',host:'opaque-host-token'};w.localStorage.setItem('kyc',JSON.stringify(session));
 // Production boot recovers the same session, including when a different room was last active.
 assert(!inline.includes('if(e.persisted)location.reload()'),'bfcache must not force navigation');
 assert.equal(errors.length,0,errors.join('\n'));
 console.log('DOM_SCORE_DOCK_TWO_ROUNDS_NEXT_MUTE_AUDIO_80_LINES_NO_REPEATS_TIES_HOST_ONLY_OK');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(()=>w.close());
