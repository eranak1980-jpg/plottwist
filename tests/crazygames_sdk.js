const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const events=[],fields=new Map(['cname','jname','jcode'].map(k=>[k,{value:'',click(){}}]));
 let roomJoin,settingsListener,shared,replays=0;
 const game={settings:{muteAudio:true},inviteParams:{code:'ABCDE'},
  addSettingsChangeListener:f=>settingsListener=f,addJoinRoomListener:f=>roomJoin=f,
  updateRoom:r=>events.push(['room',r]),gameplayStart:()=>events.push(['start']),gameplayStop:()=>events.push(['stop']),
  inviteLink:params=>'https://www.crazygames.com/game/mipo?code='+params.code};
 const window={CrazyGames:{SDK:{init:async()=>{},game,user:{systemInfo:{locale:'he-IL'},isUserAccountAvailable:true,getUser:async()=>({username:'Portal.User'})},ad:{requestAd:(kind,callbacks)=>{events.push(['ad',kind]);callbacks.adStarted();callbacks.adError('no-fill')}}}},
  dispatchEvent:event=>events.push(['settings',event.detail]),req:async(p,b)=>b||{},
  setLanguage:async language=>events.push(['language',language]),mode:mode=>events.push(['mode',mode]),
  joinGame:async()=>events.push(['join',fields.get('jcode').value,fields.get('jname').value]),
  createGame:async()=>events.push(['create']),replaySameCrew:async()=>replays++,lastState:null};
 const context={window,crazygamesMode:true,s:{},URL,URLSearchParams,console,CustomEvent:class{constructor(name,options){this.detail=options.detail}},
  navigator:{share:async data=>shared=data},location:{search:'?cg=1'},
  document:{referrer:'https://www.crazygames.com/game/mipo',hidden:false,addEventListener(){},querySelector:()=>null,getElementById:id=>fields.get(id),documentElement:{classList:{add(){},remove(){}}}}};
 vm.createContext(context);await vm.runInContext(fs.readFileSync('static/crazygames.js','utf8'),context);
 assert(events.some(e=>e[0]==='join'&&e[1]==='ABCDE'&&e[2]==='Portal.User'));
 assert(!events.some(e=>e[0]==='create'));
 assert(events.some(e=>e[0]==='language'&&e[1]==='he'));
 assert(window.mipoPlatformMuted);
 await window.req('/api/state/ABCDE',{code:'ABCDE',status:'lobby'});
 assert(!events.some(e=>e[0]==='start'),'lobby is not active gameplay');
 await window.req('/api/state/ABCDE',{code:'ABCDE',status:'lobby',players:Array.from({length:6},()=>({active:true}))});
 assert.equal(events.filter(e=>e[0]==='room').at(-1)[1].isJoinable,false);
 await window.req('/api/state/ABCDE',{code:'ABCDE',status:'playing',reveal:false});
 assert(events.some(e=>e[0]==='start'));
 await window.req('/api/state/ABCDE',{code:'ABCDE',status:'playing',reveal:true});
 assert(events.some(e=>e[0]==='stop'));
 window.lastState={code:'ABCDE',status:'finished'};await window.share();assert.equal(shared.url,'https://www.crazygames.com/game/mipo?code=ABCDE');
 await roomJoin({code:'FGHIJ'});assert.equal(fields.get('jcode').value,'FGHIJ');
 await window.replaySameCrew();assert.equal(replays,1);assert(events.some(e=>e[0]==='ad'&&e[1]==='midgame'));
 game.settings.muteAudio=false;settingsListener();assert.equal(window.mipoPlatformMuted,false);
 console.log('CG_SDK_INVITES_USER_LOCALE_SETTINGS_GAMEPLAY_AND_AD_NO_FILL_CONTINUATION_OK');
})().catch(error=>{console.error(error);process.exitCode=1});
