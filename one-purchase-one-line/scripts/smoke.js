'use strict';
// One-command smoke test: starts the simulator on a free port, calls it, stops it.  npm run smoke
const { request, startServerProcess } = require('./lib');

(async () => {
  const srv = await startServerProcess();
  try {
    const health = await request(srv.port, 'GET', '/health');
    const tx = await request(srv.port, 'GET', '/transactions');
    if (health.json?.status !== 'ok' || tx.json?.transactions?.length !== 10) {
      throw new Error(`unexpected responses: ${health.text} / ${tx.text.slice(0, 200)}`);
    }
    console.log(`SMOKE TEST OK - /health returned ok, /transactions returned ${tx.json.transactions.length} events`);
  } finally {
    await srv.stop();
  }
})().catch((err) => { console.error(`SMOKE TEST FAILED - ${err.message}`); process.exit(1); });
