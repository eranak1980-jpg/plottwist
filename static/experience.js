/* Local-only sound and loading companion. No network, AI calls or personal data. */
(() => {
  const words = {
    he: ['השתק צלילים', 'הפעל צלילים', 'רגע, מי בחר לי את הלוק הזה?', 'אני מוכן לקלוז־אפ. אתם?', 'בינתיים אני מתאמן על פרצוף מופתע.'],
    en: ['Mute sounds', 'Enable sounds', 'Wait, who picked my outfit?', 'I’m ready for my close-up. Are you?', 'Practicing my surprised face meanwhile.'],
    es: ['Silenciar sonidos', 'Activar sonidos', 'Un momento, ¿quién eligió mi look?', 'Listo para mi primer plano. ¿Y tú?', 'Mientras tanto, practico mi cara de sorpresa.'],
    'pt-BR': ['Silenciar sons', 'Ativar sons', 'Pera, quem escolheu meu look?', 'Pronto para o close. E vocês?', 'Enquanto isso, treino minha cara de surpresa.'],
    fr: ['Couper les sons', 'Activer les sons', 'Attendez, qui a choisi ma tenue ?', 'Prêt pour mon gros plan. Et vous ?', 'En attendant, je répète mon air surpris.'],
    ja: ['音をオフにする', '音をオンにする', 'ちょっと、この服を選んだのは誰？', 'アップの準備はできたよ。みんなは？', '待ちながら、びっくり顔を練習中。']
  };
  const language = () => words[document.documentElement.lang] || words.en;
  let enabled = true, context, activated = false, lastSound = 0;
  try { enabled = localStorage.getItem('plot_sound') !== 'off'; } catch (_) {}
  const toggle = document.createElement('button');
  toggle.id = 'soundToggle'; toggle.type = 'button'; toggle.className = 'soundToggle';
  function label() {
    toggle.textContent = enabled ? '🔊' : '🔇';
    toggle.setAttribute('aria-label', language()[enabled ? 0 : 1]);
    toggle.title = language()[enabled ? 0 : 1];
    toggle.setAttribute('aria-pressed', String(enabled));
  }
  function sound(kind) {
    if (!enabled || !activated || document.hidden) return;
    const now = Date.now(); if (now - lastSound < 70) return; lastSound = now;
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      context ||= new Audio();
      if (context.state === 'suspended') context.resume().catch(() => {});
      const notes = {tap:[560], saved:[660,880], next:[440,600], reveal:[440,660,880], ready:[740,990], win:[523,659,784,1046]}[kind] || [560];
      notes.forEach((hz,i) => {
        const osc=context.createOscillator(), gain=context.createGain(), start=context.currentTime+i*.085;
        osc.type='sine'; osc.frequency.setValueAtTime(hz,start);
        gain.gain.setValueAtTime(0,start); gain.gain.linearRampToValueAtTime(.035,start+.009);
        gain.gain.exponentialRampToValueAtTime(.0001,start+.12);
        osc.connect(gain); gain.connect(context.destination); osc.start(start); osc.stop(start+.13);
        osc.onended=()=>{osc.disconnect();gain.disconnect();};
      });
    } catch (_) { /* Audio must never interrupt the game. */ }
  }
  toggle.onclick = () => {
    activated=true; enabled=!enabled;
    try { localStorage.setItem('plot_sound',enabled?'on':'off'); } catch (_) {}
    label(); if(enabled)sound('tap');
  };
  document.querySelector('.topbar').appendChild(toggle); label();
  document.addEventListener('click', e => {
    const b=e.target.closest('button'); if(!b||b.disabled||b===toggle)return;
    activated=true; sound('tap');
  },true);
  const baseReq=window.req;
  window.req=async function(path,body){
    const result=await baseReq(path,body);
    if(body && /\/(answer|guess|matchanswer)$/.test(path))sound('saved');
    return result;
  };
  const baseRender=window.render; let lastState;
  window.render=function(d){
    baseRender(d);
    if(lastState && lastState.code===d.code && lastState.run===d.image_run){
      if(d.status==='finished'&&lastState.status!=='finished')sound('win');
      else if(d.reveal&&!lastState.reveal)sound('reveal');
      else if(d.round!==lastState.round)sound('next');
    }
    lastState={code:d.code,run:d.image_run,status:d.status,round:d.round,reveal:d.reveal};
    companion();
  };
  const baseGate=window.setImageGate, gateStates=new Map();
  window.setImageGate=function(d,final,state){
    const key=d.code+'_'+d.image_run+'_'+(final?'final':d.round), before=gateStates.get(key);
    baseGate(d,final,state);gateStates.set(key,state);
    if(before==='pending'&&state==='ready')sound('ready');
    if(gateStates.size>80)gateStates.delete(gateStates.keys().next().value);
  };
  let joke=0;
  function companion(){
    for(const id of ['heroStatus','finalHeroStatus']){
      const status=document.getElementById(id);
      const loading=id==='heroStatus'?document.getElementById('visualStage').classList.contains('is-loading'):status.classList.contains('is-loading');
      const existing=status.querySelector('.loadingCompanion');
      if(!loading||status.classList.contains('hidden')){if(existing)existing.remove();continue;}
      if(!existing){
        const box=document.createElement('div');box.className='loadingCompanion';
        box.innerHTML='<div class="popMascot" aria-hidden="true"><span class="popEyes">••</span><span class="popSmile"></span><span class="popSpark">✦</span></div><p class="loadingJoke"></p>';
        status.appendChild(box);
      }
      status.querySelector('.loadingJoke').textContent=language()[2+joke%3];
    }
  }
  new MutationObserver(()=>{label();companion();}).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  setInterval(()=>{if(document.hidden)return;joke++;companion();},4000);
  companion();
})();
