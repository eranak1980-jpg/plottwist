/* CrazyGames v3 integration. The game remains playable if the SDK is unavailable. */
(async () => {
 if(typeof crazygamesMode==='undefined'||!crazygamesMode)return;
 const embedded=(()=>{try{return [document.referrer,...Array.from(location.ancestorOrigins||[])].some(v=>/(^|\.)crazygames\.com$/i.test(new URL(v).hostname))}catch(_){return false}})();
 const loadSdk=()=>new Promise((resolve,reject)=>{
  if(window.CrazyGames?.SDK)return resolve();
  const script=document.createElement('script');script.src='https://sdk.crazygames.com/crazygames-sdk-v3.js';script.async=true;script.onload=resolve;script.onerror=reject;document.head.appendChild(script);
 });
 try{
  await loadSdk();const sdk=window.CrazyGames.SDK;await sdk.init();const cg=sdk.game;
  window.mipoCrazyGames=sdk;
  let playing=false,roomSignature='',adPending=false;
  const call=(name,...args)=>{try{return cg[name]?.(...args)}catch(error){console.warn('MIPO SDK '+name,error)}};
  const settings=()=>{
   const current={...cg.settings,muteAudio:!!cg.settings?.muteAudio||adPending};
   window.mipoPlatformMuted=current.muteAudio;
   window.dispatchEvent(new CustomEvent('mipo:platform-settings',{detail:current}));
  };
  settings();cg.addSettingsChangeListener?.(settings);
  function sync(state){
   if(!state?.code)return;
   const room={roomId:String(state.code),isJoinable:state.status==='lobby',inviteParams:{code:String(state.code)}};
   const signature=JSON.stringify(room);if(signature!==roomSignature){call('updateRoom',room);roomSignature=signature}
   const active=state.status==='playing'&&!state.reveal&&!document.hidden&&!adPending;
   if(active!==playing){playing=active;call(active?'gameplayStart':'gameplayStop')}
   const input=document.querySelector('#inviteCard input');if(input&&cg.inviteLink)input.value=cg.inviteLink({code:String(state.code)});
  }
  document.addEventListener('visibilitychange',()=>sync(window.lastState));
  const previousReq=window.req;
  window.req=async function(path,body){
   const result=await previousReq(path,body);
   if(typeof path==='string'&&path.startsWith('/api/state/'))sync(result);
   return result;
  };
  // Keep a platform invite URL throughout the share sheet, copy field and QR.
  window.mipoInviteUrl=code=>cg.inviteLink({code:String(code)});
  window.share=async()=>{
   const code=window.lastState?.code;if(!code)return;
   const url=window.mipoInviteUrl(code);
   if(navigator.share){try{await navigator.share({title:'Play MIPO',text:'Join my MIPO game',url});return}catch(error){if(error.name==='AbortError')return}}
   try{await navigator.clipboard.writeText(url);window.toast?.('Invite link copied')}catch(_){const box=document.querySelector('#inviteCard .inviteFallback');if(box){box.classList.remove('hidden');box.querySelector('input').value=url;box.querySelector('input').select()}}
  };
  const locale=sdk.user?.systemInfo?.locale||'en';
  if(!window.lastState&&typeof window.setLanguage==='function'){
   const language=/^pt/i.test(locale)?'pt-BR':/^ja/i.test(locale)?'ja':locale.split('-')[0];
   await window.setLanguage(['en','he','es','pt-BR','fr','ja'].includes(language)?language:'en',false);
  }
  try{
   if(sdk.user?.isUserAccountAvailable){
    const user=await sdk.user.getUser();
    if(user?.username){window.mipoPlatformUsername=user.username;for(const id of ['cname','jname']){const e=document.getElementById(id);if(e)e.value=user.username}}
   }
  }catch(error){console.warn('MIPO platform profile unavailable',error)}
  async function join(params){
   const invite=params?.inviteParams||params;const code=invite?.code||invite?.roomId||invite?.roomCode;
   if(!code||String(code)===String(window.lastState?.code))return;
   window.mode('join');document.getElementById('jcode').value=String(code).toUpperCase().slice(0,5);
   const input=document.getElementById('jname');if(!input.value.trim())input.value=window.mipoPlatformUsername||'Guest '+Math.random().toString(36).slice(2,6).toUpperCase();
   await window.joinGame();
  }
  cg.addJoinRoomListener?.(join);
  const params=new URLSearchParams(location.search);
  const invite=cg.inviteParams||{code:cg.getInviteParam?.('code')||params.get('code')};
  if(invite.code||invite.roomId||invite.roomCode)await join(invite);
  else if(!window.lastState&&!s.code){
   // A visitor can immediately invite friends; no account or purchase is needed.
   window.mode('create');document.getElementById('hostIntroContinue')?.click();
   const input=document.getElementById('cname');if(!input.value.trim())input.value=window.mipoPlatformUsername||'Player '+Math.random().toString(36).slice(2,6).toUpperCase();
   await window.createGame();
  }
  sync(window.lastState);
  // Ads occur only at a natural break, when the host chooses another match.
  // Basic Launch/ad blockers/no-fill report adError and continue immediately.
  const replay=window.replaySameCrew;
  window.replaySameCrew=async function(){
   if(adPending)return;
   if(embedded&&window.lastState?.status==='finished'&&sdk.ad?.requestAd){
    await new Promise(resolve=>{
     let settled=false;adPending=true;settings();
     const finish=()=>{if(settled)return;settled=true;adPending=false;document.documentElement.classList.remove('platformAd');settings();resolve()};
     try{sdk.ad.requestAd('midgame',{adStarted:()=>{document.documentElement.classList.add('platformAd');call('gameplayStop');playing=false},adFinished:finish,adError:finish})}catch(_){finish()}
    });
   }
   return replay();
  };
 }catch(error){console.warn('MIPO: CrazyGames SDK unavailable; free play is available.',error)}
})();
