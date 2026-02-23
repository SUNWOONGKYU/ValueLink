'use client'

export interface LoadingIndicatorProps {
  message?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingIndicator({ message = '평가 진행 중...', size = 'md' }: LoadingIndicatorProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16',
  }

  return (
    <div className="flex flex-col items-center justify-center gap-4" role="status" aria-live="polite">
      {/* Spinner */}
      <div
        className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}
        aria-hidden="true"
      />

      {/* Message */}
      {message && (
        <p className="text-sm text-gray-600 font-medium">{message}</p>
      )}

      {/* Screen reader text */}
      <span className="sr-only">{message}</span>
    </div>
  )
}
