/**
 * @task S5_FIX_PHASE2
 * @description 보고서 자동 생성 API - Draft를 PDF로 변환
 *
 * Phase 2 수정: Step 9 (Report Generation) 구현
 * - Draft 9개 섹션 읽기
 * - PDF 템플릿 적용
 * - Supabase Storage 업로드
 * - report_url 반환
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import puppeteer from 'puppeteer';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

interface GenerateReportRequest {
  draft_id: string;
  method: 'dcf' | 'asset' | 'relative' | 'intrinsic' | 'tax';
  project_id: string;
}

interface DraftData {
  draft_id: string;
  project_id: string;
  version: number;
  section_1_summary: string;
  section_2_overview: string;
  section_3_company: string;
  section_4_financial: string;
  section_5_methodology: string;
  section_6_results: string;
  section_7_sensitivity: string;
  section_8_conclusion: string;
  section_9_appendix: string;
  status: string;
  created_at: string;
}

/**
 * POST /api/reports/generate
 *
 * Draft를 PDF 보고서로 변환합니다.
 *
 * @example
 * ```
 * POST /api/reports/generate
 * {
 *   "draft_id": "draft-123",
 *   "method": "dcf",
 *   "project_id": "VL-20260222-0001"
 * }
 *
 * Response:
 * {
 *   "report_id": "report-456",
 *   "report_url": "https://xxx.supabase.co/storage/v1/object/public/reports/...",
 *   "file_size": 1024000,
 *   "status": "confirmed"
 * }
 * ```
 */
export async function POST(req: NextRequest) {
  try {
    const body: GenerateReportRequest = await req.json();
    const { draft_id, method, project_id } = body;

    // 1. Draft 데이터 읽기
    const draftTable = `${method}_drafts`;
    const { data: draft, error: draftError } = await supabase
      .from(draftTable)
      .select('*')
      .eq('draft_id', draft_id)
      .single();

    if (draftError || !draft) {
      return NextResponse.json(
        { error: 'Draft를 찾을 수 없습니다.', details: draftError },
        { status: 404 }
      );
    }

    const draftData = draft as unknown as DraftData;

    // 2. HTML 템플릿 생성
    const html = generateReportHTML(draftData, method, project_id);

    // 3. Puppeteer로 PDF 생성
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        right: '15mm',
        bottom: '20mm',
        left: '15mm',
      },
    });

    await browser.close();

    // 4. Supabase Storage에 업로드
    const fileName = `${project_id}_${method}_report_${Date.now()}.pdf`;
    const filePath = `reports/${fileName}`;

    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('valuation-reports')
      .upload(filePath, pdfBuffer, {
        contentType: 'application/pdf',
        upsert: false,
      });

    if (uploadError) {
      return NextResponse.json(
        { error: 'PDF 업로드 실패', details: uploadError },
        { status: 500 }
      );
    }

    // 5. Public URL 생성
    const { data: urlData } = supabase.storage
      .from('valuation-reports')
      .getPublicUrl(filePath);

    const reportUrl = urlData.publicUrl;
    const fileSize = pdfBuffer.length;

    // 6. Reports 테이블에 저장
    const reportTable = `${method}_reports`;
    const reportId = `report-${Date.now()}`;

    const { data: reportData, error: reportError } = await supabase
      .from(reportTable)
      .insert({
        report_id: reportId,
        project_id,
        draft_id,
        report_url: reportUrl,
        file_size: fileSize,
        status: 'confirmed',
        issued_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (reportError) {
      return NextResponse.json(
        { error: 'Report 메타데이터 저장 실패', details: reportError },
        { status: 500 }
      );
    }

    return NextResponse.json({
      report_id: reportId,
      report_url: reportUrl,
      file_size: fileSize,
      status: 'confirmed',
      message: 'PDF 보고서가 성공적으로 생성되었습니다.',
    });
  } catch (error: any) {
    console.error('Report generation error:', error);
    return NextResponse.json(
      { error: '보고서 생성 중 오류가 발생했습니다.', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * Draft 데이터를 HTML 템플릿으로 변환합니다.
 */
function generateReportHTML(
  draft: DraftData,
  method: string,
  projectId: string
): string {
  const methodNames: Record<string, string> = {
    dcf: 'DCF (현금흐름할인법)',
    asset: 'Asset (자산가치법)',
    relative: 'Relative (상대가치법)',
    intrinsic: 'Intrinsic (본질가치법)',
    tax: 'Tax (세무가치법)',
  };

  const methodName = methodNames[method] || method.toUpperCase();

  return `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>기업가치평가 보고서 - ${projectId}</title>
  <style>
    @page {
      size: A4;
      margin: 20mm 15mm;
    }

    body {
      font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
      font-size: 11pt;
      line-height: 1.6;
      color: #333;
      margin: 0;
      padding: 0;
    }

    .header {
      text-align: center;
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 3px solid #0066cc;
    }

    .header h1 {
      font-size: 24pt;
      margin: 0 0 10px 0;
      color: #0066cc;
    }

    .header .subtitle {
      font-size: 14pt;
      color: #666;
      margin: 5px 0;
    }

    .meta-info {
      display: flex;
      justify-content: space-between;
      margin: 20px 0;
      padding: 15px;
      background-color: #f5f5f5;
      border-radius: 5px;
    }

    .meta-info .item {
      flex: 1;
    }

    .meta-info .label {
      font-weight: bold;
      color: #0066cc;
    }

    .section {
      margin: 30px 0;
      page-break-inside: avoid;
    }

    .section-title {
      font-size: 16pt;
      font-weight: bold;
      color: #0066cc;
      margin: 20px 0 10px 0;
      padding-bottom: 5px;
      border-bottom: 2px solid #0066cc;
    }

    .section-content {
      font-size: 11pt;
      line-height: 1.8;
      text-align: justify;
      white-space: pre-wrap;
    }

    .footer {
      margin-top: 50px;
      padding-top: 20px;
      border-top: 1px solid #ccc;
      text-align: center;
      font-size: 10pt;
      color: #666;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 15px 0;
    }

    table th,
    table td {
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }

    table th {
      background-color: #0066cc;
      color: white;
      font-weight: bold;
    }

    .page-break {
      page-break-after: always;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>기업가치평가 보고서</h1>
    <div class="subtitle">${methodName}</div>
    <div class="subtitle">프로젝트 ID: ${projectId}</div>
  </div>

  <div class="meta-info">
    <div class="item">
      <div class="label">평가 방법</div>
      <div>${methodName}</div>
    </div>
    <div class="item">
      <div class="label">보고서 버전</div>
      <div>v${draft.version}</div>
    </div>
    <div class="item">
      <div class="label">작성일</div>
      <div>${new Date(draft.created_at).toLocaleDateString('ko-KR')}</div>
    </div>
  </div>

  <!-- Section 1: Executive Summary -->
  <div class="section">
    <h2 class="section-title">1. 요약 (Executive Summary)</h2>
    <div class="section-content">${draft.section_1_summary || '작성 중입니다.'}</div>
  </div>

  <div class="page-break"></div>

  <!-- Section 2: Overview -->
  <div class="section">
    <h2 class="section-title">2. 평가 개요 (Valuation Overview)</h2>
    <div class="section-content">${draft.section_2_overview || '작성 중입니다.'}</div>
  </div>

  <!-- Section 3: Company Analysis -->
  <div class="section">
    <h2 class="section-title">3. 회사 분석 (Company Analysis)</h2>
    <div class="section-content">${draft.section_3_company || '작성 중입니다.'}</div>
  </div>

  <div class="page-break"></div>

  <!-- Section 4: Financial Analysis -->
  <div class="section">
    <h2 class="section-title">4. 재무 분석 (Financial Analysis)</h2>
    <div class="section-content">${draft.section_4_financial || '작성 중입니다.'}</div>
  </div>

  <div class="page-break"></div>

  <!-- Section 5: Valuation Methodology -->
  <div class="section">
    <h2 class="section-title">5. 평가 방법론 (Valuation Methodology)</h2>
    <div class="section-content">${draft.section_5_methodology || '작성 중입니다.'}</div>
  </div>

  <!-- Section 6: Valuation Results -->
  <div class="section">
    <h2 class="section-title">6. 평가 결과 (Valuation Results)</h2>
    <div class="section-content">${draft.section_6_results || '작성 중입니다.'}</div>
  </div>

  <div class="page-break"></div>

  <!-- Section 7: Sensitivity Analysis -->
  <div class="section">
    <h2 class="section-title">7. 민감도 분석 (Sensitivity Analysis)</h2>
    <div class="section-content">${draft.section_7_sensitivity || '작성 중입니다.'}</div>
  </div>

  <!-- Section 8: Conclusion -->
  <div class="section">
    <h2 class="section-title">8. 결론 (Conclusion)</h2>
    <div class="section-content">${draft.section_8_conclusion || '작성 중입니다.'}</div>
  </div>

  <div class="page-break"></div>

  <!-- Section 9: Appendix -->
  <div class="section">
    <h2 class="section-title">9. 부록 (Appendix)</h2>
    <div class="section-content">${draft.section_9_appendix || '작성 중입니다.'}</div>
  </div>

  <div class="footer">
    <p><strong>ValueLink 기업가치평가 플랫폼</strong></p>
    <p>본 보고서는 ${new Date().toLocaleDateString('ko-KR')}에 생성되었습니다.</p>
    <p>보고서 ID: ${draft.draft_id} | 프로젝트 ID: ${projectId}</p>
  </div>
</body>
</html>
  `.trim();
}
