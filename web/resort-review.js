const D = JSON.parse(document.querySelector('#data').textContent),
  $ = (x) => document.getElementById(x);
let C,
  E,
  L,
  X,
  Q = '';
let selectedSource = null;
let focusSelection = false;
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
  selectedSource = null;
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

function sourceKey(e) {
  return e.source_refs?.[0] || '';
}
function sourceGroups() {
  const groups = new Map();
  for (const e of C.graph.edges) {
    for (const ref of e.source_refs || []) {
      if (!groups.has(ref)) groups.set(ref, { ref, name: e.name || ref, kind: e.kind, edges: [] });
      const group = groups.get(ref);
      group.edges.push(e);
      if (!group.name && e.name) group.name = e.name;
    }
  }
  return [...groups.values()].sort(
    (a, b) => a.name.localeCompare(b.name) || a.ref.localeCompare(b.ref),
  );
}
function updateSearch() {
  const list = $('search-results');
  list.replaceChildren();
  const query = Q.trim().toLocaleLowerCase();
  const matches = sourceGroups().filter((group) => {
    if (!query) return false;
    return [group.name, group.ref, ...group.edges.map((e) => e.id)].some((value) =>
      String(value || '')
        .toLocaleLowerCase()
        .includes(query),
    );
  });
  $('search-status').textContent = query
    ? matches.length
      ? `${matches.length} source way${matches.length === 1 ? '' : 's'} found.`
      : 'No trails or lifts match that search.'
    : 'Search by a trail or lift name, or a source way ID.';
  for (const group of matches) {
    const item = document.createElement('li');
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = `${group.name} — ${group.kind}; ${group.ref}`;
    button.setAttribute('aria-label', `${group.name}, ${group.kind}, source way ${group.ref}`);
    button.onclick = () => {
      selectedSource = group.ref;
      const representative = group.edges[0];
      detail(representative);
      $('trail-search').focus();
    };
    item.append(button);
    list.append(item);
  }
}
function clearSegmentSelection() {
  L = null;
  $('lift-review').value = '';
  E = null;
  X = null;
  selectedSource = null;
  focusSelection = false;
  $('detail').replaceChildren();
  $('lift-detail').replaceChildren();
}

function detail(e) {
  X = null;
  L = null;
  $('lift-review').value = '';
  $('lift-detail').replaceChildren();
  E = e.id;
  selectedSource = sourceKey(e);
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
  draw();
  d.focus();
}
function visibleEdge(e, cc, largest) {
  return (e.kind == 'lift' ? $('l').checked : $('p').checked) &&
    ($('d').checked || cc.get(e.from) == largest);
}
function selectedCoordinates(g, cc, largest) {
  if (X) {
    if (!$('x').checked) return [];
    const item = (C.excluded_source || []).find((e) => e.source_ref === X);
    return item?.geometry_segments?.flat() || item?.geometry || [];
  }
  const edges = g.edges.filter((e) => selectedSource && (e.source_refs || []).includes(selectedSource) && visibleEdge(e, cc, largest));
  return edges.flatMap((e) => e.geometry || []);
}
function draw() {
  let g = C.graph,
    m = C.manifest,
    v = $('map');
  v.replaceChildren();
  const excluded = C.excluded_source || [];
  const extra = (L?.endpoint_incidence || []).map((e) => e.coordinate).filter(Boolean);
  const excludedCoords = excluded.flatMap((e) => e.geometry || []);
  const cc = comps(g);
  let counts = new Map();
  for (let n of cc.values()) counts.set(n, (counts.get(n) || 0) + 1);
  let largest = [...counts].sort((a, b) => b[1] - a[1])[0]?.[0];
  const selected = selectedCoordinates(g, cc, largest);
  if (focusSelection && !selected.length) focusSelection = false;
  const allCoords = focusSelection ? selected : [
    ...g.nodes.map((n) => [n.lon, n.lat]),
    ...extra,
    ...excludedCoords,
  ];
  let allX = allCoords.map((c) => c[0]),
    allY = allCoords.map((c) => c[1]),
    a = Math.min(...allX),
    b = Math.max(...allX),
    c = Math.min(...allY),
    d = Math.max(...allY),
    cos = Math.cos((((c + d) / 2) * Math.PI) / 180);
  const minSpan = 0.0008;
  const spanX = Math.max(b - a, minSpan / Math.max(cos, 0.01));
  const spanY = Math.max(d - c, minSpan);
  const padX = spanX * 0.12;
  const padY = spanY * 0.12;
  a = (a + b) / 2 - spanX / 2 - padX;
  b = (a + b) / 2 + spanX / 2 + padX;
  c = (c + d) / 2 - spanY / 2 - padY;
  d = (c + d) / 2 + spanY / 2 + padY;
  cos = Math.cos((((c + d) / 2) * Math.PI) / 180);
  let z = Math.min(790 / ((b - a) * cos || 1), 470 / (d - c || 1)),
    f = ([x, y]) => [450 + (x - (a + b) / 2) * cos * z, 280 - (y - (c + d) / 2) * z];
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
      visibleEdge(e, cc, largest),
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
      'e ' +
        e.kind +
        (selectedSource && (e.source_refs || []).includes(selectedSource) ? ' selected' : '') +
        (cc.get(e.from) != largest ? ' dis' : ''),
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
  if (selectedSource) {
    const visible = g.edges.some(
      (e) =>
        (e.source_refs || []).includes(selectedSource) && visibleEdge(e, cc, largest),
    );
    if (!visible) {
      $('status').textContent =
        'Selected source way ' + selectedSource + ' is hidden by the current map filters.';
      $('status').classList.add('hidden-selection');
    } else {
      $('status').classList.remove('hidden-selection');
      $('status').textContent = L
        ? 'Reviewing ' + L.name + '; routing unchanged.'
        : 'Selected source way ' + selectedSource + '; visible on map.';
    }
  } else {
    $('status').classList.remove('hidden-selection');
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
  $('focus-selection').disabled = !selected.length;
  $('focus-selection').setAttribute('aria-label', selected.length ? 'Focus the selected visible geometry' : 'Focus selection unavailable because no selected geometry is visible');
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
  Q = '';
  focusSelection = false;
  selectedSource = null;
  $('trail-search').value = '';
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
  $('status').classList.remove('hidden-selection');
  updateSearch();
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
$('focus-selection').onclick = () => {
  focusSelection = true;
  draw();
};
$('fit-all').onclick = () => {
  focusSelection = false;
  draw();
};
for (let x of ['l', 'p', 'd', 'x'])
  $(x).onchange = () => {
    $('status').textContent = selectedSource
      ? 'Selection retained; checking whether the source way is visible with these filters.'
      : 'Select a segment.';
    draw();
  };
$('trail-search').oninput = () => {
  Q = $('trail-search').value;
  clearSegmentSelection();
  $('status').textContent = Q.trim() ? 'Select a search result.' : 'Select a segment.';
  updateSearch();
  draw();
};
$('trail-search-clear').onclick = () => {
  $('trail-search').value = '';
  Q = '';
  clearSegmentSelection();
  $('status').textContent = 'Select a segment.';
  updateSearch();
  draw();
  $('trail-search').focus();
};
load();

$('lift-review').onchange = () => {
  X = null;
  L = C.diagnostics?.lifts.find((l) => l.source_ref == $('lift-review').value) || null;
  E = L?.imported_edge_ids[0] || null;
  selectedSource = L?.source_ref || null;
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
