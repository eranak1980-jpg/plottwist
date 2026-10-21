const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('static/checkout.html','utf8').split('<script>')[1].split('</script>')[0];
async function page(path,search,stored,status='pending'){
 const elements={};const data=new Map(Object.entries(stored||{}));let destination;const calls=[];
 const ctx={URLSearchParams,Intl,crypto:{randomUUID:()=> 'browser-identity-12345'},document:{getElementById:id=>elements[id]??=( {hidden:false,textContent:'',href:''})},localStorage:{getItem:k=>data.get(k),setItem:(k,v)=>data.set(k,v)},sessionStorage:{getItem:()=>null},location:{pathname:path,search,replace:u=>destination=u,reload:()=>{}},setTimeout:f=>{f()},fetch:async url=>{calls.push(url);return {ok:true,json:async()=> url==='/api/pricing'?{currency:'USD',single_cents:599}:url==='/api/checkout'?{order_id:'saved-order',checkout_url:'https://payments.payplus.co.il/l/test'}:{status}}}};
 await vm.runInNewContext(source,ctx);return {elements,data,destination,calls};
}
(async()=>{
 let p=await page('/checkout','?product=one_game');
 assert.equal(p.destination,'https://payments.payplus.co.il/l/test');
 assert.equal(JSON.parse(p.data.get('mipo_checkout_pending')).order_id,'saved-order');
 const saved={mipo_checkout_pending:JSON.stringify({order_id:'saved-order',product:'one_game'})};
 p=await page('/checkout/success','?transaction_uid=untrusted',saved,'paid');
 assert(p.calls[0].startsWith('/api/order/saved-order?client_id='));assert.equal(p.elements.title.textContent,'Your MIPO game is ready');
 p=await page('/checkout/success','?status=approved',saved,'pending');
 assert.equal(p.elements.title.textContent,'Still confirming');assert.notEqual(p.elements.action.href,'/?new=1');
 p=await page('/checkout/success','?order=explicit-order',saved,'paid');assert(p.calls[0].startsWith('/api/order/explicit-order?'));
 p=await page('/checkout/success','',{mipo_checkout_pending:'broken-json'});assert.equal(p.elements.title.textContent,'Payment status unavailable');
 console.log('CHECKOUT_RETURN_PASSED: persist before redirect, recover omitted order, explicit order precedence, no unlock from redirect, corrupt storage; external requests=0');
})().catch(e=>{console.error(e);process.exit(1)});
