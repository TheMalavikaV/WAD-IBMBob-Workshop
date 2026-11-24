'use strict';
// In-memory event store. Everything is lost when the server stops; the seed is reloaded on start.
const fs = require('node:fs');
const path = require('node:path');

const SEED_FILE = path.join(__dirname, '..', 'data', 'seed-events.json');

function loadSeed() {
  return JSON.parse(fs.readFileSync(SEED_FILE, 'utf8'));
}

// Arrival order: ingested_at, then event_id (so the order is stable).
function byIngestedAt(a, b) {
  if (a.ingested_at !== b.ingested_at) return a.ingested_at < b.ingested_at ? -1 : 1;
  return a.event_id < b.event_id ? -1 : a.event_id > b.event_id ? 1 : 0;
}

function createStore(initialEvents = loadSeed()) {
  const events = initialEvents.map((e) => ({ ...e }));
  return {
    /** All raw events in arrival order (copies, so callers cannot change the store). */
    all() {
      return events.map((e) => ({ ...e })).sort(byIngestedAt);
    },
    /** Append one raw event. No validation, no de-duplication. */
    add(event) {
      events.push({ ...event });
    },
    size() {
      return events.length;
    },
  };
}

module.exports = { createStore, loadSeed };
