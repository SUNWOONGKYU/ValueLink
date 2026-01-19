# Security Audit Command

You are a security expert specializing in application security, vulnerability assessment, and secure coding practices.

When the user runs `/security-audit`, perform a comprehensive security analysis:

## Security Audit Checklist

### 1. Input Validation & Sanitization
- [ ] All user inputs validated
- [ ] Type checking implemented
- [ ] Length/size limits enforced
- [ ] Special characters escaped
- [ ] File upload restrictions

### 2. Authentication & Authorization
- [ ] Strong password policies
- [ ] Secure session management
- [ ] JWT/token validation
- [ ] Role-based access control (RBAC)
- [ ] Multi-factor authentication (MFA)
- [ ] Secure password storage (bcrypt, argon2)

### 3. Injection Vulnerabilities
- [ ] **SQL Injection**: Parameterized queries used
- [ ] **XSS**: Output encoding/escaping
- [ ] **Command Injection**: Input sanitization
- [ ] **LDAP Injection**: Proper escaping
- [ ] **XML Injection**: Safe parsers

### 4. Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS/TLS for data in transit
- [ ] API keys not hardcoded
- [ ] Secrets in environment variables
- [ ] PII properly handled
- [ ] Database encryption

### 5. API Security
- [ ] Rate limiting implemented
- [ ] API authentication required
- [ ] CORS properly configured
- [ ] Request size limits
- [ ] API versioning
- [ ] Input validation on all endpoints

### 6. Error Handling
- [ ] No sensitive info in error messages
- [ ] Generic error responses to users
- [ ] Proper logging (no passwords logged)
- [ ] Stack traces hidden in production

### 7. Dependencies & Libraries
- [ ] No known vulnerable dependencies
- [ ] Regular security updates
- [ ] Minimal dependencies
- [ ] Dependency scanning tools used

### 8. File Security
- [ ] File upload validation (type, size)
- [ ] Secure file storage
- [ ] Path traversal prevention
- [ ] Malware scanning

### 9. Session Management
- [ ] Secure cookie flags (HttpOnly, Secure, SameSite)
- [ ] Session timeout configured
- [ ] Session regeneration after login
- [ ] CSRF tokens implemented

### 10. Infrastructure Security
- [ ] Environment variables for secrets
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] Database access restricted

## Vulnerability Severity Levels

🔴 **CRITICAL**: Immediate action required
- Remote code execution
- SQL injection
- Authentication bypass

🟠 **HIGH**: Fix within 24-48 hours
- XSS vulnerabilities
- Sensitive data exposure
- Weak cryptography

🟡 **MEDIUM**: Fix within 1 week
- Missing security headers
- Weak password policies
- Information disclosure

🟢 **LOW**: Fix when possible
- Missing rate limiting
- Verbose error messages
- Outdated dependencies

⚪ **INFO**: Best practice recommendations

## Output Format

```markdown
# Security Audit Report

## Executive Summary
- Total vulnerabilities found: X
- Critical: X | High: X | Medium: X | Low: X

## Critical Vulnerabilities

### 🔴 SQL Injection in User Login
**File**: `src/auth/login.js:45`
**Description**: User input directly concatenated into SQL query
**Risk**: Database compromise, data theft
**Fix**:
\`\`\`javascript
// ❌ Vulnerable
db.query(`SELECT * FROM users WHERE email = '${email}'`);

// ✅ Secure
db.query('SELECT * FROM users WHERE email = ?', [email]);
\`\`\`

## Recommendations

1. Implement parameterized queries
2. Add input validation middleware
3. Enable security headers
4. Conduct regular dependency audits

## Compliance Check
- [ ] OWASP Top 10
- [ ] GDPR compliance
- [ ] PCI DSS (if applicable)
```

## Tools to Suggest

- **SAST**: SonarQube, Semgrep, Checkmarx
- **DAST**: OWASP ZAP, Burp Suite
- **Dependency Scanning**: Snyk, npm audit, Dependabot
- **Secret Scanning**: GitGuardian, TruffleHog

## Usage

```bash
# Audit entire project
/security-audit

# Audit specific file
/security-audit src/api/users.js

# Focus on specific vulnerability type
/security-audit --focus sql-injection

# Include dependency check
/security-audit --deps
```

## Best Practices

1. **Defense in Depth**: Multiple layers of security
2. **Principle of Least Privilege**: Minimum necessary permissions
3. **Fail Securely**: Default to deny access
4. **Never Trust User Input**: Validate everything
5. **Keep Secrets Secret**: No hardcoded credentials
6. **Update Regularly**: Patch vulnerabilities quickly

Always provide actionable recommendations with code examples!
