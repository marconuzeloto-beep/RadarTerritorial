const API_BASE = 'http://localhost:8000/coverage';

// ══════════════════════════════════════════════════════════════════
//  TAB NAVIGATION
// ══════════════════════════════════════════════════════════════════
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
    btn.classList.add('active');
    document.getElementById(`tab-${btn.dataset.tab}`).classList.remove('hidden');
  });
});

// ══════════════════════════════════════════════════════════════════
//  TAG INPUT FACTORY  (reused for both tabs)
// ══════════════════════════════════════════════════════════════════
function makeTagInput(wrapperId, listId, inputId) {
  const tags = [];
  const wrapper = document.getElementById(wrapperId);
  const list    = document.getElementById(listId);
  const input   = document.getElementById(inputId);

  function addTag(value) {
    const name = value.trim();
    if (!name) return;
    if (tags.map(t => t.toLowerCase()).includes(name.toLowerCase())) return;
    tags.push(name);
    render();
  }

  function removeTag(i) {
    tags.splice(i, 1);
    render();
  }

  function render() {
    list.innerHTML = '';
    tags.forEach((tag, i) => {
      const el = document.createElement('span');
      el.className = 'tag';
      el.innerHTML = `${escapeHtml(tag)}<button class="tag-remove" title="Remover">&times;</button>`;
      el.querySelector('.tag-remove').addEventListener('click', () => removeTag(i));
      list.appendChild(el);
    });
  }

  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(input.value.replace(/,/g, ''));
      input.value = '';
    } else if (e.key === 'Backspace' && input.value === '' && tags.length) {
      removeTag(tags.length - 1);
    }
  });

  input.addEventListener('blur', () => {
    if (input.value.trim()) { addTag(input.value); input.value = ''; }
  });

  wrapper.addEventListener('click', () => input.focus());

  return { getTags: () => [...tags] };
}

const radiusTagInput   = makeTagInput('tags-wrapper',      'tags-list',      'cities-input');
const polygonTagInput  = makeTagInput('poly-tags-wrapper', 'poly-tags-list', 'poly-cities-input');
const logisticsTagInput = makeTagInput('log-tags-wrapper', 'log-tags-list', 'log-cities-input');

// ══════════════════════════════════════════════════════════════════
//  TAB 1 — RADIUS
// ══════════════════════════════════════════════════════════════════
const radiusSlider   = document.getElementById('radius-slider');
const radiusInput    = document.getElementById('radius-input');
const analyzeBtn     = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const loadingEl      = document.getElementById('loading');
const errorMsg       = document.getElementById('error-msg');
const statAnalyzed   = document.getElementById('stat-analyzed');
const statDiscovered = document.getElementById('stat-discovered');
const statNotfound   = document.getElementById('stat-notfound');
const statNotfoundCard = document.getElementById('stat-notfound-card');
const notfoundAlert  = document.getElementById('notfound-alert');
const coveredList    = document.getElementById('covered-list');
const discoveredList = document.getElementById('discovered-list');
const searchInput    = document.getElementById('search-discovered');

radiusSlider.addEventListener('input', () => { radiusInput.value = radiusSlider.value; });
radiusInput.addEventListener('input', () => {
  const v = Math.min(5000, Math.max(1, parseInt(radiusInput.value) || 1));
  radiusSlider.value = Math.min(500, v);
});

analyzeBtn.addEventListener('click', async () => {
  const cities = radiusTagInput.getTags();
  if (!cities.length) { showError(errorMsg, 'Adicione pelo menos uma cidade.'); return; }
  const radius = parseFloat(radiusInput.value);
  if (!radius || radius <= 0) { showError(errorMsg, 'Informe um raio válido.'); return; }

  setLoading(loadingEl, analyzeBtn, true);
  hideEl(errorMsg);
  hideEl(resultsSection);

  try {
    const data = await post(`${API_BASE}/radius`, { cities, radius_km: radius });
    renderRadiusResults(data);
  } catch (err) {
    showError(errorMsg, `Erro ao consultar a API: ${err.message}`);
  } finally {
    setLoading(loadingEl, analyzeBtn, false);
  }
});

let allDiscovered = [];

function renderRadiusResults(data) {
  statAnalyzed.textContent   = data.analyzed_count;
  statDiscovered.textContent = data.discovered_count;

  if (data.not_found?.length) {
    statNotfound.textContent = data.not_found.length;
    statNotfoundCard.style.display = '';
    notfoundAlert.textContent = `Não encontradas: ${data.not_found.join(', ')}`;
    notfoundAlert.classList.remove('hidden');
  } else {
    statNotfoundCard.style.display = 'none';
    notfoundAlert.classList.add('hidden');
  }

  coveredList.innerHTML = '';
  data.covered_cities.forEach(c => coveredList.appendChild(makeCityItem(c)));

  allDiscovered = data.discovered_cities;
  renderDiscoveredList(allDiscovered);

  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderDiscoveredList(list) {
  discoveredList.innerHTML = '';
  if (!list.length) {
    discoveredList.appendChild(emptyMsg('Nenhum município encontrado neste raio.'));
    return;
  }
  list.forEach(c => discoveredList.appendChild(makeCityItem(c, true)));
}

searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  renderDiscoveredList(
    q ? allDiscovered.filter(c =>
      c.nome.toLowerCase().includes(q) || c.uf.toLowerCase().includes(q)
    ) : allDiscovered
  );
});

// ══════════════════════════════════════════════════════════════════
//  TAB 2 — POLYGON
// ══════════════════════════════════════════════════════════════════
const bufferSlider      = document.getElementById('buffer-slider');
const bufferInput       = document.getElementById('buffer-input');
const polyAnalyzeBtn    = document.getElementById('poly-analyze-btn');
const polyResultsSec    = document.getElementById('poly-results-section');
const polyLoadingEl     = document.getElementById('poly-loading');
const polyErrorMsg      = document.getElementById('poly-error-msg');
const polyStatOrigin    = document.getElementById('poly-stat-origin');
const polyStatFound     = document.getElementById('poly-stat-found');
const polyStatArea      = document.getElementById('poly-stat-area');
const polyStatNotfound  = document.getElementById('poly-stat-notfound');
const polyStatNFCard    = document.getElementById('poly-stat-notfound-card');
const polyNotfoundAlert = document.getElementById('poly-notfound-alert');
const polyOriginList    = document.getElementById('poly-origin-list');
const polyFoundList     = document.getElementById('poly-found-list');
const polySearchInput   = document.getElementById('poly-search');

bufferSlider.addEventListener('input', () => { bufferInput.value = bufferSlider.value; });
bufferInput.addEventListener('input', () => {
  const v = Math.min(2000, Math.max(1, parseInt(bufferInput.value) || 1));
  bufferSlider.value = Math.min(200, v);
});

let leafletMap = null;
let allPolyFound = [];

polyAnalyzeBtn.addEventListener('click', async () => {
  const cities = polygonTagInput.getTags();
  if (!cities.length) { showError(polyErrorMsg, 'Adicione pelo menos uma cidade.'); return; }
  const buffer = parseFloat(bufferInput.value);
  if (!buffer || buffer <= 0) { showError(polyErrorMsg, 'Informe um valor de expansão válido.'); return; }

  setLoading(polyLoadingEl, polyAnalyzeBtn, true);
  hideEl(polyErrorMsg);
  hideEl(polyResultsSec);

  try {
    const data = await post(`${API_BASE}/polygon`, { cities, buffer_km: buffer });
    renderPolygonResults(data);
  } catch (err) {
    showError(polyErrorMsg, `Erro ao consultar a API: ${err.message}`);
  } finally {
    setLoading(polyLoadingEl, polyAnalyzeBtn, false);
  }
});

function renderPolygonResults(data) {
  polyStatOrigin.textContent = data.origin_cities.length;
  polyStatFound.textContent  = data.cities_found.length;
  polyStatArea.textContent   = formatArea(data.polygon_area_km2);

  if (data.not_found?.length) {
    polyStatNotfound.textContent = data.not_found.length;
    polyStatNFCard.style.display = '';
    polyNotfoundAlert.textContent = `Não encontradas: ${data.not_found.join(', ')}`;
    polyNotfoundAlert.classList.remove('hidden');
  } else {
    polyStatNFCard.style.display = 'none';
    polyNotfoundAlert.classList.add('hidden');
  }

  polyOriginList.innerHTML = '';
  data.origin_cities.forEach(c => polyOriginList.appendChild(makeCityItem(c)));

  allPolyFound = data.cities_found;
  renderPolyFoundList(allPolyFound);

  polyResultsSec.classList.remove('hidden');
  polyResultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Map needs DOM to be visible before init
  requestAnimationFrame(() => buildMap(data));
}

function renderPolyFoundList(list) {
  polyFoundList.innerHTML = '';
  if (!list.length) {
    polyFoundList.appendChild(emptyMsg('Nenhum município encontrado na área.'));
    return;
  }
  list.forEach(c => polyFoundList.appendChild(makeCityItem(c)));
}

polySearchInput.addEventListener('input', () => {
  const q = polySearchInput.value.trim().toLowerCase();
  renderPolyFoundList(
    q ? allPolyFound.filter(c =>
      c.nome.toLowerCase().includes(q) || c.uf.toLowerCase().includes(q)
    ) : allPolyFound
  );
});

// ── Leaflet map ────────────────────────────────────────────────────
function buildMap(data) {
  if (leafletMap) {
    leafletMap.remove();
    leafletMap = null;
  }

  leafletMap = L.map('coverage-map', { zoomControl: true });

  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
    maxZoom: 19,
  }).addTo(leafletMap);

  const bounds = L.latLngBounds([]);

  // Polygon layer
  if (data.polygon_geojson) {
    const polygonLayer = L.geoJSON(data.polygon_geojson, {
      style: {
        color: '#a78bfa',
        weight: 2,
        opacity: 0.9,
        fillColor: '#a78bfa',
        fillOpacity: 0.15,
      },
    }).addTo(leafletMap);
    polygonLayer.getBounds && bounds.extend(polygonLayer.getBounds());
  }

  // Discovered cities — green markers
  data.cities_found.forEach(c => {
    const marker = L.circleMarker([c.latitude, c.longitude], {
      radius: 6,
      color: '#34d399',
      fillColor: '#34d399',
      fillOpacity: 0.85,
      weight: 1.5,
    }).addTo(leafletMap);
    marker.bindTooltip(`<b>${c.nome}</b> – ${c.uf}`, { sticky: true });
    bounds.extend([c.latitude, c.longitude]);
  });

  // Origin cities — blue markers (on top)
  data.origin_cities.forEach(c => {
    const marker = L.circleMarker([c.latitude, c.longitude], {
      radius: 9,
      color: '#fff',
      fillColor: '#4f8ef7',
      fillOpacity: 1,
      weight: 2,
    }).addTo(leafletMap);
    marker.bindTooltip(`<b>${c.nome}</b> – ${c.uf}<br><small>Origem</small>`, { sticky: true });
    bounds.extend([c.latitude, c.longitude]);
  });

  if (bounds.isValid()) {
    leafletMap.fitBounds(bounds, { padding: [30, 30] });
  } else {
    leafletMap.setView([-14.235, -51.925], 4);
  }
}

// ══════════════════════════════════════════════════════════════════
//  TAB 3 — LOGISTICS
// ══════════════════════════════════════════════════════════════════
const logAnalyzeBtn   = document.getElementById('log-analyze-btn');
const logResultsSec   = document.getElementById('log-results-section');
const logLoadingEl    = document.getElementById('log-loading');
const logErrorMsg     = document.getElementById('log-error-msg');
const logStatOrigin   = document.getElementById('log-stat-origin');
const logStatCount    = document.getElementById('log-stat-count');
const logStatPop      = document.getElementById('log-stat-pop');
const logStatDist     = document.getElementById('log-stat-dist');
const logStatTime     = document.getElementById('log-stat-time');
const logStatNFCard   = document.getElementById('log-stat-nf-card');
const logStatNF       = document.getElementById('log-stat-notfound');
const logNFAlert      = document.getElementById('log-notfound-alert');
const logOriginList   = document.getElementById('log-origin-list');
const logFoundList    = document.getElementById('log-found-list');
const logSearchInput  = document.getElementById('log-search');
const logTimeGroup    = document.getElementById('log-time-group');
const logDistGroup    = document.getElementById('log-dist-group');
const logTimeSlider   = document.getElementById('log-time-slider');
const logTimeInput    = document.getElementById('log-time-input');
const logDistSlider   = document.getElementById('log-dist-slider');
const logDistInput    = document.getElementById('log-dist-input');
const modeTimeBtnEl   = document.getElementById('mode-time-btn');
const modeDistBtnEl   = document.getElementById('mode-dist-btn');

let logMode = 'time'; // 'time' | 'distance'

// ── Mode toggle ────────────────────────────────────────────────────
[modeTimeBtnEl, modeDistBtnEl].forEach(btn => {
  btn.addEventListener('click', () => {
    logMode = btn.dataset.mode;
    modeTimeBtnEl.classList.toggle('active', logMode === 'time');
    modeDistBtnEl.classList.toggle('active', logMode === 'distance');
    logTimeGroup.classList.toggle('hidden', logMode !== 'time');
    logDistGroup.classList.toggle('hidden', logMode !== 'distance');
  });
});

// ── Sliders ────────────────────────────────────────────────────────
logTimeSlider.addEventListener('input', () => { logTimeInput.value = logTimeSlider.value; });
logTimeInput.addEventListener('input', () => {
  logTimeSlider.value = Math.min(360, Math.max(15, parseInt(logTimeInput.value) || 15));
});
logDistSlider.addEventListener('input', () => { logDistInput.value = logDistSlider.value; });
logDistInput.addEventListener('input', () => {
  logDistSlider.value = Math.min(500, Math.max(20, parseInt(logDistInput.value) || 20));
});

// ── Analyze ────────────────────────────────────────────────────────
logAnalyzeBtn.addEventListener('click', async () => {
  const cities = logisticsTagInput.getTags();
  if (!cities.length) { showError(logErrorMsg, 'Adicione pelo menos uma cidade.'); return; }

  const body = { cities };
  if (logMode === 'time') {
    const v = parseFloat(logTimeInput.value);
    if (!v || v <= 0) { showError(logErrorMsg, 'Informe um tempo válido.'); return; }
    body.max_travel_minutes = v;
  } else {
    const v = parseFloat(logDistInput.value);
    if (!v || v <= 0) { showError(logErrorMsg, 'Informe uma distância válida.'); return; }
    body.max_distance_km = v;
  }

  setLoading(logLoadingEl, logAnalyzeBtn, true);
  hideEl(logErrorMsg);
  hideEl(logResultsSec);

  try {
    const data = await post(`${API_BASE}/logistics`, body);
    renderLogisticsResults(data);
  } catch (err) {
    showError(logErrorMsg, `Erro: ${err.message}`);
  } finally {
    setLoading(logLoadingEl, logAnalyzeBtn, false);
  }
});

let logisticsMap = null;
let allLogFound  = [];

function renderLogisticsResults(data) {
  logStatOrigin.textContent = data.origin_cities.length;
  logStatCount.textContent  = data.cities_count;
  logStatPop.textContent    = formatPop(data.total_population);
  logStatDist.textContent   = data.avg_distance_km;
  logStatTime.textContent   = data.avg_time_minutes;

  if (data.not_found?.length) {
    logStatNF.textContent = data.not_found.length;
    logStatNFCard.style.display = '';
    logNFAlert.textContent = `Não encontradas: ${data.not_found.join(', ')}`;
    logNFAlert.classList.remove('hidden');
  } else {
    logStatNFCard.style.display = 'none';
    logNFAlert.classList.add('hidden');
  }

  logOriginList.innerHTML = '';
  data.origin_cities.forEach(c => logOriginList.appendChild(makeLogCityItem(c, false)));

  allLogFound = data.reachable_cities;
  renderLogFoundList(allLogFound);

  logResultsSec.classList.remove('hidden');
  logResultsSec.scrollIntoView({ behavior: 'smooth', block: 'start' });

  requestAnimationFrame(() => buildLogisticsMap(data));
}

function renderLogFoundList(list) {
  logFoundList.innerHTML = '';
  if (!list.length) {
    logFoundList.appendChild(emptyMsg('Nenhum município alcançável neste critério.'));
    return;
  }
  list.forEach(c => logFoundList.appendChild(makeLogCityItem(c, true)));
}

logSearchInput.addEventListener('input', () => {
  const q = logSearchInput.value.trim().toLowerCase();
  renderLogFoundList(
    q ? allLogFound.filter(c =>
      c.nome.toLowerCase().includes(q) || c.uf.toLowerCase().includes(q)
    ) : allLogFound
  );
});

function makeLogCityItem(city, showMeta = false) {
  const el = document.createElement('div');
  el.className = 'city-item';
  const metaHtml = showMeta ? `
    <span class="city-item-meta">
      ${city.estimated_distance_km != null
        ? `<span class="city-dist">${city.estimated_distance_km} km</span>`
        : ''}
      ${city.estimated_time_minutes != null
        ? `<span class="city-item-pop" title="Tempo estimado">${city.estimated_time_minutes} min</span>`
        : ''}
    </span>` : '';
  const popHtml = city.populacao
    ? `<span class="city-item-pop" title="População">${formatPop(city.populacao)}</span>`
    : '';
  el.innerHTML = `
    <span class="city-name">${escapeHtml(city.nome)}</span>
    <span class="city-uf">${escapeHtml(city.uf)}</span>
    ${popHtml}
    ${metaHtml}
  `;
  return el;
}

// ── Logistics Leaflet map ──────────────────────────────────────────
function buildLogisticsMap(data) {
  if (logisticsMap) { logisticsMap.remove(); logisticsMap = null; }

  logisticsMap = L.map('logistics-map', { zoomControl: true });
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO',
    maxZoom: 19,
  }).addTo(logisticsMap);

  const bounds = L.latLngBounds([]);

  // Isochrone polygon — orange
  if (data.isochrone_geojson) {
    const isoLayer = L.geoJSON(data.isochrone_geojson, {
      style: {
        color: '#fb923c',
        weight: 2,
        opacity: 0.85,
        fillColor: '#fb923c',
        fillOpacity: 0.12,
      },
    }).addTo(logisticsMap);
    if (isoLayer.getBounds().isValid()) bounds.extend(isoLayer.getBounds());
  }

  // Reachable cities — green
  data.reachable_cities.forEach(c => {
    const m = L.circleMarker([c.latitude, c.longitude], {
      radius: 6,
      color: '#34d399',
      fillColor: '#34d399',
      fillOpacity: 0.85,
      weight: 1.5,
    }).addTo(logisticsMap);
    m.bindTooltip(
      `<b>${c.nome}</b> – ${c.uf}<br>` +
      `&#128100; ${formatPop(c.populacao)}<br>` +
      `&#128650; ~${c.estimated_distance_km} km · ${c.estimated_time_minutes} min`,
      { sticky: true }
    );
    bounds.extend([c.latitude, c.longitude]);
  });

  // Origin cities — blue (on top)
  data.origin_cities.forEach(c => {
    const m = L.circleMarker([c.latitude, c.longitude], {
      radius: 9,
      color: '#fff',
      fillColor: '#4f8ef7',
      fillOpacity: 1,
      weight: 2,
    }).addTo(logisticsMap);
    m.bindTooltip(`<b>${c.nome}</b> – ${c.uf}<br><small>Origem</small>`, { sticky: true });
    bounds.extend([c.latitude, c.longitude]);
  });

  if (bounds.isValid()) {
    logisticsMap.fitBounds(bounds, { padding: [30, 30] });
  } else {
    logisticsMap.setView([-14.235, -51.925], 4);
  }
}

// ══════════════════════════════════════════════════════════════════
//  SHARED HELPERS
// ══════════════════════════════════════════════════════════════════
async function post(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function makeCityItem(city, showDist = false) {
  const el = document.createElement('div');
  el.className = 'city-item';
  el.innerHTML = `
    <span class="city-name">${escapeHtml(city.nome)}</span>
    <span class="city-uf">${escapeHtml(city.uf)}</span>
    ${showDist && city.distance_km != null
      ? `<span class="city-dist">${Number(city.distance_km).toFixed(1)} km</span>`
      : ''}
  `;
  return el;
}

function emptyMsg(text) {
  const p = document.createElement('p');
  p.style.cssText = 'color:var(--text-muted);font-size:13px;padding:8px 0';
  p.textContent = text;
  return p;
}

function setLoading(loadingEl, btn, on) {
  loadingEl.classList.toggle('hidden', !on);
  btn.disabled = on;
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}

function hideEl(el) { el.classList.add('hidden'); }

function formatArea(km2) {
  if (km2 >= 1000) return `${(km2 / 1000).toFixed(1)} mil`;
  return km2.toFixed(0);
}

function formatPop(n) {
  if (!n) return '–';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(0)}k`;
  return String(n);
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
