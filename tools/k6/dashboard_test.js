import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  vus: 50,
  duration: '30s',
};

export default function () {
  const res = http.get('http://host.docker.internal:8000/dashboard/summary');
  // optional check or processing
  sleep(0.1);
}
