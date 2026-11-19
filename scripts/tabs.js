// Abas acessíveis com roteamento por hash (#cfp, #teams...), setas/Home/End e menu mobile.
const DEFAULT_TAB = 'home';

const buttons = () => [...document.querySelectorAll('[role="tab"]')].filter(b => !b.hidden);
const panelOf = name => document.getElementById(`tab-${name}`);

function currentFromHash() {
  const name = decodeURIComponent(location.hash.slice(1));
  return buttons().some(b => b.dataset.tab === name) ? name : DEFAULT_TAB;
}

function show(name, { scroll = true } = {}) {
  for (const b of document.querySelectorAll('[role="tab"]')) {
    const active = b.dataset.tab === name;
    b.setAttribute('aria-selected', String(active));
    b.dataset.active = String(active);
    b.tabIndex = active ? 0 : -1;
    const p = panelOf(b.dataset.tab);
    if (p) p.hidden = !active;
  }
  const base = document.documentElement.dataset.siteTitle || document.title.split(' · ').pop();
  const label = document.getElementById(`tabbtn-${name}`)?.textContent.trim();
  document.title = name === DEFAULT_TAB || !label ? base : `${label} · ${base}`;
  if (scroll) window.scrollTo({ top: 0 });
}

export function initTabs() {
  const nav = document.getElementById('mainNav');
  const toggle = document.getElementById('menuToggle');

  const setMenu = open => {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('max-md:hidden', !open);
  };
  toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); }
  });
  setMenu(false);

  nav.addEventListener('click', e => {
    const b = e.target.closest('[role="tab"]');
    if (!b) return;
    setMenu(false);
    if (location.hash.slice(1) === b.dataset.tab) show(b.dataset.tab); // mesma aba: só volta ao topo
    else location.hash = b.dataset.tab;                                // histórico + hashchange
  });

  nav.addEventListener('keydown', e => {
    const tabs = buttons();
    const i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    const next = { ArrowRight: (i + 1) % tabs.length, ArrowLeft: (i - 1 + tabs.length) % tabs.length, Home: 0, End: tabs.length - 1 }[e.key];
    if (next === undefined) return;
    e.preventDefault();
    tabs[next].focus();
    location.hash = tabs[next].dataset.tab;
  });

  // links internos (ex.: logo -> #home)
  window.addEventListener('hashchange', () => show(currentFromHash()));
  show(currentFromHash(), { scroll: false });
}
