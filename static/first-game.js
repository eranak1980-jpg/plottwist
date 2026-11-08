/* First-game experience. Progressive disclosure; photos and generated art never gate play. */
(() => {
 const el=id=>document.getElementById(id),safe=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const words={
 en:['Start your game','Who’s playing?','Customize this game','8 rounds · light & fun · photos optional','Your name','Create & invite friends','Add a photo (optional)','Play with your name and avatar. A photo personalizes your avatar. AI images can be enabled separately.','Copy invite link','Invite a friend to begin. Everyone opens the link on their own phone.','Game details & extra topics','See an example round','Example round — fictional players','Alex answers in secret. What do you think Alex chose?','Alex receives a call during dinner with friends. What happens?',['Answers at the table','Calls back later','Steps outside','Sends a quick message'],'Alex chose: Calls back later','A correct prediction earns 1 point. Now it’s the next player’s turn.','Start with your friends','Close','Who knows whom?','correct guesses','No guesses recorded yet.','Save result card','Tell us: why that answer?','You’re guessing about','Your secret answer','Image is optional. Continue whenever you’re ready.','Ready for another round?','Photos are optional.','Plans & pricing'],
 he:['מתחילים לשחק','מי משחקים?','התאמה אישית למשחק','8 סיבובים · קליל וכיפי · תמונות לבחירה','השם שלך','יצירת חדר והזמנת חברים','הוספת תמונה (לא חובה)','אפשר לשחק עם שם ואווטאר. תמונה מוסיפה זיהוי אישי, רק באישורכם. אפשר להפעיל תמונות AI בנפרד.','העתקת לינק להזמנה','הזמינו חבר או חברה. כל אחד פותח את הלינק בטלפון שלו.','פרטי המשחק ונושאים נוספים','נסו סיבוב לדוגמה','סיבוב לדוגמה — דמויות בדיוניות','אלכס עונה בסוד. מה לדעתכם אלכס בחר?','אלכס מקבל שיחה בארוחה עם חברים. מה קורה?',['עונה ליד השולחן','חוזר למתקשר אחר כך','יוצא החוצה','שולח הודעה קצרה'],'אלכס בחר: חוזר למתקשר אחר כך','ניחוש נכון שווה נקודה. עכשיו התור עובר לשחקן הבא.','למשחק עם החברים','סגירה','מי מכיר את מי?','ניחושים נכונים','עדיין אין ניחושים שמורים.','שמירת כרטיס תוצאה','ספרו: למה דווקא התשובה הזאת?','מנחשים לגבי','התשובה הסודית שלך','התמונה היא תוספת. אפשר להמשיך מתי שתרצו.','מוכנים לעוד סיבוב?','תמונות אינן חובה.','חבילות ומחירים'],
 es:['Empieza a jugar','¿Quién juega?','Personalizar partida','8 rondas · divertido y ligero · fotos opcionales','Tu nombre','Crear e invitar','Añadir foto (opcional)','Juega con nombre y avatar. La foto personaliza tu avatar. Las imágenes de IA se activan por separado.','Copiar invitación','Invita a alguien. Cada persona abre el enlace en su teléfono.','Detalles y temas extra','Prueba una ronda','Ronda de ejemplo — personajes ficticios','Alex responde en secreto. ¿Qué crees que eligió?','Alex recibe una llamada cenando con amigos. ¿Qué hace?',['Contesta en la mesa','Devuelve la llamada luego','Sale a contestar','Envía un mensaje'],'Alex eligió: Devuelve la llamada luego','Cada acierto suma 1 punto. Después cambia el turno.','Jugar con amigos','Cerrar','¿Quién conoce a quién?','aciertos','Aún no hay respuestas registradas.','Guardar resultado','¿Por qué elegiste eso?','Estás adivinando sobre','Tu respuesta secreta','La imagen es opcional. Puedes continuar.','¿Otra ronda?','Las fotos son opcionales.','Ajustes y precios'],
 'pt-BR':['Comece a jogar','Quem vai jogar?','Personalizar jogo','8 rodadas · leve e divertido · fotos opcionais','Seu nome','Criar e convidar','Adicionar foto (opcional)','Jogue com nome e avatar. A foto personaliza seu avatar. Imagens de IA são ativadas separadamente.','Copiar convite','Convide alguém. Cada pessoa abre o link no próprio celular.','Detalhes e temas extras','Teste uma rodada','Rodada de exemplo — personagens fictícios','Alex responde em segredo. O que você acha que escolheu?','Alex recebe uma ligação no jantar com amigos. O que faz?',['Atende à mesa','Retorna mais tarde','Sai para atender','Envia uma mensagem'],'Alex escolheu: Retorna mais tarde','Cada acerto vale 1 ponto. Depois é a vez de outra pessoa.','Jogar com amigos','Fechar','Quem conhece quem?','acertos','Ainda não há palpites registrados.','Salvar resultado','Por que você escolheu isso?','Você está prevendo sobre','Sua resposta secreta','A imagem é opcional. Você pode continuar.','Mais uma rodada?','Fotos são opcionais.','Configurações e preços'],
 fr:['Lancez la partie','Qui joue ?','Personnaliser la partie','8 manches · léger et amusant · photos facultatives','Votre prénom','Créer et inviter','Ajouter une photo (facultatif)','Jouez avec un prénom et un avatar. La photo personnalise votre avatar. Les images IA s’activent séparément.','Copier l’invitation','Invitez quelqu’un. Chacun ouvre le lien sur son téléphone.','Détails et thèmes supplémentaires','Essayer une manche','Exemple — personnages fictifs','Alex répond en secret. Quel choix a-t-il fait ?','Alex reçoit un appel pendant un dîner entre amis. Que fait-il ?',['Répond à table','Rappelle plus tard','Sort pour répondre','Envoie un message'],'Alex a choisi : Rappelle plus tard','Une bonne réponse rapporte 1 point. Puis le tour change.','Jouer entre amis','Fermer','Qui connaît qui ?','bonnes réponses','Aucune réponse enregistrée.','Enregistrer le résultat','Pourquoi ce choix ?','Vous devinez la réponse de','Votre réponse secrète','L’image est facultative. Vous pouvez continuer.','Une autre manche ?','Les photos sont facultatives.','Réglages et tarifs'],
 ja:['ゲームを始めよう','誰と遊ぶ？','ゲームをカスタマイズ','8ラウンド・気軽に遊べる・写真は任意','名前','ルームを作って招待','写真を追加（任意）','名前とアバターで遊べます。写真は同意して追加できます。AI画像は別途オンにします。','招待リンクをコピー','友達を招待しましょう。それぞれのスマホでリンクを開きます。','ゲーム設定と追加テーマ','サンプルを試す','サンプルラウンド — 架空の人物','アレックスが秘密で回答。どれを選んだと思う？','友達との食事中にアレックスの電話が鳴った。どうする？',['席で電話に出る','後でかけ直す','外に出て電話に出る','短いメッセージを送る'],'アレックスの回答：後でかけ直す','予想が当たると1点。次の人に交代します。','友達と遊ぶ','閉じる','誰が誰を知ってる？','正解','まだ予想の記録がありません。','結果を保存','なぜその答えを選んだの？','予想する相手','あなたの秘密の答え','画像は任意です。そのまま続けられます。','もう一度遊ぶ？','写真は任意です。','設定と料金']};
 const shareLabel=()=>({he:'שיתוף הזמנה',es:'Compartir invitación','pt-BR':'Compartilhar convite',fr:'Partager l’invitation',ja:'招待リンクを共有'})[document.documentElement.lang]||'Share invitation';
 const T=()=>words[document.documentElement.lang]||words.en;
 const form=el('create'),advanced=document.createElement('details');advanced.id='advancedSetup';advanced.innerHTML='<summary></summary><div class="advancedContent"></div>';
 const quick=document.createElement('section');quick.id='quickSetup';quick.innerHTML='<label for="cname" id="quickName"></label><h3 id="quickAudience"></h3><div id="quickAudienceChoices"></div><p id="quickDefaults" class="tiny"></p>';
 const name=el('cname'),aud=el('audienceTypes'),create=el('createRoomBtn');form.insertBefore(quick,name);quick.querySelector('label').after(name);el('quickAudienceChoices').appendChild(aud);
 for(const child of [...form.children])if(![el('createTitle'),el('hostGuideLink'),quick,create].includes(child))advanced.querySelector('div').appendChild(child);
 form.insertBefore(advanced,create);advanced.ontoggle=()=>form.classList.toggle('advancedSetupOpen',advanced.open);
 audienceType=audienceType||'friends';rounds=8;document.querySelectorAll('.lengths button').forEach(b=>b.classList.toggle('on',b.dataset.r==='8'));renderAudience();
 // Keep the optional, consented photo picker collapsed instead of asking everyone to upload.
 let photoExpanded=false;el('photoToggle').onclick=()=>{photoExpanded=!photoExpanded;el('photoBox').classList.toggle('hidden',!photoExpanded);el('photoBox').dataset.editing=photoExpanded?'1':''};
 const createMessages={
  he:['מכסת ה־AI מלאה כרגע. אפשר לפתוח חדר עם השאלות המובנות ולשחק ללא תמונות AI.','פתיחת חדר ללא AI','החדר מוכן. תמונות AI אינן זמינות כרגע. אפשר להזמין חברים ולהתחיל לשחק.','לא הצלחנו ליצור את החדר. בדקו את החיבור ונסו שוב.','שליחה ב־WhatsApp','העתקת קישור'],
  en:['AI capacity is currently full. You can create a room with built-in questions and play without AI images.','Create room without AI','Your room is ready. AI images are currently unavailable. Invite your friends and start playing.','Could not create the room. Check your connection and try again.','Send with WhatsApp','Copy link'],
  es:['La capacidad de IA está llena. Puedes crear una sala con preguntas incluidas y jugar sin imágenes de IA.','Crear sala sin IA','La sala está lista. Las imágenes de IA no están disponibles. Invita a tus amigos y empieza a jugar.','No se pudo crear la sala. Revisa tu conexión e inténtalo de nuevo.','Enviar por WhatsApp','Copiar enlace'],
  'pt-BR':['A capacidade de IA está cheia. Crie uma sala com perguntas incluídas e jogue sem imagens de IA.','Criar sala sem IA','Sua sala está pronta. Imagens de IA indisponíveis. Convide seus amigos e comece a jogar.','Não foi possível criar a sala. Confira a conexão e tente novamente.','Enviar pelo WhatsApp','Copiar link'],
  fr:['La capacité IA est pleine. Créez une salle avec les questions intégrées et jouez sans images IA.','Créer une salle sans IA','La salle est prête. Les images IA sont indisponibles. Invitez vos amis et commencez à jouer.','Impossible de créer la salle. Vérifiez la connexion et réessayez.','Envoyer sur WhatsApp','Copier le lien'],
  ja:['AIの利用枠がいっぱいです。内蔵の質問を使い、AI画像なしでルームを作成できます。','AIなしでルームを作成','ルームの準備ができました。AI画像は現在利用できません。友達を招待して遊べます。','ルームを作成できませんでした。接続を確認して再試行してください。','WhatsAppで送る','リンクをコピー']
 };
 const C=()=>createMessages[document.documentElement.lang]||createMessages.en;
 const createError=document.createElement('section');createError.id='createError';createError.className='rulebox hidden';createError.setAttribute('role','alert');createError.innerHTML='<p></p><button type="button" class="primary hidden"></button>';create.before(createError);
 window.showCreateError=function(error){
  const capacity=error?.message==='pilot_limit';
  createError.querySelector('p').textContent=capacity?C()[0]:error?.message==='name_required'?(copy.name_required||T()[4]):C()[3];
  const button=createError.querySelector('button');button.textContent=C()[1];button.classList.toggle('hidden',!capacity);
  createError.classList.remove('hidden');createError.scrollIntoView({behavior:'smooth',block:'center'});
 };
 let allowAiFallback=false;
 const createReq=window.req;
 window.req=function(path,body){
  if(path==='/api/create'&&body&&allowAiFallback)body={...body,allow_ai_fallback:true};
  return createReq(path,body);
 };
 createError.querySelector('button').onclick=async()=>{
  const button=createError.querySelector('button');button.disabled=true;allowAiFallback=true;
  try{await window.createGame()}finally{allowAiFallback=false;button.disabled=false}
 };
 const lobby=document.createElement('section');lobby.id='inviteCard';lobby.className='inviteCard hidden';lobby.innerHTML='<b></b><p></p><small class="inviteAiNotice hidden" role="status"></small><button type="button"></button><div class="inviteFallback hidden"><a class="mini" target="_blank" rel="noopener">WhatsApp</a><button type="button" class="mini"></button><input readonly aria-label="Invitation link"></div>';
 el('sharedSetup').before(lobby);lobby.querySelector('button').onclick=async()=>{
  if(!s.code)return;
  const fallback=lobby.querySelector('.inviteFallback'),input=fallback.querySelector('input');
  input.value=location.origin+'/?code='+encodeURIComponent(s.code)+(crazygamesMode?'&cg=1':'');
  if(navigator.share){
   try{await navigator.share({title:'Play MIPO',text:copy.share_text||'Play MIPO',url:input.value});return}
   catch(error){if(error.name==='AbortError')return}
  }
  fallback.querySelector('a').href='https://wa.me/?text='+encodeURIComponent((copy.share_text||'Play MIPO')+' '+input.value);
  fallback.querySelector('a').textContent=C()[4];fallback.querySelector('button').textContent=C()[5];
  fallback.classList.remove('hidden');
  input.select();
 };
 lobby.querySelector('.inviteFallback button').onclick=async()=>{
  const input=lobby.querySelector('.inviteFallback input');
  try{await navigator.clipboard.writeText(input.value);toast(copy.link_copied||'Link copied')}
  catch(_){input.focus();input.select()}
 };
 const lobbyDetails=document.createElement('details');lobbyDetails.id='lobbyExtras';lobbyDetails.innerHTML='<summary></summary>';el('sharedSetup').before(lobbyDetails);lobbyDetails.appendChild(el('sharedSetup'));
 // The onboarding is available on demand; only adult rooms require an explicit confirmation.
 const priorHow=window.showHowTo;window.showHowTo=function(){if(window.lastState?.adult_required)priorHow()};
 const oldCreate=window.createGame;let creating=false;
 window.createGame=async function(){
  if(creating)return;if(!name.value.trim()){name.focus();return toast(copy.name_required||T()[4])}
  createError.classList.add('hidden');
  if(!advanced.open&&!advanced.dataset.used){
   const presets=audienceType==='family'?['מה היית עושה אם…','משפחה','אוכל']:audienceType==='couple'?['מה היית עושה אם…','זוגיות','אוכל']:['מה היית עושה אם…','חברות ואמון','סודות והרגלים'];
   document.querySelectorAll('#topics [data-topic]').forEach(b=>b.classList.toggle('on',presets.includes(b.dataset.topic)));if(!createAdultRequired())spice=1;
  }
  creating=true;create.disabled=true;try{await accessReady;await oldCreate()}finally{creating=false;create.disabled=false;labels()}
 };
 advanced.addEventListener('input',()=>advanced.dataset.used='1');advanced.addEventListener('click',e=>{if(e.target.closest('button'))advanced.dataset.used='1'});
 const demo=document.createElement('button');demo.id='exampleRoundBtn';demo.type='button';demo.className='demoLink';el('home').appendChild(demo);
 let demoBox=null,demoFocus;
 function closeDemo(){if(!demoBox)return;demoBox.remove();demoBox=null;demoFocus?.focus()}
 demo.onclick=()=>{
  closeDemo();demoFocus=document.activeElement;demoBox=document.createElement('section');demoBox.className='exampleOverlay';demoBox.setAttribute('role','dialog');demoBox.setAttribute('aria-modal','true');demoBox.setAttribute('aria-labelledby','exampleTitle');
  const t=T();demoBox.innerHTML='<div class="exampleCard"><button type="button" class="mini demoClose">'+safe(t[19])+'</button><div class="eyebrow" id="exampleTitle">'+safe(t[12])+'</div><p>'+safe(t[13])+'</p><h2>'+safe(t[14])+'</h2><div class="demoOptions">'+t[15].map((x,i)=>'<button type="button" data-demo="'+i+'">'+safe(x)+'</button>').join('')+'</div><div class="demoAnswer hidden" role="status"></div><button type="button" class="primary demoStart hidden">'+safe(t[18])+'</button></div>';
  document.body.appendChild(demoBox);demoBox.querySelector('.demoClose').onclick=closeDemo;
  demoBox.querySelectorAll('[data-demo]').forEach(b=>b.onclick=()=>{demoBox.querySelectorAll('[data-demo]').forEach(x=>{x.disabled=true;x.classList.toggle('selected',x===b)});const answer=demoBox.querySelector('.demoAnswer');answer.classList.remove('hidden');answer.innerHTML='<h3>'+safe(t[16])+'</h3><p>'+safe(t[17])+'</p>';demoBox.querySelector('.demoStart').classList.remove('hidden')});
  demoBox.querySelector('.demoStart').onclick=()=>{closeDemo();window.mode('create');name.focus()};demoBox.querySelector('.demoClose').focus();
 };
 document.addEventListener('keydown',e=>{if(!demoBox)return;if(e.key==='Escape')closeDemo();if(e.key==='Tab'){const nodes=[...demoBox.querySelectorAll('button:not(:disabled)')].filter(x=>!x.classList.contains('hidden'));const a=nodes[0],z=nodes.at(-1);if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}});
 const insight=document.createElement('section');insight.id='relationshipCard';insight.className='relationshipCard hidden';el('scores').after(insight);
 const shareResult=document.createElement('button');shareResult.id='saveResultCard';shareResult.type='button';shareResult.className='mini';insight.after(shareResult);
 let finalData=null;
 shareResult.onclick=()=>{if(!finalData)return;const cv=document.createElement('canvas');cv.width=1080;cv.height=1920;const c=cv.getContext('2d');c.fillStyle='#faf7ff';c.fillRect(0,0,1080,1920);c.textAlign='center';c.direction=document.documentElement.dir;c.fillStyle='#7135c9';c.font='bold 100px Arial';c.fillText('MIPO',540,280);c.fillStyle='#302047';c.font='bold 48px Arial';c.fillText(T()[20],540,410);c.font='40px Arial';(finalData.players||[]).slice().sort((a,b)=>b.score-a.score).slice(0,8).forEach((p,i)=>c.fillText(String(p.name).slice(0,24)+'  ·  '+p.score,540,590+i*120));c.font='32px Arial';c.fillStyle='#7135c9';c.fillText('Play together. Discover each other.',540,1650);cv.toBlob(blob=>{if(!blob)return;const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='MIPO-results.png';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)},'image/png')};
 function labels(){const t=T();el('createTitle').textContent=t[0];el('quickName').textContent=t[4];el('quickAudience').textContent=t[1];advanced.querySelector('summary').textContent=t[2];el('quickDefaults').textContent=(advanced.dataset.used||rounds!==8)?String(rounds)+' '+(copy.rounds_word||'rounds')+' · '+t[29]:t[3];create.textContent=t[5];demo.textContent=t[11];lobby.querySelector('p').textContent=t[9];lobby.querySelector('button').textContent=shareLabel();lobby.querySelector('b').textContent=shareLabel();lobbyDetails.querySelector('summary').textContent=t[10];el('hostIntroPhoto').textContent=t[7];el('how3').textContent=t[29];el('photoHelp').textContent=t[7];el('photoTitle').textContent=t[6];el('photoToggle').textContent=t[6];el('homeSub').textContent=[copy.how1,copy.how2].filter(Boolean).join(' ');const rules=el('hostIntroRules').children;if(rules[2])rules[2].querySelector('span:last-child').textContent=t[27];const packages=document.querySelector('.pilotPackagesLink');if(packages)packages.textContent=t[30];}
 const originalPlayerLabel=window.playerLabel;window.playerLabel=p=>safe(p.name);
 const oldCopy=window.applyCopy;window.applyCopy=function(){oldCopy();labels()};
 const oldRender=window.render;window.render=function(d){oldRender(d);labels();const inLobby=d.status==='lobby';el('photoToggle').classList.toggle('hidden',!inLobby||!d.me||!!d.me.has_photo);el('photoBox').classList.toggle('hidden',!inLobby||(!photoExpanded&&el('photoBox').dataset.editing!=='1'));lobby.classList.toggle('hidden',!inLobby||!d.is_host||crazygamesMode);el('shareBtn').classList.toggle('hidden',!crazygamesMode||!d.is_host);el('howOverlay').classList.toggle('hidden',!inLobby||!d.adult_required||!!d.me?.adult_confirmed||sessionStorage.getItem('how_'+d.code)==='1');lobbyDetails.classList.toggle('hidden',!inLobby);if(!inLobby)lobbyDetails.open=false;
  if(lobby.dataset.code!==d.code){lobby.dataset.code=d.code;lobby.querySelector('.inviteFallback').classList.add('hidden')}
  const notice=lobby.querySelector('.inviteAiNotice');notice.textContent=C()[2];notice.classList.toggle('hidden',!s.ai_fallback_used||s.code!==d.code||d.ai_images_enabled===true);
  const role=el('questionRole')||document.createElement('div');role.id='questionRole';role.className='questionRole';el('question').before(role);role.textContent=d.reveal?'':d.me?.id===d.subject?.id?T()[26]:T()[25]+' '+(d.subject?.name||'');
  const context=el('revealContext')||document.createElement('p');context.id='revealContext';context.className='revealContext';el('answer').before(context);context.textContent=d.question||'';context.classList.toggle('hidden',!d.reveal);
  const prompt=el('revealTalk')||document.createElement('p');prompt.id='revealTalk';prompt.className='revealTalk';el('reaction').after(prompt);prompt.textContent=T()[24];prompt.classList.toggle('hidden',!d.reveal);
  const done=d.status==='finished';insight.classList.toggle('hidden',!done);shareResult.classList.toggle('hidden',!done);if(done){finalData=d;shareResult.textContent=T()[23];const byId=new Map(d.players.map(p=>[p.id,p]));const stats=(d.relationships||[]).filter(x=>x.attempts>0);insight.innerHTML='<h3>'+safe(T()[20])+'</h3>'+(stats.length?stats.slice(0,12).map(x=>'<div class="relationshipRow"><span>'+safe(byId.get(x.guesser_id)?.name)+' → '+safe(byId.get(x.subject_id)?.name)+'</span><b>'+x.correct+'/'+x.attempts+'</b><small>'+safe(T()[21])+'</small></div>').join(''):'<p>'+safe(T()[22])+'</p>');}
 };
 const accessReady=crazygamesMode?Promise.resolve():window.req('/api/access?client_id='+encodeURIComponent(deviceId)).then(access=>{if(Number(access.paid_games)>0&&!advanced.dataset.used&&rounds===8){rounds=18;document.querySelectorAll('.lengths button').forEach(b=>b.classList.toggle('on',b.dataset.r==='18'));labels()}}).catch(()=>{});
 labels();new MutationObserver(labels).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});if(window.lastState)window.render(window.lastState);
 if(bootParams.get('new')==='1'&&bootParams.get('setup')==='1'){
  const url=new URL(location.href);url.searchParams.delete('setup');history.replaceState({},'',url);mode('create');
 }
})();
