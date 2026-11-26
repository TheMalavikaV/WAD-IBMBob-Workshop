import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const routes = new Map([
  ['/', ['public/index.html', 'text/html']],
  ['/app.js', ['public/app.js', 'text/javascript']],
  ['/claims.js', ['public/claims.js', 'text/javascript']],
  ['/styles.css', ['public/styles.css', 'text/css']],
  ['/api/desk', ['data/desk.json', 'application/json']],
]);

export async function serveDesk(req, res) {
  const route = routes.get(req.url.split('?')[0]);
  if (!route) return res.writeHead(404).end();
  if (req.method !== 'GET') return res.writeHead(405, { Allow: 'GET' }).end();
  try {
    const [file, type] = route;
    const body = await readFile(new URL(file, import.meta.url));
    res.writeHead(200, { 'Content-Type': type + '; charset=utf-8', 'Cache-Control': 'no-store' }).end(body);
  } catch (err) {
    console.error(err);
    res.writeHead(500).end('Unable to load the desk.');
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT ?? 7991);
  createServer(serveDesk)
    .on('error', err => {
      if (err.code !== 'EADDRINUSE') throw err;
      console.error(`Port ${port} is already in use. Stop the other program or set PORT (see README).`);
      process.exit(1);
    })
    .listen(port, '127.0.0.1', () => console.log('Storm Inbox at http://127.0.0.1:' + port));
}
