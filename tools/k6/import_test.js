import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

// Reads the CSV file from the k6 script working directory when running locally.
const csv = new SharedArray('csv', function () {
  // k6's open() will be available when running k6 locally; when running in Docker
  // mount the file into the container's working dir.
  return [open('test.csv', 'b')];
});

export let options = {
  vus: 10, // virtual users, tune as needed
  duration: '60s',
};

export default function () {
  const headers = { 'Content-Type': 'multipart/form-data' };
  const body = { file: http.file(csv[0], 'test.csv', 'text/csv') };
  const res = http.post('http://host.docker.internal:8000/urls/import', body, { headers });
  check(res, { 'status is 200': (r) => r.status === 200 });
}
