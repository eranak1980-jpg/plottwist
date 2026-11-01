(() => {
 const buttons=document.querySelectorAll('[data-mood]');
 function show(button){document.getElementById('actor').innerHTML=window.MipoMascot.html(button.dataset.mood);document.getElementById('caption').textContent=button.textContent;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)))}
 buttons.forEach(b=>b.onclick=()=>show(b));window.MipoMascot.preload();show(buttons[0]);
})();
