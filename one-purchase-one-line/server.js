'use strict';
// Entry point: `npm start` (or `node server.js`). Port 5001 by default; override with the PORT environment variable.
const { createApp } = require('./src/app');

const port = Number(process.env.PORT || 5001);
const server = createApp();

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${port} is already in use. Stop the other program or set PORT (see README).`);
    process.exit(1);
  }
  throw err;
});

server.listen(port, () => {
  console.log(`Banking simulator listening on http://localhost:${port}`);
});
