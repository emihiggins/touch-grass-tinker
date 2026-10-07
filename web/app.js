'use strict';
const $ = (id) => document.getElementById(id);
let terrainLoading = false,
  interpreting = false,
  graph = null,
  intent = null,
  generation = 0,
  terrainGeneration = 0,
  placeLabels = {},
  interpretationSource = '';
const mode = () => $('terrain').value;
function invalidate() {
  generation++;
  intent = null;
  $('make-plan').disabled = true;
  $('review').hidden = true;
  $('itinerary').hidden = true;
  $('step-inspector').hidden = true;
  draw();
}
async function api(path, body) {
  const r = await fetch(
    path,
    body
      ? {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }
      : {},
  );
  const data = await r.json();
  if (!r.ok) throw Error(data.error || 'Request failed');
  return data;
}
let mapZoom = 1,
  mapRoute = [],
  mapSteps = [],
  activeStep = -1,
  panX = 0,
  panY = 0;
const minutesLabel = (seconds) => `${Number((seconds / 60).toFixed(1))} min`;
function inspectStep() {
  const step = mapSteps[activeStep];
  $('step-inspector').hidden = !mapSteps.length;
  $('step-prev').disabled = activeStep <= 0;
  $('step-next').disabled = activeStep >= mapSteps.length - 1;
  $('step-focus').disabled = !step;
  $('map-detail').textContent = step ? `Step ${activeStep + 1}: ${step.name}` : '';
  $('step-timing').textContent = step
    ? `${minutesLabel(step.seconds)} estimated · ${minutesLabel(step.start_seconds)}–${minutesLabel(step.end_seconds)} into outing · includes ${minutesLabel(step.queue_seconds)} assumed queue. Simulation, not live timing.`
    : 'Select a step or choose Next to inspect this outing.';
}
function selectStep(index) {
  if (index < 0 || index >= mapSteps.length) return;
  activeStep = index;
  draw(mapRoute);
  document
    .querySelectorAll('#steps button')
    .forEach((b, i) => b.setAttribute('aria-pressed', String(i === index)));
  inspectStep();
}
function nextVisit(edgeId) {
  const indices = mapSteps
    .map((s, i) => (s.edge_ids.includes(edgeId) ? i : -1))
    .filter((i) => i >= 0);
  if (indices.length) selectStep(indices.find((i) => i > activeStep) ?? indices[0]);
}
$('step-prev').addEventListener('click', () => selectStep(activeStep - 1));
$('step-next').addEventListener('click', () => selectStep(activeStep + 1));
$('step-focus').addEventListener('click', () => {
  const step = mapSteps[activeStep];
  if (!step) return;
  const edges = graph.edges.filter((e) => step.edge_ids.includes(e.id));
  if (geoReady) {
    const bounds = new maplibregl.LngLatBounds();
    edges.forEach((e) => e.geometry.forEach((c) => bounds.extend(c)));
    geoMap.fitBounds(bounds, { padding: 65, maxZoom: 16, duration: 0 });
    return;
  }
  const points = edges.flatMap((e) => e.displayCoords || []);
  if (!points.length) return;
  const xs = points.map((p) => p[0]),
    ys = points.map((p) => p[1]);
  const minX = Math.min(...xs),
    maxX = Math.max(...xs),
    minY = Math.min(...ys),
    maxY = Math.max(...ys);
  mapZoom = Math.max(
    1,
    Math.min(3, 540 / Math.max(maxX - minX, 1), 320 / Math.max(maxY - minY, 1)),
  );
  panX = (350 - (minX + maxX) / 2) * mapZoom;
  panY = (240 - (minY + maxY) / 2) * mapZoom;
  draw(mapRoute);
});
function draw(selected = []) {
  if (!graph) return;
  mapRoute = selected;
  if (!selected.length) {
    mapSteps = [];
    activeStep = -1;
    $('map-detail').textContent = '';
  }
  const svg = $('map');
  svg.replaceChildren();
  const points = graph.edges.flatMap((e) => e.geometry || []);
  if (!points.length) return;
  const xs = points.map((p) => p[0]),
    ys = points.map((p) => p[1]);
  const xmin = Math.min(...xs),
    xmax = Math.max(...xs),
    ymin = Math.min(...ys),
    ymax = Math.max(...ys);
  const geographic = mode() !== 'synthetic',
    factor = geographic ? Math.cos(((ymin + ymax) * Math.PI) / 360) : 1;
  const scale = Math.min(580 / ((xmax - xmin) * factor || 1), 350 / (ymax - ymin || 1));
  const project = ([x, y]) =>
    !geographic
      ? x === 1
        ? [440, 85]
        : x === 0
          ? [350, 395]
          : [120, 275]
      : [350 + (x - (xmin + xmax) / 2) * factor * scale, 240 - (y - (ymin + ymax) / 2) * scale];
  const ns = 'http://www.w3.org/2000/svg';
  const element = (tag, attrs, parent = svg, text) => {
    const n = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (text !== undefined) n.textContent = text;
    parent.append(n);
    return n;
  };
  const defs = element('defs', {});
  const marker = element(
    'marker',
    {
      id: 'route-arrow',
      viewBox: '0 0 10 10',
      refX: 8,
      refY: 5,
      markerWidth: 5,
      markerHeight: 5,
      orient: 'auto-start-reverse',
    },
    defs,
  );
  element('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill: '#b54112' }, marker);
  const layer = element('g', {
    transform: `translate(${350 + panX} ${240 + panY}) scale(${mapZoom}) translate(-350 -240)`,
  });
  if (!geographic) {
    // Illustration only: no elevation or additional routing edges are implied.
    element(
      'path',
      {
        d: 'M 45 420 L 110 250 L 200 285 L 435 45 L 655 365 L 675 445 Z',
        fill: '#f7faf4',
        stroke: '#c8d8cd',
        'stroke-width': 1,
      },
      layer,
    );
    for (const d of [
      'M 100 360 Q 220 340 330 210 Q 405 130 470 160',
      'M 90 390 Q 250 385 375 270 Q 440 215 525 255',
      'M 230 430 Q 390 345 580 345',
    ])
      element('path', { d, fill: 'none', stroke: '#d3e0d5', 'stroke-width': 1.5 }, layer);
  }
  const ids = new Set(selected);
  for (const e of [...graph.edges].sort((a, b) => Number(ids.has(a.id)) - Number(ids.has(b.id)))) {
    if (!e.geometry?.length) continue;
    let coords = e.geometry.map(project);
    if (!geographic && coords.length === 2) {
      const bends = {
        chair: [315, 220],
        blue: [455, 250],
        red: [555, 215],
        tow: [205, 330],
        practice: [155, 390],
      };
      coords = [
        coords[0],
        bends[e.id] || [(coords[0][0] + coords[1][0]) / 2, (coords[0][1] + coords[1][1]) / 2],
        coords[1],
      ];
    }
    const active = ids.has(e.id),
      focused = mapSteps[activeStep]?.edge_ids.includes(e.id);
    e.displayCoords = coords;
    const attrs = {
      points: coords.map((p) => p.join(',')).join(' '),
      fill: 'none',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
    };
    if (active) element('polyline', { ...attrs, stroke: '#fff', 'stroke-width': 9 }, layer);
    const p = element(
      'polyline',
      {
        ...attrs,
        stroke: focused
          ? '#77218c'
          : active
            ? '#b54112'
            : e.kind === 'lift'
              ? '#203f3f'
              : e.difficulty === 'green'
                ? '#237748'
                : e.difficulty === 'red'
                  ? '#97424a'
                  : e.difficulty === 'black'
                    ? '#152b2c'
                    : '#326f9c',
        'stroke-width': active ? 5 : 3,
        ...(e.kind === 'lift' ? { 'stroke-dasharray': '6 4' } : {}),
        ...(active ? { 'marker-end': 'url(#route-arrow)' } : {}),
      },
      layer,
    );
    p.dataset.edgeId = e.id;
    if (active) p.style.cursor = 'pointer';
    if (!geographic) {
      const m = coords[Math.floor(coords.length / 2)];
      element(
        'text',
        { x: m[0] + 10, y: m[1] - 10, class: 'trail-label' },
        layer,
        `${e.name || { chair: 'Chairlift', blue: 'Blue run', red: 'Red run', tow: 'Rope tow', practice: 'Practice run' }[e.id] || e.id}`,
      );
    }
    element('title', {}, p, `${e.name || e.id}: ${e.kind}, ${e.difficulty || e.lift_type}`);
  }
  const edges = selected.map((id) => graph.edges.find((e) => e.id === id)).filter(Boolean);
  // Grouped itinerary steps retain their actual source-edge membership.
  const seen = new Set();
  mapSteps.forEach((step, i) => {
    const eid = step.edge_ids[0];
    if (seen.has(eid)) return;
    seen.add(eid);
    const e = graph.edges.find((e) => e.id === eid);
    if (!e?.geometry?.length) return;
    const [x, y] = e.displayCoords[Math.floor(e.displayCoords.length / 2)];
    element('circle', { cx: x, cy: y, r: 12, fill: '#fff', stroke: '#b54112' }, layer);
    element(
      'text',
      { x, y: y + 4, 'text-anchor': 'middle', class: 'map-number' },
      layer,
      String(i + 1),
    );
  });
  for (const [id, label] of Object.entries(placeLabels)) {
    const node = graph.nodes.find((n) => n.id === id);
    if (!node) continue;
    const [x, y] = project([node.lon, node.lat]);
    element('circle', { cx: x, cy: y, r: 4, fill: '#123b3c' }, layer);
    element(
      'text',
      { x: x + 10, y: y - 22, class: 'map-label', 'text-anchor': x > 400 ? 'end' : 'start' },
      layer,
      label,
    );
  }
  if (edges.length) {
    const start = edges[0].geometry[0],
      finish = edges.at(-1).geometry.at(-1);
    const same = start[0] === finish[0] && start[1] === finish[1];
    for (const [p, label] of same
      ? [[start, 'Start / finish']]
      : [
          [start, 'Start'],
          [finish, 'Finish'],
        ]) {
      const [x, y] = project(p);
      element('circle', { cx: x, cy: y, r: 5, fill: '#123b3c' }, layer);
      element('text', { x: x + 9, y: y + 30, class: 'map-label' }, layer, label);
    }
  }

  element(
    'text',
    { x: 24, y: 30, class: 'map-label' },
    svg,
    geographic ? '↑ N' : 'Fictional schematic',
  );
  if (geographic && mapZoom === 1) {
    const metresPerPixel = 111320 / scale;
    const distance = 10 ** Math.floor(Math.log10(metresPerPixel * 100));
    const width = distance / metresPerPixel;
    element('path', { d: `M 25 435 v 6 h ${width} v -6`, stroke: '#123b3c', fill: 'none' }, svg);
    element(
      'text',
      { x: 25, y: 459, class: 'map-label' },
      svg,
      `≈ ${distance >= 1000 ? distance / 1000 + ' km' : distance + ' m'} at fit view`,
    );
  }
  inspectStep();
  updateGeoRoute();
  $('map-zoom-label').textContent = `${Math.round(mapZoom * 100)}%`;
}
for (const [id, change] of [
  ['map-in', 0.25],
  ['map-out', -0.25],
  ['map-reset', 0],
])
  $(id).addEventListener('click', () => {
    if (!change) {
      panX = 0;
      panY = 0;
    }
    mapZoom = change ? Math.max(1, Math.min(3, mapZoom + change)) : 1;
    draw(mapRoute);
  });
window.addEventListener('beforeprint', () => {
  window.previousMapView = [mapZoom, panX, panY];
  mapZoom = 1;
  panX = 0;
  panY = 0;
  draw(mapRoute);
});
window.addEventListener('afterprint', () => {
  [mapZoom, panX, panY] = window.previousMapView || [1, 0, 0];
  draw(mapRoute);
});
function syncInterpret() {
  $('interpret').disabled = interpreting || terrainLoading || !graph;
}
async function loadTerrain() {
  closeGeo();
  $('geo-toggle').hidden = mode() !== 'alpendorf';
  $('geo-toggle').disabled = true;
  $('geo-status').textContent = '';
  $('terrain-credit').hidden = mode() !== 'alpendorf';
  invalidate();
  const gen = ++terrainGeneration;
  graph = null;
  placeLabels = {};
  mapSteps = [];
  mapRoute = [];
  activeStep = -1;
  terrainLoading = true;
  $('map').replaceChildren();
  $('map-label').textContent = 'Loading terrain…';
  $('attribution').textContent = '';
  $('retry-terrain').hidden = true;
  syncInterpret();
  $('status').textContent = 'Loading terrain…';
  try {
    const data = await api(`/api/context?terrain=${encodeURIComponent(mode())}`);
    if (gen !== terrainGeneration) return;
    graph = data.graph;
    mapZoom = 1;
    panX = 0;
    panY = 0;
    $('adapter').querySelector('[value=live]').disabled = !data.live_model_enabled;
    $('adapter').querySelector('[value=replay]').disabled = !data.recorded_model_available;
    placeLabels = Object.fromEntries(data.catalog.map((p) => [p.id, p.label]));
    draw();
    $('map-label').textContent =
      mode() === 'synthetic'
        ? 'Fictional terrain · not to scale'
        : 'Unreviewed OSM geometry · geographic';
    $('attribution').textContent =
      mode() === 'synthetic'
        ? 'Original fictional graph.'
        : '© OpenStreetMap contributors · ODbL. No current operating status.';
    $('status').textContent = interpreting
      ? 'Terrain ready. Waiting for the previous interpretation to finish; its result will be discarded.'
      : 'Ready. Review constraints before planning.';
  } catch (e) {
    if (gen === terrainGeneration) {
      $('status').textContent = 'Terrain unavailable. Retry loading before planning.';
      $('map-label').textContent = 'Terrain unavailable';
      $('retry-terrain').hidden = false;
    }
  } finally {
    if (gen === terrainGeneration) {
      terrainLoading = false;
      $('geo-toggle').disabled = !graph;
      syncInterpret();
    }
  }
}
$('retry-terrain').addEventListener('click', loadTerrain);
$('terrain').addEventListener('change', loadTerrain);
for (const id of ['minutes', 'difficulty', 'closures', 'request', 'adapter'])
  $(id).addEventListener('input', () => {
    invalidate();
    draw();
    $('status').textContent = terrainLoading
      ? 'Loading terrain…'
      : graph
        ? 'Settings changed. Review constraints again.'
        : 'Terrain unavailable. Retry loading before planning.';
  });
$('request-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (interpreting || terrainLoading || !graph) return;
  interpreting = true;
  invalidate();
  const gen = generation,
    restoreFocus = document.activeElement === $('interpret');
  $('interpret').disabled = true;
  $('status').textContent =
    $('adapter').value === 'live'
      ? 'Asking Qwen3-8B… Do not resubmit while waiting.'
      : 'Reading your request…';
  try {
    const data = await api('/api/interpret', {
      terrain: mode(),
      minutes: Number($('minutes').value),
      difficulty: $('difficulty').value,
      text: $('request').value,
      adapter: $('adapter').value,
    });
    if (gen !== generation) return;
    intent = data.intent;
    $('review-request').textContent =
      'Your request: ' + ($('request').value || '(form settings only)');
    $('review-settings').textContent =
      `Selected settings: ${$('minutes').value} minutes · maximum ${$('difficulty').value}. Check for any differences below.`;
    interpretationSource = data.notice || data.adapter;
    $('model-note').textContent = interpretationSource;
    $('constraints').replaceChildren();
    for (const [label, value] of [
      ['Maximum difficulty', intent.hard_max_difficulty],
      ['Minutes', intent.duration_minutes],
      ['Start time', intent.start_time],
      ['Vary runs', intent.prefer_variety ? 'Yes' : 'No'],
      ['Excluded lifts', intent.excluded_lift_types.join(', ') || 'None'],
      ['Prefer to avoid lifts', (intent.avoided_lift_types || []).join(', ') || 'None'],
      ['Preferred grades', intent.preferred_difficulties.join(', ') || 'None'],
      [
        'Start → finish',
        `${placeLabels[intent.start_place_id] || 'Needs clarification'} → ${placeLabels[intent.finish_place_id] || 'Needs clarification'}`,
      ],
    ]) {
      const dt = document.createElement('dt'),
        dd = document.createElement('dd');
      dt.textContent = label;
      dd.textContent = value ?? 'Needs clarification';
      $('constraints').append(dt, dd);
    }
    $('lift-checks').replaceChildren();
    for (const type of [
      'chairlift',
      'gondola',
      'cable-car',
      't-bar',
      'platter',
      'rope-tow',
      'magic-carpet',
    ]) {
      const label = document.createElement('label'),
        check = document.createElement('input');
      check.type = 'checkbox';
      check.value = type;
      check.checked = intent.excluded_lift_types.includes(type);
      check.disabled = intent.status !== 'ready';
      check.addEventListener('change', () => {
        generation++;
        $('make-plan').disabled = false;
        intent.excluded_lift_types = [...$('lift-checks').querySelectorAll('input:checked')]
          .map((x) => x.value)
          .sort();
        intent.avoided_lift_types = intent.avoided_lift_types.filter(
          (x) => !intent.excluded_lift_types.includes(x),
        );
        interpretationSource = data.notice + ' Hard exclusions corrected by the user.';
        $('model-note').textContent = interpretationSource;
        const terms = [...$('constraints').querySelectorAll('dt')];
        terms.find((x) => x.textContent === 'Excluded lifts').nextElementSibling.textContent =
          intent.excluded_lift_types.join(', ') || 'None';
        terms.find(
          (x) => x.textContent === 'Prefer to avoid lifts',
        ).nextElementSibling.textContent = intent.avoided_lift_types.join(', ') || 'None';
        $('itinerary').hidden = true;
        draw();
        $('status').textContent = 'Correction applied locally. Confirm the updated constraints.';
      });
      label.append(check, document.createTextNode(' ' + type));
      $('lift-checks').append(label);
    }
    $('review').hidden = false;
    $('make-plan').disabled = intent.status !== 'ready';
    $('parser-note').textContent =
      intent.status === 'ready'
        ? 'Check these values before confirming.'
        : `Needs review: ${[...intent.clarification_fields, ...intent.unsupported_preferences].join(', ')}. Unparsed: ${data.unparsed || 'none'}. Edit the request or use the form.`;
    $('status').textContent =
      intent.status === 'ready'
        ? 'Ready for your confirmation.'
        : 'No route requested until the interpretation is resolved.';
  } catch (err) {
    if (gen === generation) $('status').textContent = err.message;
  } finally {
    interpreting = false;
    syncInterpret();
    if (gen !== generation && graph && !terrainLoading)
      $('status').textContent = 'Settings changed. Review constraints again.';
    if (gen === generation && restoreFocus) $('interpret').focus({ preventScroll: true });
  }
});
$('make-plan').addEventListener('click', async () => {
  if (!intent) return;
  const gen = generation,
    restoreFocus = document.activeElement === $('make-plan');
  $('make-plan').disabled = true;
  $('status').textContent = 'Searching a simulated outing…';
  try {
    const r = await api('/api/plan', { terrain: mode(), intent, closures: $('closures').value });
    if (gen !== generation) return;
    if (r.status !== 'ok') {
      $('itinerary').hidden = true;
      draw();
      $('status').textContent =
        r.status === 'no_route'
          ? 'No outing meets these constraints in this scenario.'
          : r.status === 'search_limit'
            ? 'Search reached its limit; this does not prove no route exists.'
            : `Planner: ${r.status}`;
      return;
    }
    mapSteps = r.steps;
    activeStep = -1;
    draw(r.route.edge_ids);
    $('itinerary').hidden = false;
    $('route-source').textContent = interpretationSource;
    $('route-constraints').replaceChildren(
      ...[...$('constraints').children].map((x) => x.cloneNode(true)),
    );
    $('summary').textContent =
      `${Math.round(r.route.total_seconds / 60)} estimated minutes · ${r.steps.length} itinerary steps · simulation only`;
    $('tradeoffs').textContent = (r.preference_tradeoffs || [])
      .map((t) => `${t.lift_types.join(', ')}: ${t.message}`)
      .join(' ');
    $('steps').replaceChildren();
    for (const step of r.steps) {
      const li = document.createElement('li');
      const button = document.createElement('button');
      button.className = 'step-select';
      button.setAttribute('aria-pressed', 'false');
      button.addEventListener('click', () => selectStep(r.steps.indexOf(step)));
      button.textContent = `${step.kind === 'lift' ? 'Lift' : 'Piste'}: ${step.name}${step.difficulty ? ' · ' + step.difficulty : ''} · ${minutesLabel(step.seconds)} estimated`;
      li.append(button);
      $('steps').append(li);
    }
    $('status').textContent =
      'Simulated route passed the independent validator. No real-world access claim.';
  } catch (e) {
    if (gen === generation) $('status').textContent = e.message;
  } finally {
    if (gen === generation) {
      $('make-plan').disabled = false;
      if (restoreFocus) $('make-plan').focus({ preventScroll: true });
    }
  }
});
$('load-example').addEventListener('click', () => {
  $('terrain').value = 'synthetic';
  $('minutes').value = '60';
  $('difficulty').value = 'blue';
  $('closures').value = 'none';
  $('request').value = 'Only blues, no drag lifts, 45 minutes';
  loadTerrain();
});
$('print').addEventListener('click', () => window.print());
$('save-itinerary').addEventListener('click', () => {
  if ($('itinerary').hidden || !mapSteps.length) return;
  const constraints = [...$('route-constraints').querySelectorAll('dt')].map(
    (dt) => `${dt.textContent}: ${dt.nextElementSibling.textContent}`,
  );
  const lines = [
    'LIFT / LAP — SIMULATED ITINERARY',
    'Simulation only. Not navigation or current resort conditions.',
    'Travel and queue times are assumptions; check real access and closures independently.',
    '',
    `Terrain: ${$('terrain').selectedOptions[0].textContent}`,
    $('summary').textContent,
    $('route-source').textContent,
    '',
    'APPROVED CONSTRAINTS',
    ...constraints,
    '',
    'STEPS',
    ...mapSteps.map(
      (s, i) =>
        `${i + 1}. ${s.kind === 'lift' ? 'Lift' : 'Piste'}: ${s.name}${s.difficulty ? ' / ' + s.difficulty : ''} — ${minutesLabel(s.seconds)} estimated (${minutesLabel(s.start_seconds)}–${minutesLabel(s.end_seconds)} elapsed; ${minutesLabel(s.queue_seconds)} assumed queue)`,
    ),
    '',
    $('tradeoffs').textContent,
    $('attribution').textContent,
  ];
  const url = URL.createObjectURL(
    new Blob([lines.join('\n') + '\n'], { type: 'text/plain;charset=utf-8' }),
  );
  const link = document.createElement('a');
  link.href = url;
  link.download = 'liftlap-simulated-itinerary.txt';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});

let drag = null;
$('map').addEventListener('pointerdown', (e) => {
  if (e.button !== 0) return;
  drag = { x: e.clientX, y: e.clientY, px: panX, py: panY, edge: e.target.dataset.edgeId };
  $('map').setPointerCapture(e.pointerId);
});
$('map').addEventListener('pointermove', (e) => {
  if (!drag) return;
  const ratio = 700 / $('map').getBoundingClientRect().width;
  panX = Math.max(-700, Math.min(700, drag.px + (e.clientX - drag.x) * ratio));
  panY = Math.max(-480, Math.min(480, drag.py + (e.clientY - drag.y) * ratio));
  if (Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) > 4) draw(mapRoute);
});
$('map').addEventListener('pointerup', (e) => {
  if (drag?.edge && Math.abs(e.clientX - drag.x) + Math.abs(e.clientY - drag.y) < 5) {
    nextVisit(drag.edge);
  }
  drag = null;
});
$('map').addEventListener('pointercancel', () => {
  drag = null;
});
$('map').addEventListener('keydown', (e) => {
  const delta = { ArrowLeft: [40, 0], ArrowRight: [-40, 0], ArrowUp: [0, 40], ArrowDown: [0, -40] }[
    e.key
  ];
  if (!delta) return;
  e.preventDefault();
  panX = Math.max(-700, Math.min(700, panX + delta[0]));
  panY = Math.max(-480, Math.min(480, panY + delta[1]));
  draw(mapRoute);
});
let geoMap = null,
  geoReady = false;
function updateGeoRoute() {
  if (!geoReady) return;
  geoMap.setFilter('outing', ['in', ['get', 'id'], ['literal', mapRoute]]);
  geoMap.setFilter('focused', [
    'in',
    ['get', 'id'],
    ['literal', mapSteps[activeStep]?.edge_ids || []],
  ]);
}
function closeGeo() {
  $('map-heading').textContent = 'Mountain sketch';
  document.querySelector('.map-panel').classList.remove('geographic-active');
  $('geo-toggle').setAttribute('aria-pressed', 'false');
  if (geoMap) geoMap.remove();
  geoMap = null;
  geoReady = false;
  $('geo-map').hidden = true;
  $('geo-toggle').textContent = 'Open geographic map';
}
$('geo-toggle').addEventListener('click', () => {
  if (geoMap) {
    closeGeo();
    return;
  }
  if (mode() !== 'alpendorf' || !graph) return;
  try {
    if (!window.maplibregl) throw Error('Renderer unavailable');
    maplibregl.setWorkerUrl('/maplibre-gl-csp-worker.js');
    $('geo-map').hidden = false;
    geoMap = new maplibregl.Map({
      container: 'geo-map',
      attributionControl: false,
      style: {
        version: 8,
        sources: {},
        layers: [
          { id: 'background', type: 'background', paint: { 'background-color': '#e4ebe6' } },
        ],
      },
      center: [13.235, 47.31],
      zoom: 13,
      pitch: 0,
    });
    geoMap.addControl(new maplibregl.NavigationControl({ showCompass: true }));
    geoMap.on('load', () => {
      if (!geoMap) return;
      const features = graph.edges
        .filter((e) => e.geometry?.length > 1)
        .map((e) => ({
          type: 'Feature',
          properties: {
            id: e.id,
            name: e.name || e.id,
            kind: e.kind,
            difficulty: e.difficulty || '',
          },
          geometry: { type: 'LineString', coordinates: e.geometry },
        }));
      geoMap.addSource('elevation', {
        type: 'raster-dem',
        tiles: [location.origin + '/terrain/12/2198/1435.png'],
        tileSize: 256,
        minzoom: 12,
        maxzoom: 12,
        bounds: [13.18359375, 47.27922900257082, 13.271484375, 47.338822694822],
        encoding: 'terrarium',
      });
      geoMap.addLayer({
        id: 'hillshade',
        type: 'hillshade',
        source: 'elevation',
        paint: {
          'hillshade-exaggeration': 0.45,
          'hillshade-shadow-color': '#657360',
          'hillshade-highlight-color': '#fffef5',
          'hillshade-accent-color': '#a8b49c',
        },
      });
      geoMap.addSource('terrain', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features },
      });
      geoMap.addLayer({
        id: 'pistes',
        type: 'line',
        source: 'terrain',
        filter: ['==', ['get', 'kind'], 'piste'],
        paint: {
          'line-color': [
            'match',
            ['get', 'difficulty'],
            'green',
            '#237748',
            'red',
            '#97424a',
            'black',
            '#152b2c',
            '#326f9c',
          ],
          'line-width': 3,
        },
      });
      geoMap.addLayer({
        id: 'lifts',
        type: 'line',
        source: 'terrain',
        filter: ['==', ['get', 'kind'], 'lift'],
        paint: { 'line-color': '#203f3f', 'line-width': 3, 'line-dasharray': [2, 2] },
      });
      for (const [id, color, width] of [
        ['outing', '#b54112', 6],
        ['focused', '#77218c', 8],
      ])
        geoMap.addLayer({
          id,
          type: 'line',
          source: 'terrain',
          filter: ['in', ['get', 'id'], ['literal', []]],
          paint: { 'line-color': color, 'line-width': width },
        });
      const bounds = new maplibregl.LngLatBounds();
      features.forEach((f) => f.geometry.coordinates.forEach((c) => bounds.extend(c)));
      geoMap.fitBounds(bounds, { padding: 35, duration: 0 });
      geoReady = true;
      updateGeoRoute();
      for (const [id, label] of Object.entries(placeLabels)) {
        const node = graph.nodes.find((n) => n.id === id);
        if (!node) continue;
        const el = document.createElement('span');
        el.className = 'station-marker';
        el.setAttribute('role', 'img');
        el.setAttribute('aria-label', label);
        el.textContent = label;
        new maplibregl.Marker({ element: el, anchor: 'bottom' })
          .setLngLat([node.lon, node.lat])
          .addTo(geoMap);
      }

      geoMap.on('click', (e) => {
        const f = geoMap.queryRenderedFeatures(e.point, {
          layers: ['focused', 'outing', 'lifts', 'pistes'],
        })[0];
        if (!f) return;
        if (mapSteps.some((s) => s.edge_ids.includes(f.properties.id))) {
          nextVisit(f.properties.id);
        } else {
          activeStep = -1;
          draw(mapRoute);
          document
            .querySelectorAll('#steps button')
            .forEach((b) => b.setAttribute('aria-pressed', 'false'));
          $('step-inspector').hidden = false;
          $('step-timing').textContent = 'This segment is not part of the current itinerary.';
          $('map-detail').textContent =
            `${f.properties.name} · ${f.properties.kind} · unreviewed OSM geometry`;
        }
      });
    });
    geoMap.on('error', (e) => {
      if (e.sourceId === 'elevation') {
        if (geoMap.getLayer('hillshade')) geoMap.removeLayer('hillshade');
        $('geo-status').textContent = 'Elevation unavailable; trail geometry remains visible.';
        return;
      }
      $('geo-status').textContent = 'Geographic renderer failed; use the offline sketch below.';
      closeGeo();
    });
    $('map-heading').textContent = 'Geographic mountain view';
    document.querySelector('.map-panel').classList.add('geographic-active');
    $('geo-toggle').setAttribute('aria-pressed', 'true');
    geoMap.resize();
    $('geo-toggle').textContent = 'Switch to sketch';
    $('geo-status').textContent =
      'Local Alpendorf geometry · © OpenStreetMap contributors, ODbL · local hillshade for orientation only · no live conditions.';
  } catch (e) {
    closeGeo();
    $('geo-status').textContent =
      'Geographic renderer unavailable; the offline sketch remains available.';
  }
});

loadTerrain();
