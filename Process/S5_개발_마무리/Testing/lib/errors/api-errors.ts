/**
 * @task S5T2
 * @description API Error Classes - Comprehensive Error Handling for ValueLink Platform
 * @version 1.0
 */

/**
 * Base Error Class for all API errors
 *
 * Provides standardized error handling with:
 * - Unique error codes
 * - HTTP status codes
 * - Additional error details
 * - JSON serialization
 */
export class APIError extends Error {
  public code: string
  public statusCode: number
  public details?: Record<string, any>
  public timestamp: string

  constructor(
    message: string,
    code: string,
    statusCode: number,
    details?: Record<string, any>
  ) {
    super(message)
    this.name = 'APIError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
    this.timestamp = new Date().toISOString()

    // Maintain proper prototype chain
    Object.setPrototypeOf(this, APIError.prototype)
  }

  /**
   * Convert error to JSON for API response
   */
  toJSON() {
    return {
      error: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: this.timestamp
    }
  }

  /**
   * Convert error to string
   */
  toString(): string {
    return `${this.name}: [${this.code}] ${this.message}`
  }
}

/**
 * Validation Error - HTTP 400
 *
 * Thrown when request data fails validation
 *
 * @example
 * throw new ValidationError('Invalid email format', {
 *   field: 'email',
 *   value: 'invalid-email',
 *   rule: 'email-format'
 * })
 */
export class ValidationError extends APIError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'VALIDATION_ERROR', 400, details)
    this.name = 'ValidationError'
    Object.setPrototypeOf(this, ValidationError.prototype)
  }
}

/**
 * Not Found Error - HTTP 404
 *
 * Thrown when requested resource doesn't exist
 *
 * @example
 * throw new NotFoundError('Project', { project_id: 'VL-20260223-0001' })
 */
export class NotFoundError extends APIError {
  constructor(
    resource: string,
    details?: Record<string, any>
  ) {
    const message = `${resource} not found`
    super(message, 'NOT_FOUND', 404, details)
    this.name = 'NotFoundError'
    Object.setPrototypeOf(this, NotFoundError.prototype)
  }
}

/**
 * Unauthorized Error - HTTP 401
 *
 * Thrown when authentication fails or credentials are invalid
 *
 * @example
 * throw new UnauthorizedError('Invalid JWT token')
 */
export class UnauthorizedError extends APIError {
  constructor(message: string = 'Unauthorized access') {
    super(message, 'UNAUTHORIZED', 401, { reason: message })
    this.name = 'UnauthorizedError'
    Object.setPrototypeOf(this, UnauthorizedError.prototype)
  }
}

/**
 * Forbidden Error - HTTP 403
 *
 * Thrown when user doesn't have permission to access resource
 *
 * @example
 * throw new ForbiddenError('You do not have permission to delete this project')
 */
export class ForbiddenError extends APIError {
  constructor(
    message: string = 'Access forbidden',
    details?: Record<string, any>
  ) {
    super(message, 'FORBIDDEN', 403, details)
    this.name = 'ForbiddenError'
    Object.setPrototypeOf(this, ForbiddenError.prototype)
  }
}

/**
 * Database Error - HTTP 500
 *
 * Thrown when database operations fail
 *
 * @example
 * throw new DatabaseError('Failed to insert project', {
 *   operation: 'INSERT',
 *   table: 'projects',
 *   originalError: err.message
 * })
 */
export class DatabaseError extends APIError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'DATABASE_ERROR', 500, details)
    this.name = 'DatabaseError'
    Object.setPrototypeOf(this, DatabaseError.prototype)
  }
}

/**
 * External API Error - HTTP 502
 *
 * Thrown when external service calls fail (Stripe, SendGrid, OpenAI, etc.)
 *
 * @example
 * throw new ExternalAPIError('Stripe', 'Payment processing failed: insufficient funds')
 */
export class ExternalAPIError extends APIError {
  constructor(
    service: string,
    message: string,
    details?: Record<string, any>
  ) {
    const fullMessage = `${service} API error: ${message}`
    super(fullMessage, 'EXTERNAL_API_ERROR', 502, {
      service,
      ...details
    })
    this.name = 'ExternalAPIError'
    Object.setPrototypeOf(this, ExternalAPIError.prototype)
  }
}

/**
 * Rate Limit Error - HTTP 429
 *
 * Thrown when rate limit is exceeded
 *
 * @example
 * throw new RateLimitError('Too many requests', { retryAfter: 60 })
 */
export class RateLimitError extends APIError {
  constructor(
    message: string = 'Too many requests',
    retryAfter?: number
  ) {
    super(message, 'RATE_LIMIT_EXCEEDED', 429, { retryAfter })
    this.name = 'RateLimitError'
    Object.setPrototypeOf(this, RateLimitError.prototype)
  }
}

/**
 * Conflict Error - HTTP 409
 *
 * Thrown when request conflicts with existing state
 *
 * @example
 * throw new ConflictError('Project with this name already exists')
 */
export class ConflictError extends APIError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'CONFLICT', 409, details)
    this.name = 'ConflictError'
    Object.setPrototypeOf(this, ConflictError.prototype)
  }
}

/**
 * Request Timeout Error - HTTP 408
 *
 * Thrown when request times out
 *
 * @example
 * throw new RequestTimeoutError('Database query timed out after 30 seconds')
 */
export class RequestTimeoutError extends APIError {
  constructor(
    message: string = 'Request timeout',
    details?: Record<string, any>
  ) {
    super(message, 'REQUEST_TIMEOUT', 408, details)
    this.name = 'RequestTimeoutError'
    Object.setPrototypeOf(this, RequestTimeoutError.prototype)
  }
}

/**
 * Bad Request Error - HTTP 400
 *
 * Thrown for malformed requests
 *
 * @example
 * throw new BadRequestError('Invalid query parameters')
 */
export class BadRequestError extends APIError {
  constructor(
    message: string,
    details?: Record<string, any>
  ) {
    super(message, 'BAD_REQUEST', 400, details)
    this.name = 'BadRequestError'
    Object.setPrototypeOf(this, BadRequestError.prototype)
  }
}

// ============================================================================
// ERROR HANDLER UTILITIES
// ============================================================================

/**
 * Error code mapping from external services to internal error codes
 */
const ERROR_CODE_MAP: Record<string, string> = {
  'PGRST116': 'NOT_FOUND',
  'PGRST100': 'DATABASE_ERROR',
  'PGRST201': 'CONFLICT',
  'PGRST403': 'UNAUTHORIZED',
  'ECONNREFUSED': 'DATABASE_ERROR',
  'ENOTFOUND': 'EXTERNAL_API_ERROR',
  'ETIMEDOUT': 'REQUEST_TIMEOUT',
  'ECONNRESET': 'EXTERNAL_API_ERROR'
}

/**
 * Centralized error handler for API routes
 *
 * Converts various error types to standardized APIError instances
 *
 * @param error - The error to handle
 * @returns APIError instance
 *
 * @example
 * try {
 *   // API logic
 * } catch (error) {
 *   const apiError = handleAPIError(error)
 *   return Response.json(apiError.toJSON(), { status: apiError.statusCode })
 * }
 */
export function handleAPIError(error: unknown): APIError {
  // Already an APIError
  if (error instanceof APIError) {
    return error
  }

  // Handle Error instances
  if (error instanceof Error) {
    // Supabase specific errors
    if ('code' in error) {
      const code = (error as any).code
      if (code === 'PGRST116') {
        return new NotFoundError('Resource', { originalCode: code })
      }
      if (code === 'PGRST201') {
        return new ConflictError('Resource already exists', { originalCode: code })
      }
      if (code && code.startsWith('PGRST')) {
        return new DatabaseError(`Supabase error: ${error.message}`, { code })
      }
    }

    // Network errors
    if (error.message.includes('timeout') || error.message.includes('ETIMEDOUT')) {
      return new RequestTimeoutError('Request exceeded timeout', { originalMessage: error.message })
    }

    if (error.message.includes('Connection refused') || error.message.includes('ECONNREFUSED')) {
      return new DatabaseError('Database connection failed', { originalMessage: error.message })
    }

    if (error.message.includes('JSON') || error.message.includes('parse')) {
      return new BadRequestError('Invalid JSON payload', { originalMessage: error.message })
    }

    // Generic error
    return new APIError(error.message, 'INTERNAL_ERROR', 500, { type: error.constructor.name })
  }

  // Handle unknown error types
  return new APIError('An unexpected error occurred', 'UNKNOWN_ERROR', 500)
}

/**
 * Async error wrapper for Next.js API routes
 *
 * Catches errors and converts them to proper API responses
 *
 * @example
 * export const POST = catchAsyncErrors(async (req: Request) => {
 *   const data = await req.json()
 *   // API logic
 *   return Response.json({ success: true })
 * })
 */
export function catchAsyncErrors(
  handler: (req: Request) => Promise<Response>
) {
  return async (req: Request): Promise<Response> => {
    try {
      return await handler(req)
    } catch (error) {
      const apiError = handleAPIError(error)
      return Response.json(apiError.toJSON(), { status: apiError.statusCode })
    }
  }
}

/**
 * Error response formatter for consistency
 *
 * @example
 * const errorResponse = formatErrorResponse(error)
 * return Response.json(errorResponse, { status: error.statusCode })
 */
export function formatErrorResponse(error: APIError) {
  return {
    success: false,
    error: {
      message: error.message,
      code: error.code,
      statusCode: error.statusCode,
      ...(error.details && { details: error.details }),
      timestamp: error.timestamp
    }
  }
}

/**
 * Success response formatter for consistency
 *
 * @example
 * const successResponse = formatSuccessResponse(data)
 * return Response.json(successResponse)
 */
export function formatSuccessResponse(data: any, meta?: Record<string, any>) {
  return {
    success: true,
    data,
    ...(meta && { meta }),
    timestamp: new Date().toISOString()
  }
}

/**
 * Validate required fields in object
 *
 * @throws ValidationError if required fields are missing
 *
 * @example
 * validateRequired(body, ['email', 'password'])
 */
export function validateRequired(
  obj: Record<string, any>,
  fields: string[]
): void {
  const missing: string[] = []

  for (const field of fields) {
    if (!obj[field] && obj[field] !== 0 && obj[field] !== false) {
      missing.push(field)
    }
  }

  if (missing.length > 0) {
    throw new ValidationError('Missing required fields', {
      fields: missing
    })
  }
}

/**
 * Validate email format
 *
 * @throws ValidationError if email is invalid
 */
export function validateEmail(email: string): void {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format', { email })
  }
}

/**
 * Validate project ID format (VL-YYYYMMDD-XXXX)
 *
 * @throws ValidationError if project ID is invalid
 */
export function validateProjectId(projectId: string): void {
  const projectIdRegex = /^VL-\d{8}-\d{4}$/

  if (!projectIdRegex.test(projectId)) {
    throw new ValidationError('Invalid project_id format', {
      projectId,
      expectedFormat: 'VL-YYYYMMDD-XXXX'
    })
  }
}

/**
 * Validate URL format
 *
 * @throws ValidationError if URL is invalid
 */
export function validateURL(url: string): void {
  try {
    new URL(url)
  } catch {
    throw new ValidationError('Invalid URL format', { url })
  }
}

/**
 * Authenticate user from request headers
 *
 * @throws UnauthorizedError if authentication fails
 */
export function authenticateRequest(headers: Record<string, string>): string {
  const authHeader = headers['authorization']

  if (!authHeader) {
    throw new UnauthorizedError('Missing authorization header')
  }

  const [scheme, token] = authHeader.split(' ')

  if (scheme !== 'Bearer' || !token) {
    throw new UnauthorizedError('Invalid authorization header format')
  }

  // In real implementation, verify JWT token here
  if (token.length < 20) {
    throw new UnauthorizedError('Invalid or expired token')
  }

  return token
}

/**
 * Check user permission
 *
 * @throws ForbiddenError if user lacks permission
 */
export function requirePermission(
  userRole: string,
  requiredRoles: string[]
): void {
  if (!requiredRoles.includes(userRole)) {
    throw new ForbiddenError('Insufficient permissions', {
      userRole,
      requiredRoles
    })
  }
}

// ============================================================================
// ERROR LOGGER
// ============================================================================

/**
 * Log errors to console/monitoring service
 */
export class ErrorLogger {
  static log(error: APIError, context?: Record<string, any>): void {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      name: error.name,
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      details: error.details,
      context
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('[APIError]', JSON.stringify(logEntry, null, 2))
    }

    // In production, send to monitoring service (Sentry, DataDog, etc.)
    // await monitoringService.captureException(error, { extra: context })
  }

  static logWarning(message: string, details?: Record<string, any>): void {
    console.warn('[Warning]', { message, details, timestamp: new Date().toISOString() })
  }

  static logInfo(message: string, details?: Record<string, any>): void {
    if (process.env.NODE_ENV === 'development') {
      console.log('[Info]', { message, details, timestamp: new Date().toISOString() })
    }
  }
}

export default {
  // Error classes
  APIError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  DatabaseError,
  ExternalAPIError,
  RateLimitError,
  ConflictError,
  RequestTimeoutError,
  BadRequestError,

  // Utilities
  handleAPIError,
  catchAsyncErrors,
  formatErrorResponse,
  formatSuccessResponse,
  validateRequired,
  validateEmail,
  validateProjectId,
  validateURL,
  authenticateRequest,
  requirePermission,
  ErrorLogger
}
