// Exercise actual production render code, including decoded preload and late AI delivery.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const page=fs.readFileSync('static/kyc.html','utf8');
const source=page.slice(page.indexOf('const visualCache='),page.indexOf('async function makeFinalHero('));
const elements={},images={};
function element(id){return elements[id]||={dataset:{},style:{},classList:{set:new Set(),add(x){this.set.add(x)},remove(x){this.set.delete(x)},toggle(x,v){v?this.add(x):this.remove(x)}}}}
class Image {set src(url){this.url=url;images[url]=this}get src(){return this.url}}
const sandbox={Image,performance:{now:()=>100},requestAnimationFrame:fn=>fn(),imageView:'run1',heroAsked:-1,$:element,makeHero(){throw Error('unexpected generation')},makeFinalHero(){throw Error('unexpected generation')}};
vm.createContext(sandbox);vm.runInContext(source,sandbox);
const instant='/api/instant-image/TEST/0?run=1',full='/api/hero-image/TEST/0?run=1';
const d={instant_visual:instant,hero:null,subject:{photo_url:'/photo.jpg'},hero_status:'running'};
sandbox.preloadVisual(instant);images[instant].complete=true;images[instant].naturalWidth=640;
sandbox.renderRoundImage(d);
assert.equal(element('#heroImg').src,instant,'preloaded visual appears synchronously');
assert.equal(element('#heroImg').dataset.visualKind,'instant');
assert.equal(element('#revealPhoto').style.display,'none');
sandbox.renderRoundImage({...d,hero:full,hero_status:'ready'});
assert.equal(element('#heroImg').src,instant,'keep instant while full loads');
images[full].onload();assert.equal(element('#heroImg').src,full);
assert.equal(element('#heroImg').dataset.visualKind,'full-ai');
// Delivery failure keeps a valid instant visual and hides all long AI status messages.
sandbox.renderRoundImage({...d,hero:'/broken'});images['/broken'].onerror();
assert.equal(element('#heroImg').src,instant);
sandbox.renderRoundImage({...d,hero_status:'failed'});assert.equal(element('#heroImg').src,instant);
assert.ok(element('#heroStatus').classList.set.has('hidden'));
// Stale completion cannot repaint after Play Again / next round.
sandbox.renderRoundImage({...d,hero:'/old'});const late=images['/old'].onload;
sandbox.imageView='run2';element('#heroImg').src='new-round';late();assert.equal(element('#heroImg').src,'new-round');
// Full AI already cached before Reveal can display directly.
images[full].complete=true;images[full].naturalWidth=832;element('#heroImg').dataset.requested='';
sandbox.renderRoundImage({...d,hero:full});assert.equal(element('#heroImg').src,full);
console.log('HYBRID_PRELOAD_LATE_EARLY_FAILURE_STALE_OK');

// Full ready in DB must never suppress an instant visual while its bytes download.
sandbox.imageView='run3';element('#heroImg').dataset.loaded='';element('#heroImg').dataset.requested='';
const coldInstant='/api/instant-image/TEST/2?run=1',coldFull='/api/hero-image/TEST/2?run=1';
sandbox.renderRoundImage({...d,instant_visual:coldInstant,hero:coldFull});
images[coldInstant].onload();assert.equal(element('#heroImg').src,coldInstant);
images[coldFull].onload();assert.equal(element('#heroImg').src,coldFull);
images[coldInstant].onload();assert.equal(element('#heroImg').src,coldFull,'late instant must not downgrade full AI');
console.log('INSTANT_FIRST_WHILE_READY_AI_DOWNLOADS_OK');
