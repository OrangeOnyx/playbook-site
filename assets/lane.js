/* Remembers the lane picked at Intake (personal or business) and lifts it first on every section page. */
(function () {
  var d = document.documentElement, KEY = 'pb-lane';
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} apply(); }
  function apply() {
    var v = get();
    if (v === 'personal' || v === 'business') d.setAttribute('data-lane', v); else d.removeAttribute('data-lane');
    document.querySelectorAll('.lane-pick').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-lane') === v ? 'true' : 'false'); });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.lane-pick'); if (!b) return;
    set(b.getAttribute('data-lane'));
  });
  apply();
})();
