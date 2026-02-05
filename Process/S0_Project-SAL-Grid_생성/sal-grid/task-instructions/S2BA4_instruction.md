# S2BA4: AI Client & Email Services

## Task 정보

- **Task ID**: S2BA4
- **Task Name**: AI 클라이언트 및 이메일 서비스
- **Stage**: S2 (Core Platform - 개발 1차)
- **Area**: BA (Backend APIs)
- **Dependencies**: S1BI1 (환경변수 설정)
- **Task Agent**: backend-developer
- **Verification Agent**: code-reviewer

---

## Task 목표

Claude/Gemini/GPT-4 AI 통합 클라이언트 및 이메일 발송 서비스(Resend) 구현

---

## 상세 지시사항

### 1. AI 클라이언트

**파일**: `lib/ai/client.ts`

```typescript
export type AIProvider = 'claude' | 'gemini' | 'gpt'

export interface AIMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface AIResponse {
  content: string
  provider: AIProvider
  tokens_used?: number
}

export class AIClient {
  async chat(
    provider: AIProvider,
    messages: AIMessage[],
    options?: { temperature?: number; max_tokens?: number }
  ): Promise<AIResponse> {
    switch (provider) {
      case 'claude':
        return this.callClaude(messages, options)
      case 'gemini':
        return this.callGemini(messages, options)
      case 'gpt':
        return this.callGPT(messages, options)
      default:
        throw new Error(`Unsupported AI provider: ${provider}`)
    }
  }

  private async callClaude(
    messages: AIMessage[],
    options?: { temperature?: number; max_tokens?: number }
  ): Promise<AIResponse> {
    // Claude API 호출 (60% 사용량)
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY!,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-3-5-sonnet-20241022',
        messages: messages.filter((m) => m.role !== 'system'),
        system: messages.find((m) => m.role === 'system')?.content,
        temperature: options?.temperature || 0.7,
        max_tokens: options?.max_tokens || 4096,
      }),
    })

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.statusText}`)
    }

    const data = await response.json()

    return {
      content: data.content[0].text,
      provider: 'claude',
      tokens_used: data.usage.output_tokens,
    }
  }

  private async callGemini(
    messages: AIMessage[],
    options?: { temperature?: number; max_tokens?: number }
  ): Promise<AIResponse> {
    // Gemini API 호출 (20% 사용량)
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${process.env.GOOGLE_AI_API_KEY}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: messages.map((m) => ({
            role: m.role === 'assistant' ? 'model' : 'user',
            parts: [{ text: m.content }],
          })),
          generationConfig: {
            temperature: options?.temperature || 0.7,
            maxOutputTokens: options?.max_tokens || 4096,
          },
        }),
      }
    )

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`)
    }

    const data = await response.json()

    return {
      content: data.candidates[0].content.parts[0].text,
      provider: 'gemini',
    }
  }

  private async callGPT(
    messages: AIMessage[],
    options?: { temperature?: number; max_tokens?: number }
  ): Promise<AIResponse> {
    // OpenAI GPT API 호출 (20% 사용량)
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4-turbo-preview',
        messages,
        temperature: options?.temperature || 0.7,
        max_tokens: options?.max_tokens || 4096,
      }),
    })

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`)
    }

    const data = await response.json()

    return {
      content: data.choices[0].message.content,
      provider: 'gpt',
      tokens_used: data.usage.completion_tokens,
    }
  }

  // AI 승인 포인트 검증
  async validateApproval(
    provider: AIProvider,
    projectData: any
  ): Promise<{ approved: boolean; reason: string }> {
    const messages: AIMessage[] = [
      {
        role: 'system',
        content: 'You are an expert accountant reviewing financial valuation data.',
      },
      {
        role: 'user',
        content: `Please review the following valuation data and approve or reject:

${JSON.stringify(projectData, null, 2)}

Provide a JSON response with { "approved": boolean, "reason": string }`,
      },
    ]

    const response = await this.chat(provider, messages)

    try {
      return JSON.parse(response.content)
    } catch (error) {
      return { approved: false, reason: 'Failed to parse AI response' }
    }
  }
}
```

---

### 2. 이메일 서비스

**파일**: `lib/email/sender.ts`

```typescript
export interface EmailOptions {
  to: string | string[]
  subject: string
  html: string
  from?: string
}

export class EmailSender {
  private fromEmail: string = 'noreply@valuation.ai.kr'

  async send(options: EmailOptions): Promise<boolean> {
    try {
      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        },
        body: JSON.stringify({
          from: options.from || this.fromEmail,
          to: Array.isArray(options.to) ? options.to : [options.to],
          subject: options.subject,
          html: options.html,
        }),
      })

      if (!response.ok) {
        console.error('Resend API error:', await response.text())
        return false
      }

      return true
    } catch (error) {
      console.error('Email send error:', error)
      return false
    }
  }

  // 프로젝트 생성 알림
  async sendProjectCreatedEmail(
    userEmail: string,
    projectName: string
  ): Promise<boolean> {
    const html = `
      <h1>프로젝트가 생성되었습니다</h1>
      <p>안녕하세요,</p>
      <p><strong>${projectName}</strong> 프로젝트가 성공적으로 생성되었습니다.</p>
      <p>진행 상황을 확인하려면 로그인해주세요.</p>
      <br>
      <p>감사합니다,<br>ValueLink 팀</p>
    `

    return this.send({
      to: userEmail,
      subject: `[ValueLink] ${projectName} 프로젝트 생성 완료`,
      html,
    })
  }

  // 승인 요청 알림
  async sendApprovalRequestEmail(
    accountantEmail: string,
    projectName: string,
    stepNumber: number
  ): Promise<boolean> {
    const html = `
      <h1>승인 요청</h1>
      <p>안녕하세요,</p>
      <p><strong>${projectName}</strong> 프로젝트의 Step ${stepNumber} 승인이 필요합니다.</p>
      <p>관리자 페이지에서 확인해주세요.</p>
      <br>
      <p>감사합니다,<br>ValueLink 팀</p>
    `

    return this.send({
      to: accountantEmail,
      subject: `[ValueLink] 승인 요청 - ${projectName} (Step ${stepNumber})`,
      html,
    })
  }

  // 보고서 완료 알림
  async sendReportCompletedEmail(
    userEmail: string,
    projectName: string,
    downloadUrl: string
  ): Promise<boolean> {
    const html = `
      <h1>평가 보고서가 완성되었습니다</h1>
      <p>안녕하세요,</p>
      <p><strong>${projectName}</strong> 프로젝트의 평가 보고서가 완성되었습니다.</p>
      <p><a href="${downloadUrl}">보고서 다운로드</a></p>
      <br>
      <p>감사합니다,<br>ValueLink 팀</p>
    `

    return this.send({
      to: userEmail,
      subject: `[ValueLink] ${projectName} 평가 보고서 완성`,
      html,
    })
  }
}
```

---

### 3. 알림 디스패처

**파일**: `lib/notifications/service.ts`

```typescript
import { EmailSender } from '@/lib/email/sender'

export type NotificationType =
  | 'project_created'
  | 'approval_required'
  | 'report_completed'
  | 'payment_confirmed'

export interface NotificationPayload {
  type: NotificationType
  recipient: string
  data: Record<string, any>
}

export class NotificationService {
  private emailSender = new EmailSender()

  async dispatch(notification: NotificationPayload): Promise<boolean> {
    switch (notification.type) {
      case 'project_created':
        return this.emailSender.sendProjectCreatedEmail(
          notification.recipient,
          notification.data.projectName
        )

      case 'approval_required':
        return this.emailSender.sendApprovalRequestEmail(
          notification.recipient,
          notification.data.projectName,
          notification.data.stepNumber
        )

      case 'report_completed':
        return this.emailSender.sendReportCompletedEmail(
          notification.recipient,
          notification.data.projectName,
          notification.data.downloadUrl
        )

      default:
        console.error(`Unknown notification type: ${notification.type}`)
        return false
    }
  }

  async dispatchMultiple(
    notifications: NotificationPayload[]
  ): Promise<boolean[]> {
    return Promise.all(notifications.map((n) => this.dispatch(n)))
  }
}
```

---

## 생성/수정 파일

| 파일 | 변경 내용 | 라인 수 (예상) |
|------|----------|---------------|
| `lib/ai/client.ts` | AI 통합 클라이언트 | ~200줄 |
| `lib/email/sender.ts` | 이메일 발송 서비스 | ~130줄 |
| `lib/notifications/service.ts` | 알림 디스패처 | ~70줄 |

**총 파일 수**: 3개
**총 라인 수**: ~400줄

---

## 환경 변수

`.env.local`에 추가:

```
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
OPENAI_API_KEY=sk-proj-...

# Email API Key
RESEND_API_KEY=re_...
```

---

## 완료 기준

### 필수
- [ ] AI 클라이언트 구현 (Claude, Gemini, GPT)
- [ ] 이메일 발송 서비스 구현 (Resend)
- [ ] 알림 디스패처 구현
- [ ] API 키 환경변수 설정

### 검증
- [ ] AI API 호출 성공
- [ ] 이메일 발송 성공
- [ ] 에러 핸들링 동작 확인

### 권장
- [ ] AI 응답 캐싱
- [ ] 재시도 로직
- [ ] 비동기 큐 처리

---

**작업 복잡도**: High
**작성일**: 2026-02-05
