/* Local companion, audio and accessible score dock. Never delays game actions. */
(() => {
  const labels={
    he:['השתק צלילים','הפעל צלילים','ניקוד','סגור','יש לנו {n} מנצחים!','המנצח: {name}','הפרס לכל זוכה: ','רוצים להכריע?','שובר שוויון: מחזור תורות מלא לכולם. עד 3 מחזורים.','שובר שוויון','חוגגים את התיקו!','תיקו במקום הראשון','הכללים'],
    en:['Mute sounds','Enable sounds','Scores','Close','We have {n} winners!','Winner: {name}','Prize for each winner: ','Break the tie?','A full turn cycle for everyone. Up to 3 cycles.','Tie-break','Celebrate the tie!','Tied for first','Rules'],
    es:['Silenciar sonidos','Activar sonidos','Puntos','Cerrar','¡Tenemos {n} ganadores!','Ganador: {name}','Premio para cada ganador: ','¿Desempatamos?','Un ciclo completo de turnos para todos. Máximo 3 ciclos.','Desempate','¡Celebramos el empate!','Empate en primer lugar','Reglas'],
    'pt-BR':['Silenciar sons','Ativar sons','Pontos','Fechar','Temos {n} vencedores!','Vencedor: {name}','Prêmio para cada vencedor: ','Desempatar?','Um ciclo completo de turnos para todos. Até 3 ciclos.','Desempate','Vamos celebrar o empate!','Empate em primeiro','Regras'],
    fr:['Couper les sons','Activer les sons','Scores','Fermer','Nous avons {n} gagnants !','Gagnant : {name}','Prix pour chaque gagnant : ','Départager ?','Un cycle complet de tours pour tous. Jusqu’à 3 cycles.','Départage','Célébrons l’égalité !','Égalité en tête','Règles'],
    ja:['音をオフにする','音をオンにする','得点','閉じる','優勝者は{n}人！','優勝：{name}','各優勝者の賞品：','決着をつける？','全員に同じ回数の出番。最大３周。','延長戦','同点を祝おう！','同点１位','ルール']
  };
  const lang=()=>document.documentElement.lang;
  const L=()=>labels[lang()]||labels.en;
  const el=id=>document.getElementById(id);
  const safe=x=>String(x??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch(_){return fallback}};
  const write=(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value))}catch(_){}};
  let enabled=true,activated=false,context,busyUntil=0,audioEpoch=0;
  try{enabled=localStorage.getItem('plot_sound')!=='off'}catch(_){}
  const nodes=new Set();
  function hush(){audioEpoch++;busyUntil=0;for(const n of nodes){try{n.stop()}catch(_){}}nodes.clear();if(context&&context.state==='running')context.suspend().catch(()=>{});}
  function unlock(){activated=true;try{const A=window.AudioContext||window.webkitAudioContext;if(enabled&&A){context ||= new A();if(context.state==='suspended')context.resume().catch(()=>{});}}catch(_){}}
  function sound(kind){
    if(!enabled||!activated||document.hidden||Date.now()<busyUntil)return;
    try{
      unlock();if(!context)return;
      const melodies={tap:[560],saved:[660,880],next:[440,600],ready:[523,659,784],win:[523,659,784,1046]};
      const voice={hum:[[170,190,.30],[190,150,.18]],peek:[[340,540,.12],[450,270,.16]],oops:[[450,180,.32]],wow:[[200,570,.24],[570,340,.14]],tie:[[290,420,.15],[420,290,.20]],taDa:[[320,440,.12],[470,660,.30]]};
      const syllables=voice[kind]||((melodies[kind]||melodies.tap).map(hz=>[hz,hz,.09]));
      const epoch=audioEpoch;let start=context.currentTime+.015;
      for(const [from,to,duration] of syllables){
        const oscillator=context.createOscillator(),gain=context.createGain();
        oscillator.type=voice[kind]?'triangle':'sine';oscillator.frequency.setValueAtTime(from,start);oscillator.frequency.exponentialRampToValueAtTime(to,start+duration);
        gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(voice[kind]?.13:.035,start+.015);gain.gain.exponentialRampToValueAtTime(.0001,start+duration+.045);
        if(voice[kind]&&context.createBiquadFilter){const formant=context.createBiquadFilter();formant.type='bandpass';formant.frequency.setValueAtTime(kind==='hum'?280:440,start);formant.Q.value=.7;oscillator.connect(formant);formant.connect(gain);oscillator.onended=()=>{nodes.delete(oscillator);oscillator.disconnect();formant.disconnect();gain.disconnect()};}
        else{oscillator.connect(gain);oscillator.onended=()=>{nodes.delete(oscillator);oscillator.disconnect();gain.disconnect()};}
        gain.connect(context.destination);nodes.add(oscillator);if(epoch!==audioEpoch)return;
        oscillator.start(start);oscillator.stop(start+duration+.06);start+=duration+.065;
      }
      busyUntil=Date.now()+(start-context.currentTime)*1000;
    }catch(_){/* Sound never blocks play. */}
  }
  const toggle=document.createElement('button');toggle.id='soundToggle';toggle.type='button';toggle.className='soundToggle';
  function label(){toggle.textContent=enabled?'🔊':'🔇';toggle.setAttribute('aria-label',L()[enabled?0:1]);toggle.title=L()[enabled?0:1];toggle.setAttribute('aria-pressed',String(enabled));}
  toggle.onclick=()=>{enabled=!enabled;try{localStorage.setItem('plot_sound',enabled?'on':'off')}catch(_){}label();if(enabled){unlock();sound('tap')}else hush()};
  document.querySelector('.topbar').appendChild(toggle);label();
  document.addEventListener('pointerdown',unlock,{passive:true});
  document.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')unlock()});
  document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||b.disabled||b===toggle)return;unlock();sound('tap')},true);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)hush()});

  const dock=document.createElement('aside');dock.id='scoreDock';dock.className='scoreDock hidden';
  dock.innerHTML='<div id="companionMoment" class="companionMoment hidden"></div><section id="scorePanel" class="scorePanel hidden" aria-label="Scores"><div class="scorePanelHeading"><b id="scorePanelTitle"></b><button id="closeScores" type="button"></button></div><div id="scoreRows"></div></section><button id="scoreBar" class="scoreBar" type="button" aria-controls="scorePanel" aria-expanded="false"></button>';
  document.body.appendChild(dock);dock.appendChild(document.querySelector('.nextDock'));
  let current=null,previous=null,panelPinned=false,autoTimer,momentTimer,lastScores='',lastLine='',lineUntil=0,loadingKey='',lastAntic=0;
  const shownBoards=new Set(),reactions=new Set(),gateStates=new Map();
  function openScores(manual=false){panelPinned=manual;clearTimeout(autoTimer);el('scorePanel').classList.remove('hidden');el('scoreBar').setAttribute('aria-expanded','true');if(!manual)autoTimer=setTimeout(closeScores,4500)}
  function closeScores(){panelPinned=false;clearTimeout(autoTimer);el('scorePanel').classList.add('hidden');el('scoreBar').setAttribute('aria-expanded','false')}
  el('scoreBar').onclick=()=>el('scorePanel').classList.contains('hidden')?openScores(true):closeScores();
  el('closeScores').onclick=closeScores;
  el('scorePanel').addEventListener('pointerdown',()=>{panelPinned=true;clearTimeout(autoTimer)});
  el('scorePanel').addEventListener('focusin',()=>{panelPinned=true;clearTimeout(autoTimer)});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeScores()});
  function ranked(d){const ids=d.tiebreak?.contenders||[];return [...d.players].sort((a,b)=>(ids.length?(Number(ids.includes(b.id))-Number(ids.includes(a.id))):0)||b.score-a.score||a.id-b.id)}
  function leaders(d){const list=ranked(d).filter(p=>!d.tiebreak?.contenders?.length||d.tiebreak.contenders.includes(p.id));return list.filter(p=>p.score===list[0]?.score)}
  function autoScores(d){
    if(d.status!=='playing'||!d.reveal||(d.round+1)%2!==0)return;
    const key=d.code+'_'+d.image_run+'_'+d.round;
    if(gateStates.get(key)==='pending'||shownBoards.has(key))return;
    shownBoards.add(key);if(!panelPinned)openScores();
  }
  function scoreUI(d){
    const playing=d.status==='playing';dock.classList.toggle('hidden',!playing);document.body.classList.toggle('hasScoreDock',playing);
    dock.querySelector('.nextDock').classList.toggle('hidden',!playing||!d.reveal||!d.is_host);if(!playing){closeScores();return}
    const list=ranked(d),top=list[0]?.score,front=list.slice(0,d.players.length===2?2:3);
    if(d.me&&!front.some(p=>p.id===d.me.id)){const me=list.find(p=>p.id===d.me.id);if(me)front.push(me)}
    const key=JSON.stringify([list.map(p=>[p.id,p.name,p.score]),lang(),d.me?.id]);
    if(key!==lastScores){lastScores=key;
      el('scoreBar').innerHTML='<span class="scoreCaption">'+safe(L()[2])+' ▴</span><span class="scoreChips">'+front.map(p=>'<span class="scoreChip '+(p.id===d.me?.id?'isMe':'')+'"><span class="scoreName">'+safe(p.name)+'</span><strong>'+p.score+'</strong></span>').join('')+'</span>';
      el('scoreRows').innerHTML=list.map(p=>'<div class="dockScoreRow"><span class="dockRank">'+(1+list.filter(x=>x.score>p.score).length)+'</span><span class="dockName">'+safe(p.name)+'</span>'+((d.winner_ids||leaders(d).map(x=>x.id)).includes(p.id)?'<span aria-hidden="true">🏆</span>':'')+'<strong>'+p.score+'</strong></div>').join('');
    }
    el('scorePanelTitle').textContent=leaders(d).length>1?L()[11]:L()[2];el('closeScores').textContent=L()[3];el('scorePanel').setAttribute('aria-label',L()[2]);
    autoScores(d);
  }
  function mascot(mood='peek'){return '<div class="popMascot mood-'+mood+'" aria-hidden="true"><span class="popBrow"></span><span class="popEyes">••</span><span class="popSmile"></span><span class="popHand left"></span><span class="popHand right"></span><span class="popSpark">✦</span></div>'}
  function draw(kind='wait'){
    const language=lang(),bank=window.PlotLines[language]||window.PlotLines.en;
    const gameKey=(current?.code||'home')+'_'+((current?.image_run||0)-(current?.tiebreak?.sets||0))+'_'+language;
    const store=read('plot_companion_history',{games:{},recent:[]});store.games ||= {};store.recent ||= [];
    const used=store.games[gameKey]||[];let entries=(bank[kind]||bank.wait).map((line,i)=>({id:language+':'+kind+':'+i,line}));
    let available=entries.filter(e=>!used.includes(e.id));
    if(!available.length&&kind!=='wait')return draw('wait');
    if(!available.length){available=entries;store.games[gameKey]=[]}
    const fresh=available.filter(e=>!store.recent.includes(e.id));if(fresh.length)available=fresh;
    const pick=available[Math.floor(Math.random()*available.length)];
    store.games[gameKey]=[...(store.games[gameKey]||[]),pick.id];store.recent=[...store.recent,pick.id].slice(-24);
    const keys=Object.keys(store.games);while(keys.length>10)delete store.games[keys.shift()];write('plot_companion_history',store);
    return pick.line.replaceAll('{name}',current?leaders(current)[0]?.name||'':'');
  }
  function eventKind(d){
    const lead=leaders(d),old=previous?leaders(previous):[];
    if(previous&&previous.code===d.code&&old.length===1&&lead.length===1&&old[0].id!==lead[0].id)return 'leader';
    if(lead.length>1&&lead[0].score>0)return 'tie';
    if(d.all_guesses?.length&&d.all_guesses.every(g=>!g.correct))return 'miss';
    return 'correct';
  }
  function moment(kind){const box=el('companionMoment');box.innerHTML=mascot(kind)+'<p></p>';box.querySelector('p').textContent=draw(kind);box.classList.remove('hidden');clearTimeout(momentTimer);momentTimer=setTimeout(()=>box.classList.add('hidden'),6000);sound({leader:'wow',tie:'tie',miss:'oops',correct:'taDa',win:'win'}[kind]||'peek')}
  function companion(force=false){
    if(!current)return;
    const targets=['heroStatus','finalHeroStatus'].map(el).filter(st=>st&&!st.classList.contains('hidden')&&(st.id==='heroStatus'?el('visualStage').classList.contains('is-loading'):st.classList.contains('is-loading')));
    const waiting=el('waiting');if(!targets.length&&current.status==='playing'&&!current.reveal&&waiting&&!waiting.classList.contains('hidden'))targets.push(waiting);
    if(!targets.length){loadingKey='';return}
    const key=current.code+'_'+current.image_run+'_'+current.round+'_'+current.status+'_'+targets[0].id;
    const changed=loadingKey!==key;let newAntic=false;
    if(changed||force||Date.now()>lineUntil){newAntic=true;loadingKey=key;lastLine=draw(current.status==='finished'?'win':'wait');lineUntil=Date.now()+7500}
    for(const status of targets){let box=status.querySelector('.loadingCompanion');if(!box){box=document.createElement('div');box.className='loadingCompanion';box.innerHTML=mascot(['peek','hum','wow','tie'][Math.floor(Math.random()*4)])+'<p class="loadingJoke"></p>';status.appendChild(box)}box.querySelector('.loadingJoke').textContent=lastLine;if(newAntic)animateMascot(box)}
    // Spaced, soft vocal gestures. Never an endless audio loop or overlapping voices.
    if((force||changed)&&Date.now()-lastAntic>11000){lastAntic=Date.now();sound(['hum','peek','wow'][Math.floor(Math.random()*3)])}
  }
  function animateMascot(box){
    const actor=box.querySelector('.popMascot');if(!actor||window.matchMedia?.('(prefers-reduced-motion: reduce)').matches)return;
    actor.classList.remove('antic-spin','antic-dive','antic-hop');void actor.offsetWidth;
    actor.classList.add(['antic-spin','antic-dive','antic-hop'][Math.floor(Math.random()*3)]);
  }
  // The companion also peeks from the score strip during quiet question time.
  const visitor=document.createElement('div');visitor.className='companionVisitor hidden';visitor.innerHTML=mascot();dock.prepend(visitor);
  let visitorTimer;
  setInterval(()=>{
    if(document.hidden||!current||current.status!=='playing'||current.reveal||!el('waiting').classList.contains('hidden'))return;
    visitor.classList.remove('hidden');animateMascot(visitor);sound(['hum','peek','oops','wow'][Math.floor(Math.random()*4)]);
    clearTimeout(visitorTimer);visitorTimer=setTimeout(()=>visitor.classList.add('hidden'),2300);
  },17000);
  function finishUI(d){
    if(d.status!=='finished')return;
    const ws=d.players.filter(p=>(d.winner_ids||leaders(d).map(x=>x.id)).includes(p.id));
    el('finishTitle').textContent=ws.length>1?L()[4].replace('{n}',ws.length):L()[5].replace('{name}',ws[0]?.name||'');
    el('finalPrize').classList.toggle('hidden',!d.prize);el('finalPrize').textContent=d.prize?L()[6]+d.prize:'';
    let choice=el('tieChoice');if(!choice){choice=document.createElement('div');choice.id='tieChoice';el('finish').insertBefore(choice,el('finalHeroStatus'))}
    choice.classList.toggle('hidden',!d.can_tiebreak||!d.is_host);
    if(d.can_tiebreak&&d.is_host){
      if(!el('tieBreakBtn'))choice.innerHTML='<p id="tieHelp"></p><button type="button" id="tieBreakBtn"></button>';
      el('tieHelp').textContent=L()[8];el('tieBreakBtn').disabled=gateStates.get(d.code+'_'+d.image_run+'_final')==='pending';el('tieBreakBtn').textContent='⚡ '+L()[7];el('tieBreakBtn').onclick=async()=>{
        const button=el('tieBreakBtn');button.disabled=true;
        try{await window.req('/api/'+s.code+'/tiebreak',{host:s.host,image_run:d.image_run});stateSig='';await load()}catch(_){toast(copy.retry||'Try again')}finally{button.disabled=false}
      };
    }
  }
  const adultTopics=new Set(['דייטים','אינטימיות למבוגרים']);
  const phrase=(he,en)=>lang()==='he'?he:en;
  const guideCopy={
    he:['לפני שמתחילים — איך משחקים?','הבנתי, בואו ניצור משחק','איך משחקים?',[
      'בכל סיבוב שחקן עונה בסוד, והאחרים מנחשים מה בחר.',
      'כל ניחוש נכון מזכה בנקודה. הניקוד זמין בתחתית המסך.',
      'תמונת AI מצחיקה ממחישה את התשובה. מחכים שתופיע לפני שממשיכים.',
      'המארח בוחר נושאים ורמת חריפות, ומשתף לינק להזמנת השחקנים.'
    ],'רוצים ערב למבוגרים? בהגדרות יש אפשרויות 18+ לדייטים, משיכה ואינטימיות. הן נפתחות לבחירה, והמשחק מתחיל רק לאחר אישור גיל והסכמה מכל המשתתפים. במצב משפחה האפשרויות מוסתרות.','דייטים, משיכה ואינטימיות — לבחירה ובהסכמת כל המשתתפים.'],
    en:['Before we play — the basics','Got it, let’s create a game','How to play',[
      'Each round, one player answers secretly. Everyone else guesses their choice.',
      'Each correct guess earns a point. Scores are available at the bottom.',
      'A funny AI image brings the answer to life. Wait for it before continuing.',
      'The host picks topics and boldness, then shares an invitation link.'
    ],'Want an adults-only evening? Settings include optional 18+ dating, attraction and intimacy topics. Every player must confirm their age and consent before play. These options are hidden in family mode.','Dating, attraction and intimacy — optional, with everyone’s consent.'],
    es:['Antes de jugar — las reglas','Entendido, vamos a crear una partida','Cómo jugar',[
      'En cada ronda, alguien responde en secreto y los demás adivinan su elección.',
      'Cada acierto suma un punto. Los puntos están abajo.',
      'Una imagen divertida de IA representa la respuesta. Esperad a verla antes de continuar.',
      'El anfitrión elige temas e intensidad y comparte un enlace de invitación.'
    ],'¿Una noche para adultos? Los ajustes incluyen temas opcionales de citas, atracción e intimidad para mayores de 18. Todos deben confirmar su edad y consentimiento antes de jugar. Se ocultan en modo familia.','Citas, atracción e intimidad: opcionales y con el consentimiento de todos.'],
    'pt-BR':['Antes de jogar — as regras','Entendi, vamos criar um jogo','Como jogar',[
      'A cada rodada, uma pessoa responde em segredo e as outras adivinham sua escolha.',
      'Cada acerto vale um ponto. A pontuação fica na parte inferior.',
      'Uma imagem divertida de IA ilustra a resposta. Esperem aparecer antes de continuar.',
      'Quem organiza escolhe temas e intensidade e compartilha o link de convite.'
    ],'Querem uma noite para adultos? As configurações incluem temas opcionais de encontros, atração e intimidade para maiores de 18. Todos confirmam idade e consentimento antes de jogar. Essas opções ficam ocultas no modo família.','Encontros, atração e intimidade — opcionais, com o consentimento de todos.'],
    fr:['Avant de jouer — les règles','Compris, créons une partie','Comment jouer',[
      'À chaque tour, une personne répond en secret et les autres devinent son choix.',
      'Chaque bonne réponse rapporte un point. Les scores restent accessibles en bas.',
      'Une image IA amusante illustre la réponse. Attendez son affichage avant de continuer.',
      'L’hôte choisit les thèmes et le niveau, puis partage un lien d’invitation.'
    ],'Une soirée entre adultes ? Les réglages proposent des thèmes facultatifs de rencontres, attirance et intimité réservés aux 18 ans et plus. Chaque joueur confirme son âge et son accord avant de jouer. Ces options sont masquées en mode famille.','Rencontres, attirance et intimité — au choix, avec l’accord de tous.'],
    ja:['始める前に — 遊び方','わかった！ゲームを作る','遊び方',[
      '毎回、1人がこっそり回答し、ほかの人はその答えを予想します。',
      '予想が当たると1点。得点は画面下で確認できます。',
      '答えをもとに楽しいAI画像が完成します。表示されてから次へ進みましょう。',
      'ホストがテーマとレベルを選び、招待リンクを共有します。'
    ],'大人だけの夜にしたい？設定には、デート・魅力・親密さを扱う18歳以上向けの選択肢があります。開始前に全員の年齢確認と同意が必要です。ファミリーモードでは表示されません。','デート・魅力・親密さのテーマ — 全員の同意のもとで選べます。']
  };
  const guideText=()=>guideCopy[lang()]||guideCopy.en;
  const intro=document.createElement('section');intro.id='hostIntro';intro.className='card hidden';intro.setAttribute('aria-labelledby','hostIntroTitle');
  intro.innerHTML='<h2 id="hostIntroTitle" tabindex="-1"></h2><ol id="hostIntroRules"></ol><p id="hostIntroAdult" class="setup-note"></p><button type="button" id="hostIntroContinue" class="primary"></button>';
  el('create').before(intro);
  const guideLink=document.createElement('button');guideLink.type='button';guideLink.id='hostGuideLink';guideLink.className='mini';el('createTitle').after(guideLink);
  function guideLabels(){const c=guideText();el('hostIntroTitle').textContent=c[0];el('hostIntroContinue').textContent=c[1];guideLink.textContent=c[2];el('hostIntroRules').innerHTML=c[3].map(rule=>'<li>'+safe(rule)+'</li>').join('');el('hostIntroAdult').textContent=c[4];if(el('adultOptionsHint'))el('adultOptionsHint').textContent=c[5]}
  const baseMode=window.mode;
  function showHostGuide(){baseMode('create');el('create').classList.add('hidden');intro.classList.remove('hidden');guideLabels();intro.scrollIntoView({block:'start'});el('hostIntroTitle').focus({preventScroll:true})}
  window.mode=function(next){intro.classList.add('hidden');if(next==='create')showHostGuide();else baseMode(next)};
  guideLink.onclick=showHostGuide;
  el('hostIntroContinue').onclick=()=>{intro.classList.add('hidden');baseMode('create');el('create').scrollIntoView({block:'start'});el('cname').focus({preventScroll:true})};
  guideLabels();
  function adultSetup(){
    const content=el('contentTopics');if(!content)return;
    let section=el('adultOptions');
    if(!section){section=document.createElement('details');section.id='adultOptions';section.innerHTML='<summary></summary><div class="topics"></div>';content.after(section)}
    section.querySelector('summary').textContent=phrase('אפשרויות לערב של מבוגרים · 18+','Adult evening options · 18+');
    let hint=el('adultOptionsHint');if(!hint){hint=document.createElement('span');hint.id='adultOptionsHint';section.querySelector('summary').appendChild(hint)}hint.textContent=guideText()[5];
    const family=audienceType==='family';section.classList.toggle('hidden',family);
    const target=section.querySelector('div');if(content.querySelector('[data-topic="דייטים"]'))target.querySelectorAll('[data-topic]').forEach(b=>b.remove());
    for(const b of document.querySelectorAll('#topics [data-topic]'))if(adultTopics.has(b.dataset.topic)){
      target.appendChild(b);b.dataset.extra='0';b.classList.remove('hidden');
      if(family)b.classList.remove('on');
    }
    const bold=document.querySelector('.spice [data-s="3"]');
    bold.classList.toggle('hidden',family||!section.open);
    if((family||!section.open)&&spice===3){spice=2;document.querySelectorAll('.spice button').forEach(b=>b.classList.toggle('on',b.dataset.s==='2'))}
    el('adultText').textContent=phrase('אני בן/בת 18 ומעלה ומסכים/ה לתכנים למבוגרים. כל שחקן יאשר בנפרד לפני ההתחלה.','I am 18+ and agree to adult content. Each player must confirm separately before play.');
    section.ontoggle=()=>{if(!section.open){target.querySelectorAll('.on').forEach(b=>b.classList.remove('on'));el('adultConfirm').checked=false}adultSetup();syncCreateAdult()};
    syncCreateAdult();
    section.appendChild(el('adultBox'));
  }
  const baseTopics=window.renderCreateTopics;window.renderCreateTopics=function(){baseTopics();adultSetup()};
  const baseAudience=window.renderAudience;window.renderAudience=function(){baseAudience();adultSetup()};
  adultSetup();
  const baseEdit=window.openSetupEdit;window.openSetupEdit=function(){
    baseEdit();let section=el('editAdultOptions');if(!section){section=document.createElement('details');section.id='editAdultOptions';section.innerHTML='<summary></summary>';el('editTopics').appendChild(section)}
    section.querySelector('summary').textContent=phrase('אפשרויות לערב של מבוגרים · 18+','Adult evening options · 18+');
    document.querySelectorAll('#editTopics [data-topic]').forEach(b=>{if(adultTopics.has(b.dataset.topic))section.appendChild(b)});
    section.open=!!window.lastState?.adult_required;
  };
  const age=document.createElement('div');age.id='playerAge';age.className='setup-note hidden';
  age.innerHTML='<label><input type="checkbox" id="playerAgeCheck"><span></span></label><button class="mini" id="playerAgeSave"></button>';
  el('host').before(age);
  el('playerAgeSave').onclick=async()=>{if(!el('playerAgeCheck').checked)return;const b=el('playerAgeSave');b.disabled=true;try{await req('/api/'+s.code+'/adultconfirm',{token:s.token,confirmed:true});stateSig='';await load()}catch(_){toast(copy.retry)}finally{b.disabled=false}};
  function lobbyPolish(d){
    document.querySelectorAll('#voteTopics [data-topic]').forEach(b=>{if(adultTopics.has(b.dataset.topic)&&!d.adult_required)b.classList.add('hidden')});
    age.classList.toggle('hidden',d.status!=='lobby'||!d.adult_required||!d.me||d.me.adult_confirmed);
    age.querySelector('span').textContent=phrase('אני מאשר/ת שאני בן/בת 18 ומעלה ומסכים/ה לתכני החדר','I confirm I am 18+ and agree to this room’s adult content');
    el('playerAgeSave').textContent=phrase('אישור 18+','Confirm 18+');
    el('photoHelp').textContent=phrase('כדי להשתתף, הוסיפו תמונה שלכם ואשרו שימוש בה לתמונות המשחק הפרטי.','To play, add your photo and consent to using it for this private game’s images.');
    if(d.status==='lobby'){
      if(d.me&&!d.me.has_photo)el('photoBox').classList.remove('hidden');
      const start=el('start');if(start&&start.disabled&&d.players.filter(p=>p.active).length>=2)start.textContent=d.players.some(p=>p.active&&!p.has_photo)?phrase('ממתינים לתמונות מכל השחקנים','Waiting for everyone’s photo'):phrase('ממתינים לאישור 18+ מכל השחקנים','Waiting for everyone’s 18+ confirmation');
    }
  }
  // Invitation links are the visible join mechanism; the room code stays internal.
  el('jcode').placeholder=phrase('הדביקו את לינק ההזמנה','Paste invitation link');el('jcode').removeAttribute('maxlength');
  el('jcode').classList.toggle('hidden',!!new URLSearchParams(location.search).get('code'));
  const baseJoin=window.joinGame;window.joinGame=async function(){let field=el('jcode');try{if(field.value.includes('://'))field.value=new URL(field.value).searchParams.get('code')||''}catch(_){}return baseJoin()};
  const baseReq=window.req;
  window.req=async function(path,body){const result=await baseReq(path,body);if(body&&/\/(answer|guess|matchanswer)$/.test(path))sound('saved');return result};
  const baseRender=window.render;
  window.render=function(d){
    const newGame=current&&(current.code!==d.code||current.image_run!==d.image_run);if(newGame){closeScores();lastLine='';loadingKey='';el('companionMoment').classList.add('hidden')}
    if(previous&&previous.round!==d.round)closeScores();
    current=d;baseRender(d);label();scoreUI(d);finishUI(d);lobbyPolish(d);
    const help=el('ruleHelp');if(help)help.querySelector('summary span').textContent=L()[12];
    if(d.tiebreak?.sets&&d.status==='playing')el('round').textContent=L()[9]+' '+d.tiebreak.sets+' / 3 · '+(d.round-d.tiebreak.start+1)+' / '+d.tiebreak.order.length;
    const key=d.code+'_'+d.image_run+'_'+d.round+'_'+d.status;
    if(previous&&previous.code===d.code&&!reactions.has(key)){
      if(d.status==='finished'&&previous.status!=='finished'){reactions.add(key);sound('win')}
      else if(d.reveal&&!previous.reveal&&d.status==='playing'){reactions.add(key);moment(eventKind(d))}
      else if(d.round!==previous.round)sound('next');
    }
    companion();previous=d;
  };
  const baseGate=window.setImageGate;
  window.setImageGate=function(d,final,state){
    const key=d.code+'_'+d.image_run+'_'+(final?'final':d.round),before=gateStates.get(key);baseGate(d,final,state);gateStates.set(key,state);
    if(final&&el('tieBreakBtn'))el('tieBreakBtn').disabled=state==='pending';if(before==='pending'&&state==='ready')sound('ready');if(gateStates.size>100)gateStates.delete(gateStates.keys().next().value);
    if(!final&&state!=='pending')autoScores(d);
  };
  new MutationObserver(()=>{guideLabels();label();lastScores='';if(current){scoreUI(current);finishUI(current)}companion(true)}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  setInterval(()=>{if(!document.hidden)companion(Date.now()>lineUntil)},7500);
  if(window.lastState)window.render(window.lastState);
  if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'}).catch(()=>{});
})();
