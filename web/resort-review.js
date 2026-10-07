const D = JSON.parse(document.querySelector('#data').textContent),
  $ = (x) => document.getElementById(x);
let C, E;
function comps(g) {
  let a = new Map(g.nodes.map((n) => [n.id, new Set()]));
  g.edges.forEach((e) => {
    a.get(e.from)?.add(e.to);
    a.get(e.to)?.add(e.from);
  });
  let r = new Map(),
    s = new Set(),
    c = 0;
  for (let n of g.nodes) {
    if (s.has(n.id)) continue;
    c++;
    let q = [n.id];
    s.add(n.id);
    while (q.length) {
      let x = q.pop();
      r.set(x, c);
      for (let y of a.get(x) || []) {
        if (!s.has(y)) {
          s.add(y);
          q.push(y);
        }
      }
    }
  }
  return r;
}
function detail(e) {
  E = e.id;
  draw();
  let d = $('detail');
  d.replaceChildren();
  let b = document.createElement('b');
  b.textContent = e.name || e.id;
  d.append(b);
  let dl = document.createElement('dl');
  for (let x of [
    ['Kind', e.kind],
    ['Native grade', e.source_difficulty || 'unknown'],
    ['Normalized grade', e.difficulty || 'unknown'],
    ['Source way', e.source_refs?.[0] || 'unknown'],
    ['Review status', e.review_status || C.graph.review_status],
    ['Direction', e.from + ' → ' + e.to],
  ]) {
    let a = document.createElement('dt'),
      b = document.createElement('dd');
    a.textContent = x[0];
    b.textContent = x[1];
    dl.append(a, b);
  }
  let a = document.createElement('a');
  a.href = 'https://www.openstreetmap.org/' + (e.source_refs?.[0] || '');
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.textContent = 'Open source way';
  d.append(dl, a);
  $('status').textContent = 'Selected ' + (e.name || e.id);
  d.focus();
}
function draw() {
  let g = C.graph,
    m = C.manifest,
    v = $('map');
  v.replaceChildren();
  let X = g.nodes.map((n) => n.lon),
    Y = g.nodes.map((n) => n.lat),
    a = Math.min(...X),
    b = Math.max(...X),
    c = Math.min(...Y),
    d = Math.max(...Y),
    cos = Math.cos((((c + d) / 2) * Math.PI) / 180),
    z = Math.min(790 / ((b - a) * cos || 1), 470 / (d - c || 1)),
    f = ([x, y]) => [450 + (x - (a + b) / 2) * cos * z, 280 - (y - (c + d) / 2) * z],
    cc = comps(g);
  let counts = new Map();
  for (let n of cc.values()) counts.set(n, (counts.get(n) || 0) + 1);
  let largest = [...counts].sort((a, b) => b[1] - a[1])[0]?.[0];
  for (let e of g.edges.filter(
    (e) =>
      (e.kind == 'lift' ? $('l').checked : $('p').checked) &&
      ($('d').checked || cc.get(e.from) == largest),
  )) {
    let q = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    q.setAttribute(
      'points',
      e.geometry
        .map(f)
        .map((x) => x.join(','))
        .join(' '),
    );
    q.setAttribute(
      'class',
      'e ' + e.kind + (E == e.id ? ' selected' : '') + (cc.get(e.from) != largest ? ' dis' : ''),
    );
    q.setAttribute('tabindex', '0');
    q.setAttribute('role', 'button');
    q.setAttribute(
      'aria-label',
      (e.name || e.id) + ', native grade ' + (e.source_difficulty || 'unknown'),
    );
    q.onclick = () => detail(e);
    q.onkeydown = (x) => {
      if (x.key == 'Enter' || x.key == ' ') {
        x.preventDefault();
        detail(e);
      }
    };
    v.append(q);
  }
  $('sum').textContent =
    'Nodes: ' +
    g.nodes.length +
    ' · Edges: ' +
    g.edges.length +
    ' · Lifts: ' +
    g.edges.filter((e) => e.kind == 'lift').length +
    ' · Pistes: ' +
    g.edges.filter((e) => e.kind == 'piste').length +
    ' · Weak components: ' +
    new Set(cc.values()).size;
  $('cov').textContent = 'Bounded coverage: ' + m.coverage_status;
  $('src').textContent =
    'Fetched ' + m.fetched_at + ' · ' + m.attribution + ' · graph ' + m.graph_sha256;
}
for (let k in D) {
  let o = document.createElement('option');
  o.value = k;
  o.textContent = D[k].label;
  $('s').append(o);
}
function load() {
  C = D[$('s').value];
  E = null;
  $('detail').replaceChildren();
  $('status').textContent = 'Select a segment.';
  draw();
}
$('s').onchange = load;
for (let x of ['l', 'p', 'd'])
  $(x).onchange = () => {
    E = null;
    $('detail').replaceChildren();
    $('status').textContent = 'Select a segment.';
    draw();
  };
load();
