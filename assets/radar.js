/* Readiness radar: 6 dimensions x 3 indicators, 0..4. Baseline saved once; latest drawn over it. */
(function () {
  var DIMS = ['Context', 'Truth', 'Memory', 'Workflow', 'Governance', 'Operations'];
  var form = document.getElementById('radar-form'), svg = document.getElementById('radar-svg'), cap = document.getElementById('radar-caption'), con = document.getElementById('radar-constraint');
  if (!form) return;
  function read() {
    var sums = [0, 0, 0, 0, 0, 0];
    form.querySelectorAll('fieldset.q').forEach(function (f) { var c = f.querySelector('input:checked'); sums[+f.getAttribute('data-dim')] += c ? +c.value : 0; });
    return sums.map(function (s) { return s / 12; });
  }
  function get(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function pt(k, r) { var a = -Math.PI / 2 + k * Math.PI / 3; return [200 + 150 * r * Math.cos(a), 200 + 150 * r * Math.sin(a)]; }
  function poly(vals) { return vals.map(function (v, k) { return pt(k, Math.max(v, 0.04)).join(','); }).join(' '); }
  function draw() {
    var base = get('pb-radar-baseline'), latest = get('pb-radar-latest'), cur = read();
    var s = '';
    [0.25, 0.5, 0.75, 1].forEach(function (r) { s += '<polygon points="' + poly([r, r, r, r, r, r]) + '" fill="none" stroke="var(--rule)" stroke-width="1"/>'; });
    DIMS.forEach(function (d, k) { var p = pt(k, 1), q = pt(k, 1.17); s += '<line x1="200" y1="200" x2="' + p[0] + '" y2="' + p[1] + '" stroke="var(--rule)"/><text x="' + q[0] + '" y="' + (q[1] + 4) + '" text-anchor="middle" font-size="9" font-family="Courier Prime" fill="var(--ink-soft)">' + d.toUpperCase() + '</text>'; });
    if (base) s += '<polygon points="' + poly(base.v) + '" fill="none" stroke="var(--ink-soft)" stroke-dasharray="4 3" stroke-width="1.2"/>';
    s += '<polygon points="' + poly(latest ? latest.v : cur) + '" fill="var(--terra)" fill-opacity=".12" stroke="var(--terra-deep)" stroke-width="1.8"/>';
    svg.innerHTML = s;
    var v = latest ? latest.v : cur, lo = v.indexOf(Math.min.apply(null, v));
    cap.textContent = (base ? 'Baseline ' + base.d + ' (dashed). ' : '') + (latest ? 'Latest ' + latest.d + '.' : 'Unsaved draft.');
    con.textContent = 'Binding constraint: ' + DIMS[lo] + ', the dimension most limiting your results right now.' + (v[4] < 0.5 ? ' Governance is weak: the verdict is capped until limits are enforced.' : '');
  }
  document.getElementById('radar-save').addEventListener('click', function () {
    var rec = { v: read(), d: new Date().toISOString().slice(0, 10) };
    if (!get('pb-radar-baseline')) set('pb-radar-baseline', rec);
    set('pb-radar-latest', rec); draw();
  });
  document.getElementById('radar-reset').addEventListener('click', function () { try { localStorage.removeItem('pb-radar-baseline'); localStorage.removeItem('pb-radar-latest'); } catch (e) {} draw(); });
  form.addEventListener('change', draw);
  draw();
})();
