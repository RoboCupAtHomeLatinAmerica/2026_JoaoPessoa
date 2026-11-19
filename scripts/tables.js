import { fetchCSV } from './csv.js';

const CELL = 'px-3 py-2';
const ROW = 'border-t border-slate-200 dark:border-slate-800';
const LINK = 'text-blue-700 dark:text-blue-400 hover:underline';
const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' });

function el(tag, cls, ...children) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  n.append(...children);
  return n;
}

function link(url, label) {
  const a = el('a', LINK, label || url);
  a.href = url; a.target = '_blank'; a.rel = 'noopener';
  return a;
}

function setStatus(id, msg) {
  const s = document.getElementById(id);
  if (s) { s.textContent = msg; s.hidden = !msg; }
}

// "Photos/robots/Bill.jpg" -> "Photos/thumbs/robots/Bill.webp"
const robotThumb = src => src.replace(/^Photos\/robots\/(.+)\.[^.]+$/i, 'Photos/thumbs/robots/$1.webp');

// Como cada coluna do CSV de equipes é exibida (por nome do cabeçalho).
const TEAM_RENDERERS = {
  'TDP': v => (v ? link(v, 'TDP') : ''),
  'Poster': v => (v ? link(v, 'Poster') : ''),
  'Robot Photo': (v, row) => {
    if (!v) return '';
    const img = el('img', 'h-14 w-auto rounded ring-1 ring-slate-200 dark:ring-slate-800 bg-white');
    img.src = robotThumb(v);
    img.alt = `Robot of team ${row[0] || ''}`;
    img.loading = 'lazy';
    img.height = 56;
    img.addEventListener('error', () => { if (img.src.indexOf(v) < 0) img.src = v; }, { once: true });
    const a = el('a', '', img);
    a.href = v; a.target = '_blank'; a.rel = 'noopener'; a.setAttribute('aria-label', `Open full-size photo of ${row[0] || 'the robot'}`);
    return a;
  },
};
const UNSORTABLE = new Set(['TDP', 'Poster', 'Robot Photo']);

// Tabela de registros (uma linha por registro) com ordenação por coluna e busca.
function buildRecordTable(table, rows, { renderers = {}, unsortable = new Set(), emptyText }) {
  const [headers, ...data] = rows;
  const thead = table.createTHead();
  const tbody = table.tBodies[0] || table.createTBody();
  const state = { col: -1, dir: 1 };

  const draw = () => {
    const order = data.map((r, i) => i);
    if (state.col >= 0) order.sort((a, b) => state.dir * collator.compare(data[a][state.col] ?? '', data[b][state.col] ?? ''));
    tbody.replaceChildren(...order.map(i => {
      const tr = el('tr', ROW);
      headers.forEach((h, c) => {
        const val = data[i][c] ?? '';
        const content = renderers[h] ? renderers[h](val, data[i]) : /^https?:\/\//i.test(val) ? link(val) : val;
        tr.append(el('td', CELL, content));
      });
      tr.dataset.search = data[i].join(' ').toLowerCase();
      return tr;
    }));
    if (!data.length) tbody.append(el('tr', ROW, Object.assign(el('td', CELL + ' text-slate-600 dark:text-slate-400', emptyText || 'Nothing to show yet.'), { colSpan: headers.length })));
    thead.querySelectorAll('th').forEach((th, c) => th.setAttribute('aria-sort', c === state.col ? (state.dir > 0 ? 'ascending' : 'descending') : 'none'));
    applyFilter();
  };

  const input = document.querySelector(`[data-filter-for="${table.id}"]`);
  const applyFilter = () => {
    if (!input) return;
    const q = input.value.trim().toLowerCase();
    let shown = 0;
    tbody.querySelectorAll('tr[data-search]').forEach(tr => { const ok = !q || tr.dataset.search.includes(q); tr.hidden = !ok; if (ok) shown++; });
    setStatus(`${table.id}Status`, q && data.length && !shown ? 'No results match your search.' : '');
  };
  input?.addEventListener('input', applyFilter);

  const tr = el('tr');
  headers.forEach((h, c) => {
    const th = el('th', CELL + ' font-semibold');
    th.scope = 'col';
    if (unsortable.has(h)) th.append(h);
    else {
      const b = el('button', 'sort-btn font-semibold', h);
      b.type = 'button';
      b.addEventListener('click', () => { state.dir = state.col === c ? -state.dir : 1; state.col = c; draw(); });
      th.append(b);
    }
    th.setAttribute('aria-sort', 'none');
    tr.append(th);
  });
  thead.className = 'bg-slate-50 dark:bg-slate-800/50';
  thead.replaceChildren(tr);
  draw();
}

async function loadRecordTable(id, renderers, unsortable, emptyText) {
  const table = document.getElementById(id);
  if (!table) return;
  try {
    const rows = await fetchCSV(table.dataset.csv);
    if (!rows.length) throw new Error('empty CSV');
    buildRecordTable(table, rows, { renderers, unsortable, emptyText });
  } catch (e) {
    console.error(`Could not load ${table.dataset.csv}`, e);
    setStatus(`${id}Status`, 'Could not load this table. Please try again later.');
  }
}

// Objetos: cada coluna do CSV é uma categoria (pasta em Photos/objects).
async function loadObjects(placeholder = false) {
  const table = document.getElementById('objectsTable');
  if (!table) return;
  const BASE = 'Photos/objects', THUMBS = 'Photos/thumbs/objects';
  try {
    const [headers, ...rows] = await fetchCSV(table.dataset.csv);
    const trh = el('tr');
    headers.forEach(h => { const th = el('th', CELL + ' font-semibold'); th.scope = 'col'; th.append(h); trh.append(th); });
    table.createTHead().className = 'bg-slate-50 dark:bg-slate-800/50';
    table.tHead.replaceChildren(trh);

    const valid = f => f && f.toLowerCase() !== 'a.png' && f !== '.';
    const tbody = table.tBodies[0] || table.createTBody();

    // Lista ainda não definida para esta edição: mostra só as categorias com "Coming soon".
    if (placeholder) {
      const tr = el('tr', ROW);
      headers.forEach(h => {
        const tile = el('div', 'mx-auto flex h-28 w-28 flex-col items-center justify-center gap-1 rounded-md bg-slate-100 text-xs text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700');
        tile.setAttribute('role', 'img');
        tile.setAttribute('aria-label', `${h}: objects coming soon`);
        const logo = el('img', 'h-14 w-14 opacity-70');
        logo.src = 'Photos/RCB-H.png'; logo.alt = ''; logo.width = 56; logo.height = 56; logo.loading = 'lazy';
        tile.append(logo, 'Coming soon');
        tr.append(el('td', CELL + ' align-top text-center', tile));
      });
      tbody.replaceChildren(tr);
      setStatus('objectsTableStatus', 'The object list will be published during competition week.');
      return;
    }
    tbody.replaceChildren(...rows.map(r => {
      const tr = el('tr', ROW);
      headers.forEach((folder, c) => {
        const td = el('td', CELL + ' align-top text-center');
        const file = r[c];
        if (valid(file)) {
          const name = file.replace(/\.[^.]+$/, '');
          const img = el('img', 'mx-auto h-24 w-24 rounded-md border border-slate-300 bg-white object-contain p-1 dark:border-slate-600');
          img.src = `${THUMBS}/${folder}/${encodeURIComponent(name)}.webp`;
          img.alt = name; img.width = 96; img.height = 96; img.loading = 'lazy';
          img.addEventListener('error', () => { img.src = `${BASE}/${folder}/${encodeURIComponent(file)}`; }, { once: true });
          const a = el('a', '', img);
          a.href = `${BASE}/${folder}/${encodeURIComponent(file)}`; a.target = '_blank'; a.rel = 'noopener';
          td.append(el('figure', 'space-y-1', a, el('figcaption', 'text-xs text-slate-600 dark:text-slate-400', name)));
        }
        tr.append(td);
      });
      return tr;
    }));
  } catch (e) {
    console.error('Could not load objects', e);
    setStatus('objectsTableStatus', 'Could not load the object list. Please try again later.');
  }
}

export function initTables(ev) {
  return Promise.all([
    loadRecordTable('teamsTable', TEAM_RENDERERS, UNSORTABLE, 'No teams registered yet.'),
    loadRecordTable('peopleTable', {}, new Set(), 'No names available yet.'),
    loadObjects(Boolean(ev?.objects?.placeholder)),
  ]);
}
