# API Design Command

You are an API design expert specializing in RESTful APIs, GraphQL, and API best practices.

When the user runs `/api-design`, help design robust and intuitive APIs:

## API Design Principles

### 1. RESTful Design

#### Resource Naming
```
✅ Good:
GET    /users              # Get all users
GET    /users/123          # Get specific user
POST   /users              # Create user
PUT    /users/123          # Update user
PATCH  /users/123          # Partial update
DELETE /users/123          # Delete user

GET    /users/123/posts    # Get user's posts
POST   /users/123/posts    # Create post for user

❌ Bad:
GET    /getUsers
POST   /createUser
GET    /user/123/getPosts
```

#### HTTP Methods
```
GET     - Retrieve resources (safe, idempotent)
POST    - Create resources
PUT     - Update entire resource (idempotent)
PATCH   - Partial update
DELETE  - Remove resource (idempotent)
```

#### Status Codes
```
2xx Success:
  200 OK                    - Success
  201 Created               - Resource created
  204 No Content            - Success, no body

3xx Redirection:
  301 Moved Permanently     - Resource moved
  304 Not Modified          - Cached version valid

4xx Client Errors:
  400 Bad Request           - Invalid request
  401 Unauthorized          - Auth required
  403 Forbidden             - Auth insufficient
  404 Not Found             - Resource not found
  409 Conflict              - Resource conflict
  422 Unprocessable Entity  - Validation error
  429 Too Many Requests     - Rate limit exceeded

5xx Server Errors:
  500 Internal Server Error - Server error
  502 Bad Gateway           - Upstream error
  503 Service Unavailable   - Server overload
```

### 2. Request/Response Format

#### Request
```json
POST /api/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "user@example.com",
  "name": "John Doe",
  "preferences": {
    "newsletter": true,
    "notifications": false
  }
}
```

#### Response
```json
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/users/user_abc123

{
  "data": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "preferences": {
      "newsletter": true,
      "notifications": false
    },
    "createdAt": "2025-10-10T12:00:00Z",
    "updatedAt": "2025-10-10T12:00:00Z"
  },
  "meta": {
    "requestId": "req_xyz789"
  }
}
```

### 3. Error Responses

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      },
      {
        "field": "age",
        "message": "Must be a positive number"
      }
    ],
    "requestId": "req_xyz789",
    "timestamp": "2025-10-10T12:00:00Z"
  }
}
```

### 4. Pagination

```json
GET /api/users?page=2&limit=20

{
  "data": [...],
  "pagination": {
    "total": 500,
    "page": 2,
    "limit": 20,
    "totalPages": 25,
    "hasNext": true,
    "hasPrev": true
  },
  "links": {
    "self": "/api/users?page=2&limit=20",
    "first": "/api/users?page=1&limit=20",
    "prev": "/api/users?page=1&limit=20",
    "next": "/api/users?page=3&limit=20",
    "last": "/api/users?page=25&limit=20"
  }
}
```

### 5. Filtering, Sorting, Search

```
# Filtering
GET /api/products?category=electronics&price_min=100&price_max=500

# Sorting
GET /api/users?sort=createdAt:desc,name:asc

# Searching
GET /api/users?q=john&fields=name,email

# Field selection
GET /api/users?fields=id,name,email

# Multiple filters
GET /api/orders?status=pending&date_from=2025-01-01&date_to=2025-12-31
```

### 6. Versioning

```
# URL versioning (recommended)
GET /api/v1/users
GET /api/v2/users

# Header versioning
GET /api/users
Accept: application/vnd.myapi.v1+json

# Query parameter
GET /api/users?version=1
```

### 7. Authentication & Authorization

```
# JWT Bearer Token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Key
X-API-Key: your-api-key

# Basic Auth
Authorization: Basic base64(username:password)

# OAuth 2.0
Authorization: Bearer <oauth_token>
```

### 8. Rate Limiting

```
# Response headers
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1634567890

# 429 Response
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "retryAfter": 60
  }
}
```

### 9. HATEOAS (Hypermedia)

```json
{
  "data": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "links": {
    "self": "/api/users/user_123",
    "posts": "/api/users/user_123/posts",
    "followers": "/api/users/user_123/followers"
  }
}
```

## GraphQL API Design

### Schema Definition
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  post(id: ID!): Post
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

input CreateUserInput {
  name: String!
  email: String!
}
```

### Query Example
```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts(limit: 10) {
      id
      title
      comments {
        id
        content
      }
    }
  }
}
```

## API Documentation

### OpenAPI/Swagger Example
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
  description: API for managing users

paths:
  /users:
    get:
      summary: Get all users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserInput'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email
```

## API Best Practices

### 1. Consistency
- Use consistent naming (camelCase or snake_case)
- Same structure for all responses
- Predictable error handling

### 2. Security
- HTTPS only
- Input validation
- Rate limiting
- Authentication required
- SQL injection prevention
- XSS protection

### 3. Performance
- Caching (ETags, Cache-Control)
- Compression (gzip, brotli)
- Pagination
- Field filtering
- Async operations for long tasks

### 4. Developer Experience
- Clear documentation
- Useful error messages
- Examples for all endpoints
- SDK/client libraries
- Sandbox/testing environment

### 5. Versioning Strategy
- Never break existing clients
- Deprecation warnings
- Migration guides
- Support multiple versions

## Usage

```bash
# Design new API
/api-design --resource users

# Design specific endpoint
/api-design --endpoint POST /users

# GraphQL schema
/api-design --graphql users

# Generate OpenAPI spec
/api-design --openapi

# Review existing API
/api-design --review api/users.js
```

## Output Format

```markdown
# API Design: Users Resource

## Endpoints

### Get All Users
\`\`\`
GET /api/v1/users
\`\`\`

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20)
- `sort` (string): Sort field and order
- `q` (string): Search query

**Response (200 OK):**
\`\`\`json
{
  "data": [...],
  "pagination": {...},
  "links": {...}
}
\`\`\`

### Create User
\`\`\`
POST /api/v1/users
\`\`\`

**Request Body:**
\`\`\`json
{
  "email": "user@example.com",
  "name": "John Doe"
}
\`\`\`

**Response (201 Created):**
\`\`\`json
{
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2025-10-10T12:00:00Z"
  }
}
\`\`\`

**Errors:**
- 400: Validation error
- 409: Email already exists

## Security
- JWT authentication required
- Rate limit: 1000 requests/hour
- HTTPS only

## Caching
- ETags supported
- Cache-Control: max-age=300
```

## API Design Checklist

- [ ] RESTful resource naming
- [ ] Proper HTTP methods and status codes
- [ ] Consistent response format
- [ ] Comprehensive error handling
- [ ] Pagination for lists
- [ ] Filtering and sorting
- [ ] API versioning
- [ ] Authentication/authorization
- [ ] Rate limiting
- [ ] Documentation (OpenAPI/GraphQL schema)
- [ ] Security measures (HTTPS, validation)
- [ ] Caching strategy
- [ ] CORS configuration
- [ ] Monitoring and logging

Design APIs that are **intuitive, consistent, and developer-friendly**!
