import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { serveDesk } from '../server.mjs';
import { filedTime, filterClaims, missingDocuments, statusOf } from '../public/claims.js';

const read = async path => JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'));
const { claims, adjusters } = await read('../data/desk.json');
const claim = id => claims.find(record => record.id === id);

test('desk opens with twelve unique claims and two available adjusters each handling one claim', () => {
  assert.equal(claims.length, 12);
  assert.equal(new Set(claims.map(c => c.id)).size, 12);
  assert.equal(adjusters.length, 2);
  for (const person of adjusters) {
    assert.equal(person.available, true);
    assert.equal(person.capacity, 2);
    assert.equal(claims.filter(c => c.owner === person.id).length, 1);
  }
});

test('an adjuster can inspect missing documents and the original local filing time', () => {
  assert.deepEqual(missingDocuments(claim('CLM-003')), ['Roof photo']);
  assert.deepEqual(missingDocuments(claim('CLM-002')), ['Roof photo', 'Repair estimate']);
  assert.equal(filedTime(claim('CLM-003')), '08:10');
});

test('status filter retains the register order and shows the relevant records', () => {
  assert.deepEqual(filterClaims(claims, 'Assigned').map(c => c.id), ['CLM-005', 'CLM-006']);
  assert.deepEqual(filterClaims(claims, 'Awaiting documents').map(c => c.id), ['CLM-002', 'CLM-003', 'CLM-011']);
  assert.equal(filterClaims(claims, 'Unassigned').length, 7);
  assert.deepEqual(filterClaims(claims, 'All claims'), claims);
});

test('claim details retain Meera as the owner of the HSR Layout case', () => {
  const current = claim('CLM-006');
  assert.equal(current.owner, 'meera');
  assert.equal(current.area, 'HSR Layout');
  assert.equal(statusOf(current), 'Assigned');
});

test('dashboard and API routes serve the register and its seed records', async () => {
  async function request(url) {
    const response = new ResponseCapture();
    await serveDesk({ url, method: 'GET' }, response);
    assert.equal(response.statusCode, 200);
    return response.body.toString();
  }

  class ResponseCapture {
    writeHead(statusCode) {
      this.statusCode = statusCode;
      return this;
    }

    end(body) {
      this.body = body;
    }
  }

  assert.deepEqual(JSON.parse(await request('/api/desk')), { claims, adjusters });
  assert.match(await request('/'), /Claims register/);
  for (const asset of ['/app.js', '/claims.js', '/styles.css']) {
    assert.ok((await request(asset)).length > 0);
  }
});
