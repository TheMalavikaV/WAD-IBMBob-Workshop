'use strict';
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { startServer, request } = require('./helpers');
const { formatPaise } = require('../src/format');

let app;
before(async () => { app = await startServer(); });
after(async () => { await app.close(); });

test('GET /health says ok', async () => {
  const res = await request(app.port, 'GET', '/health');
  assert.equal(res.status, 200);
  assert.deepEqual(res.json, { status: 'ok' });
});

test('GET /transactions lists all 10 seeded raw events in arrival (ingested_at) order', async () => {
  const { json } = await request(app.port, 'GET', '/transactions');
  assert.equal(json.transactions.length, 10);
  const arrival = json.transactions.map((e) => e.ingested_at);
  assert.deepEqual(arrival, [...arrival].sort());
});

test('the pizza purchase shows up as TWO raw events (this is the problem to solve)', async () => {
  const { json } = await request(app.port, 'GET', '/transactions');
  const pizza = json.transactions.filter((e) => e.auth_id === 'AUTH-1001');
  assert.deepEqual(pizza.map((e) => e.type), ['AUTHORISED', 'CAPTURED']);
});

test('unknown routes return 404 JSON', async () => {
  const res = await request(app.port, 'GET', '/nope');
  assert.equal(res.status, 404);
  assert.ok(res.json.error);
});

test('formatPaise formats integer paise as rupees', () => {
  assert.equal(formatPaise(79900), 'Rs.799.00');
  assert.equal(formatPaise(32050), 'Rs.320.50');
  assert.equal(formatPaise(1299900), 'Rs.12,999.00');
  assert.equal(formatPaise(5), 'Rs.0.05');
});
