const API_URL = 'http://localhost:8000/coverage/radius';

// ── State ──────────────────────────────────────────────────────────────────
const state = { tags: [] };

// ── DOM refs ───────────────────────────────────────────────────────────────
const tagsWrapper    = document.getElementById('tags-wrapper');
const tagsList       = document.getElementById('tags-list');
const citiesInput    = document.getElementById('cities-input');
const radiusSlider   = document.getElementById('radius-slider');
const radiusInput    = document.getElementById('radius-input');
const analyzeBtn     = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const loading        = document.getElementById('loading');
const errorMsg       = document.getElementById('error-msg');
const statAnalyzed   = document.getElementById('stat-analyzed');
const statDiscovered = document.getElementById('stat-discovered');
const statNotfound   = document.getElementById('stat-notfound');
const statNotfoundCard = document.getElementById('stat-notfound-card');
const notfoundAlert  = document.getElementById('notfound-alert');
const coveredList    = document.getElementById('covered-list');
const discoveredList = document.getElementById('discovered-list');
const searchInput    = document.getElementById('search-discovered');

// ── Tags logic ─────────────────────────────────────────────────────────────
function addTag(value) {
  const name = value.trim();
  if (!name) return;
  if (state.tags.map(t => t.toLowerCase()).includes(name.toLowerCase())) return;
  state.tags.push(name);
  renderTags();
}

function removeTag(index) {
  state.tags.splice(index, 1);
  renderTags();
}

function renderTags() {
  tagsList.innerHTML = '';
  state.tags.forEach((tag, i) => {
    const el = document.createElement('span');
    el.className = 'tag';
    el.innerHTML = `${escapeHtml(tag)}<button class="tag-remove" title="Remover">&times;</button>`;
    el.querySelector('.tag-remove').addEventListener('click', () => removeTag(i));
    tagsList.appendChild(el);
  });
}

citiesInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault();
    addTag(citiesInput.value.replace(/,/g, ''));
    citiesInput.value = '';
  } else if (e.key === 'Backspace' && citiesInput.value === '' && state.tags.length) {
    removeTag(state.tags.length - 1);
  }
});

citiesInput.addEventListener('blur', () => {
  if (citiesInput.value.trim()) {
    addTag(citiesInput.value);
    citiesInput.value = '';
  }
});

tagsWrapper.addEventListener('click', () => citiesInput.focus());

// ── Radius sync ────────────────────────────────────────────────────────────
radiusSlider.addEventListener('input', () => { radiusInput.value = radiusSlider.value; });
radiusInput.addEventListener('input', () => {
  const v = Math.min(5000, Math.max(1, parseInt(radiusInput.value) || 1));
  radiusSlider.value = Math.min(500, v);
});

// ── Analyze ────────────────────────────────────────────────────────────────
analyzeBtn.addEventListener('click', analyze);

async function analyze() {
  if (state.tags.length === 0) {
    showError('Adicione pelo menos uma cidade antes de analisar.');
    return;
  }

  const radius = parseFloat(radiusInput.value);
  if (!radius || radius <= 0) {
    showError('Informe um raio válido em quilômetros.');
    return;
  }

  setLoading(true);
  hideError();
  resultsSection.classList.add('hidden');

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cities: state.tags, radius_km: radius }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Erro ${response.status}`);
    }

    const data = await response.json();
    renderResults(data);
  } catch (err) {
    showError(`Falha ao consultar a API: ${err.message}`);
  } finally {
    setLoading(false);
  }
}

// ── Render results ─────────────────────────────────────────────────────────
let allDiscovered = [];

function renderResults(data) {
  statAnalyzed.textContent   = data.analyzed_count;
  statDiscovered.textContent = data.discovered_count;

  if (data.not_found && data.not_found.length > 0) {
    statNotfound.textContent = data.not_found.length;
    statNotfoundCard.style.display = '';
    notfoundAlert.textContent = `Cidades não encontradas no banco: ${data.not_found.join(', ')}`;
    notfoundAlert.classList.remove('hidden');
  } else {
    statNotfoundCard.style.display = 'none';
    notfoundAlert.classList.add('hidden');
  }

  coveredList.innerHTML = '';
  data.covered_cities.forEach(c => {
    coveredList.appendChild(makeCityItem(c));
  });

  allDiscovered = data.discovered_cities;
  renderDiscovered(allDiscovered);

  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderDiscovered(list) {
  discoveredList.innerHTML = '';
  if (list.length === 0) {
    const empty = document.createElement('p');
    empty.style.cssText = 'color:var(--text-muted);font-size:13px;padding:8px 0';
    empty.textContent = 'Nenhum município encontrado neste raio.';
    discoveredList.appendChild(empty);
    return;
  }
  list.forEach(c => discoveredList.appendChild(makeCityItem(c, true)));
}

function makeCityItem(city, showDist = false) {
  const el = document.createElement('div');
  el.className = 'city-item';
  el.innerHTML = `
    <span class="city-name">${escapeHtml(city.nome)}</span>
    <span class="city-uf">${escapeHtml(city.uf)}</span>
    ${showDist && city.distance_km != null
      ? `<span class="city-dist">${city.distance_km.toFixed(1)} km</span>`
      : ''}
  `;
  return el;
}

// ── Search filter ──────────────────────────────────────────────────────────
searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { renderDiscovered(allDiscovered); return; }
  const filtered = allDiscovered.filter(c =>
    c.nome.toLowerCase().includes(q) || c.uf.toLowerCase().includes(q)
  );
  renderDiscovered(filtered);
});

// ── Helpers ────────────────────────────────────────────────────────────────
function setLoading(on) {
  loading.classList.toggle('hidden', !on);
  analyzeBtn.disabled = on;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove('hidden');
}

function hideError() {
  errorMsg.classList.add('hidden');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
