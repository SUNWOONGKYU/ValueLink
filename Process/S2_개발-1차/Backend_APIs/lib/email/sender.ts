/**
 * @task S2BA4
 * @description Email sending service via Resend API
 *
 * Handles transactional emails for the valuation platform:
 * - Project creation notifications
 * - Approval request emails
 * - Report completion emails
 *
 * Uses the Resend REST API via fetch (no SDK).
 */

// ---------------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------------

/** Optional fields when sending an email */
interface EmailOptions {
  from?: string;
  replyTo?: string;
  cc?: string[];
}

/** Result of an email send attempt */
interface EmailResult {
  success: boolean;
  messageId?: string;
  error?: string;
}

/** Internal retry configuration */
interface EmailConfig {
  maxRetries: number;
  timeout: number;
  defaultFrom: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RESEND_API_URL = 'https://api.resend.com/emails';

const DEFAULT_EMAIL_CONFIG: EmailConfig = {
  maxRetries: 2,
  timeout: 10_000,
  defaultFrom: 'ValueLink <noreply@valuelink.kr>',
};

/**
 * RFC 5322-compliant email validation pattern.
 * Covers the vast majority of real-world addresses.
 */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// ---------------------------------------------------------------------------
// HTML Escaping utility
// ---------------------------------------------------------------------------

/**
 * Escape a string for safe inclusion in HTML content.
 * Prevents XSS when user-supplied data is interpolated into email templates.
 *
 * @param str - The raw string to escape
 * @returns HTML-safe string
 */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ---------------------------------------------------------------------------
// EmailSender
// ---------------------------------------------------------------------------

/**
 * Transactional email service backed by the Resend API.
 *
 * All API calls use the native `fetch` function with configurable retry and
 * timeout. User-supplied data is HTML-escaped before being interpolated into
 * templates to prevent XSS.
 *
 * @example
 * ```ts
 * const sender = new EmailSender();
 * const result = await sender.sendProjectCreatedEmail(
 *   'user@example.com',
 *   'My Project',
 *   'proj_123',
 * );
 * if (result.success) console.log('Sent:', result.messageId);
 * ```
 */
class EmailSender {
  private config: EmailConfig;

  constructor(config?: Partial<EmailConfig>) {
    this.config = { ...DEFAULT_EMAIL_CONFIG, ...config };
  }

  // -----------------------------------------------------------------------
  // Core send method
  // -----------------------------------------------------------------------

  /**
   * Send a single email via the Resend API.
   *
   * @param to      - Recipient email address
   * @param subject - Email subject line
   * @param html    - Email body as HTML
   * @param options - Optional overrides (from, replyTo, cc)
   * @returns An {@link EmailResult} indicating success or failure
   */
  async send(
    to: string,
    subject: string,
    html: string,
    options?: EmailOptions,
  ): Promise<EmailResult> {
    // Validate API key
    const apiKey = process.env.RESEND_API_KEY;
    if (!apiKey) {
      return { success: false, error: 'RESEND_API_KEY is not set' };
    }

    // Validate recipient
    if (!this.isValidEmail(to)) {
      return { success: false, error: `Invalid email address: ${to}` };
    }

    // Validate cc addresses if provided
    if (options?.cc) {
      for (const cc of options.cc) {
        if (!this.isValidEmail(cc)) {
          return { success: false, error: `Invalid CC email address: ${cc}` };
        }
      }
    }

    const payload: Record<string, unknown> = {
      from: options?.from ?? this.config.defaultFrom,
      to: [to],
      subject,
      html,
    };
    if (options?.replyTo) payload.reply_to = options.replyTo;
    if (options?.cc && options.cc.length > 0) payload.cc = options.cc;

    let lastError: string | null = null;

    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        const res = await this.fetchWithTimeout(RESEND_API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          const data = await res.json();
          return { success: true, messageId: data.id };
        }

        const errText = await res.text();
        lastError = `Resend API error ${res.status}: ${errText}`;

        // Only retry on server errors (5xx)
        if (res.status < 500) {
          return { success: false, error: lastError };
        }
      } catch (err) {
        lastError = err instanceof Error ? err.message : String(err);
      }

      // Exponential back-off before retry
      if (attempt < this.config.maxRetries) {
        await this.sleep(1000 * attempt);
      }
    }

    return {
      success: false,
      error: `Failed after ${this.config.maxRetries} retries: ${lastError}`,
    };
  }

  // -----------------------------------------------------------------------
  // Template methods
  // -----------------------------------------------------------------------

  /**
   * Send a "project created" notification email.
   *
   * @param to          - Recipient email address
   * @param projectName - Name of the created project
   * @param projectId   - Unique identifier of the project
   * @returns An {@link EmailResult}
   */
  async sendProjectCreatedEmail(
    to: string,
    projectName: string,
    projectId: string,
  ): Promise<EmailResult> {
    const safeName = escapeHtml(projectName);
    const safeId = escapeHtml(projectId);

    const subject = `[ValueLink] 프로젝트 "${safeName}" 생성 완료`;
    const html = this.wrapTemplate(`
      <h2>프로젝트가 생성되었습니다</h2>
      <p>안녕하세요,</p>
      <p>요청하신 프로젝트 <strong>${safeName}</strong>이(가) 성공적으로 생성되었습니다.</p>
      <table style="border-collapse:collapse;margin:16px 0;">
        <tr>
          <td style="padding:8px 16px;background:#f5f5f5;font-weight:bold;">프로젝트명</td>
          <td style="padding:8px 16px;">${safeName}</td>
        </tr>
        <tr>
          <td style="padding:8px 16px;background:#f5f5f5;font-weight:bold;">프로젝트 ID</td>
          <td style="padding:8px 16px;font-family:monospace;">${safeId}</td>
        </tr>
      </table>
      <p>대시보드에서 프로젝트 상세 내용을 확인하실 수 있습니다.</p>
    `);

    return this.send(to, subject, html);
  }

  /**
   * Send an "approval request" email to an accountant / reviewer.
   *
   * @param to          - Recipient email address
   * @param projectName - Name of the project awaiting approval
   * @param stage       - The stage requiring approval (e.g. "S2")
   * @returns An {@link EmailResult}
   */
  async sendApprovalRequestEmail(
    to: string,
    projectName: string,
    stage: string,
  ): Promise<EmailResult> {
    const safeName = escapeHtml(projectName);
    const safeStage = escapeHtml(stage);

    const subject = `[ValueLink] 승인 요청 - "${safeName}" ${safeStage} 단계`;
    const html = this.wrapTemplate(`
      <h2>승인 요청</h2>
      <p>안녕하세요,</p>
      <p>프로젝트 <strong>${safeName}</strong>의 <strong>${safeStage}</strong> 단계가 완료되어 승인을 요청드립니다.</p>
      <p style="margin:24px 0;">
        <a href="#"
           style="background:#2563eb;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold;">
          승인 페이지로 이동
        </a>
      </p>
      <p>검토 후 승인 또는 반려 처리를 부탁드립니다.</p>
    `);

    return this.send(to, subject, html);
  }

  /**
   * Send a "report completed" notification email.
   *
   * @param to          - Recipient email address
   * @param projectName - Name of the project
   * @param reportUrl   - Direct URL to the generated report
   * @returns An {@link EmailResult}
   */
  async sendReportCompletedEmail(
    to: string,
    projectName: string,
    reportUrl: string,
  ): Promise<EmailResult> {
    const safeName = escapeHtml(projectName);
    const safeUrl = escapeHtml(reportUrl);

    const subject = `[ValueLink] 보고서 생성 완료 - "${safeName}"`;
    const html = this.wrapTemplate(`
      <h2>보고서가 준비되었습니다</h2>
      <p>안녕하세요,</p>
      <p>프로젝트 <strong>${safeName}</strong>의 기업가치평가 보고서가 생성되었습니다.</p>
      <p style="margin:24px 0;">
        <a href="${safeUrl}"
           style="background:#2563eb;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold;">
          보고서 다운로드
        </a>
      </p>
      <p>보고서에 대한 문의사항이 있으시면 언제든지 연락 주세요.</p>
    `);

    return this.send(to, subject, html);
  }

  // -----------------------------------------------------------------------
  // Private helpers
  // -----------------------------------------------------------------------

  /**
   * Validate an email address format.
   *
   * @param email - The email string to validate
   * @returns true if the format is valid
   */
  private isValidEmail(email: string): boolean {
    if (!email || typeof email !== 'string') return false;
    return EMAIL_REGEX.test(email.trim());
  }

  /**
   * Wrap inner HTML in a consistent email template with basic styling.
   *
   * @param innerHtml - The content to wrap
   * @returns Complete HTML email string
   */
  private wrapTemplate(innerHtml: string): string {
    return `
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8" /></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:'Apple SD Gothic Neo','Noto Sans KR',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#fff;border:1px solid #e5e7eb;border-radius:8px;margin-top:24px;">
    <tr>
      <td style="padding:32px 24px;border-bottom:1px solid #e5e7eb;background:#1e293b;">
        <h1 style="margin:0;color:#fff;font-size:20px;">ValueLink</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 24px;">
        ${innerHtml}
      </td>
    </tr>
    <tr>
      <td style="padding:16px 24px;border-top:1px solid #e5e7eb;color:#6b7280;font-size:12px;text-align:center;">
        <p style="margin:0;">ValueLink - AI 기반 기업가치평가 플랫폼</p>
        <p style="margin:4px 0 0;">본 이메일은 발신 전용입니다.</p>
      </td>
    </tr>
  </table>
</body>
</html>`.trim();
  }

  /**
   * `fetch` wrapper that aborts after the configured timeout.
   */
  private async fetchWithTimeout(
    url: string,
    init: RequestInit,
  ): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      return await fetch(url, { ...init, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  /**
   * Promise-based sleep utility.
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

/** Pre-configured singleton email sender */
const emailSender = new EmailSender();

export { EmailSender, emailSender, escapeHtml };
export type { EmailOptions, EmailResult, EmailConfig };
