const RESULTS_EL = document.getElementById('results');
const MODAL = document.getElementById('details-modal');
const MODAL_BODY = document.getElementById('modal-body');
const MODAL_TITLE = document.getElementById('modal-title');

function showLoading(parent) {
  parent.innerHTML = '<progress class="progress is-small is-primary" max="100">Loading</progress>';
}

async function listWeather(query) {
  showLoading(RESULTS_EL);
  try {
    const params = new URLSearchParams();
    if (query) params.set('location', query);
    const url = query ? `/api/v1/weather/search?${params.toString()}` : `/api/v1/weather?skip=0&limit=20`;
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:'Request failed'}));
      return { error: err.detail || 'Request failed' };
    }
    return await res.json();
  } catch (e) {
    return { error: String(e) };
  }
}

function renderList(data) {
  RESULTS_EL.innerHTML = '';
  if (!data || data.error) {
    RESULTS_EL.innerHTML = `<div class="notification is-danger">${data ? data.error : 'No data'}</div>`;
    return;
  }
  const items = data.items || data.data || [];
  if (items.length === 0) {
    RESULTS_EL.innerHTML = '<div class="notification is-warning">No records found.</div>';
    return;
  }
  const list = document.createElement('div');
  list.className = 'list';
  for (const it of items) {
    const item = document.createElement('a');
    item.className = 'list-item';
    item.style.display = 'block';
    item.style.padding = '8px 0';
    item.href = '#';
    item.textContent = `${it.location_name || it.location || it.location_name} — ${new Date(it.created_at || it.start_date).toLocaleString()}`;
    item.addEventListener('click', (e) => {
      e.preventDefault();
      openDetails(it.id || it.id);
    });
    list.appendChild(item);
  }
  RESULTS_EL.appendChild(list);
}

async function openDetails(id) {
  if (!id) return;
  MODAL.classList.add('is-active');
  MODAL_BODY.innerHTML = '<progress class="progress is-small is-primary" max="100">Loading</progress>';
  MODAL_TITLE.textContent = 'Details';
  try {
    const res = await fetch(`/api/v1/weather/${id}`);
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:'Failed to load'}));
      MODAL_BODY.innerHTML = `<div class="notification is-danger">${err.detail || 'Failed to load'}</div>`;
      return;
    }
    const json = await res.json();
    MODAL_TITLE.textContent = `${json.location_name || json.location}`;
    MODAL_BODY.innerHTML = `<pre>${JSON.stringify(json, null, 2)}</pre>`;
  } catch (e) {
    MODAL_BODY.innerHTML = `<div class="notification is-danger">${String(e)}</div>`;
  }
}

function closeModal() {
  MODAL.classList.remove('is-active');
}

document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('modal-close-2').addEventListener('click', closeModal);

document.getElementById('search-btn').addEventListener('click', async (e) => {
  const sel = document.getElementById('locations-select');
  const q = sel.value || document.getElementById('location-input')?.value?.trim() || '';
  const data = await listWeather(q || null);
  renderList(data);
});

document.getElementById('refresh-btn').addEventListener('click', async (e) => {
  const data = await listWeather();
  renderList(data);
});

// load distinct locations into select
async function loadLocations() {
  try {
    const res = await fetch('/api/v1/weather/locations');
    if (!res.ok) return;
    const locations = await res.json();
    const sel = document.getElementById('locations-select');
    while (sel.options.length > 1) sel.remove(1);
    for (const loc of locations) {
      const opt = document.createElement('option');
      opt.value = loc;
      opt.textContent = loc;
      sel.appendChild(opt);
    }
  } catch (e) {
    // ignore
  }
}

async function loadLocationsByCountry(country) {
  try {
    const res = await fetch(`/api/v1/weather/locations?country=${country}`);
    if (!res.ok) return;
    const locations = await res.json();
    const sel = document.getElementById('locations-select');
    while (sel.options.length > 1) sel.remove(1);
    for (const loc of locations) {
      const opt = document.createElement('option');
      opt.value = loc;
      opt.textContent = loc;
      sel.appendChild(opt);
    }
  } catch (e) {
    // ignore
  }
}

// Create form handler
document.getElementById('create-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const loc = document.getElementById('create-location').value.trim();
  const start = document.getElementById('create-start').value;
  const end = document.getElementById('create-end').value;
  if (!loc || !start || !end) {
    document.getElementById('create-result').innerHTML = '<div class="notification is-danger">Please fill all fields.</div>';
    return;
  }
  document.getElementById('create-result').innerHTML = '<progress class="progress is-small is-primary" max="100">Creating</progress>';
  try {
    // convert datetime-local to ISO
    const startISO = new Date(start).toISOString();
    const endISO = new Date(end).toISOString();
    const body = { location: loc, start_date: startISO, end_date: endISO };
    const res = await fetch('/api/v1/weather', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:'Create failed'}));
      document.getElementById('create-result').innerHTML = `<div class="notification is-danger">${err.detail || err.error || 'Failed to create'}</div>`;
      return;
    }
    const json = await res.json();
    document.getElementById('create-result').innerHTML = '<div class="notification is-success">Created successfully.</div>';
    // refresh list
    const data = await listWeather();
    renderList(data);
  } catch (e) {
    document.getElementById('create-result').innerHTML = `<div class="notification is-danger">${String(e)}</div>`;
  }
});

// initial load
loadLocations();
listWeather().then(renderList).catch((e)=>{RESULTS_EL.textContent = String(e)});
document.getElementById('load-india').addEventListener('click', async (e) => {
  e.preventDefault();
  await loadLocationsByCountry('IN');
});
