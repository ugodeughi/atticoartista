(()=>{
const nav=document.querySelector('.nav'),burger=nav.querySelector('.burger');
const onScroll=()=>nav.classList.toggle('solid',scrollY>40);onScroll();addEventListener('scroll',onScroll,{passive:true});
burger.onclick=()=>{const o=nav.classList.toggle('open');burger.setAttribute('aria-expanded',o)};
nav.querySelectorAll('nav a').forEach(a=>a.onclick=()=>{nav.classList.remove('open');burger.setAttribute('aria-expanded',false)});

// confronto prima/dopo
document.querySelectorAll('.ba').forEach(b=>{
  const i=b.querySelector('input'),k=document.createElement('span');k.className='knob';k.textContent='⇆';b.append(k);
  i.oninput=()=>b.style.setProperty('--p',i.value+'%');
});

// lightbox
const d=document.getElementById('lb'),img=d.querySelector('img'),cap=d.querySelector('figcaption');
const links=[...document.querySelectorAll('a.lb')];let n=0;
const show=j=>{n=(j+links.length)%links.length;img.src=links[n].href;img.alt=cap.textContent=links[n].dataset.cap||''};
links.forEach((a,j)=>a.onclick=e=>{e.preventDefault();show(j);d.showModal()});
d.querySelector('.lb-x').onclick=()=>d.close();
d.querySelector('.lb-p').onclick=()=>show(n-1);
d.querySelector('.lb-n').onclick=()=>show(n+1);
d.onclick=e=>{if(e.target===d||e.target.tagName==='FIGURE')d.close()};
d.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')show(n-1);if(e.key==='ArrowRight')show(n+1)});
let x0=null;d.addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});
d.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>50)show(n+(dx<0?1:-1));x0=null});

// comparsa morbida
if('IntersectionObserver'in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.sec h2,.sec .lead,.card,.room,.details article,.steps li,.price,.split>*').forEach(el=>{el.classList.add('rv');io.observe(el)});
}
// suggerimento lingua del browser (nessun redirect automatico, così Google indicizza tutte le versioni)
try{
  const cur=document.documentElement.lang,K='lang-hint';
  if(!localStorage.getItem(K)){
    const pref=(navigator.languages||[navigator.language]).map(l=>(l||'').slice(0,2).toLowerCase());
    const first=pref.find(l=>document.querySelector('.langs a[hreflang="'+l+'"]'));
    const a=first&&first!==cur&&document.querySelector('.langs a[hreflang="'+first+'"]');
    if(a){
      const b=document.createElement('div');b.className='suggest';b.lang=first;
      b.innerHTML='<span></span><a class="btn"></a><button aria-label="×">×</button>';
      b.querySelector('span').textContent=a.dataset.s;const g=b.querySelector('a');g.textContent=a.dataset.go;g.href=a.href;
      const done=()=>{try{localStorage.setItem(K,'1')}catch(e){}b.remove()};
      b.querySelector('button').onclick=done;g.onclick=done;document.body.append(b);
    }
  }
}catch(e){}
})();
