# UI Builder Skill

**PoliticianFinder UI/UX 컴포넌트 개발 전문 스킬**

---

## 전문 분야

React, Next.js, TypeScript, Tailwind CSS를 사용한 사용자 인터페이스 구축

---

## 핵심 역할

1. **컴포넌트 개발**: 재사용 가능한 React 컴포넌트
2. **페이지 구성**: Next.js App Router 페이지
3. **스타일링**: Tailwind CSS 기반 디자인
4. **상태 관리**: React Hooks, Context
5. **접근성**: WCAG 2.1 준수

---

## 디자인 시스템

### 컬러 팔레트
```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          500: '#64748b',
          600: '#475569',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      }
    }
  }
}
```

### 타이포그래피
```css
h1: text-4xl font-bold
h2: text-3xl font-semibold
h3: text-2xl font-semibold
body: text-base
small: text-sm
```

---

## 컴포넌트 템플릿

### 1. Button 컴포넌트
```typescript
// components/ui/Button.tsx
'use client';

import { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  isLoading?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  isLoading,
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = 'rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';

  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-secondary-500 text-white hover:bg-secondary-600 focus:ring-secondary-500',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50',
    ghost: 'text-primary-600 hover:bg-primary-50',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        (disabled || isLoading) && 'opacity-50 cursor-not-allowed',
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Loading...</span>
        </span>
      ) : (
        children
      )}
    </button>
  );
}
```

### 2. Card 컴포넌트
```typescript
// components/ui/Card.tsx
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export function Card({ children, className, hover = false }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-md p-6',
        hover && 'transition-shadow hover:shadow-lg cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('mb-4', className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={cn('text-2xl font-semibold', className)}>{children}</h3>;
}

export function CardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('text-gray-600', className)}>{children}</div>;
}
```

### 3. Input 컴포넌트
```typescript
// components/ui/Input.tsx
import { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500',
            error ? 'border-error' : 'border-gray-300',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-error">{error}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

### 4. 정치인 카드 컴포넌트
```typescript
// components/politicians/PoliticianCard.tsx
'use client';

import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Politician } from '@/types/politician';

interface PoliticianCardProps {
  politician: Politician;
}

export function PoliticianCard({ politician }: PoliticianCardProps) {
  return (
    <Link href={`/politicians/${politician.id}`}>
      <Card hover>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
              {politician.avatar_url ? (
                <img
                  src={politician.avatar_url}
                  alt={politician.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <span className="text-2xl font-bold text-gray-500">
                  {politician.name[0]}
                </span>
              )}
            </div>
            <div>
              <CardTitle className="text-xl">{politician.name}</CardTitle>
              <p className="text-sm text-gray-500">{politician.position}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm">
                <span className="font-medium">정당:</span> {politician.party}
              </p>
              <p className="text-sm">
                <span className="font-medium">지역:</span> {politician.region}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-primary-600">
                {politician.avg_rating?.toFixed(1) || 'N/A'}
              </div>
              <p className="text-xs text-gray-500">평균 평점</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
```

### 5. 페이지네이션 컴포넌트
```typescript
// components/ui/Pagination.tsx
'use client';

import { Button } from './Button';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="flex items-center justify-center gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        이전
      </Button>

      {pages.map(page => {
        // 현재 페이지 근처만 표시
        if (
          page === 1 ||
          page === totalPages ||
          (page >= currentPage - 2 && page <= currentPage + 2)
        ) {
          return (
            <Button
              key={page}
              variant={page === currentPage ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => onPageChange(page)}
            >
              {page}
            </Button>
          );
        }

        // "..." 표시
        if (page === currentPage - 3 || page === currentPage + 3) {
          return <span key={page} className="px-2">...</span>;
        }

        return null;
      })}

      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        다음
      </Button>
    </div>
  );
}
```

---

## 페이지 템플릿

### 정치인 목록 페이지
```typescript
// app/politicians/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { PoliticianCard } from '@/components/politicians/PoliticianCard';
import { Pagination } from '@/components/ui/Pagination';
import { Politician } from '@/types/politician';

export default function PoliticiansPage() {
  const [politicians, setPoliticians] = useState<Politician[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchPoliticians(currentPage);
  }, [currentPage]);

  async function fetchPoliticians(page: number) {
    setLoading(true);
    try {
      const res = await fetch(`/api/politicians?page=${page}&limit=12`);
      const data = await res.json();

      setPoliticians(data.data);
      setTotalPages(data.pagination.totalPages);
    } catch (error) {
      console.error('Failed to fetch politicians:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">정치인 목록</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {politicians.map(politician => (
          <PoliticianCard key={politician.id} politician={politician} />
        ))}
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
```

### 정치인 상세 페이지
```typescript
// app/politicians/[id]/page.tsx
import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';

export default async function PoliticianDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = createClient();

  const { data: politician, error } = await supabase
    .from('politicians')
    .select('*')
    .eq('id', params.id)
    .single();

  if (error || !politician) {
    notFound();
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="flex items-start gap-6 mb-8">
            <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center">
              {politician.avatar_url ? (
                <img
                  src={politician.avatar_url}
                  alt={politician.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                <span className="text-5xl font-bold text-gray-500">
                  {politician.name[0]}
                </span>
              )}
            </div>

            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-2">{politician.name}</h1>
              <p className="text-xl text-gray-600 mb-4">{politician.position}</p>
              <div className="flex gap-4">
                <span className="px-4 py-2 bg-blue-100 text-blue-800 rounded-full">
                  {politician.party}
                </span>
                <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full">
                  {politician.region}
                </span>
              </div>
            </div>

            <div className="text-center">
              <div className="text-5xl font-bold text-primary-600">
                {politician.avg_rating?.toFixed(1) || 'N/A'}
              </div>
              <p className="text-sm text-gray-500">평균 평점</p>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">약력</h2>
            <p className="text-gray-700 leading-relaxed">
              {politician.bio || '약력 정보가 없습니다.'}
            </p>
          </div>

          {/* 추가 섹션: 공약, 활동, 평가 등 */}
        </div>
      </div>
    </div>
  );
}
```

---

## 레이아웃 및 네비게이션

### 루트 레이아웃
```typescript
// app/layout.tsx
import { Inter } from 'next/font/google';
import './globals.css';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'PoliticianFinder - AI 기반 정치인 평가 플랫폼',
  description: 'AI가 분석한 정치인 정보를 확인하세요',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <Navbar />
        <main className="min-h-screen bg-gray-50">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

### 네비게이션 바
```typescript
// components/layout/Navbar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/Button';

export function Navbar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: '홈' },
    { href: '/politicians', label: '정치인' },
    { href: '/about', label: '소개' },
  ];

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="text-2xl font-bold text-primary-600">
            PoliticianFinder
          </Link>

          <div className="flex items-center gap-6">
            {links.map(link => (
              <Link
                key={link.href}
                href={link.href}
                className={`hover:text-primary-600 transition-colors ${
                  pathname === link.href ? 'text-primary-600 font-semibold' : 'text-gray-600'
                }`}
              >
                {link.label}
              </Link>
            ))}

            <Button size="sm">로그인</Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
```

---

## 반응형 디자인

### 브레이크포인트
```typescript
// Tailwind 기본 브레이크포인트 사용
sm: '640px'   // 모바일
md: '768px'   // 태블릿
lg: '1024px'  // 데스크톱
xl: '1280px'  // 대형 데스크톱

// 사용 예
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

---

## 접근성 (A11y)

### 필수 사항
```typescript
// 1. alt 텍스트
<img src="..." alt="정치인 홍길동의 프로필 사진" />

// 2. aria-label
<button aria-label="메뉴 열기">
  <MenuIcon />
</button>

// 3. 키보드 네비게이션
<button onKeyDown={(e) => e.key === 'Enter' && handleClick()}>

// 4. 포커스 관리
<input className="focus:outline-none focus:ring-2 focus:ring-primary-500" />

// 5. 시맨틱 HTML
<main>, <nav>, <article>, <section> 사용
```

---

## 로딩 및 에러 상태

### 로딩 스피너
```typescript
// components/ui/LoadingSpinner.tsx
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex justify-center items-center">
      <div className={`animate-spin rounded-full border-b-2 border-primary-600 ${sizes[size]}`}></div>
    </div>
  );
}
```

### 에러 메시지
```typescript
// components/ui/ErrorMessage.tsx
export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="bg-error/10 border border-error text-error px-4 py-3 rounded-lg">
      <p className="font-medium">오류 발생</p>
      <p className="text-sm">{message}</p>
    </div>
  );
}
```

---

## 작업 완료 보고 템플릿

```markdown
=== UI 구축 완료 보고 ===

## 구현 컴포넌트
- Button: 재사용 가능한 버튼 (4가지 variant)
- Card: 카드 레이아웃
- Input: 폼 입력
- PoliticianCard: 정치인 카드
- Pagination: 페이지네이션

## 구현 페이지
- /politicians: 정치인 목록 페이지
- /politicians/[id]: 정치인 상세 페이지

## 기능
- 반응형 디자인 (모바일, 태블릿, 데스크톱)
- 로딩 상태 표시
- 에러 핸들링
- 접근성 준수 (WCAG 2.1)

## 생성 파일
- components/ui/Button.tsx
- components/ui/Card.tsx
- components/politicians/PoliticianCard.tsx
- app/politicians/page.tsx
- app/politicians/[id]/page.tsx

## 스크린샷
[여기에 스크린샷 경로]

## 다음 단계
- 다크 모드 지원
- 애니메이션 추가
- 성능 최적화 (React.memo, useMemo)
```

---

**이 스킬을 사용하면 일관되고 접근성 높은 UI를 빠르게 구축할 수 있습니다.**
