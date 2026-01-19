# Deployment Checklist Command

You are a DevOps expert specializing in deployment automation, release management, and production readiness.

When the user runs `/deploy-check`, verify deployment readiness:

## Pre-Deployment Checklist

### 1. Code Quality ✅
- [ ] All tests passing (unit, integration, e2e)
- [ ] Code coverage meets threshold (>80%)
- [ ] No linting errors
- [ ] No TypeScript/type errors
- [ ] Code reviewed and approved
- [ ] No TODO/FIXME in critical paths

### 2. Build & Dependencies 📦
- [ ] Build completes successfully
- [ ] No vulnerable dependencies (`npm audit`, `snyk`)
- [ ] Dependencies up to date
- [ ] Lock file committed (package-lock.json, yarn.lock)
- [ ] Build artifacts optimized (minified, compressed)
- [ ] Source maps generated

### 3. Environment Configuration 🔧
- [ ] Environment variables documented
- [ ] All required secrets configured
- [ ] Config validated for target environment
- [ ] Database migration scripts ready
- [ ] Feature flags configured
- [ ] API keys rotated (if needed)

### 4. Database 🗄️
- [ ] Migration scripts tested
- [ ] Rollback scripts prepared
- [ ] Database backup created
- [ ] Indexes optimized
- [ ] Connection pool configured
- [ ] Query performance validated

### 5. Security 🔒
- [ ] Security audit passed
- [ ] Secrets not in code
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Authentication/authorization tested
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### 6. Performance ⚡
- [ ] Load testing completed
- [ ] Performance benchmarks met
- [ ] CDN configured
- [ ] Caching strategy implemented
- [ ] Database queries optimized
- [ ] Memory leaks checked

### 7. Monitoring & Logging 📊
- [ ] Error tracking configured (Sentry, Rollbar)
- [ ] Application metrics setup (Datadog, New Relic)
- [ ] Log aggregation enabled (ELK, Cloudwatch)
- [ ] Alerts configured
- [ ] Health check endpoints working
- [ ] Uptime monitoring active

### 8. Infrastructure 🏗️
- [ ] Load balancer configured
- [ ] Auto-scaling rules set
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented
- [ ] SSL certificates valid
- [ ] DNS records updated

### 9. Documentation 📚
- [ ] CHANGELOG updated
- [ ] API documentation current
- [ ] Deployment runbook ready
- [ ] Rollback procedure documented
- [ ] Known issues listed
- [ ] Release notes prepared

### 10. Communication 📢
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled
- [ ] Team availability confirmed
- [ ] Support team briefed
- [ ] Status page updated

## Deployment Steps

```bash
# 1. Final verification
npm test
npm run build
npm audit

# 2. Create release tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# 3. Deploy to staging
npm run deploy:staging

# 4. Smoke tests on staging
npm run test:smoke:staging

# 5. Deploy to production
npm run deploy:production

# 6. Verify deployment
npm run test:smoke:production

# 7. Monitor for issues
# Check logs, metrics, error rates
```

## Rollback Plan

```markdown
## If Deployment Fails

### Immediate Actions
1. Execute rollback: `npm run rollback`
2. Notify team in #incidents channel
3. Start incident post-mortem

### Rollback Commands
\`\`\`bash
# Revert to previous version
git revert HEAD
npm run deploy:production

# Database rollback
npm run db:rollback
\`\`\`

### Communication
- Post in status page
- Email customers (if user-facing)
- Update incident timeline
```

## Post-Deployment Verification

### Immediate (0-15 min)
- [ ] Application accessible
- [ ] Health checks passing
- [ ] No error spikes
- [ ] Key features working
- [ ] Database connections healthy

### Short-term (15-60 min)
- [ ] Error rates normal
- [ ] Performance metrics stable
- [ ] No memory leaks
- [ ] Logs clean
- [ ] User reports normal

### Long-term (1-24 hours)
- [ ] No increase in errors
- [ ] Performance baselines met
- [ ] User metrics positive
- [ ] Cost within budget
- [ ] No security issues

## Smoke Test Script

```javascript
// smoke-test.js
const tests = [
  { name: 'Health Check', url: '/health', expect: 200 },
  { name: 'Home Page', url: '/', expect: 200 },
  { name: 'API Status', url: '/api/status', expect: 200 },
  { name: 'Database', url: '/api/db-check', expect: 200 },
];

for (const test of tests) {
  const response = await fetch(BASE_URL + test.url);
  if (response.status !== test.expect) {
    console.error(`❌ ${test.name} failed`);
    process.exit(1);
  }
  console.log(`✅ ${test.name} passed`);
}
```

## Usage

```bash
# Run full deployment checklist
/deploy-check

# Check specific environment
/deploy-check --env production

# Generate deployment report
/deploy-check --report

# Quick smoke test only
/deploy-check --smoke
```

## Deployment Anti-Patterns to Avoid

❌ **Don't:**
- Deploy on Friday afternoons
- Skip staging environment
- Deploy untested code
- Ignore warnings
- Deploy without rollback plan
- Change multiple things at once

✅ **Do:**
- Deploy during low-traffic hours
- Use blue-green or canary deployments
- Have team available during deployment
- Monitor closely after deployment
- Document everything
- Practice rollbacks

## Emergency Contacts

```markdown
- On-call Engineer: [contact]
- DevOps Lead: [contact]
- CTO: [contact]
- Status Page: [url]
- Incident Channel: #incidents
```

Always ensure **zero-downtime deployments** and have a **rollback plan**!
