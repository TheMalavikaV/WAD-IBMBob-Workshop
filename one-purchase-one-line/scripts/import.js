'use strict';
// Send a batch file to a RUNNING simulator:  npm run import -- data/batch-1.json   (start it first with npm start)
// Uses POST /import, which you build at Level 2. Set PORT if your server is not on 5001.
const fs = require('node:fs');
const { request } = require('./lib');

(async () => {
  const file = process.argv[2];
  if (!file) { console.error('usage: npm run import -- <batch-file.json>'); process.exit(2); }
  const events = JSON.parse(fs.readFileSync(file, 'utf8'));
  const port = Number(process.env.PORT || 5001);
  const res = await request(port, 'POST', '/import', events);
  if (res.status === 404) {
    console.error('POST /import does not exist yet - building it is Level 2 (see LEVELS.md).');
    process.exit(1);
  }
  console.log(`HTTP ${res.status}`);
  console.log(res.text);
})().catch((err) => {
  console.error(`Could not reach the simulator (${err.code || err.message}). Is it running? Start it with: npm start`);
  process.exit(1);
});
