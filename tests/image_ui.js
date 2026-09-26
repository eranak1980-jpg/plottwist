// Execute the actual image render functions against a small controlled DOM.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const page = fs.readFileSync('static/kyc.html','utf8');
const source = page.slice(page.indexOf('function showGeneratedImage('),page.indexOf('async function makeFinalHero('));
const elements = {};
function element(id) {
  return elements[id] ||= {dataset:{},style:{},classList:{set:new Set(),add(x){this.set.add(x)},remove(x){this.set.delete(x)},toggle(x,v){v?this.add(x):this.remove(x)}}};
}
const sandbox={imageView:'run1',heroAsked:-1,$:s=>element(s),copy:{ai_image_missing:'fallback',ai_reveal_ready:'ready',ai_reveal_generating:'generating',final_ai_missing:'final fallback'},makeHero(){throw Error('unexpected generation')},makeFinalHero(){throw Error('unexpected generation')}};
vm.createContext(sandbox);vm.runInContext(source,sandbox);
const d={hero:'/api/hero-image/TEST/0?run=1',subject:{photo_url:'/original.jpg'},hero_status:'ready'};
element('#revealPhoto').style.display='block';
sandbox.renderRoundImage(d);
assert.equal(element('#revealPhoto').style.display,'block','original stays until AI image loaded');
element('#heroImg').onload();
assert.equal(element('#revealPhoto').style.display,'none');
assert.equal(element('#heroImg').style.display,'block');
assert.equal(element('#heroStatus').textContent,'ready');
// Delivery fails even though DB says ready: preserve a usable Reveal.
const d2={...d,hero:'/api/hero-image/TEST/1?run=1'};
sandbox.renderRoundImage(d2);element('#heroImg').onerror();
assert.equal(element('#revealPhoto').style.display,'block');
assert.equal(element('#heroImg').style.display,'none');
assert.equal(element('#heroStatus').textContent,'fallback');
// A late onload from an old game cannot mutate the new game's screen.
sandbox.renderRoundImage({...d,hero:'/old-pending.jpg'});
const oldLoad=element('#heroImg').onload;sandbox.imageView='run2';
element('#heroImg').style.display='none';oldLoad();
assert.equal(element('#heroImg').style.display,'none');
sandbox.renderRoundImage({...d,hero:null,hero_status:'failed'});
assert.equal(element('#heroStatus').textContent,'fallback');
sandbox.renderFinalImage({final_hero:null,final_hero_status:'failed',photo_count:1});
assert.equal(element('#finalHeroStatus').textContent,'final fallback');
console.log('IMAGE_UI_LOADING_FALLBACK_STALE_CALLBACK_OK');
