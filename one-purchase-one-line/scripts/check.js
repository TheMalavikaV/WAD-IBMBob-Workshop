'use strict';
// Acceptance checks with the expected results in expected/. Starts a fresh server for every check.
//   npm run check            all levels
//   npm run check -- L1      only Level 1 (L2, L3 likewise)
// Comparison: every key in the expected JSON must be present with the same value (extra keys are allowed);
// lists must have the same items in the same order.
const fs = require('node:fs');
const path = require('node:path');
const { ROOT, request, startServerProcess } = require('./lib');

const load = (rel) => JSON.parse(fs.readFileSync(path.join(ROOT, rel), 'utf8'));

function diff(expected, actual, where = '$') {
  if (expected === null || typeof expected !== 'object') {
    return Object.is(expected, actual) ? null : `${where}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`;
  }
  if (Array.isArray(expected)) {
    if (!Array.isArray(actual)) return `${where}: expected a list, got ${JSON.stringify(actual)?.slice(0, 120)}`;
    for (let i = 0; i < Math.min(expected.length, actual.length); i++) {
      const d = diff(expected[i], actual[i], `${where}[${i}]`);
      if (d) return d;
    }
    return expected.length === actual.length ? null : `${where}: expected ${expected.length} items, got ${actual.length}`;
  }
  if (actual === null || typeof actual !== 'object' || Array.isArray(actual)) {
    return `${where}: expected an object, got ${JSON.stringify(actual)?.slice(0, 120)}`;
  }
  for (const key of Object.keys(expected)) {
    if (!(key in actual)) return `${where}: missing key "${key}"`;
    const d = diff(expected[key], actual[key], `${where}.${key}`);
    if (d) return d;
  }
  return null;
}

async function expectJson(port, method, url, body, expectedFile) {
  const res = await request(port, method, url, body);
  if (res.status !== 200) return `${method} ${url} returned HTTP ${res.status}: ${res.text.slice(0, 200)}`;
  const d = diff(load(expectedFile), res.json);
  return d ? `${method} ${url} vs ${expectedFile}: ${d}` : null;
}

const CHECKS = [
  ['L1', 'seed timeline (GET /timeline)', async (p) =>
    expectJson(p, 'GET', '/timeline', undefined, 'expected/timeline-seed.json')],
  ['L2', 'import batch-1 once (POST /import, then GET /timeline)', async (p) =>
    (await expectJson(p, 'POST', '/import', load('data/batch-1.json'), 'expected/import-batch-1-first.json'))
    || expectJson(p, 'GET', '/timeline', undefined, 'expected/timeline-after-batch-1.json')],
  ['L2', 'import batch-1 twice is idempotent', async (p) => {
    const batch = load('data/batch-1.json');
    await request(p, 'POST', '/import', batch);
    const before = (await request(p, 'GET', '/transactions')).json;
    return (await expectJson(p, 'POST', '/import', batch, 'expected/import-batch-1-second.json'))
      || (await expectJson(p, 'GET', '/timeline', undefined, 'expected/timeline-after-batch-1.json'))
      || diff(before, (await request(p, 'GET', '/transactions')).json, 'GET /transactions after 2nd import');
  }],
  ['L3', 'edge cases (POST /import data/batch-edge-cases.json)', async (p) =>
    (await expectJson(p, 'POST', '/import', load('data/batch-edge-cases.json'), 'expected/import-edge-cases.json'))
    || expectJson(p, 'GET', '/timeline', undefined, 'expected/timeline-after-edge-cases.json')],
];

(async () => {
  const only = process.argv[2];
  const selected = CHECKS.filter(([level]) => !only || level === only.toUpperCase());
  let failed = 0;
  for (const [level, name, run] of selected) {
    const srv = await startServerProcess();
    let problem;
    try { problem = await run(srv.port); } catch (err) { problem = `crashed: ${err.message}`; }
    await srv.stop();
    console.log(`${problem ? 'FAIL' : 'PASS'}  ${level}  ${name}${problem ? `\n      ${problem}` : ''}`);
    if (problem) failed++;
  }
  console.log(`\n${selected.length - failed}/${selected.length} checks passed`);
  process.exitCode = failed ? 1 : 0;
})();
