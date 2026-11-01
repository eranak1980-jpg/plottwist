/* Playtest polish: explicit choices, no open-ended answer stage. */
(() => {
 const el=id=>document.getElementById(id);
 const text={
  he:['תוכן למבוגרים · 18+','לחברים או לזוגות. כל משתתף מאשר בעצמו.','תמונות AI במהלך המשחק','תמונות AI עשויות להוסיף זמן טעינה. השאירו כבוי למשחק מהיר; אפשר להעלות תמונת פרופיל גם בלי יצירת AI.','רגעים מהמשחק שלכם','מי ניחש את מי הכי טוב?','הפתעת הסיבוב','ניחושים נכונים','בוחרים מבין שאר המשתתפים','לא הצלחנו לשמור. נסו שוב.'],
  en:['Adult content · 18+','For friends or couples. Each player confirms separately.','AI images during the game','AI images may add loading time. Leave off for faster play; profile photos are still optional.','Your game highlights','Who predicted whom best?','A surprising reveal','correct guesses','Choose from the other players','Could not save. Please retry.'],
  es:['Contenido adulto · 18+','Para amigos o parejas. Cada persona confirma por separado.','Imágenes de IA durante el juego','Las imágenes de IA pueden tardar. Desactívalas para jugar más rápido; la foto de perfil sigue siendo opcional.','Momentos de la partida','¿Quién acertó más sobre quién?','Una respuesta sorprendente','aciertos','Elige entre los demás jugadores','No se pudo guardar. Inténtalo de nuevo.'],
  'pt-BR':['Conteúdo adulto · 18+','Para amigos ou casais. Cada pessoa confirma separadamente.','Imagens de IA durante o jogo','Imagens de IA podem demorar. Desative para jogar mais rápido; a foto de perfil continua opcional.','Momentos do jogo','Quem acertou mais sobre quem?','Uma resposta surpreendente','acertos','Escolha entre os outros jogadores','Não foi possível salvar. Tente novamente.'],
  fr:['Contenu adulte · 18+','Entre amis ou en couple. Chaque personne confirme séparément.','Images IA pendant la partie','Les images IA peuvent prendre du temps. Désactivez-les pour jouer plus vite ; la photo de profil reste facultative.','Les moments de votre partie','Qui a le mieux deviné les réponses ?','Une réponse surprenante','bonnes réponses','Choisissez parmi les autres joueurs','Enregistrement impossible. Réessayez.'],
  ja:['大人向け・18歳以上','友達やカップル向け。各自の同意が必要です。','ゲーム中のAI画像','AI画像には読み込み時間がかかる場合があります。オフならすぐ次へ進めます。プロフィール写真は任意です。','今回のハイライト','誰の回答を一番当てた？','意外な回答','正解','他のプレイヤーから選択','保存できませんでした。もう一度お試しください。']
 };
 const T=()=>text[document.documentElement.lang]||text.en;
 function choice(id){const row=document.createElement('label');row.className='playtestChoice';row.innerHTML='<input type="checkbox" id="'+id+'"><span><b></b><small></small></span>';return row}
 const adult=choice('quickAdult'),images=choice('quickImages');el('quickSetup').append(adult,images);
 const lobbyImages=choice('lobbyImages');el('lobbyExtras').before(lobbyImages);
 const warning=document.createElement('p');warning.className='tiny imageSpeedNote';el('photoHelp').after(warning);
 const highlights=document.createElement('section');highlights.id='playtestHighlights';highlights.className='relationshipCard hidden';el('relationshipCard').before(highlights);
 const insightCopy={
  he:['מי קרא אותך הכי טוב?','הבחירה שאף אחד לא ניחש','הבחירה האמיתית של','כולם בחרו {guess}. הבחירה של {name}: {answer}.','{n} מתוך {total} ניחשו נכון.','תיקו: ','עוד משחק עם אותה חבורה','חדר חדש · שאלות חדשות · אותם אנשים והגדרות','אחד פותח. כולם מצטרפים בטלפון. רכישה אחת לכל החבורה.'],
  en:['Who read you best?','The choice nobody predicted','The real choice from','Everyone picked {guess}. {name} chose {answer}.','{n} of {total} guessed correctly.','Tied: ','Play again with this group','New room · new questions · same people and settings','One person hosts. Everyone joins on their phone. One payment for the group.'],
  es:['¿Quién te conoce mejor?','La respuesta que nadie adivinó','La elección real de','Todos eligieron {guess}. {name} eligió {answer}.','{n} de {total} acertaron.','Empate: ','Jugar de nuevo con este grupo','Sala nueva · preguntas nuevas · mismo grupo y ajustes','Una persona organiza. Todos se unen con su teléfono. Un pago para el grupo.'],
  'pt-BR':['Quem mais acertou sobre você?','A escolha que ninguém acertou','A escolha real de','Todos escolheram {guess}. {name} escolheu {answer}.','{n} de {total} acertaram.','Empate: ','Jogar de novo com este grupo','Nova sala · novas perguntas · mesmas pessoas e ajustes','Uma pessoa organiza. Todos entram pelo celular. Um pagamento para o grupo.'],
  fr:['Qui vous a le mieux compris ?','Le choix que personne n’a deviné','Le vrai choix de','Tout le monde a choisi {guess}. {name} a choisi {answer}.','{n} sur {total} ont trouvé.','Égalité : ','Rejouer avec ce groupe','Nouvelle salle · nouvelles questions · mêmes joueurs et réglages','Une personne organise. Chacun rejoint sur son téléphone. Un paiement pour le groupe.'],
  ja:['あなたを一番理解していたのは？','誰も当てられなかった答え','本当に選んだ人：','全員の予想は「{guess}」。{name}の答えは「{answer}」。','{total}人中{n}人が正解。','同率：','同じメンバーでもう一度','新しいルーム・新しい質問・同じメンバーと設定','1人がホストになり、全員がスマホで参加。支払いはグループで1回。']
 };
 const I=()=>insightCopy[document.documentElement.lang]||insightCopy.en;
 const fill=(str,vars)=>str.replace(/\{(\w+)\}/g,(_,key)=>String(vars[key]??''));
 const revealInsight=document.createElement('p');revealInsight.id='revealInsight';revealInsight.className='revealInsight hidden';el('reaction').before(revealInsight);
 const answerOwner=document.createElement('div');answerOwner.id='answerOwner';answerOwner.className='eyebrow hidden';el('answer').before(answerOwner);
 const promise=document.createElement('p');promise.id='groupPromise';promise.className='groupPromise';el('createRoomBtn').after(promise);
 const replayHint=document.createElement('p');replayHint.id='replayHint';replayHint.className='tiny';el('replayBtn').after(replayHint);
 let last=null;
 const safe=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function labels(){
  const t=T(),family=audienceType==='family';adult.querySelector('b').textContent=t[0];adult.querySelector('small').textContent=t[1];adult.classList.toggle('hidden',family||crazygamesMode);
  el('quickAdult').checked=!family&&createAdultRequired();
  for(const node of [images,lobbyImages]){node.querySelector('b').textContent=t[2];node.querySelector('small').textContent=t[3]}
  images.classList.toggle('hidden',crazygamesMode);warning.textContent=t[3];
  promise.textContent=I()[8];promise.classList.toggle('hidden',crazygamesMode);
  const talk=el('revealTalk');if(talk){talk.textContent='';talk.classList.add('hidden')}
 }
 function setAdult(on){
  spice=on?3:1;el('advancedSetup').dataset.used='1';
  if(on){el('advancedSetup').open=true;el('adultOptions').open=true}
  else{document.querySelectorAll('#topics [data-topic]').forEach(b=>{if(['דייטים','אינטימיות למבוגרים'].includes(b.dataset.topic))b.classList.remove('on')});el('adultConfirm').checked=false;el('hostIntroAge').checked=false;el('adultOptions').open=false}
  document.querySelectorAll('.spice button').forEach((b,i)=>b.classList.toggle('on',i+1===spice));syncCreateAdult();labels();
 }
 el('quickAdult').onchange=()=>setAdult(el('quickAdult').checked);
 const oldAudience=window.renderAudience;window.renderAudience=function(){if(audienceType==='family'&&spice===3)setAdult(false);oldAudience();labels()};
 const oldReq=window.req;window.req=function(path,body){if(path==='/api/create'&&body)body={...body,ai_images_enabled:!crazygamesMode&&el('quickImages').checked};return oldReq(path,body)};
 el('lobbyImages').onchange=async()=>{const cb=el('lobbyImages');cb.disabled=true;try{await req('/api/'+s.code+'/image-settings',{host:s.host,enabled:cb.checked});stateSig='';await load()}catch(_){cb.checked=!!last?.ai_images_enabled;toast(T()[9])}finally{cb.disabled=false}};
 const oldRender=window.render;function renderActual(d){
  oldRender(d);last=d;labels();lobbyImages.classList.toggle('hidden',d.status!=='lobby'||!d.is_host||crazygamesMode);el('lobbyImages').checked=d.ai_images_enabled!==false;
  if(d.ai_images_enabled===false){el('visualStage')?.classList.add('hidden');el('heroStatus')?.classList.add('hidden');el('finalHeroStatus')?.classList.add('hidden')}
  if(d.type==='room'&&!d.reveal){const role=el('questionRole');if(role)role.textContent+=' · '+T()[8]}
  const guesses=d.all_guesses||[],visible=d.status==='playing'&&d.reveal&&guesses.length>0;
  answerOwner.classList.toggle('hidden',!visible);answerOwner.textContent=I()[2]+' '+(d.subject?.name||'');
  revealInsight.classList.toggle('hidden',!visible);
  if(visible){const n=guesses.filter(g=>g.correct).length;revealInsight.textContent=guesses.length>1&&!n&&guesses.every(g=>g.guess===guesses[0].guess)?fill(I()[3],{guess:guesses[0].guess,name:d.subject?.name||'',answer:d.answer}):fill(I()[4],{n,total:guesses.length})}
  replayHint.classList.toggle('hidden',d.status!=='finished'||!d.is_host);replayHint.textContent=I()[7];
  if(d.status==='finished'&&d.is_host)el('replayBtn').textContent='↻ '+I()[6];
  renderFeedback(d);
  const done=d.status==='finished';highlights.classList.toggle('hidden',!done);if(!done)return;
  const t=T(),byId=new Map((d.players||[]).map(p=>[p.id,p.name]));
  const pairs=(d.relationships||[]).filter(p=>p.attempts>=2&&p.correct>0);
  const mine=pairs.filter(p=>p.subject_id===d.me?.id),pool=mine.length?mine:pairs;
  pool.sort((a,b)=>b.correct/b.attempts-a.correct/a.attempts||b.attempts-a.attempts);
  const best=pool[0],tied=best?pool.filter(p=>p.correct*best.attempts===best.correct*p.attempts):[];
  const surprises=(d.round_insights||[]).slice().sort((a,b)=>Number(b.subject===byId.get(d.me?.id))-Number(a.subject===byId.get(d.me?.id))).slice(0,3);
  highlights.innerHTML='<h3>'+safe(t[4])+'</h3>'+(best?'<div class="personalInsight"><b>'+safe(mine.length?I()[0]:t[5])+'</b>'+(tied.length>1?'<small>'+safe(I()[5])+'</small>':'')+tied.map(p=>'<p>'+'<bdi>'+safe(byId.get(p.guesser_id))+'</bdi> → <bdi>'+safe(byId.get(p.subject_id))+'</bdi>'+' · '+p.correct+'/'+p.attempts+' '+safe(t[7])+'</p>').join('')+'</div>':'')+surprises.map(r=>'<article class="roundInsight"><small>'+safe(r.correct===0?I()[1]:t[6])+' · '+safe(r.subject)+'</small><p>'+safe(r.question)+'</p><b>'+safe(r.answer)+'</b><span>'+r.correct+'/'+r.attempts+' '+safe(t[7])+'</span></article>').join('');
  if(!best&&!surprises.length)highlights.classList.add('hidden');
 };
 const feedbackCopy={
  he:['משוב על השאלה','שאלה חלשה','תשובות לא מתאימות','תודה, המשוב נשמר. המשחק ממשיך כרגיל.','המשוב לא נשמר. נסו שוב.','כולם בחרו. הנה הניחושים…','הצגת התשובה'],
  en:['Question feedback','Weak question','Answers don’t fit','Thanks, feedback saved. Keep playing.','Could not save feedback. Please retry.','Everyone has chosen. Here are the predictions…','Show the answer'],
  es:['Opinión sobre la pregunta','Pregunta floja','Respuestas poco relacionadas','Gracias, opinión guardada. Sigue jugando.','No se pudo guardar. Inténtalo de nuevo.','Todos eligieron. Estas son las predicciones…','Mostrar respuesta'],
  'pt-BR':['Avaliar pergunta','Pergunta fraca','Respostas inadequadas','Obrigado! Avaliação salva. Continue jogando.','Não foi possível salvar. Tente novamente.','Todos escolheram. Veja os palpites…','Mostrar resposta'],
  fr:['Avis sur la question','Question peu intéressante','Réponses inadaptées','Merci, votre avis est enregistré. Continuez à jouer.','Enregistrement impossible. Réessayez.','Tout le monde a choisi. Voici les prédictions…','Voir la réponse'],
  ja:['質問へのフィードバック','質問がいまひとつ','選択肢が合わない','保存しました。ゲームはそのまま続けられます。','保存できませんでした。もう一度お試しください。','全員が選びました。みんなの予想は…','答えを見る']
 };
 const F=()=>feedbackCopy[document.documentElement.lang]||feedbackCopy.en;
 const roundKey=d=>[d.code,d.image_run,d.round].join('_');
 const reports=new Map(),sending=new Set();let feedbackKey='';
 const feedback=document.createElement('details');feedback.id='questionFeedback';feedback.className='questionFeedback hidden';
 feedback.innerHTML='<summary></summary><div class="feedbackActions"><button type="button" data-reason="weak_question"></button><button type="button" data-reason="unrelated_options"></button></div><p role="status" aria-live="polite"></p>';
 el('play').appendChild(feedback);
 function renderFeedback(d){
  feedback.classList.toggle('hidden',!d.is_host||d.status!=='playing');
  const key=roundKey(d),t=F();if(feedbackKey!==key){feedbackKey=key;feedback.open=false;feedback.querySelector('p').textContent=''}
  const done=reports.get(key)||new Set();(d.feedback_reasons||[]).forEach(x=>done.add(x));reports.set(key,done);
  if(reports.size>90)reports.delete(reports.keys().next().value);
  feedback.querySelector('summary').textContent=t[0];
  feedback.querySelectorAll('button').forEach((b,i)=>{b.textContent=(done.has(b.dataset.reason)?'✓ ':'')+t[i+1];b.disabled=done.has(b.dataset.reason)||sending.has(key)});
 }
 feedback.querySelectorAll('button').forEach(b=>b.onclick=async()=>{
  const d=last;if(!d?.is_host||d.status!=='playing')return;
  const key=roundKey(d),reason=b.dataset.reason;if(sending.has(key)||reports.get(key)?.has(reason))return;
  sending.add(key);renderFeedback(d);
  try{await req('/api/'+encodeURIComponent(d.code)+'/question-feedback',{host:s.host,round:d.round,image_run:d.image_run,reason});const done=reports.get(key)||new Set();done.add(reason);reports.set(key,done);if(last&&roundKey(last)===key)feedback.querySelector('p').textContent=F()[3]}
  catch(_){if(last&&roundKey(last)===key)feedback.querySelector('p').textContent=F()[4]}
  finally{sending.delete(key);if(last&&roundKey(last)===key)renderFeedback(last)}
 });
 const prelude=document.createElement('section');prelude.id='revealPrelude';prelude.className='revealPrelude hidden';prelude.setAttribute('aria-live','polite');el('reveal').before(prelude);
 const seenReveals=new Set();let pending=null,revealTimer=null,previousState=null;
 function finishPrelude(){
  if(!pending)return;const focusWasInside=prelude.contains(document.activeElement),d=pending;pending=null;clearTimeout(revealTimer);revealTimer=null;
  prelude.classList.add('hidden');document.body.classList.remove('reveal-paused');seenReveals.add(roundKey(d));renderActual(d);previousState=d;if(focusWasInside){const target=d.is_host?el('next'):el('reveal');target.setAttribute('tabindex','-1');target.focus({preventScroll:true})}
 }
 window.render=function(d){
  const key=roundKey(d);
  if(pending){if(roundKey(pending)===key&&d.status==='playing'&&d.reveal){pending=d;return}clearTimeout(revealTimer);pending=null;prelude.classList.add('hidden');document.body.classList.remove('reveal-paused')}
  if(d.status==='playing'&&d.reveal&&d.all_guesses?.length&&!seenReveals.has(key)){
   pending=d;document.body.classList.add('reveal-paused');
   const prior=previousState&&roundKey(previousState)===key?previousState:d;
   renderActual({...d,reveal:false,answer:null,all_guesses:[],players:prior.players,me:d.me?{...d.me,score:prior.me?.score??d.me.score}:null});
   const t=F(),guesses=(d.all_guesses||[]).slice(0,4);
   prelude.innerHTML='<h3>'+safe(t[5])+'</h3><div class="predictionPreview">'+guesses.map(g=>'<p><span>'+safe(g.name)+'</span><b>'+safe(g.guess)+'</b></p>').join('')+'</div><button type="button" class="mini">'+safe(t[6])+'</button>';
   prelude.querySelector('button').onclick=finishPrelude;prelude.classList.remove('hidden');
   revealTimer=setTimeout(finishPrelude,1000);if(seenReveals.size>90)seenReveals.delete(seenReveals.values().next().value);return;
  }
  renderActual(d);previousState=d;
 };
 const oldCopy=window.applyCopy;window.applyCopy=function(){oldCopy();labels()};
 labels();new MutationObserver(()=>{labels();if(last&&!pending)renderActual(last)}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});if(window.lastState)window.render(window.lastState);
})();
