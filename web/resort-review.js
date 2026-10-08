const D = JSON.parse(document.querySelector('#data').textContent),
  $ = (x) => document.getElementById(x);
let C, E, L, X;
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
function excludedDetail(e) {
  E = null;
  L = null;
  $('lift-review').value = '';
  $('lift-detail').replaceChildren();
  $('x').checked = true;
  X = e.source_ref;
  draw();
  const d = $('detail');
  d.replaceChildren();
  const h = document.createElement('b');
  h.textContent = e.name || e.source_ref;
  d.append(h);
  const dl = document.createElement('dl');
  for (const pair of [
    ['Status', e.status],
    ['Class', e.classification],
    ['Reason', e.reason],
    ['Native grade', e.difficulty || 'unknown'],
    ['Native tags', JSON.stringify(e.native_tags || {})],
    ['Source way', e.source_ref],
  ]) {
    const dt = document.createElement('dt'),
      dd = document.createElement('dd');
    dt.textContent = pair[0];
    dd.textContent =
      pair[0] === 'Reason' ? String(pair[1] || 'not recorded').replaceAll('_', ' ') : pair[1];
    dl.append(dt, dd);
  }
  const a = document.createElement('a');
  a.href = 'https://www.openstreetmap.org/' + e.source_ref;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.textContent = 'Open source way';
  d.append(dl, a);
  $('status').textContent = 'Selected excluded source geometry; routing unchanged.';
  d.focus();
}
function appendSourceEvidence(container, refs) {
  for (const ref of refs) {
    const evidence = C.source_evidence?.[ref];
    const heading = document.createElement('h3');
    heading.textContent = 'Native source evidence · ' + ref;
    const note = document.createElement('p');
    note.textContent =
      'Snapshot tags are not current operating status or permission. Missing tags mean unknown, not allowed. Imported direction is not independently verified.';
    container.append(heading, note);
    const dl = document.createElement('dl');
    const tags = evidence?.tags || {};
    const groups = [
      ['Source version', evidence?.version || 'Not recorded'],
      [
        'Access tags',
        ['access', 'ski', 'foot', 'aerialway:access', 'access:conditional', 'ski:conditional'],
      ],
      ['Direction tags', ['oneway', 'piste:oneway']],
      ['Operating tags', ['opening_hours', 'seasonal']],
      ['Source duration (not measured)', ['aerialway:duration']],
    ];
    for (const [label, keys] of groups) {
      const dt = document.createElement('dt'),
        dd = document.createElement('dd');
      dt.textContent = label;
      dd.textContent = Array.isArray(keys)
        ? keys
            .filter((k) => Object.hasOwn(tags, k))
            .map((k) => k + '=' + tags[k])
            .join('; ') || 'Not recorded — unknown'
        : keys;
      dl.append(dt, dd);
    }
    container.append(dl);
  }
}

function detail(e) {
  X = null;
  L = null;
  $('lift-review').value = '';
  $('lift-detail').replaceChildren();
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
    ['Imported direction (unverified)', e.from + ' → ' + e.to],
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
  appendSourceEvidence(d, e.source_refs || []);
  $('status').textContent = 'Selected ' + (e.name || e.id);
  d.focus();
}
function draw() {
  let g = C.graph,
    m = C.manifest,
    v = $('map');
  v.replaceChildren();
  let extra = (L?.endpoint_incidence || []).map((e) => e.coordinate).filter(Boolean);
  const excluded = C.excluded_source || [];
  const excludedCoords = excluded.flatMap((e) => e.geometry || []);
  let allX = [
    ...g.nodes.map((n) => n.lon),
    ...extra.map((c) => c[0]),
    ...excludedCoords.map((c) => c[0]),
  ];
  let allY = [
    ...g.nodes.map((n) => n.lat),
    ...extra.map((c) => c[1]),
    ...excludedCoords.map((c) => c[1]),
  ];
  let lonValues = allX,
    latValues = allY,
    a = Math.min(...lonValues),
    b = Math.max(...lonValues),
    c = Math.min(...latValues),
    d = Math.max(...latValues),
    cos = Math.cos((((c + d) / 2) * Math.PI) / 180),
    z = Math.min(790 / ((b - a) * cos || 1), 470 / (d - c || 1)),
    f = ([x, y]) => [450 + (x - (a + b) / 2) * cos * z, 280 - (y - (c + d) / 2) * z],
    cc = comps(g);
  let counts = new Map();
  for (let n of cc.values()) counts.set(n, (counts.get(n) || 0) + 1);
  let largest = [...counts].sort((a, b) => b[1] - a[1])[0]?.[0];
  for (const e of $('x').checked ? excluded : []) {
    const segments = e.geometry_segments || [e.geometry || []];
    for (const segment of segments) {
      const q = document.createElementNS(
        'http://www.w3.org/2000/svg',
        e.classification === 'closed-area' && e.geometry_complete !== false
          ? 'polygon'
          : 'polyline',
      );
      q.setAttribute(
        'points',
        segment
          .map(f)
          .map((x) => x.join(','))
          .join(' '),
      );
      q.setAttribute(
        'class',
        'excluded ' + e.classification + (X === e.source_ref ? ' selected' : ''),
      );
      q.setAttribute('tabindex', '0');
      q.setAttribute('role', 'button');
      q.setAttribute(
        'aria-label',
        (e.name || e.source_ref) +
          ', excluded source geometry, ' +
          (e.reason || 'no reason recorded'),
      );
      q.onclick = () => excludedDetail(e);
      q.onkeydown = (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          excludedDetail(e);
        }
      };
      v.append(q);
    }
  }
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
  for (const [i, endpoint] of (L?.endpoint_incidence || []).entries()) {
    if (!endpoint.coordinate) continue;
    const [x, y] = f(endpoint.coordinate);
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', x);
    circle.setAttribute('cy', y);
    circle.setAttribute('r', 11);
    circle.setAttribute('class', 'endpoint');
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', x);
    label.setAttribute('y', y + 5);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('class', 'endpoint-label');
    label.textContent = String(i + 1);
    v.append(circle, label);
  }
  $('sum').textContent =
    'Excluded source shapes: ' +
    excluded.length +
    ' · Nodes: ' +
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
  X = null;
  E = null;
  L = null;
  $('lift-detail').replaceChildren();
  const select = $('lift-review');
  select.replaceChildren(new Option('Choose a source lift', ''));
  for (const lift of C.diagnostics?.lifts || [])
    select.add(
      new Option(
        lift.name + (lift.imported_edge_ids.length ? '' : ' (not imported)'),
        lift.source_ref,
      ),
    );
  select.disabled = !C.diagnostics;
  $('lift-summary').textContent = C.diagnostics
    ? 'Markers 1/2 are source start/end, not verified boarding/alighting.'
    : 'Endpoint diagnostics have not been generated for this sample.';
  $('detail').replaceChildren();
  $('status').textContent = 'Select a segment.';
  renderExcludedList();
  draw();
}
function renderExcludedList() {
  const list = $('excluded-list');
  list.replaceChildren();
  for (const item of C.excluded_source || []) {
    const li = document.createElement('li'),
      b = document.createElement('button');
    b.type = 'button';
    b.textContent = `${item.name || item.source_ref} — ${item.classification}; ${item.reason || 'excluded'}`;
    b.onclick = () => excludedDetail(item);
    li.append(b);
    list.append(li);
  }
  if (!list.children.length) {
    const li = document.createElement('li');
    li.textContent = 'No excluded source geometry in this snapshot.';
    list.append(li);
  }
}
$('s').onchange = load;
for (let x of ['l', 'p', 'd', 'x'])
  $(x).onchange = () => {
    E = null;
    X = null;
    $('detail').replaceChildren();
    $('status').textContent = 'Select a segment.';
    draw();
  };
load();

$('lift-review').onchange = () => {
  X = null;
  L = C.diagnostics?.lifts.find((l) => l.source_ref == $('lift-review').value) || null;
  E = L?.imported_edge_ids[0] || null;
  $('detail').replaceChildren();
  $('lift-detail').replaceChildren();
  if (L) {
    const heading = document.createElement('h3');
    heading.textContent = L.name + ' — source endpoint evidence';
    $('lift-detail').append(heading);
    appendSourceEvidence($('lift-detail'), [L.source_ref]);
    for (const [i, e] of L.endpoint_incidence.entries()) {
      const section = document.createElement('div');
      const h = document.createElement('h4');
      h.textContent = `${i + 1}. Source ${i ? 'end' : 'start'} · node ${e.source_node}`;
      section.append(h);
      const p = document.createElement('p');
      p.textContent =
        `Exact incoming piste segments: ${e.incoming_piste_edge_ids.length}. Exact outgoing piste segments: ${e.outgoing_piste_edge_ids.length}. ` +
        (e.station_tags === null
          ? 'Raw station tags not recovered.'
          : `Raw tags: ${JSON.stringify(e.station_tags)}. `) +
        'Missing incidence is a data-review gap, not proof that access is impossible.';
      section.append(p);
      const a = document.createElement('a');
      a.href = 'https://www.openstreetmap.org/node/' + e.source_node;
      a.textContent = 'Inspect source node';
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      section.append(a);
      $('lift-detail').append(section);
    }
  }
  $('status').textContent = L
    ? 'Reviewing ' + L.name + '; routing unchanged.'
    : 'Select a segment.';
  draw();
};
