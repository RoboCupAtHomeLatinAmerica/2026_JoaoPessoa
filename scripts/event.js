// Carrega data/event.json e preenche o que depende dele na página.
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') node.className = v; else node.setAttribute(k, v);
  }
  node.append(...children);
  return node;
}

const LINK = 'text-blue-700 dark:text-blue-400 hover:underline';

// Data de hoje em São Paulo (YYYY-MM-DD), independente do fuso do visitante.
const todayISO = () => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date());
const brToISO = d => d.split('/').reverse().join('-'); // 24/08/2026 -> 2026-08-24

// Prazos vencidos ficam esmaecidos com "Closed"; o próximo prazo em aberto ganha destaque.
function renderImportantDates(dates) {
  const list = $('#importantDates');
  if (!list) return;
  const today = todayISO();
  let nextMarked = false, anyClosed = false;
  list.replaceChildren(...dates.map(d => {
    const closed = brToISO(d.date) < today;
    const li = el('li', { class: closed ? 'text-slate-500 dark:text-slate-400' : '' });
    li.append(el('span', { class: 'font-medium tabular-nums' }, d.date), ` – ${d.text}`);
    if (closed) {
      anyClosed = true;
      li.append(el('span', { class: 'ml-2 rounded bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200' }, 'Closed'));
    } else if (!nextMarked) {
      nextMarked = true;
      li.append(el('span', { class: 'ml-2 rounded bg-blue-700 px-2 py-0.5 text-xs font-medium text-white' }, 'Next deadline'));
    }
    return li;
  }));
  const note = $('#importantDatesNote');
  if (note) note.hidden = !anyClosed;
}

// Rodapé: WhatsApp + e-mail dos chairs (dados vêm de data/event.json).
function renderContact(ev) {
  const list = $('#contactList');
  if (!list) return;
  const items = [];
  if (ev.links?.whatsapp) {
    const li = el('li');
    li.append('WhatsApp group: ', el('a', { href: ev.links.whatsapp, target: '_blank', rel: 'noopener', class: LINK }, 'join here'));
    items.push(li);
  }
  for (const c of ev.chairs.filter(c => c.email)) {
    const li = el('li');
    li.append(`${c.name.split(' ')[0]}: `, el('a', { href: `mailto:${c.email}`, class: LINK }, c.email));
    items.push(li);
  }
  list.replaceChildren(...items);
}

function personItem(p) {
  const li = el('li');
  li.append(p.name);
  if (p.affiliation) li.append(` (${p.affiliation})`);
  if (p.email) li.append(' — ', el('a', { href: `mailto:${p.email}`, class: LINK }, p.email));
  return li;
}

function photoCard(p) {
  const fig = el('figure', { class: 'space-y-2' });
  if (p.placeholder) {
    fig.append(el('div', {
      class: 'flex aspect-[3/2] w-full flex-col items-center justify-center gap-2 rounded-md bg-slate-100 text-sm text-slate-600 ring-1 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700',
      role: 'img', 'aria-label': p.alt,
    }, el('img', { src: 'Photos/RCB-H.png', alt: '', width: 96, height: 96, class: 'h-24 w-24 opacity-70', loading: 'lazy' }), 'Photo coming soon'));
  } else {
    const img = el('img', {
      src: p.thumb || p.src, alt: p.alt, loading: 'lazy', decoding: 'async',
      class: 'w-full rounded-md ring-1 ring-slate-200 dark:ring-slate-800',
    });
    if (p.w) { img.width = p.w; img.height = p.h; }
    fig.append(el('a', { href: p.src, target: '_blank', rel: 'noopener', 'aria-label': `${p.caption} (full size)` }, img));
  }
  fig.append(el('figcaption', { class: 'text-sm text-slate-600 dark:text-slate-400' }, p.caption));
  return fig;
}

export async function loadEvent() {
  const res = await fetch('data/event.json', { cache: 'no-cache' });
  if (!res.ok) throw new Error(`data/event.json: HTTP ${res.status}`);
  const ev = await res.json();

  document.documentElement.dataset.siteTitle = `${ev.name} ${ev.year}`;
  document.title = `${ev.name} ${ev.year}`;
  $$('.year').forEach(n => (n.textContent = ev.year));
  $$('.city').forEach(n => (n.textContent = ev.city));
  $$('.date').forEach(n => (n.textContent = ev.dateText));
  $$('.tagline').forEach(n => (n.textContent = ev.tagline));

  $$('[data-link]').forEach(a => { const href = ev.links?.[a.dataset.link]; if (href) a.href = href; });

  $('.chair')?.replaceChildren(...ev.chairs.map(personItem));
  $('.oc')?.replaceChildren(...ev.oc.map(personItem));

  renderImportantDates(ev.importantDates);
  renderContact(ev);

  $('#photosGrid')?.replaceChildren(...ev.photos.map(photoCard));

  // Aba de resultados: só aparece quando existir uma URL em data/event.json -> results.url
  if (ev.results?.url) {
    $('#tabbtn-results').hidden = false;
    const a = $('#resultsLink');
    a.href = ev.results.url;
    a.textContent = ev.results.label || 'Official results';
  }
  return ev;
}
