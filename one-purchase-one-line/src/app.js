'use strict';
// HTTP routes of the banking simulator. Plain node:http, no framework.
const http = require('node:http');
const { createStore } = require('./store');
const { sendJson, sendHtml, escapeHtml } = require('./http-utils');
const { formatPaise, formatTime } = require('./format');

function renderTransactionsPage(events) {
  // Newest first, like a banking app. One row per raw event -- which is exactly the problem.
  const rows = [...events]
    .sort((a, b) => (a.event_time < b.event_time ? 1 : -1))
    .map((e) => `<tr><td>${escapeHtml(formatTime(e.event_time))}</td><td>${escapeHtml(e.merchant)}</td>`
      + `<td class="amt">${escapeHtml(formatPaise(e.amount_paise))}</td><td><small>${escapeHtml(e.type)}</small></td></tr>`)
    .join('\n');
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Your transactions</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 42rem; margin: 2rem auto; padding: 0 1rem; color: #1d2433; }
  table { width: 100%; border-collapse: collapse; } td { padding: .55rem .4rem; border-bottom: 1px solid #e3e6ec; }
  .amt { text-align: right; font-variant-numeric: tabular-nums; } small { color: #6b7385; }
</style></head>
<body><h1>Your transactions</h1>
<p><small>${events.length} entries from <code>GET /transactions</code></small></p>
<table>${rows}</table></body></html>`;
}

function createApp({ store = createStore() } = {}) {
  return http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');
    try {
      if (req.method === 'GET' && url.pathname === '/health') {
        return sendJson(res, 200, { status: 'ok' });
      }
      if (req.method === 'GET' && url.pathname === '/transactions') {
        return sendJson(res, 200, { transactions: store.all() });
      }
      if (req.method === 'GET' && url.pathname === '/') {
        return sendHtml(res, 200, renderTransactionsPage(store.all()));
      }
      return sendJson(res, 404, { error: `no route for ${req.method} ${url.pathname}` });
    } catch (err) {
      console.error(err);
      return sendJson(res, 500, { error: 'internal error' });
    }
  });
}

module.exports = { createApp };
