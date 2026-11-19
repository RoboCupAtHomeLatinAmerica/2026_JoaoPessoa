import { loadEvent } from './event.js';
import { initTabs } from './tabs.js';
import { initTables } from './tables.js';

let ev;
try { ev = await loadEvent(); } catch (e) { console.error('Could not load event data', e); }
initTabs();
initTables(ev);
