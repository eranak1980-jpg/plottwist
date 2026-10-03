/* Local companion, audio and accessible score dock. Never delays game actions. */
(() => {
  // Commerce guard: server enforcement remains authoritative. This wrapper only
  // gives the host a clear route to checkout instead of a generic retry toast.
  const commerceReq=window.req;
  if(typeof commerceReq==='function'){
    window.req=async function(path,body){
      const params=new URLSearchParams(location.search),requestedAccess=params.get('access');
      if(path==='/api/create'&&body&&(requestedAccess==='trial'||requestedAccess==='qa')){
        body={...body,access:requestedAccess};
        if(requestedAccess==='qa')body.qa_key=params.get('qa')||'';
      }
      try{
        const result=await commerceReq(path,body);
        if(/^\/api\/state\//.test(path)&&result?.is_host&&result.status==='lobby'&&result.access_kind==='paid'&&Number(result.max_rounds||18)<30){
          setTimeout(()=>{
            const host=document.getElementById('host');if(!host||document.getElementById('extendGameBtn'))return;
            const button=document.createElement('button');button.id='extendGameBtn';button.className='mini';button.textContent='✨ Extend to 30 questions · $2.99';
            button.onclick=()=>{try{sessionStorage.setItem('mipo_extension_auth',JSON.stringify({code:result.code,host:s.host}))}catch(_){}location.href='/checkout?product=extension'};host.appendChild(button);
          },0);
        }
        return result;
      }catch(error){
        if(error?.message==='payment_required'||error?.message==='trial_already_used'){
          try{sessionStorage.setItem('mipo_commerce_notice',error.message)}catch(_){}
          location.href='/play-mipo#pricing';
          return new Promise(()=>{});
        }
        throw error;
      }
    };
    try{req=window.req}catch(_){}
  }
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
  let enabled=true,activated=false,context,busyUntil=0,audioEpoch=0,pendingSound;
  try{enabled=localStorage.getItem('plot_sound')!=='off'}catch(_){}
  const nodes=new Set();
  function hush(){audioEpoch++;busyUntil=0;clearTimeout(pendingSound);for(const n of nodes){try{n.stop()}catch(_){}}nodes.clear();if(context&&context.state==='running')context.suspend().catch(()=>{});}
  function unlock(){activated=true;try{const A=window.AudioContext||window.webkitAudioContext;if(enabled&&A){context ||= new A();if(context.state!=='running')context.resume().catch(()=>{});}}catch(_){}}
  function sound(kind){
    if(!enabled||!activated||document.hidden)return;
    if(Date.now()<busyUntil){
      // A fast save/reveal must not lose its voice just because the tap is still playing.
      if(kind!=='tap'){clearTimeout(pendingSound);const epoch=audioEpoch;pendingSound=setTimeout(()=>{if(epoch===audioEpoch)sound(kind)},busyUntil-Date.now()+20)}
      return;
    }
    try{
      clearTimeout(pendingSound);
      unlock();if(!context)return;
      const spoken={
        hum:['Hmm…','Mmm-hmm…'],peek:['Oh!','Well, well…'],oops:['Oops!','Uh-oh…'],
        wow:['Whoa!','Oh wow!'],tie:['Ooh…','Interesting…'],taDa:['Ta-da!','There it is!'],
        snicker:['Heh heh…','Ha! Knew it.'],wink:['Mm-hmm!','Nice one!'],
        mischief:['Heh heh…','Oh, this is good…'],hmm:['Hmm…','Come on…'],gasp:['Oh!','No way!']
      };
      // Companion moments should sound like a character, not an arcade. Native
      // speech is tiny, works offline on most phones and falls back to WebAudio.
      if(spoken[kind]&&window.speechSynthesis&&window.SpeechSynthesisUtterance){
        const lines=spoken[kind],utterance=new SpeechSynthesisUtterance(lines[Math.floor(Math.random()*lines.length)]);
        utterance.lang='en-US';utterance.rate=kind==='snicker'||kind==='mischief'?1.2:.95;
        utterance.pitch=kind==='hmm'?.72:kind==='gasp'?1.28:1.05;utterance.volume=.32;
        window.speechSynthesis.cancel();window.speechSynthesis.speak(utterance);
        busyUntil=Date.now()+900;return;
      }
      const melodies={tap:[560],saved:[660,880],next:[440,600],ready:[523,659,784],win:[523,659,784,1046]};
      const voice={
        hum:[[300,350,.24],[350,270,.18]],peek:[[420,690,.12],[560,340,.16]],oops:[[510,260,.32]],wow:[[300,740,.24],[740,440,.14]],tie:[[360,520,.15],[520,360,.20]],taDa:[[420,560,.12],[590,830,.30]],
        snicker:[[560,430,.07],[510,390,.07],[590,450,.10]],wink:[[760,1080,.07],[520,820,.08]],mischief:[[280,460,.10],[540,330,.10],[390,720,.09]],hmm:[[270,320,.20],[320,280,.22]],gasp:[[380,940,.12],[940,670,.14]]
      };
      const syllables=voice[kind]||((melodies[kind]||melodies.tap).map(hz=>[hz,hz,.09]));
      const epoch=audioEpoch;let start=context.currentTime+.015;
      for(const [from,to,duration] of syllables){
        const oscillator=context.createOscillator(),gain=context.createGain();
        oscillator.type=voice[kind]?'triangle':'sine';oscillator.frequency.setValueAtTime(from,start);oscillator.frequency.exponentialRampToValueAtTime(to,start+duration);
        gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(voice[kind]?.18:.05,start+.015);gain.gain.exponentialRampToValueAtTime(.0001,start+duration+.045);
        if(voice[kind]&&context.createBiquadFilter){const formant=context.createBiquadFilter();formant.type='lowpass';formant.frequency.setValueAtTime(1800,start);formant.Q.value=.5;oscillator.connect(formant);formant.connect(gain);oscillator.onended=()=>{nodes.delete(oscillator);oscillator.disconnect();formant.disconnect();gain.disconnect()};}
        else{oscillator.connect(gain);oscillator.onended=()=>{nodes.delete(oscillator);oscillator.disconnect();gain.disconnect()};}
        gain.connect(context.destination);nodes.add(oscillator);if(epoch!==audioEpoch)return;
        oscillator.start(start);oscillator.stop(start+duration+.06);start+=duration+.065;
      }
      busyUntil=Date.now()+(start-context.currentTime)*1000;
    }catch(_){/* Sound never blocks play. */}
  }
  let voiceBag=[],lastVoice='';
  function variedSound(pool){
    if(!pool.length)return;
    if(!voiceBag.length||voiceBag.some(k=>!pool.includes(k))){
      voiceBag=[...pool].filter(k=>k!==lastVoice);
      for(let i=voiceBag.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[voiceBag[i],voiceBag[j]]=[voiceBag[j],voiceBag[i]]}
    }
    const kind=voiceBag.shift()||pool.find(k=>k!==lastVoice)||pool[0];lastVoice=kind;sound(kind);
  }
  const toggle=document.createElement('button');toggle.id='soundToggle';toggle.type='button';toggle.className='soundToggle';
  function label(){toggle.textContent=enabled?'🔊':'🔇';toggle.setAttribute('aria-label',L()[enabled?0:1]);toggle.title=L()[enabled?0:1];toggle.setAttribute('aria-pressed',String(enabled));}
  toggle.onclick=()=>{enabled=!enabled;try{localStorage.setItem('plot_sound',enabled?'on':'off')}catch(_){}label();if(enabled){unlock();sound('peek')}else hush()};
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
  function mascot(mood='peek'){return `<div class="popMascot mood-${mood}" aria-hidden="true"><svg viewBox="0 0 100 100" focusable="false"><path fill="#60249c" d="M14 65C14 37 29 27 50 27s36 13 36 38v22H14z"/><path fill="#b9d729" d="M48 35C69 22 22 22 46 2c-2 13 40 10 22 39-3-10-12-8-20-6z"/><g class="mascotEyes"><path fill="#fff9ef" d="M23 54q12-6 24 2c-2 16-24 18-24-2zm32 4q12-8 24-1c-1 18-22 18-24 1z"/><circle cx="30" cy="58" r="6" fill="#381453"/><circle cx="61" cy="61" r="6" fill="#381453"/></g><path fill="none" stroke="#fff9ef" stroke-width="4" stroke-linecap="round" d="M25 44q8-7 17-3m16 5 17 2"/><path class="mascotSmirk" d="M44 76q13 7 24-4" fill="none" stroke="#fff9ef" stroke-width="3" stroke-linecap="round"/><path fill="#60249c" d="M8 78q12-7 19 4v12H7zm65 4q12-10 20 0v12H73z"/><path d="M14 86v7m7-7v7m58-7v7m7-7v7" stroke="#8e52c2" stroke-width="2" stroke-linecap="round"/></svg></div>`}

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
  function moment(kind){const box=el('companionMoment');box.innerHTML=mascot(kind)+'<p></p>';box.querySelector('p').textContent=draw(kind);box.classList.remove('hidden');clearTimeout(momentTimer);momentTimer=setTimeout(()=>box.classList.add('hidden'),6000);const pools={leader:['mischief','wow'],tie:['hmm','tie'],miss:['snicker','gasp','oops'],correct:['wink','taDa'],win:['win']};variedSound(pools[kind]||['peek'])}
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
    if(newAntic&&Date.now()-lastAntic>=8000){lastAntic=Date.now();variedSound(['hum','hmm','peek','snicker','wink'])}
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
    visitor.classList.remove('hidden');animateMascot(visitor);variedSound(['peek','wink','mischief','hmm','gasp']);
    clearTimeout(visitorTimer);visitorTimer=setTimeout(()=>visitor.classList.add('hidden'),2300);
  },15000);
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
  const setupCopy={
    he:['אם בוחרים תכני 18+, סמנו כאן לפני יצירת החדר. כל משתתף יאשר גם בעצמו. במשחק רגיל אין צורך.','אני בן/בת 18 ומעלה ומסכים/ה לתכנים למבוגרים','לפני המשחק: העלו תמונת פנים ברורה ואשרו שימוש בה. התמונה הופכת אתכם לכוכבי תמונות ה־AI.','📸 העלו תמונה כדי להתחיל','בחירת תמונה מהטלפון','סמנו את אישור השימוש מתחת לתמונה — השמירה אוטומטית.','✓ התמונה שלכם מוכנה למשחק','בחדר הזה יש תכני 18+. סמנו אישור ואז לחצו על הכפתור להמשך.'],
    en:['For 18+ topics, tick here before creating the room. Each player also confirms separately. Not needed for a regular game.','I am 18+ and agree to adult content','Before playing, upload a clear face photo and consent to its use. You will star in the AI images.','📸 Add your photo to get started','Choose a photo from your phone','Tick photo consent below the preview — it saves automatically.','✓ Your photo is ready to play','This room includes 18+ topics. Tick to confirm, then press the continue button.'],
    es:['Para temas de 18+, marca aquí antes de crear la sala. Cada participante confirma por separado. No hace falta en una partida normal.','Tengo 18 años o más y acepto el contenido para adultos','Antes de jugar, sube una foto clara de tu cara y autoriza su uso. Serás protagonista de las imágenes de IA.','📸 Añade tu foto para empezar','Elige una foto del teléfono','Marca el permiso bajo la vista previa: se guarda automáticamente.','✓ Tu foto está lista','Esta sala incluye temas de 18+. Marca la casilla y pulsa continuar.'],
    'pt-BR':['Para temas de 18+, marque aqui antes de criar a sala. Cada pessoa confirma separadamente. Não é necessário no jogo comum.','Tenho 18 anos ou mais e aceito conteúdo adulto','Antes de jogar, envie uma foto nítida do rosto e autorize seu uso. Você será protagonista das imagens de IA.','📸 Adicione sua foto para começar','Escolha uma foto do celular','Marque a autorização abaixo da prévia: a foto é salva automaticamente.','✓ Sua foto está pronta','Esta sala inclui temas de 18+. Marque a confirmação e toque em continuar.'],
    fr:['Pour les thèmes 18+, cochez ici avant de créer la salle. Chaque personne confirme séparément. Inutile pour une partie classique.','J’ai 18 ans ou plus et j’accepte le contenu pour adultes','Avant de jouer, ajoutez une photo nette de votre visage et autorisez son utilisation. Vous serez la vedette des images IA.','📸 Ajoutez votre photo pour commencer','Choisir une photo du téléphone','Cochez l’autorisation sous l’aperçu : la photo sera enregistrée automatiquement.','✓ Votre photo est prête','Cette salle propose des thèmes 18+. Cochez la case, puis appuyez sur continuer.'],
    ja:['18歳以上向けテーマを選ぶ場合は、ルーム作成前にここをチェックしてください。全員が個別に確認します。通常のゲームには不要です。','18歳以上で、大人向けの内容に同意します','開始前に顔がはっきり写った写真を追加し、使用に同意してください。AI画像の主役になれます。','📸 写真を追加して始めよう','スマホから写真を選ぶ','プレビュー下の使用同意をチェックすると自動保存されます。','✓ 写真の準備ができました','このルームは18歳以上向けです。同意欄をチェックして続行してください。']
  };
  const S=()=>setupCopy[lang()]||setupCopy.en;
  const intro=document.createElement('section');intro.id='hostIntro';intro.className='card hidden';intro.setAttribute('aria-labelledby','hostIntroTitle');
  intro.innerHTML='<h2 id="hostIntroTitle" tabindex="-1"></h2><ol id="hostIntroRules"></ol><p id="hostIntroPhoto" class="setup-note photoInstruction"></p><div class="setup-note"><p id="hostIntroAdult"></p><label class="ageChoice"><input type="checkbox" id="hostIntroAge"><span id="hostIntroAgeLabel"></span></label></div><button type="button" id="hostIntroContinue" class="primary"></button>';
  el('create').before(intro);
  const guideLink=document.createElement('button');guideLink.type='button';guideLink.id='hostGuideLink';guideLink.className='mini';el('createTitle').after(guideLink);
  function guideLabels(){const c=guideText();el('hostIntroTitle').textContent=c[0];el('hostIntroContinue').textContent=c[1];guideLink.textContent=c[2];const icons=['🤫','🎯','🖼️','🔗'];el('hostIntroRules').innerHTML=c[3].map((rule,i)=>'<li><span class="guideStepIcon" aria-hidden="true">'+icons[i]+'</span><span>'+safe(rule)+'</span></li>').join('');el('hostIntroAdult').textContent=S()[0];el('hostIntroAgeLabel').textContent=S()[1];el('hostIntroPhoto').textContent=S()[2];if(el('adultOptionsHint'))el('adultOptionsHint').textContent=c[5]}
  const baseMode=window.mode;
  function showHostGuide(){baseMode('create');el('create').classList.add('hidden');intro.classList.remove('hidden');el('hostIntroAge').checked=el('adultConfirm').checked;guideLabels();intro.scrollIntoView({block:'start'});el('hostIntroTitle').focus({preventScroll:true})}
  window.mode=function(next){intro.classList.add('hidden');if(next==='create')showHostGuide();else baseMode(next)};
  guideLink.onclick=showHostGuide;
  el('hostIntroAge').onchange=()=>{el('adultConfirm').checked=el('hostIntroAge').checked;if(el('hostIntroAge').checked&&audienceType!=='family')el('adultOptions').open=true};
  el('hostIntroContinue').onclick=()=>{intro.classList.add('hidden');baseMode('create');adultSetup();el('create').scrollIntoView({block:'start'});el('cname').focus({preventScroll:true})};
  guideLabels();
  const baseSyncAdult=window.syncCreateAdult;
  window.syncCreateAdult=function(){baseSyncAdult();if(el('adultOptions')?.open&&audienceType!=='family')el('adultBox').classList.remove('hidden')};
  function adultSetup(){
    const content=el('contentTopics');if(!content)return;
    let section=el('adultOptions');
    if(!section){section=document.createElement('details');section.id='adultOptions';section.innerHTML='<summary></summary><div class="topics"></div>';content.after(section)}
    section.querySelector('summary').textContent=phrase('אפשרויות לערב של מבוגרים · 18+','Adult evening options · 18+');
    let hint=el('adultOptionsHint');if(!hint){hint=document.createElement('span');hint.id='adultOptionsHint';section.querySelector('summary').appendChild(hint)}hint.textContent=guideText()[5];
    const family=audienceType==='family';section.classList.toggle('hidden',family);
    // The age choice lives on the preceding guide screen. Honour it every time
    // topics are rebuilt so mobile re-renders cannot collapse the 18+ controls.
    if(!family&&(el('hostIntroAge')?.checked||el('adultConfirm').checked))section.open=true;
    const target=section.querySelector('div');if(content.querySelector('[data-topic="דייטים"]'))target.querySelectorAll('[data-topic]').forEach(b=>b.remove());
    for(const b of document.querySelectorAll('#topics [data-topic]'))if(adultTopics.has(b.dataset.topic)){
      target.appendChild(b);b.dataset.extra='0';b.classList.remove('hidden');
      if(family)b.classList.remove('on');
    }
    const bold=document.querySelector('.spice [data-s="3"]');
    bold.classList.toggle('hidden',family||!section.open);
    if((family||!section.open)&&spice===3){spice=2;document.querySelectorAll('.spice button').forEach(b=>b.classList.toggle('on',b.dataset.s==='2'))}
    el('adultText').textContent=S()[1];
    if(family){el('adultConfirm').checked=false;el('hostIntroAge').checked=false}
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
  // Put both readiness steps ahead of the shared settings, where guests actually look.
  el('sharedSetup').before(el('photoBox'));el('sharedSetup').before(age);
  const photoPick=document.createElement('label');photoPick.className='photoPick';photoPick.htmlFor='photoInput';el('photoInput').before(photoPick);
  const photoHint=document.createElement('p');photoHint.className='photoConsentHint';el('photoConsent').closest('label').before(photoHint);
  const photoReady=document.createElement('div');photoReady.id='photoReadyCard';photoReady.className='photoReadyCard hidden';
  photoReady.innerHTML='<img id="savedPhotoThumb" alt=""><div><b id="savedPhotoLabel"></b><button type="button" id="replacePhotoBtn" class="mini"></button></div>';
  el('photoBox').after(photoReady);
  el('replacePhotoBtn').onclick=()=>{photoReady.classList.add('hidden');el('photoBox').classList.remove('hidden');el('photoBox').dataset.editing='1';el('photoBox').scrollIntoView({behavior:'smooth',block:'center'})};
  new MutationObserver(()=>{if(!el('photoBox').classList.contains('photoSaved'))return;const src=el('photoPreview').src;if(src)el('savedPhotoThumb').src=src;photoReady.classList.remove('hidden');setTimeout(()=>el('photoBox').classList.add('hidden'),300)}).observe(el('photoBox'),{attributes:true,attributeFilter:['class']});
  const howAge=document.createElement('label');howAge.id='howAge';howAge.className='ageChoice hidden';howAge.innerHTML='<input type="checkbox" id="howAgeCheck"><span></span>';el('howBtn').before(howAge);
  let ageRoomKey='';
  el('howAgeCheck').onchange=()=>{el('playerAgeCheck').checked=el('howAgeCheck').checked};
  const baseCloseHow=window.closeHowTo;
  window.closeHowTo=async function(){if(current?.adult_required&&!current.me?.adult_confirmed&&el('howAgeCheck').checked){await el('playerAgeSave').onclick();if(!current?.me?.adult_confirmed)return}baseCloseHow()};
  const baseCreate=window.createGame;
  window.createGame=async function(){if(createAdultRequired()&&!el('adultConfirm').checked){el('adultOptions').open=true;syncCreateAdult();el('adultBox').scrollIntoView({block:'center'});el('adultConfirm').focus();return toast(S()[1])}return baseCreate()};
  const baseShare=window.share;window.share=function(){if(current?.is_host)return baseShare()};
  function lobbyPolish(d){
    el('shareBtn').classList.toggle('hidden',!d.is_host);
    el('shareBtn').closest('.roomHeading').classList.toggle('hidden',!d.is_host);
    const ageKey=d.code+'_'+d.image_run+'_'+!!d.adult_required;
    if(ageKey!==ageRoomKey){ageRoomKey=ageKey;el('howAgeCheck').checked=false;el('playerAgeCheck').checked=false}
    document.querySelectorAll('#voteTopics [data-topic]').forEach(b=>{if(adultTopics.has(b.dataset.topic)&&!d.adult_required)b.classList.add('hidden')});
    age.classList.toggle('hidden',d.status!=='lobby'||!d.adult_required||!d.me||d.me.adult_confirmed);
    age.querySelector('span').textContent=S()[1];
    el('playerAgeSave').textContent=phrase('אישור 18+','Confirm 18+');
    el('photoHelp').textContent=S()[2];el('photoTitle').textContent=d.me?.has_photo?S()[6]:S()[3];photoPick.textContent=S()[4];photoHint.textContent=S()[5];el('photoBox').classList.toggle('needsPhoto',!d.me?.has_photo);
    el('photoToggle').classList.add('hidden');photoReady.classList.toggle('hidden',d.status!=='lobby'||!d.me?.has_photo);
    const mine=d.players.find(p=>p.id===d.me?.id);if(mine?.photo_url)el('savedPhotoThumb').src=mine.photo_url+(mine.photo_url.includes('?')?'&':'?')+'v='+(d.photo_count||0);
    el('savedPhotoLabel').textContent=S()[6];el('replacePhotoBtn').textContent=phrase('החלפת תמונה','Replace photo');
    el('how3').textContent=S()[2];el('how4').textContent=d.adult_required?S()[7]:(copy.how4||guideText()[3][3]);
    howAge.classList.toggle('hidden',!d.adult_required||!!d.me?.adult_confirmed);howAge.querySelector('span').textContent=S()[1];
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
  window.req=async function(path,body){if(body&&current&&/\/(answer|guess|skip|next)$/.test(path))body={...body,image_run:current.image_run,round:current.round};try{const result=await baseReq(path,body);if(body&&/\/(answer|guess|matchanswer)$/.test(path))sound('saved');return result}catch(error){if(['pilot_limit','game_ai_limit','retry_limit'].includes(error.message)){let note=el('pilotLimitNote');if(!note){note=document.createElement('div');note.id='pilotLimitNote';note.className='rulebox';note.setAttribute('role','alert');document.querySelector('main').prepend(note)}note.textContent=phrase('מכסת הניסיון זמנית מלאה. אין חיוב. משחק קיים ניתן לפתוח שוב דרך הקישור שלו.','The pilot allowance is currently full. No charge was made. Use your existing game link to resume.')}throw error}};

  const featureCopy={
    he:{chat:'צ׳אט במשחק',close:'סגירה',placeholder:'כתבו משהו לקבוצה…',send:'שליחה',empty:'עוד אין הודעות. תתחילו אתם 👋',react:'איך הגבתם לחשיפה?',guessed:'ניחש/ה',newTitle:'איזה משחק חדש לפתוח?',newHelp:'אפשר לשמור את הקבוצה, התמונות וההגדרות, או להתחיל מחדש לגמרי.',keep:'אותם אנשים והגדרות',keepHint:'שומר שחקנים, תמונות, נושאים והסכמות. הניקוד והשאלות מתאפסים ונוצר לינק חדש.',fresh:'להתחיל מאפס',freshHint:'חדר חדש לגמרי, כולל העלאת תמונות ובחירת הגדרות מחדש.',cancel:'ביטול',creating:'יוצר משחק חדש…',created:'נוצר משחק חדש עם אותה קבוצה',failed:'לא הצלחנו ליצור משחק חדש. נסו שוב.',remove:'אם תמשיכו, {name} יצא/תצא מהמשחק. להמשיך?',removed:'{name} יצא/ה מהמשחק',photoReady:'✓ התמונה שלכם מוכנה למשחק',replace:'החלפת תמונה',chatFailed:'ההודעה לא נשלחה. נסו שוב.',openChat:'פתיחת הצ׳אט'},
    en:{chat:'Game chat',close:'Close',placeholder:'Message the group…',send:'Send',empty:'No messages yet. Say hi 👋',react:'React to the reveal',guessed:'guessed',newTitle:'How should the new game start?',newHelp:'Keep this group, photos and settings, or begin completely fresh.',keep:'Same people & settings',keepHint:'Keeps players, photos, topics and consent. Scores and questions reset and a new link is created.',fresh:'Start from scratch',freshHint:'A completely new room, including new photos and settings.',cancel:'Cancel',creating:'Creating a new game…',created:'New game created with the same group',failed:'Could not create the new game. Please try again.',remove:'If you continue, {name} will leave the game. Continue?',removed:'{name} left the game',photoReady:'✓ Your photo is ready to play',replace:'Replace photo',chatFailed:'Message was not sent. Please retry.',openChat:'Open chat'},
    es:{chat:'Chat del juego',close:'Cerrar',placeholder:'Escribe al grupo…',send:'Enviar',empty:'Todavía no hay mensajes. Saluda 👋',react:'Reacciona a la revelación',guessed:'adivinó',newTitle:'¿Cómo quieres empezar la nueva partida?',newHelp:'Conserva el grupo, las fotos y los ajustes, o empieza desde cero.',keep:'Mismas personas y ajustes',keepHint:'Conserva jugadores, fotos, temas y permisos. Reinicia puntos y preguntas y crea un enlace nuevo.',fresh:'Empezar desde cero',freshHint:'Una sala completamente nueva, con fotos y ajustes nuevos.',cancel:'Cancelar',creating:'Creando la nueva partida…',created:'Nueva partida creada con el mismo grupo',failed:'No se pudo crear la partida. Inténtalo de nuevo.',remove:'Si continúas, {name} saldrá de la partida. ¿Continuar?',removed:'{name} salió de la partida',photoReady:'✓ Tu foto está lista',replace:'Cambiar foto',chatFailed:'No se envió el mensaje. Inténtalo de nuevo.',openChat:'Abrir chat'},
    'pt-BR':{chat:'Chat do jogo',close:'Fechar',placeholder:'Escreva para o grupo…',send:'Enviar',empty:'Ainda não há mensagens. Diga oi 👋',react:'Reaja à revelação',guessed:'escolheu',newTitle:'Como começar o novo jogo?',newHelp:'Mantenha o grupo, as fotos e as configurações, ou comece do zero.',keep:'Mesmas pessoas e ajustes',keepHint:'Mantém jogadores, fotos, temas e permissões. Zera pontos e perguntas e cria um novo link.',fresh:'Começar do zero',freshHint:'Uma sala totalmente nova, com novas fotos e configurações.',cancel:'Cancelar',creating:'Criando novo jogo…',created:'Novo jogo criado com o mesmo grupo',failed:'Não foi possível criar o jogo. Tente novamente.',remove:'Se continuar, {name} sairá do jogo. Continuar?',removed:'{name} saiu do jogo',photoReady:'✓ Sua foto está pronta',replace:'Trocar foto',chatFailed:'A mensagem não foi enviada. Tente novamente.',openChat:'Abrir chat'},
    fr:{chat:'Chat du jeu',close:'Fermer',placeholder:'Écrivez au groupe…',send:'Envoyer',empty:'Aucun message pour le moment. Dites bonjour 👋',react:'Réagissez au Reveal',guessed:'a choisi',newTitle:'Comment lancer la nouvelle partie ?',newHelp:'Gardez le groupe, les photos et les réglages, ou repartez de zéro.',keep:'Même groupe et réglages',keepHint:'Conserve joueurs, photos, thèmes et accords. Les scores et questions repartent à zéro avec un nouveau lien.',fresh:'Repartir de zéro',freshHint:'Une toute nouvelle salle, avec de nouvelles photos et de nouveaux réglages.',cancel:'Annuler',creating:'Création de la partie…',created:'Nouvelle partie créée avec le même groupe',failed:'Impossible de créer la partie. Réessayez.',remove:'Si vous continuez, {name} quittera la partie. Continuer ?',removed:'{name} a quitté la partie',photoReady:'✓ Votre photo est prête',replace:'Changer la photo',chatFailed:'Le message n’a pas été envoyé. Réessayez.',openChat:'Ouvrir le chat'},
    ja:{chat:'ゲームチャット',close:'閉じる',placeholder:'みんなにメッセージ…',send:'送信',empty:'まだメッセージはありません。話しかけてみよう 👋',react:'Revealにリアクション',guessed:'の予想',newTitle:'新しいゲームをどう始めますか？',newHelp:'今のメンバー・写真・設定を残すか、すべて新しく始められます。',keep:'同じメンバーと設定',keepHint:'プレイヤー、写真、テーマ、同意を保持します。得点と質問をリセットし、新しいリンクを作ります。',fresh:'最初から始める',freshHint:'写真や設定も含めて、まったく新しいルームを作ります。',cancel:'キャンセル',creating:'新しいゲームを作成中…',created:'同じメンバーで新しいゲームを作成しました',failed:'新しいゲームを作れませんでした。もう一度お試しください。',remove:'続けると{name}さんはゲームから退出します。続けますか？',removed:'{name}さんがゲームから退出しました',photoReady:'✓ 写真の準備ができました',replace:'写真を変更',chatFailed:'メッセージを送信できませんでした。もう一度お試しください。',openChat:'チャットを開く'}
  };
  const F=()=>featureCopy[lang()]||featureCopy.en;
  const reactionCopy={
    he:['לב','צחוק','בכי','שובבות'],en:['Love','Laugh','Cry','Mischief'],es:['Me encanta','Risa','Llanto','Travesura'],'pt-BR':['Amei','Risada','Choro','Travessura'],fr:['J’adore','Rire','Pleurs','Malice'],ja:['いいね','笑い','泣き','いたずら']
  };
  const ft=(value,name)=>String(value||'').replaceAll('{name}',name||'');

  const chatRoot=document.createElement('div');chatRoot.id='gameChat';chatRoot.className='gameChat hidden';
  chatRoot.innerHTML='<button id="chatFab" class="chatFab" type="button" aria-controls="chatSheet" aria-expanded="false"><span aria-hidden="true">💬</span><span id="chatFabLabel"></span><i id="chatUnread" class="chatUnread hidden"></i></button><section id="chatSheet" class="chatSheet hidden" role="dialog" aria-modal="true" aria-labelledby="chatTitle"><header><b id="chatTitle"></b><button id="chatClose" class="chatClose" type="button">×</button></header><div id="chatMessages" class="chatMessages" aria-live="polite"></div><div class="chatQuick" aria-label="Quick reactions"><button type="button" data-reaction="❤️">❤️</button><button type="button" data-reaction="😂">😂</button><button type="button" data-reaction="😭">😭</button><button type="button" data-reaction="😈">😈</button></div><form id="chatForm" class="chatForm"><input id="chatInput" maxlength="160" autocomplete="off"><button id="chatSend" type="submit" class="primary"></button></form></section>';
  document.body.appendChild(chatRoot);
  const revealReactions=document.createElement('div');revealReactions.id='revealReactions';revealReactions.className='revealReactions hidden';
  revealReactions.innerHTML='<b id="revealReactTitle"></b><div><button type="button" data-reaction="❤️">❤️</button><button type="button" data-reaction="😂">😂</button><button type="button" data-reaction="😭">😭</button><button type="button" data-reaction="😈">😈</button></div>';
  el('guessBoard').before(revealReactions);
  let chatRoom='',lastChatId=0,chatLoading=false,chatOpen=false,chatInitialLoaded=false,unread=0;
  const chatItems=new Map();
  function chatLabels(){const c=F(),title=copy.chat_title||c.chat,names=[copy.reaction_heart,copy.reaction_laugh,copy.reaction_cry,copy.reaction_mischief].map((x,i)=>x||(reactionCopy[lang()]||reactionCopy.en)[i]);el('chatTitle').textContent=title;el('chatFabLabel').textContent=title;el('chatFab').setAttribute('aria-label',c.openChat);el('chatClose').setAttribute('aria-label',c.close);el('chatInput').placeholder=copy.chat_placeholder||c.placeholder;el('chatSend').textContent=copy.chat_send||c.send;el('revealReactTitle').textContent=copy.chat_quick||c.react;el('savedPhotoLabel').textContent=c.photoReady;el('savedPhotoThumb').alt=c.photoReady;el('replacePhotoBtn').textContent=c.replace;document.querySelectorAll('[data-reaction]').forEach((b,i)=>{const label=names[i%4];b.setAttribute('aria-label',label);b.title=label});newGameLabels();renderChat()}
  function setUnread(value){unread=Math.max(0,value);el('chatUnread').textContent=unread>99?'99+':String(unread);el('chatUnread').classList.toggle('hidden',!unread)}
  function renderChat(){const list=[...chatItems.values()].sort((a,b)=>Number(a.id)-Number(b.id)),box=el('chatMessages');if(!list.length){box.innerHTML='<p class="chatEmpty">'+safe(F().empty)+'</p>';return}box.innerHTML=list.map(m=>{const mine=Number(m.player_id)===Number(current?.me?.id),reaction=m.kind==='reaction';return '<div class="chatMessage '+(mine?'mine ':'')+(reaction?'reaction':'')+'"><span class="chatAuthor">'+safe(m.name||'')+'</span><span class="chatBody">'+safe(m.body||'')+'</span></div>'}).join('');box.scrollTop=box.scrollHeight}
  function setChatRoom(code){if(chatRoom===code)return;chatRoom=code||'';lastChatId=0;chatInitialLoaded=false;chatItems.clear();setUnread(0);renderChat()}
  async function fetchChat(initial=false){if(chatLoading||!current?.me||!s.token||!current.code||current.code!==s.code||document.hidden)return;const requestedRoom=current.code;chatLoading=true;try{const result=await window.req('/api/chat/'+encodeURIComponent(requestedRoom)+'?token='+encodeURIComponent(s.token)+'&after='+(initial?0:lastChatId));if(chatRoom!==requestedRoom)return;const messages=Array.isArray(result.messages)?result.messages:[];let incoming=0;for(const m of messages){const id=Number(m.id)||0;if(chatItems.has(id))continue;chatItems.set(id,m);lastChatId=Math.max(lastChatId,id);if(!initial&&!chatOpen&&Number(m.player_id)!==Number(current.me.id))incoming++}chatInitialLoaded=true;while(chatItems.size>100)chatItems.delete(chatItems.keys().next().value);if(messages.length)renderChat();if(incoming){setUnread(unread+incoming);variedSound(['wink','peek'])}}catch(_){/* Chat retries quietly without blocking play. */}finally{chatLoading=false}}
  async function sendChat(body,kind='text'){body=String(body||'').trim();if(!body||!current?.me)return;const id=(window.crypto?.randomUUID?.()||String(Date.now())+'_'+Math.random().toString(36).slice(2));try{const result=await window.req('/api/'+encodeURIComponent(current.code)+'/chat',{token:s.token,kind,body,client_msg_id:id}),m=result.message;if(m&&chatRoom===current.code){chatItems.set(Number(m.id),m);lastChatId=Math.max(lastChatId,Number(m.id)||0);renderChat()}else await fetchChat(false)}catch(_){toast(F().chatFailed)}}
  function openChat(){chatOpen=true;setUnread(0);el('chatSheet').classList.remove('hidden');el('chatFab').setAttribute('aria-expanded','true');document.body.classList.add('chatOpen');fetchChat(true);setTimeout(()=>el('chatInput').focus({preventScroll:true}),80)}
  function closeChat(){chatOpen=false;el('chatSheet').classList.add('hidden');el('chatFab').setAttribute('aria-expanded','false');document.body.classList.remove('chatOpen')}
  el('chatFab').onclick=()=>chatOpen?closeChat():openChat();el('chatClose').onclick=closeChat;
  el('chatForm').onsubmit=e=>{e.preventDefault();const input=el('chatInput'),body=input.value.trim();if(!body)return;input.value='';sendChat(body,'text')};
  for(const area of [chatRoot,revealReactions])area.addEventListener('click',e=>{const b=e.target.closest('[data-reaction]');if(b)sendChat(b.dataset.reaction,'reaction')});

  const newGameOverlay=document.createElement('div');newGameOverlay.id='newGameOverlay';newGameOverlay.className='choiceOverlay hidden';newGameOverlay.setAttribute('role','dialog');newGameOverlay.setAttribute('aria-modal','true');
  newGameOverlay.innerHTML='<div class="choiceDialog"><button type="button" id="newGameClose" class="dialogClose">×</button><h2 id="newGameTitle" tabindex="-1"></h2><p id="newGameHelp"></p><button type="button" id="keepGameBtn" class="gameChoice primary"><b id="keepGameLabel"></b><small id="keepGameHint"></small></button><button type="button" id="freshGameBtn" class="gameChoice"><b id="freshGameLabel"></b><small id="freshGameHint"></small></button><button type="button" id="newGameCancel" class="textChoice"></button></div>';
  document.body.appendChild(newGameOverlay);
  function newGameLabels(){if(!el('newGameTitle'))return;const c=F();el('newGameTitle').textContent=c.newTitle;el('newGameHelp').textContent=c.newHelp;el('keepGameLabel').textContent=c.keep;el('keepGameHint').textContent=c.keepHint;el('freshGameLabel').textContent=c.fresh;el('freshGameHint').textContent=c.freshHint;el('newGameCancel').textContent=c.cancel;el('newGameClose').setAttribute('aria-label',c.close)}
  function closeNewGame(){newGameOverlay.classList.add('hidden')}
  function openNewGameOptions(){if(!s.code){writeStored('kyc',{});location.href='/?new=1';return}newGameLabels();el('keepGameBtn').classList.toggle('hidden',!(current?.is_host||s.host));newGameOverlay.classList.remove('hidden');el('newGameTitle').focus({preventScroll:true})}
  window.openNewGameOptions=openNewGameOptions;
  el('newGameClose').onclick=closeNewGame;el('newGameCancel').onclick=closeNewGame;newGameOverlay.onclick=e=>{if(e.target===newGameOverlay)closeNewGame()};
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(chatOpen)closeChat();if(!newGameOverlay.classList.contains('hidden'))closeNewGame()}});
  el('freshGameBtn').onclick=()=>{writeStored('kyc',{});s={};stateSig='';window.lastState=null;location.href='/?new=1'};
  async function createFreshRoom(button,labelNode){const b=button,old=labelNode.textContent;b.disabled=true;labelNode.textContent=F().creating;try{const oldCode=s.code,result=await window.req('/api/'+encodeURIComponent(oldCode)+'/freshroom',{host:s.host});if(result.code&&result.code!==oldCode){s.code=result.code;save();setChatRoom(result.code);history.replaceState({},'',location.pathname+'?code='+encodeURIComponent(result.code))}stateSig='';heroAsked=-1;sessionStorage.removeItem('how_'+oldCode);sessionStorage.removeItem('how_'+s.code);closeNewGame();toast(F().created);await load();setTimeout(showHowTo,80)}catch(_){toast(F().failed)}finally{b.disabled=false;labelNode.textContent=old}}
  el('keepGameBtn').onclick=()=>createFreshRoom(el('keepGameBtn'),el('keepGameLabel'));
  el('replayBtn').onclick=()=>createFreshRoom(el('replayBtn'),el('replayBtn'));
  for(const id of ['globalNewGameBtn','newGameBtn'])if(el(id))el(id).onclick=openNewGameOptions;

  window.dropPlayer=async function(id){const d=window.lastState,p=d?.players?.find(x=>x.id===id);if(!p||!window.confirm(ft(F().remove,p.name)))return;try{await window.req('/api/'+s.code+'/drop',{host:s.host,player_id:id});stateSig='';toast(ft(F().removed,p.name));await load()}catch(e){toast(e.message==='need_2'?copy.need_two:copy.remove_failed)}};

  function featureRender(d){
    setChatRoom(d.code);chatRoot.classList.toggle('hidden',!d.me);if(d.me&&!chatInitialLoaded)fetchChat(true);
    document.body.classList.toggle('hasNextDock',!!(d.status==='playing'&&d.reveal&&d.is_host));
    el('interactiveTwist').classList.add('hidden');el('interactiveTwist').setAttribute('aria-hidden','true');
    revealReactions.classList.toggle('hidden',!d.reveal||!d.me);
    if(d.reveal){
      el('next').classList.toggle('hidden',!d.is_host);
      const guesses=d.all_guesses||[];el('guessBoard').classList.toggle('hidden',!guesses.length);
      el('guessRows').innerHTML=guesses.map(g=>'<div class="guessRow emphasizedGuess">'+(g.photo_url?'<img class="avatar" src="'+safe(g.photo_url)+'">':'<div class="avatarFallback">'+safe(String(g.name||'?').charAt(0))+'</div>')+'<div class="guessStatement"><span><b>'+playerLabel(g)+'</b> '+safe(F().guessed)+'</span><strong class="guessChoice">'+safe(g.guess)+'</strong></div><span class="guessResult '+(g.correct?'good':'bad')+'">'+(g.correct?'✓ +1':'✕')+'</span></div>').join('');
    }
    el('savedPhotoLabel').textContent=F().photoReady;el('replacePhotoBtn').textContent=F().replace;
    if(d.status==='finished'&&d.is_host&&!document.body.classList.contains('finalImagePending'))el('replayBtn').textContent='↻ '+F().keep;
  }
  const packages=document.createElement('a');packages.className='pilotPackagesLink';packages.href='/pricing';
  function packageLabel(){packages.textContent=phrase('חבילות ומחירים לקראת ההשקה','Launch packages & pricing');packages.href='/pricing?lang='+encodeURIComponent(lang())}
  packageLabel();el('home').appendChild(packages);
  const costs=document.createElement('details');costs.id='pilotCostReport';costs.className='rulebox hidden';costs.innerHTML='<summary></summary><button type="button"></button><p></p>';el('finish').appendChild(costs);
  costs.querySelector('button').onclick=async()=>{const b=costs.querySelector('button'),p=costs.querySelector('p');b.disabled=true;try{const r=await baseReq('/api/costs/'+encodeURIComponent(current.code)+'?host='+encodeURIComponent(s.host));p.textContent=phrase('עלות AI שנמדדה: $','Measured AI cost: $')+r.measured_usd.toFixed(4)+phrase(' · קריאות שטרם תומחרו: ',' · Unpriced calls: ')+r.unpriced_calls+phrase(' · אומדן כולל: $',' · Combined estimate: $')+r.estimated_usd.toFixed(4)+phrase(' — אינו חשבונית ואינו כולל שרת וסליקה.',' — not an invoice; excludes hosting and payments.')}catch(_){p.textContent=phrase('לא הצלחנו לטעון את המדידה. נסו שוב.','Could not load usage. Please retry.')}finally{b.disabled=false}};
  const baseRender=window.render;
  window.render=function(d){
    const newGame=current&&(current.code!==d.code||current.image_run!==d.image_run);if(newGame){closeScores();lastLine='';loadingKey='';el('companionMoment').classList.add('hidden')}
    if(previous&&previous.round!==d.round)closeScores();
    current=d;baseRender(d);label();scoreUI(d);finishUI(d);lobbyPolish(d);featureRender(d);chatLabels();packageLabel();costs.classList.toggle('hidden',!d.is_host||d.status!=='finished');costs.querySelector('summary').textContent=phrase('מדידת עלויות — למארח בטסט','Cost measurement — pilot host');costs.querySelector('button').textContent=phrase('עדכן מדידה','Refresh measurement');
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
  new MutationObserver(()=>{guideLabels();label();chatLabels();packageLabel();lastScores='';if(current){scoreUI(current);finishUI(current);featureRender(current)}companion(true)}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  setInterval(()=>{if(!document.hidden&&current?.me)fetchChat(false)},1800);
  setInterval(()=>{if(!document.hidden)companion(Date.now()>lineUntil)},7500);
  if(window.lastState)window.render(window.lastState);
  if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'}).catch(()=>{});
})();
