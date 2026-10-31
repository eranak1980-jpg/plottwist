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
 let last=null;
 const safe=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function labels(){
  const t=T(),family=audienceType==='family';adult.querySelector('b').textContent=t[0];adult.querySelector('small').textContent=t[1];adult.classList.toggle('hidden',family||crazygamesMode);
  el('quickAdult').checked=!family&&createAdultRequired();
  for(const node of [images,lobbyImages]){node.querySelector('b').textContent=t[2];node.querySelector('small').textContent=t[3]}
  images.classList.toggle('hidden',crazygamesMode);warning.textContent=t[3];
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
 const oldRender=window.render;window.render=function(d){
  oldRender(d);last=d;labels();lobbyImages.classList.toggle('hidden',d.status!=='lobby'||!d.is_host||crazygamesMode);el('lobbyImages').checked=d.ai_images_enabled!==false;
  if(d.ai_images_enabled===false){el('visualStage')?.classList.add('hidden');el('heroStatus')?.classList.add('hidden');el('finalHeroStatus')?.classList.add('hidden')}
  if(d.type==='room'&&!d.reveal){const role=el('questionRole');if(role)role.textContent+=' · '+T()[8]}
  const done=d.status==='finished';highlights.classList.toggle('hidden',!done);if(!done)return;
  const t=T(),byId=new Map((d.players||[]).map(p=>[p.id,p.name]));
  const pairs=(d.relationships||[]).filter(p=>p.attempts>=2).sort((a,b)=>b.correct/b.attempts-a.correct/a.attempts||b.attempts-a.attempts);
  const best=pairs[0],surprises=d.round_insights||[];
  highlights.innerHTML='<h3>'+safe(t[4])+'</h3>'+(best?'<p><b>'+safe(t[5])+'</b><br>'+safe(byId.get(best.guesser_id))+' → '+safe(byId.get(best.subject_id))+' · '+best.correct+'/'+best.attempts+' '+safe(t[7])+'</p>':'')+surprises.map(r=>'<article class="roundInsight"><small>'+safe(t[6])+' · '+safe(r.subject)+'</small><p>'+safe(r.question)+'</p><b>'+safe(r.answer)+'</b><span>'+r.correct+'/'+r.attempts+' '+safe(t[7])+'</span></article>').join('');
  if(!best&&!surprises.length)highlights.classList.add('hidden');
 };
 const oldCopy=window.applyCopy;window.applyCopy=function(){oldCopy();labels()};
 labels();new MutationObserver(labels).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});if(window.lastState)window.render(window.lastState);
})();
