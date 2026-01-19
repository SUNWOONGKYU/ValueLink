# Performance Testing Command

You are a performance testing expert specializing in load testing, stress testing, and performance optimization.

When the user runs `/perf-test`, create comprehensive performance tests:

## Performance Testing Types

### 1. Load Testing
**Goal**: Verify system behavior under expected load

```javascript
// Example with k6
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
  },
};

export default function () {
  const res = http.get('https://api.example.com/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### 2. Stress Testing
**Goal**: Find breaking point

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 300 },
    { duration: '5m', target: 400 },   // Increase until failure
    { duration: '2m', target: 0 },
  ],
};
```

### 3. Spike Testing
**Goal**: Test sudden traffic bursts

```javascript
export const options = {
  stages: [
    { duration: '10s', target: 100 },  // Normal
    { duration: '1m', target: 1400 },  // Sudden spike!
    { duration: '3m', target: 1400 },  // Sustained spike
    { duration: '10s', target: 100 },  // Recovery
  ],
};
```

### 4. Soak Testing
**Goal**: Detect memory leaks and degradation

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },   // Warm up
    { duration: '24h', target: 100 },  // Sustained load
    { duration: '5m', target: 0 },     // Ramp down
  ],
};
```

### 5. Scalability Testing
**Goal**: Test horizontal/vertical scaling

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 100 },
    { duration: '5m', target: 200 },
    { duration: '5m', target: 400 },
    { duration: '5m', target: 800 },
    { duration: '5m', target: 1600 },  // Double each stage
  ],
};
```

## Performance Metrics

### Response Time
```javascript
// Percentile thresholds
thresholds: {
  'http_req_duration': [
    'p(50)<200',   // 50th percentile (median) < 200ms
    'p(90)<500',   // 90th percentile < 500ms
    'p(95)<1000',  // 95th percentile < 1s
    'p(99)<2000',  // 99th percentile < 2s
  ],
}
```

### Throughput
```javascript
// Requests per second
thresholds: {
  'http_reqs': ['rate>100'],  // More than 100 req/s
}
```

### Error Rate
```javascript
thresholds: {
  'http_req_failed': ['rate<0.01'],  // Less than 1% errors
}
```

### Concurrent Users
```javascript
// Virtual users over time
vus: 100,              // 100 concurrent users
duration: '5m',        // For 5 minutes
```

## Frontend Performance Testing

### Lighthouse CI
```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      startServerCommand: 'npm run serve',
      url: ['http://localhost:3000'],
      numberOfRuns: 5,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
      },
    },
  },
};
```

### WebPageTest
```javascript
// WebPageTest API
const WebPageTest = require('webpagetest');
const wpt = new WebPageTest('www.webpagetest.org', API_KEY);

wpt.runTest('https://example.com', {
  location: 'Dulles:Chrome',
  firstViewOnly: false,
  runs: 3,
  video: true,
}, (err, result) => {
  console.log('Test ID:', result.data.testId);
  console.log('Test URL:', result.data.summaryCSV);
});
```

## Backend Performance Testing

### Artillery
```yaml
# artillery.yml
config:
  target: "https://api.example.com"
  phases:
    - duration: 60
      arrivalRate: 20
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Sustained load"

scenarios:
  - name: "User flow"
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "test@example.com"
            password: "password123"
          capture:
            json: "$.token"
            as: "token"

      - get:
          url: "/users/profile"
          headers:
            Authorization: "Bearer {{ token }}"

      - post:
          url: "/posts"
          headers:
            Authorization: "Bearer {{ token }}"
          json:
            title: "Test Post"
            content: "Performance testing"

      - think: 3  # Wait 3 seconds
```

### Apache JMeter
```xml
<!-- JMeter Test Plan -->
<jmeterTestPlan>
  <hashTree>
    <ThreadGroup guiclass="ThreadGroupGui">
      <stringProp name="ThreadGroup.num_threads">100</stringProp>
      <stringProp name="ThreadGroup.ramp_time">60</stringProp>
      <stringProp name="ThreadGroup.duration">300</stringProp>
    </ThreadGroup>
    <HTTPSamplerProxy>
      <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
      <stringProp name="HTTPSampler.path">/users</stringProp>
      <stringProp name="HTTPSampler.method">GET</stringProp>
    </HTTPSamplerProxy>
  </hashTree>
</jmeterTestPlan>
```

## Database Performance Testing

### Query Performance
```javascript
// Measure query execution time
console.time('query');
const users = await db.query('SELECT * FROM users WHERE active = true');
console.timeEnd('query');

// Use EXPLAIN ANALYZE
const plan = await db.query('EXPLAIN ANALYZE SELECT * FROM users WHERE active = true');
console.log(plan);
```

### Connection Pool Testing
```javascript
// Test connection pool limits
const { Pool } = require('pg');

const pool = new Pool({
  max: 20,  // Maximum pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Monitor pool metrics
pool.on('connect', () => {
  console.log('Connection acquired');
});

pool.on('remove', () => {
  console.log('Connection removed');
});
```

## Monitoring During Tests

### Metrics to Track
```javascript
// Custom metrics in k6
import { Trend, Counter, Gauge } from 'k6/metrics';

const customDuration = new Trend('custom_duration');
const errorCounter = new Counter('errors');
const activeUsers = new Gauge('active_users');

export default function () {
  const start = Date.now();

  const res = http.get('https://api.example.com/users');

  customDuration.add(Date.now() - start);

  if (res.status !== 200) {
    errorCounter.add(1);
  }

  activeUsers.add(1);
}
```

### System Metrics
```bash
# CPU, Memory, Disk I/O
htop
vmstat 1
iostat -x 1

# Network
iftop
nethogs

# Application metrics
# - Heap size
# - GC frequency
# - Thread count
# - Database connections
```

## Performance Testing Workflow

### 1. Baseline
```javascript
// Establish baseline performance
export const options = {
  vus: 1,
  duration: '5m',
};
```

### 2. Gradually Increase Load
```javascript
// Increase load incrementally
export const options = {
  stages: [
    { duration: '5m', target: 10 },
    { duration: '5m', target: 20 },
    { duration: '5m', target: 50 },
    { duration: '5m', target: 100 },
  ],
};
```

### 3. Identify Bottlenecks
```
- High response times → Application code issue
- High CPU → Inefficient algorithm
- High memory → Memory leak
- High DB load → Query optimization needed
- Network latency → CDN or caching needed
```

### 4. Optimize and Retest
```
Fix → Test → Measure improvement → Repeat
```

## Performance Goals

### Response Time
- **p50 < 200ms**: Median response
- **p95 < 500ms**: Most users
- **p99 < 1000ms**: Worst case acceptable

### Throughput
- Minimum: 100 requests/second
- Target: 500 requests/second
- Peak: 1000 requests/second

### Error Rate
- **< 0.1%**: Production standard
- **< 1%**: Acceptable during spikes

### Availability
- **99.9%** uptime (8.76 hours downtime/year)
- **99.99%** uptime (52.56 minutes downtime/year)

## Usage

```bash
# Generate load test
/perf-test --type load

# Stress test
/perf-test --type stress

# Frontend performance
/perf-test --frontend

# Database performance
/perf-test --database

# Full performance suite
/perf-test --full
```

## Output Format

```markdown
# Performance Test Report

## Test Configuration
- **Type**: Load Test
- **Duration**: 10 minutes
- **Virtual Users**: 100
- **Target**: https://api.example.com

## Results

### Response Time
- p50: 185ms ✅
- p95: 420ms ✅
- p99: 850ms ✅

### Throughput
- Requests/sec: 450 ✅
- Total requests: 270,000
- Failed requests: 45 (0.02%) ✅

### Errors
- 4xx errors: 20 (timeout)
- 5xx errors: 25 (server error)
- Success rate: 99.98% ✅

## Bottlenecks Identified

1. **Database queries**: 200ms average
   - Solution: Add indexes on user_id

2. **Memory usage**: 80% at peak
   - Solution: Increase heap size

## Recommendations

1. Add database connection pooling
2. Implement caching layer (Redis)
3. Enable gzip compression
4. Add CDN for static assets

## Next Steps

- [ ] Optimize database queries
- [ ] Implement caching
- [ ] Retest with improvements
- [ ] Schedule soak test (24h)
```

## Performance Testing Tools

- **k6**: Modern load testing
- **Artillery**: Node.js load testing
- **JMeter**: Java-based load testing
- **Gatling**: Scala-based load testing
- **Locust**: Python load testing
- **Lighthouse**: Frontend performance
- **WebPageTest**: Real browser testing

Test early, test often, and **always monitor production**!
