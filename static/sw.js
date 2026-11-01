/* Public app shell only. Never cache player tokens, API state, photos or answers. */
const CACHE='plot-shell-v15';
const SHELL=['/','/static/mascot.js?v=1','/static/mascot.css?v=1',...['smirk','surprise','suspicious','wink','celebrate'].map(p=>'/static/mascot/'+p+'.webp?v=1'),'/static/premium.css?v=cream-v3','/static/experience.css?v=11','/static/companion-copy.js?v=3','/static/experience.js?v=15','/static/first-game.js?v=4','/static/first-game.css?v=3','/static/playtest.js?v=2','/static/playtest.css?v=2'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('plot-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);if(url.origin!==self.location.origin||event.request.method!=='GET')return;
 const navigation=event.request.mode==='navigate'&&(url.pathname==='/'||url.pathname==='/index.html');
 const asset=SHELL.includes(url.pathname+url.search)&&url.pathname!=='/';
 if(!navigation&&!asset)return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE),key=navigation?'/':url.pathname+url.search;
  const cached=await cache.match(key);
  if(asset&&cached)return cached;
  try{
   // A cold/temporarily unavailable origin should not replace a saved game with a browser error.
   const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),6000);
   let response;try{response=await fetch(event.request,{signal:controller.signal})}finally{clearTimeout(timer)}
   if(response.ok){if(!navigation||response.headers.get('content-type')?.includes('text/html'))await cache.put(key,response.clone());return response}
   if(cached)return cached;return response;
  }catch(error){if(cached)return cached;throw error}
 })());
});
