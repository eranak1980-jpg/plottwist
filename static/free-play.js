/* The free edition uses bundled artwork; no metered generation or purchase UI. */
(() => {
 if(!window.MIPO_CONFIG?.freePlay&&!crazygamesMode)return;
 document.documentElement.classList.add('freePlay');
 const css=document.createElement('style');
 css.textContent=`html.freePlay .pilotPackagesLink,html.freePlay #extendGameBtn,html.freePlay #quickImages,html.freePlay #lobbyImages,html.freePlay .imageSpeedNote{display:none!important}
 html.platformAd body{pointer-events:none}html.crazygamesMode #photoToggle,html.crazygamesMode #photoBox,html.crazygamesMode .chatFab,html.crazygamesMode .chatSheet,html.crazygamesMode #customAnswer,html.crazygamesMode #revealReactions,html.crazygamesMode #advancedSetup,html.crazygamesMode #context,html.crazygamesMode #prize,html.crazygamesMode #vibeChips,html.crazygamesMode #contextLabel,html.crazygamesMode #buildDescriptionBtn,html.crazygamesMode #showExamplesBtn{display:none!important}`;
 document.head.appendChild(css);
 const labels=()=>{
  const he=document.documentElement.lang==='he';
  const defaults=document.getElementById('quickDefaults');
  if(defaults)defaults.textContent=String(rounds)+(he?' שאלות · משחק חינמי':' rounds · Free to play');
  for(const id of ['quickImages','lobbyImages'])document.getElementById(id)?.closest('label')?.classList.add('hidden');
  const promise=document.getElementById('groupPromise');if(promise)promise.textContent=he?'אחד פותח חדר. כולם מצטרפים ומשחקים בחינם.':'One person hosts. Everyone joins and plays for free.';
  if(crazygamesMode){
   document.title='MIPO Free — Party Game';
   const heading=document.getElementById('homeTitle');if(heading)heading.textContent='MIPO Free';
   for(const id of ['cname','jname']){const e=document.getElementById(id);if(e&&!e.value)e.value=window.mipoPlatformUsername||'Player '+Math.random().toString(36).slice(2,6).toUpperCase()}
  }
 };
 const priorCopy=window.applyCopy;window.applyCopy=function(){priorCopy();labels()};
 const priorRender=window.render;window.render=function(d){priorRender(d);labels()};
 const priorReq=window.req;window.req=function(path,body){
  if(path==='/api/create'&&body)body={...body,ai_images_enabled:false,save_for_checkout:false};
  return priorReq(path,body);
 };
 labels();
 if(new URLSearchParams(location.search).get('portal')==='1'&&!s.code&&!new URLSearchParams(location.search).get('code')){window.mode('create');window.createGame()}
 new MutationObserver(labels).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
})();
