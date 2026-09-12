
document.documentElement.classList.remove('no-js');
(function(){
  // draw-in on scroll
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target);} });
  },{threshold:0.35, rootMargin:'0px 0px -10% 0px'});
  document.querySelectorAll('svg.fig[data-anim], .reveal').forEach(el=>io.observe(el));
  function replay(svg){
    svg.classList.remove('is-in'); svg.getBoundingClientRect();
    requestAnimationFrame(()=>requestAnimationFrame(()=>svg.classList.add('is-in')));
  }
  document.querySelectorAll('svg.fig').forEach(s=>s.addEventListener('click',()=>replay(s)));
  document.querySelectorAll('.replay').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();replay(b.closest('.plate').querySelector('svg.fig'))}));
  // figures inside collapsed cards: observe when the card opens
  // mobile nav
  const nt=document.querySelector('.navtoggle'), links=document.querySelector('.links');
  if(nt){nt.addEventListener('click',()=>{const o=links.classList.toggle('open'); nt.setAttribute('aria-expanded',o);});}
  // cards
  document.querySelectorAll('.icard').forEach(card=>{
    const head=card.querySelector('.head');
    head.addEventListener('click',()=>{
      const open=card.getAttribute('data-open')==='true';
      card.setAttribute('data-open', open?'false':'true'); head.setAttribute('aria-expanded', !open);
      if(!open){ card.querySelectorAll('svg.fig').forEach(s=>setTimeout(()=>s.classList.add('is-in'),260)); }
    });
    card.querySelectorAll('.tabs button').forEach(b=>b.addEventListener('click',()=>{
      card.querySelectorAll('.tabs button').forEach(x=>x.setAttribute('aria-selected','false'));
      card.querySelectorAll('.panel').forEach(p=>p.removeAttribute('data-active'));
      b.setAttribute('aria-selected','true');
      const p=card.querySelector('#'+b.getAttribute('aria-controls')); p.setAttribute('data-active','');
      p.querySelectorAll('svg.fig').forEach(s=>s.classList.add('is-in'));
    }));
    card.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{
      const t=b.parentElement.querySelector('pre').innerText;
      try{ await navigator.clipboard.writeText(t); b.setAttribute('data-done',''); b.textContent='Copied'; setTimeout(()=>{b.removeAttribute('data-done'); b.textContent='Copy prompt';},1600);}catch(e){}
    }));
  });
  const all=document.getElementById('expand-all'), none=document.getElementById('collapse-all');
  if(all){all.addEventListener('click',()=>document.querySelectorAll('.icard').forEach(c=>{c.setAttribute('data-open','true');c.querySelectorAll('svg.fig').forEach(s=>s.classList.add('is-in'));}));}
  if(none){none.addEventListener('click',()=>document.querySelectorAll('.icard').forEach(c=>c.setAttribute('data-open','false')));}
  // open a card addressed by the hash
  function openHash(){ const h=location.hash.slice(1); if(!h) return; const c=document.getElementById(h); if(c&&c.classList.contains('icard')){c.setAttribute('data-open','true'); c.querySelectorAll('svg.fig').forEach(s=>s.classList.add('is-in'));} }
  window.addEventListener('hashchange',openHash); openHash();
  // toc scroll-spy
  const tocLinks=[...document.querySelectorAll('.toc a[href^="#"]')];
  if(tocLinks.length){
    const map=new Map(tocLinks.map(a=>[a.getAttribute('href').slice(1),a]));
    const spy=new IntersectionObserver(es=>{es.forEach(e=>{ if(e.isIntersecting){ tocLinks.forEach(a=>a.removeAttribute('aria-current')); const a=map.get(e.target.id); if(a) a.setAttribute('aria-current','true'); } });},{rootMargin:'-20% 0px -70% 0px'});
    map.forEach((a,id)=>{const el=document.getElementById(id); if(el) spy.observe(el);});
  }
  // print: open everything first
  window.addEventListener('beforeprint',()=>document.querySelectorAll('.icard').forEach(c=>c.setAttribute('data-open','true')));
})();
