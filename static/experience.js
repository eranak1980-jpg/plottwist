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
        gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(voice[kind]?.042:.028,start+.015);gain.gain.exponentialRampToValueAtTime(.0001,start+duration+.045);
        if(voice[kind]&&context.createBiquadFilter){const formant=context.createBiquadFilter();formant.type='bandpass';formant.frequency.setValueAtTime(kind==='hum'?650:1100,start);formant.Q.value=.7;oscillator.connect(formant);formant.connect(gain);oscillator.onended=()=>{nodes.delete(oscillator);oscillator.disconnect();formant.disconnect();gain.disconnect()};}
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
    const changed=loadingKey!==key;
    if(changed||force||Date.now()>lineUntil){loadingKey=key;lastLine=draw(current.status==='finished'?'win':'wait');lineUntil=Date.now()+7500}
    for(const status of targets){let box=status.querySelector('.loadingCompanion');if(!box){box=document.createElement('div');box.className='loadingCompanion';box.innerHTML=mascot(['peek','hum','wow','tie'][Math.floor(Math.random()*4)])+'<p class="loadingJoke"></p>';status.appendChild(box)}box.querySelector('.loadingJoke').textContent=lastLine}
    // Spaced, soft vocal gestures. Never an endless audio loop or overlapping voices.
    if((force||changed)&&Date.now()-lastAntic>11000){lastAntic=Date.now();sound(['hum','peek','wow'][Math.floor(Math.random()*3)])}
  }
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
  const baseReq=window.req;
  window.req=async function(path,body){const result=await baseReq(path,body);if(body&&/\/(answer|guess|matchanswer)$/.test(path))sound('saved');return result};
  const baseRender=window.render;
  window.render=function(d){
    const newGame=current&&(current.code!==d.code||current.image_run!==d.image_run);if(newGame){closeScores();lastLine='';loadingKey='';el('companionMoment').classList.add('hidden')}
    current=d;baseRender(d);label();scoreUI(d);finishUI(d);
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
  new MutationObserver(()=>{label();lastScores='';if(current){scoreUI(current);finishUI(current)}companion(true)}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  setInterval(()=>{if(!document.hidden)companion(Date.now()>lineUntil)},7500);
  if(window.lastState)window.render(window.lastState);
  if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js',{updateViaCache:'none'}).catch(()=>{});
})();
