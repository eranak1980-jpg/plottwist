/* Approved MIPO comic mascot. Decorative only: gameplay never waits for art. */
(() => {
 const expressions=['smirk','surprise','suspicious','wink','celebrate'];
 const poses={peek:'smirk',hum:'smirk',wait:'smirk',hmm:'suspicious',tie:'suspicious',suspicious:'suspicious',miss:'surprise',wow:'surprise',oops:'surprise',gasp:'surprise',correct:'wink',wink:'wink',leader:'wink',win:'celebrate'};
 function expression(mood){return poses[mood]||(expressions.includes(mood)?mood:'smirk')}
 function src(pose){return '/static/mascot/'+pose+'.webp?v=1'}
 function html(mood='peek'){
  const pose=expression(mood);
  return '<span class="popMascot mipoComic expression-'+pose+'" data-expression="'+pose+'" aria-hidden="true"><img src="'+src(pose)+'" width="384" height="384" alt="" draggable="false" decoding="async"></span>';
 }
 document.addEventListener('error',event=>{const img=event.target;if(img?.tagName==='IMG'&&img.closest('.mipoComic'))img.closest('.mipoComic').style.visibility='hidden'},true);
 let preloaded=false;
 function preload(){if(preloaded)return;preloaded=true;for(const pose of expressions){const img=new Image();img.src=src(pose)}}
 // No voice, timers, game data or paid generation in the mascot module.
 window.MipoMascot=Object.freeze({html,expression,preload});
})();
