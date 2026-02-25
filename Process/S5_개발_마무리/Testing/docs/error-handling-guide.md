# API Error Handling Guide - ValueLink Platform

**Version:** 1.0
**Last Updated:** 2026-02-23
**Task:** S5T2
**Area:** Testing

---

## Table of Contents

1. [Error Code Reference](#error-code-reference)
2. [Error Classes](#error-classes)
3. [API Response Format](#api-response-format)
4. [Client-Side Error Handling](#client-side-error-handling)
5. [Server-Side Error Handling](#server-side-error-handling)
6. [Common Error Scenarios](#common-error-scenarios)
7. [Debugging Tips](#debugging-tips)
8. [Best Practices](#best-practices)

---

## Error Code Reference

### Complete Error Code List

| Error Code | HTTP Status | Description | Possible Causes | Client Action |
|-----------|-------------|-------------|-----------------|----------------|
| **VALIDATION_ERROR** | 400 | Input validation failed | Missing/invalid fields, wrong data type | Check input format and retry |
| **BAD_REQUEST** | 400 | Malformed request | Invalid JSON, missing headers | Review request format |
| **NOT_FOUND** | 404 | Resource doesn't exist | Wrong ID, deleted resource | Verify resource ID or create new |
| **CONFLICT** | 409 | Resource already exists | Duplicate name, duplicate entry | Use different name or update existing |
| **UNAUTHORIZED** | 401 | Authentication failed | Missing/invalid token, expired session | Login again and retry |
| **FORBIDDEN** | 403 | Insufficient permissions | User role doesn't have access | Contact admin or use authorized account |
| **REQUEST_TIMEOUT** | 408 | Request exceeded timeout | Server slow, network issue | Retry with longer timeout |
| **RATE_LIMIT_EXCEEDED** | 429 | Too many requests | API rate limit reached | Wait before retrying |
| **DATABASE_ERROR** | 500 | Database operation failed | Connection lost, query error | Contact support or retry |
| **EXTERNAL_API_ERROR** | 502 | External service failed | Third-party API down, invalid credentials | Check external service status |
| **INTERNAL_ERROR** | 500 | Unexpected server error | Unhandled exception, bug | Contact support with error details |
| **UNKNOWN_ERROR** | 500 | Unknown error type | Uncaught exception | Check logs and contact support |

---

## Error Classes

### Class Hierarchy

```
APIError (Base)
├── ValidationError (400)
├── BadRequestError (400)
├── NotFoundError (404)
├── ConflictError (409)
├── UnauthorizedError (401)
├── ForbiddenError (403)
├── RequestTimeoutError (408)
├── RateLimitError (429)
├── DatabaseError (500)
├── ExternalAPIError (502)
└── [Others]
```

### Error Class Examples

#### ValidationError (400)
```typescript
// Thrown when request data fails validation
throw new ValidationError('Invalid email format', {
  field: 'email',
  value: 'not-an-email',
  rule: 'email-format'
})
```

#### NotFoundError (404)
```typescript
// Thrown when resource doesn't exist
throw new NotFoundError('Project', {
  project_id: 'VL-20260223-0001'
})
```

#### UnauthorizedError (401)
```typescript
// Thrown when authentication fails
throw new UnauthorizedError('Invalid JWT token')
```

#### DatabaseError (500)
```typescript
// Thrown when database operations fail
throw new DatabaseError('Failed to insert project', {
  operation: 'INSERT',
  table: 'projects',
  originalError: err.message
})
```

#### ExternalAPIError (502)
```typescript
// Thrown when external service calls fail
throw new ExternalAPIError('Stripe', 'Payment processing failed: insufficient funds')
```

---

## API Response Format

### Error Response Structure

```json
{
  "error": "String message describing the error",
  "code": "ERROR_CODE",
  "statusCode": 400,
  "details": {
    "field": "field_name",
    "expected": "value",
    "received": "invalid_value"
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

### Success Response Structure

```json
{
  "success": true,
  "data": {
    "project_id": "VL-20260223-0001",
    "project_name": "My Project",
    "created_at": "2026-02-23T10:00:00.000Z"
  },
  "meta": {
    "total": 1,
    "page": 1
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

### Common Response Patterns

#### Empty Resource (No Data Found)
```json
{
  "success": true,
  "data": [],
  "meta": {
    "total": 0,
    "page": 1
  }
}
```

#### Paginated Response
```json
{
  "success": true,
  "data": [
    { "id": "item1", "name": "Item 1" },
    { "id": "item2", "name": "Item 2" }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "pageSize": 10,
    "totalPages": 10
  }
}
```

#### Error with Validation Details
```json
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "statusCode": 400,
  "details": {
    "fields": ["email", "password"],
    "missing": true
  }
}
```

---

## Client-Side Error Handling

### Basic Error Handling Pattern

```typescript
/**
 * @task S5T2
 * @description Basic error handling in React components
 */

import { useState } from 'react'
import type { APIError } from '@/lib/errors/api-errors'

interface Project {
  project_id: string
  project_name: string
}

export function ProjectForm() {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(formData: FormData) {
    setError(null)
    setLoading(true)

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: formData.get('name'),
          description: formData.get('description')
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to create project')
      }

      const result = await response.json()
      console.log('Project created:', result.data)
      // Handle success...

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      setError(message)
      console.error('Error:', message)

    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={(e) => {
      e.preventDefault()
      handleSubmit(new FormData(e.currentTarget))
    }}>
      {error && <div className="alert alert-error">{error}</div>}
      {/* Form fields */}
      <button disabled={loading}>{loading ? 'Creating...' : 'Create'}</button>
    </form>
  )
}
```

### Error Handling with Error Codes

```typescript
/**
 * Handle specific errors differently based on error code
 */

async function fetchProject(projectId: string): Promise<Project | null> {
  try {
    const response = await fetch(`/api/projects/${projectId}`)

    if (!response.ok) {
      const errorData = await response.json()

      switch (errorData.code) {
        case 'NOT_FOUND':
          console.log('Project does not exist')
          return null

        case 'UNAUTHORIZED':
          // Redirect to login
          window.location.href = '/login'
          return null

        case 'FORBIDDEN':
          console.error('You do not have permission to view this project')
          return null

        case 'VALIDATION_ERROR':
          console.error('Invalid project ID format:', errorData.details)
          return null

        case 'RATE_LIMIT_EXCEEDED':
          // Retry with exponential backoff
          await new Promise(resolve => setTimeout(resolve, 1000))
          return fetchProject(projectId)

        default:
          console.error('Unexpected error:', errorData.error)
          return null
      }
    }

    const result = await response.json()
    return result.data

  } catch (err) {
    console.error('Network error:', err)
    return null
  }
}
```

### Retry Logic with Exponential Backoff

```typescript
/**
 * Retry failed requests with exponential backoff
 */

async function fetchWithRetry<T>(
  url: string,
  options: RequestInit = {},
  maxRetries: number = 3
): Promise<T> {
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })

      if (!response.ok) {
        const error = await response.json()

        // Don't retry client errors (4xx)
        if (response.status >= 400 && response.status < 500) {
          throw new Error(`${error.code}: ${error.error}`)
        }

        // Retry server errors (5xx) and rate limits (429)
        throw new Error(`Server error: ${response.status}`)
      }

      return response.json()

    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err))

      if (attempt < maxRetries) {
        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, attempt - 1) * 1000
        console.log(`Retry attempt ${attempt}/${maxRetries} after ${delay}ms`)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }

  throw lastError || new Error('Max retries exceeded')
}

// Usage
try {
  const project = await fetchWithRetry('/api/projects/VL-20260223-0001')
  console.log('Project:', project)
} catch (err) {
  console.error('Failed after retries:', err)
}
```

### Form Validation Error Display

```typescript
/**
 * Display validation errors for each field
 */

interface FormErrors {
  [key: string]: string
}

export function FormWithValidation() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    projectName: ''
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        const error = await response.json()

        if (error.code === 'VALIDATION_ERROR' && error.details?.fields) {
          // Display field-specific errors
          const fieldErrors: FormErrors = {}
          for (const field of error.details.fields) {
            fieldErrors[field] = `${field} is required`
          }
          setErrors(fieldErrors)
        } else {
          setErrors({ form: error.error })
        }
        return
      }

      // Success
      console.log('Registered successfully')

    } catch (err) {
      setErrors({ form: 'Network error. Please try again.' })
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {errors.form && <div className="alert-error">{errors.form}</div>}

      <div>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          onBlur={() => setTouched({ ...touched, email: true })}
          className={touched.email && errors.email ? 'error' : ''}
        />
        {touched.email && errors.email && <span className="error">{errors.email}</span>}
      </div>

      {/* More fields... */}
    </form>
  )
}
```

---

## Server-Side Error Handling

### Basic API Error Handling

```typescript
/**
 * @task S5T2
 * @description Server-side error handling in API routes
 */

import { handleAPIError, ValidationError, NotFoundError } from '@/lib/errors/api-errors'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    // Validate required fields
    if (!body.project_name || !body.description) {
      throw new ValidationError('Missing required fields', {
        required: ['project_name', 'description'],
        received: Object.keys(body)
      })
    }

    // Validate field types
    if (typeof body.project_name !== 'string') {
      throw new ValidationError('project_name must be a string')
    }

    // Database operation
    const { data: project, error: dbError } = await supabase
      .from('projects')
      .insert([{
        project_name: body.project_name,
        description: body.description
      }])
      .select()
      .single()

    if (dbError) {
      throw new Error(`Database error: ${dbError.message}`)
    }

    return Response.json(
      { success: true, data: project },
      { status: 201 }
    )

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

### Error Handling with Context Wrapper

```typescript
/**
 * Wrap handler to automatically catch errors
 */

import { catchAsyncErrors, validateRequired } from '@/lib/errors/api-errors'

export const POST = catchAsyncErrors(async (req: Request) => {
  const body = await req.json()

  // Validation
  validateRequired(body, ['email', 'password'])

  // API logic
  const user = await createUser(body.email, body.password)

  return Response.json({ success: true, data: user }, { status: 201 })
})
```

### Database Error Handling

```typescript
/**
 * Handle Supabase-specific errors
 */

import { DatabaseError, NotFoundError, ConflictError } from '@/lib/errors/api-errors'

export async function GET(req: Request, { params }: { params: { id: string } }) {
  try {
    const { data: project, error } = await supabase
      .from('projects')
      .select('*')
      .eq('project_id', params.id)
      .single()

    if (error) {
      // Handle specific Supabase error codes
      if (error.code === 'PGRST116') {
        throw new NotFoundError('Project', { project_id: params.id })
      }

      if (error.code === 'PGRST201') {
        throw new ConflictError('Project already exists')
      }

      throw new DatabaseError(`Database query failed: ${error.message}`, {
        code: error.code,
        details: error
      })
    }

    return Response.json({ success: true, data: project })

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

### External API Error Handling

```typescript
/**
 * Handle external API calls (Stripe, SendGrid, etc.)
 */

import { ExternalAPIError } from '@/lib/errors/api-errors'

export async function POST(req: Request) {
  try {
    const body = await req.json()

    // Call external payment processor
    const response = await fetch('https://api.stripe.com/v1/payment_intents', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.STRIPE_API_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams(body)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new ExternalAPIError(
        'Stripe',
        error.error.message,
        { errorCode: error.error.code }
      )
    }

    const result = await response.json()
    return Response.json({ success: true, data: result })

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

### Authentication Error Handling

```typescript
/**
 * Middleware for authentication
 */

import { UnauthorizedError, ForbiddenError, authenticateRequest } from '@/lib/errors/api-errors'

export async function POST(req: Request) {
  try {
    // Extract and validate token
    const token = authenticateRequest(
      Object.fromEntries(req.headers)
    )

    // Verify token (in real app)
    const decoded = verifyJWT(token)

    // Check permissions
    if (decoded.role !== 'admin') {
      throw new ForbiddenError('Only admins can perform this action', {
        userRole: decoded.role,
        required: 'admin'
      })
    }

    // API logic
    return Response.json({ success: true })

  } catch (error) {
    const apiError = handleAPIError(error)
    return Response.json(apiError.toJSON(), { status: apiError.statusCode })
  }
}
```

---

## Common Error Scenarios

### Scenario 1: User Tries to Access Non-Existent Project

**Request:**
```bash
curl -X GET https://api.valuelink.com/api/projects/VL-20260223-9999 \
  -H "Authorization: Bearer token123"
```

**Response (404):**
```json
{
  "error": "Project not found",
  "code": "NOT_FOUND",
  "statusCode": 404,
  "details": {
    "project_id": "VL-20260223-9999"
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

**Client Handling:**
```typescript
if (response.status === 404) {
  // Show "Project not found" message
  // Offer to create new project or go back
}
```

### Scenario 2: Invalid Request Data

**Request:**
```json
POST /api/projects
{
  "project_name": "My Project"
  // Missing: "description"
}
```

**Response (400):**
```json
{
  "error": "Missing required fields",
  "code": "VALIDATION_ERROR",
  "statusCode": 400,
  "details": {
    "fields": ["description"]
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

**Client Handling:**
```typescript
if (response.status === 400 && error.code === 'VALIDATION_ERROR') {
  // Highlight missing fields in form
  error.details.fields.forEach(field => {
    highlightField(field)
  })
}
```

### Scenario 3: Authentication Failure

**Request:**
```bash
curl -X POST https://api.valuelink.com/api/projects \
  -H "Authorization: Bearer invalid-token"
```

**Response (401):**
```json
{
  "error": "Invalid or expired token",
  "code": "UNAUTHORIZED",
  "statusCode": 401,
  "details": {
    "reason": "Invalid or expired token"
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

**Client Handling:**
```typescript
if (response.status === 401) {
  // Clear stored token
  localStorage.removeItem('auth_token')
  // Redirect to login
  window.location.href = '/login'
}
```

### Scenario 4: Rate Limit Exceeded

**Request:**
```bash
# 101st request in 1 minute
curl -X GET https://api.valuelink.com/api/projects
```

**Response (429):**
```json
{
  "error": "Too many requests",
  "code": "RATE_LIMIT_EXCEEDED",
  "statusCode": 429,
  "details": {
    "retryAfter": 60
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

**Client Handling:**
```typescript
if (response.status === 429) {
  const retryAfter = error.details.retryAfter || 60
  console.log(`Rate limited. Retry after ${retryAfter} seconds`)
  await new Promise(resolve => setTimeout(resolve, retryAfter * 1000))
  // Retry request
}
```

### Scenario 5: External Service Failure

**Request:**
```json
POST /api/payments
{
  "amount": 10000,
  "currency": "KRW"
}
```

**Response (502):**
```json
{
  "error": "Stripe API error: Your card was declined",
  "code": "EXTERNAL_API_ERROR",
  "statusCode": 502,
  "details": {
    "service": "Stripe",
    "originalCode": "card_declined"
  },
  "timestamp": "2026-02-23T10:30:00.000Z"
}
```

**Client Handling:**
```typescript
if (error.code === 'EXTERNAL_API_ERROR') {
  if (error.details.service === 'Stripe') {
    // Show payment-specific error message
    showError(`Payment failed: ${error.error}`)
    // Suggest alternative payment method
  }
}
```

---

## Debugging Tips

### Enable Debug Logging

```typescript
// In development, log all API errors
if (process.env.NODE_ENV === 'development') {
  window.addEventListener('unhandledrejection', event => {
    console.error('[Unhandled Promise Rejection]', event.reason)
  })
}
```

### Use Network DevTools

1. Open DevTools → Network tab
2. Look for failed requests (red)
3. Click request → Response tab to see error JSON
4. Check status code and error code

### Common Error Code Quick Reference

| Status | Code | Quick Fix |
|--------|------|-----------|
| 400 | VALIDATION_ERROR | Check input fields |
| 401 | UNAUTHORIZED | Login again |
| 403 | FORBIDDEN | Check permissions |
| 404 | NOT_FOUND | Verify resource ID |
| 409 | CONFLICT | Use different name |
| 429 | RATE_LIMIT_EXCEEDED | Wait and retry |
| 500 | DATABASE_ERROR | Retry or contact support |
| 502 | EXTERNAL_API_ERROR | Check external service status |

### Logging Errors

```typescript
// Log to monitoring service
function logError(error: APIError, context?: any) {
  console.error({
    code: error.code,
    message: error.message,
    statusCode: error.statusCode,
    timestamp: error.timestamp,
    context
  })

  // Send to external monitoring
  // sendToSentry(error, { extra: context })
}
```

---

## Best Practices

### 1. Always Validate User Input

```typescript
// ❌ Bad
const name = req.body.name
saveUser(name)

// ✅ Good
validateRequired(req.body, ['name'])
if (!isValidName(req.body.name)) {
  throw new ValidationError('Invalid name format')
}
saveUser(req.body.name)
```

### 2. Provide Specific Error Messages

```typescript
// ❌ Bad
throw new Error('Invalid input')

// ✅ Good
throw new ValidationError('Email must contain @ symbol', {
  field: 'email',
  value: email
})
```

### 3. Use Appropriate HTTP Status Codes

```typescript
// ❌ Bad - Always returning 500
return Response.json({ error: 'Not found' }, { status: 500 })

// ✅ Good - Using correct status codes
throw new NotFoundError('Project')
// Returns 404
```

### 4. Handle Errors at the Right Level

```typescript
// ❌ Bad - Generic catch in main function
try {
  const user = getUser()
  const projects = getProjects()
  const reports = getReports()
} catch (err) {
  // Don't know which operation failed
}

// ✅ Good - Handle errors where they occur
try {
  const user = getUser()
} catch (err) {
  throw new DatabaseError('Failed to fetch user')
}

try {
  const projects = getProjects()
} catch (err) {
  throw new DatabaseError('Failed to fetch projects')
}
```

### 5. Include Context in Error Details

```typescript
// ❌ Bad - No context
throw new DatabaseError('Query failed')

// ✅ Good - Include helpful context
throw new DatabaseError('Failed to insert project', {
  table: 'projects',
  operation: 'INSERT',
  projectId: 'VL-20260223-0001',
  originalError: err.message
})
```

### 6. Test Error Scenarios

```typescript
// Always test error paths
describe('Error Handling', () => {
  it('should return 404 for non-existent project', async () => {
    const response = await GET('VL-20260223-9999')
    expect(response.status).toBe(404)
    expect(response.json().code).toBe('NOT_FOUND')
  })

  it('should return 400 for invalid project ID format', async () => {
    const response = await POST({ project_id: 'invalid' })
    expect(response.status).toBe(400)
    expect(response.json().code).toBe('VALIDATION_ERROR')
  })
})
```

### 7. Never Expose Sensitive Information

```typescript
// ❌ Bad - Leaks database details
throw new Error(`Database error: ${error.sql}`)

// ✅ Good - Generic message in production
const isDev = process.env.NODE_ENV === 'development'
throw new DatabaseError(
  isDev ? error.message : 'Database operation failed',
  { originalError: isDev ? error.message : undefined }
)
```

---

## Summary

### Error Handling Checklist

- [ ] Validate all user input before processing
- [ ] Use appropriate error classes for different scenarios
- [ ] Include error codes in all API responses
- [ ] Provide context in error details
- [ ] Handle errors at the right level
- [ ] Test all error scenarios
- [ ] Don't expose sensitive information
- [ ] Log errors for debugging
- [ ] Use correct HTTP status codes
- [ ] Provide actionable error messages to clients

### Key Takeaways

1. **Errors are communication** - Use them to tell clients what went wrong and how to fix it
2. **Be specific** - "Invalid email format" is better than "Invalid input"
3. **Be consistent** - Use the same error structure for all APIs
4. **Be helpful** - Include context that helps debug the issue
5. **Be secure** - Don't leak sensitive information in error messages

---

**For more information, see:**
- `/lib/errors/api-errors.ts` - Error class implementations
- `/tests/integration/edge-cases.test.ts` - Error handling tests
- `Task S5T2 Instruction` - Full task specification
