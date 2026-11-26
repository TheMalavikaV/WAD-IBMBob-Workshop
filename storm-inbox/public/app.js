import { filedTime, filterClaims, statusOf } from './claims.js';

const get = id => document.getElementById(id);
function el(tag, value, className) {
  const node = document.createElement(tag);
  if (value !== undefined) node.textContent = value;
  if (className) node.className = className;
  return node;
}

function showDesk({ claims, adjusters }) {
  let selectedId = claims[0]?.id;
  for (const adjuster of adjusters) {
    const count = claims.filter(c => c.owner === adjuster.id).length;
    const card = el('div', undefined, 'roster-card');
    card.append(el('strong', adjuster.name), el('span', adjuster.available ? 'Available' : 'Unavailable'),
      el('small', count + ' of ' + adjuster.capacity + ' active claims'));
    get('roster').append(card);
  }

  function render() {
    const visible = filterClaims(claims, get('status').value);
    const selected = visible.find(c => c.id === selectedId) ?? visible[0];
    selectedId = selected?.id;
    const rows = visible.map(claim => {
      const tr = el('tr');
      if (claim.id === selectedId) tr.className = 'selected';
      const button = el('button', claim.id);
      button.onclick = () => { selectedId = claim.id; render(); get('rows').querySelector('.selected button')?.focus(); };
      const cell = el('td');
      cell.append(button, el('small', claim.area));
      tr.append(cell, el('td', filedTime(claim)), el('td', claim.severity), el('td', statusOf(claim)));
      return tr;
    });
    get('rows').replaceChildren(...rows);
    const details = get('details');
    details.replaceChildren();
    if (!selected) {
      details.append(el('p', 'No matching claims.'));
      return;
    }
    const owner = adjusters.find(a => a.id === selected.owner);
    details.append(el('p', selected.id, 'overline'), el('h2', selected.summary), el('p', selected.area),
      el('h3', 'Assigned adjuster'), el('p', owner?.name ?? 'Unassigned'), el('h3', 'Required documents'));
    const docs = el('ul');
    for (const name of selected.requiredDocuments) {
      const item = el('li', name);
      item.append(el('strong', selected.receivedDocuments.includes(name) ? 'Received' : 'Missing'));
      docs.append(item);
    }
    details.append(docs);
  }

  get('status').onchange = render;
  render();
}

try {
  const response = await fetch('/api/desk');
  if (!response.ok) throw new Error();
  showDesk(await response.json());
  get('notice').textContent = '';
} catch {
  get('notice').textContent = 'Unable to load claims. Refresh to try again.';
}
