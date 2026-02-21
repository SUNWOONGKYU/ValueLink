/**
 * @task S2BA4
 * @description Notification dispatcher service
 *
 * Routes notifications to the appropriate delivery channel (currently email).
 * Designed to be extended with additional channels (push, SMS, in-app) as
 * the platform grows.
 */

import { EmailSender, emailSender } from '../email/sender';
import type { EmailResult } from '../email/sender';

// ---------------------------------------------------------------------------
// Type Definitions
// ---------------------------------------------------------------------------

/** Supported notification event types */
type NotificationType =
  | 'project_created'
  | 'approval_needed'
  | 'report_ready'
  | 'payment_received'
  | 'status_changed';

/** A single notification to be dispatched */
interface Notification {
  type: NotificationType;
  recipientEmail: string;
  recipientName?: string;
  data: Record<string, string>;
}

/** Result of a dispatch attempt */
interface DispatchResult {
  success: boolean;
  notificationType: NotificationType;
  error?: string;
}

/** Aggregate result for batch dispatches */
interface BatchDispatchResult {
  total: number;
  succeeded: number;
  failed: number;
  results: DispatchResult[];
}

// ---------------------------------------------------------------------------
// NotificationService
// ---------------------------------------------------------------------------

/**
 * Central notification dispatcher.
 *
 * Receives typed notifications and routes them to the correct delivery
 * method. Currently supports email (via {@link EmailSender}). Each
 * notification type maps to a specific email template method.
 *
 * @example
 * ```ts
 * const svc = new NotificationService();
 * const result = await svc.notifyProjectCreated('proj_123', 'user@example.com');
 * console.log(result.success);
 * ```
 */
class NotificationService {
  private email: EmailSender;

  constructor(emailService?: EmailSender) {
    this.email = emailService ?? emailSender;
  }

  // -----------------------------------------------------------------------
  // Core dispatch
  // -----------------------------------------------------------------------

  /**
   * Route a single notification to the appropriate channel.
   *
   * @param notification - The notification to dispatch
   * @returns A {@link DispatchResult} indicating success or failure
   */
  async dispatch(notification: Notification): Promise<DispatchResult> {
    try {
      const emailResult = await this.routeToEmail(notification);

      return {
        success: emailResult.success,
        notificationType: notification.type,
        error: emailResult.error,
      };
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      this.log('error', `Dispatch failed for ${notification.type}: ${message}`);

      return {
        success: false,
        notificationType: notification.type,
        error: message,
      };
    }
  }

  /**
   * Dispatch multiple notifications concurrently.
   *
   * Uses `Promise.allSettled` so that a single failure does not prevent the
   * remaining notifications from being sent.
   *
   * @param notifications - Array of notifications to dispatch
   * @returns A {@link BatchDispatchResult} with per-notification results
   */
  async dispatchMultiple(
    notifications: Notification[],
  ): Promise<BatchDispatchResult> {
    const settled = await Promise.allSettled(
      notifications.map((n) => this.dispatch(n)),
    );

    const results: DispatchResult[] = settled.map((s, idx) => {
      if (s.status === 'fulfilled') return s.value;
      return {
        success: false,
        notificationType: notifications[idx].type,
        error: s.reason instanceof Error ? s.reason.message : String(s.reason),
      };
    });

    const succeeded = results.filter((r) => r.success).length;

    return {
      total: results.length,
      succeeded,
      failed: results.length - succeeded,
      results,
    };
  }

  // -----------------------------------------------------------------------
  // Convenience methods (domain events)
  // -----------------------------------------------------------------------

  /**
   * Notify a user that their project has been created.
   *
   * @param projectId - The unique project identifier
   * @param userId    - Recipient email address
   * @returns A {@link DispatchResult}
   */
  async notifyProjectCreated(
    projectId: string,
    userId: string,
  ): Promise<DispatchResult> {
    return this.dispatch({
      type: 'project_created',
      recipientEmail: userId,
      data: {
        projectId,
        projectName: projectId, // Caller should pass actual name if available
      },
    });
  }

  /**
   * Notify an accountant / reviewer that their approval is needed.
   *
   * @param projectId    - The project awaiting approval
   * @param accountantId - Recipient email address
   * @param stage        - The stage requiring approval (e.g. "S2")
   * @returns A {@link DispatchResult}
   */
  async notifyApprovalNeeded(
    projectId: string,
    accountantId: string,
    stage: string,
  ): Promise<DispatchResult> {
    return this.dispatch({
      type: 'approval_needed',
      recipientEmail: accountantId,
      data: {
        projectId,
        projectName: projectId,
        stage,
      },
    });
  }

  /**
   * Notify a user that their valuation report is ready for download.
   *
   * @param projectId - The project identifier
   * @param userId    - Recipient email address
   * @param reportUrl - Direct URL to the report
   * @returns A {@link DispatchResult}
   */
  async notifyReportReady(
    projectId: string,
    userId: string,
    reportUrl: string,
  ): Promise<DispatchResult> {
    return this.dispatch({
      type: 'report_ready',
      recipientEmail: userId,
      data: {
        projectId,
        projectName: projectId,
        reportUrl,
      },
    });
  }

  // -----------------------------------------------------------------------
  // Private routing
  // -----------------------------------------------------------------------

  /**
   * Route a notification to the matching email template method.
   *
   * @param notification - The notification to route
   * @returns An {@link EmailResult} from the email sender
   */
  private async routeToEmail(notification: Notification): Promise<EmailResult> {
    const { type, recipientEmail, data } = notification;

    this.log(
      'info',
      `Routing ${type} notification to ${recipientEmail}`,
    );

    switch (type) {
      case 'project_created':
        return this.email.sendProjectCreatedEmail(
          recipientEmail,
          data.projectName ?? 'Unknown Project',
          data.projectId ?? '',
        );

      case 'approval_needed':
        return this.email.sendApprovalRequestEmail(
          recipientEmail,
          data.projectName ?? 'Unknown Project',
          data.stage ?? '',
        );

      case 'report_ready':
        return this.email.sendReportCompletedEmail(
          recipientEmail,
          data.projectName ?? 'Unknown Project',
          data.reportUrl ?? '#',
        );

      case 'payment_received':
        return this.email.send(
          recipientEmail,
          `[ValueLink] 결제 확인 - ${data.projectName ?? ''}`,
          this.buildGenericHtml(
            '결제가 확인되었습니다',
            `프로젝트 <strong>${data.projectName ?? ''}</strong>에 대한 결제가 정상적으로 처리되었습니다. 감사합니다.`,
          ),
        );

      case 'status_changed':
        return this.email.send(
          recipientEmail,
          `[ValueLink] 상태 변경 - ${data.projectName ?? ''}`,
          this.buildGenericHtml(
            '프로젝트 상태가 변경되었습니다',
            `프로젝트 <strong>${data.projectName ?? ''}</strong>의 상태가 <strong>${data.newStatus ?? ''}</strong>(으)로 변경되었습니다.`,
          ),
        );

      default: {
        // Exhaustive check - should never happen
        const _exhaustive: never = type;
        return {
          success: false,
          error: `Unknown notification type: ${_exhaustive}`,
        };
      }
    }
  }

  /**
   * Build a simple HTML email body for notification types that do not have
   * a dedicated template method on EmailSender.
   *
   * @param heading - Email heading
   * @param body    - Body paragraph (may contain safe HTML)
   * @returns HTML string
   */
  private buildGenericHtml(heading: string, body: string): string {
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
        <h2>${heading}</h2>
        <p>안녕하세요,</p>
        <p>${body}</p>
        <p>대시보드에서 상세 내용을 확인하실 수 있습니다.</p>
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
   * Internal structured logger.
   *
   * @param level   - Log level
   * @param message - Log message
   */
  private log(level: 'info' | 'warn' | 'error', message: string): void {
    const timestamp = new Date().toISOString();
    const prefix = `[NotificationService][${timestamp}]`;

    switch (level) {
      case 'info':
        console.log(`${prefix} ${message}`);
        break;
      case 'warn':
        console.warn(`${prefix} ${message}`);
        break;
      case 'error':
        console.error(`${prefix} ${message}`);
        break;
    }
  }
}

// ---------------------------------------------------------------------------
// Singleton export
// ---------------------------------------------------------------------------

/** Pre-configured singleton notification service */
const notificationService = new NotificationService();

export { NotificationService, notificationService };
export type {
  NotificationType,
  Notification,
  DispatchResult,
  BatchDispatchResult,
};
