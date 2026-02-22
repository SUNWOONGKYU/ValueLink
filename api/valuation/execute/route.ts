/**
 * @task S5_FIX_CRITICAL
 * @description Valuation 실행 API - 5개 평가 엔진 통합
 *
 * CRITICAL FIX: Step 5 (Valuation Execution) 구현
 * - DCF, Asset, Relative, Intrinsic, Tax 엔진 등록
 * - ValuationOrchestrator 통한 평가 실행
 */

import { NextRequest, NextResponse } from 'next/server';
import { ValuationOrchestrator } from '@/lib/valuation/valuation-orchestrator';
import {
  DCFEngine,
  AssetEngine,
  RelativeEngine,
  IntrinsicEngine,
  TaxEngine,
} from '@/lib/valuation/engines';
import type { ValuationInput } from '@/lib/valuation/types';

// 싱글톤 orchestrator 가져오기 및 엔진 등록
const orchestrator = ValuationOrchestrator.getInstance();

// 5개 엔진 등록 (앱 시작 시 1회 실행)
let enginesRegistered = false;

function registerEngines() {
  if (enginesRegistered) return;

  orchestrator.registerEngine('dcf', new DCFEngine());
  orchestrator.registerEngine('asset', new AssetEngine());
  orchestrator.registerEngine('relative', new RelativeEngine());
  orchestrator.registerEngine('intrinsic', new IntrinsicEngine());
  orchestrator.registerEngine('tax', new TaxEngine());

  enginesRegistered = true;
  console.log('[Valuation] 5개 엔진 등록 완료:', orchestrator.listEngines());
}

// 앱 초기화
registerEngines();

/**
 * POST /api/valuation/execute
 *
 * 평가를 실행합니다.
 *
 * @example
 * ```
 * POST /api/valuation/execute
 * {
 *   "method": "dcf",
 *   "projectId": "VL-20260222-0001",
 *   "cashFlows": [500000000, 600000000, 720000000],
 *   "wacc": 0.12,
 *   "terminalGrowthRate": 0.03,
 *   "netDebt": 5000000000,
 *   "sharesOutstanding": 10000000
 * }
 *
 * Response:
 * {
 *   "method": "DCF",
 *   "enterpriseValue": 12345678900,
 *   "equityValue": 7345678900,
 *   "sharePrice": 734.57,
 *   "details": { ... },
 *   "duration": 45,
 *   "timestamp": "2026-02-22T12:34:56.789Z"
 * }
 * ```
 */
export async function POST(req: NextRequest) {
  try {
    const body: ValuationInput = await req.json();
    const { method } = body;

    if (!method) {
      return NextResponse.json(
        { error: 'method 파라미터가 필요합니다.' },
        { status: 400 }
      );
    }

    const validMethods = ['dcf', 'asset', 'relative', 'intrinsic', 'tax'];
    if (!validMethods.includes(method)) {
      return NextResponse.json(
        {
          error: `지원하지 않는 평가 방법입니다: ${method}. 지원 방법: ${validMethods.join(', ')}`,
        },
        { status: 400 }
      );
    }

    // Valuation 실행
    const result = await orchestrator.valuate(method, body);

    return NextResponse.json(result);
  } catch (error: any) {
    console.error('[POST /api/valuation/execute] Error:', error);

    // ValuationError인 경우 상세 정보 포함
    if (error.name === 'ValuationError') {
      return NextResponse.json(
        {
          error: error.message,
          code: error.code,
          method: error.method,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        error: '평가 실행 중 오류가 발생했습니다.',
        details: error.message,
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/valuation/execute?method={method}
 *
 * 등록된 엔진 목록 또는 특정 엔진 정보를 조회합니다.
 */
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const method = searchParams.get('method');

    if (method) {
      // 특정 엔진 확인
      const engine = orchestrator['engines'].get(method);
      if (!engine) {
        return NextResponse.json(
          { error: `엔진을 찾을 수 없습니다: ${method}` },
          { status: 404 }
        );
      }

      return NextResponse.json({
        method,
        name: engine.getName(),
        status: 'registered',
      });
    }

    // 모든 등록된 엔진 목록
    const engines = orchestrator.listEngines();

    return NextResponse.json({
      engines,
      count: engines.length,
      message: '등록된 평가 엔진 목록',
    });
  } catch (error: any) {
    console.error('[GET /api/valuation/execute] Error:', error);
    return NextResponse.json(
      { error: '엔진 목록 조회 실패', details: error.message },
      { status: 500 }
    );
  }
}
