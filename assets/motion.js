/* Groundwork article motion layer (Sept 2, 2026). The homepage's figure system, shared by every article.
   Plates and drawings (.fig, [data-ink]) ink themselves in as they arrive; prose blocks settle into register.
   Reduced motion pins every final state; without this script the pages are simply complete and still. */
(function () {
  'use strict';
  var rm = matchMedia('(prefers-reduced-motion: reduce)');
  var inks = Array.prototype.slice.call(document.querySelectorAll('.fig, [data-ink]'));
  var parts = [];

  function pin() {
    inks.forEach(function (f) { f.classList.add('ink'); });
    parts.forEach(function (p) { p.classList.add('in'); });
  }

  if (rm.matches || !('IntersectionObserver' in window)) { pin(); }
  else {
    /* plates and drawings draw as each one arrives */
    var plateIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('ink'); plateIO.unobserve(en.target); }
      });
    }, { threshold: 0.35 });
    inks.forEach(function (f) { plateIO.observe(f); });

    /* prose below the fold settles into register; above the fold is left exactly as it loaded */
    var main = document.getElementById('main') || document.querySelector('main');
    var SKIP = 'script,style,noscript,link,template,.crumb,.journeystrip,header.page,[hidden]';
    function collect(parent, grid) {
      Array.prototype.forEach.call(parent.children, function (el, i) {
        if (el.matches(SKIP)) return;
        if (el.matches('section,form,.grid2')) { collect(el, el.classList.contains('grid2')); return; }
        if (grid) el.style.setProperty('--i', String(i));
        parts.push(el);
      });
    }
    if (main) collect(main, false);
    var fold = window.innerHeight * 0.92;
    parts = parts.filter(function (el) { return el.getBoundingClientRect().top > fold; });
    parts.forEach(function (el) { el.classList.add('part'); });
    var partIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (en.intersectionRatio >= 0.12 || en.boundingClientRect.top < window.innerHeight * 0.85) {
          en.target.classList.add('in'); partIO.unobserve(en.target);
        }
      });
    }, { threshold: [0, 0.12] });
    parts.forEach(function (el) { partIO.observe(el); });
  }

  rm.addEventListener('change', function (e) { if (e.matches) pin(); });

  /* a plate replays when clicked (per-plate replay, the PR's own follow-up) */
  document.querySelectorAll('.fig').forEach(function (f) {
    f.addEventListener('click', function () {
      if (rm.matches) return;
      f.classList.remove('ink');
      void f.getBoundingClientRect();
      f.classList.add('ink');
    });
  });
})();
