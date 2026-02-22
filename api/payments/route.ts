/**
 * @task S5_FIX_PHASE3
 * @description 결제 처리 API
 *
 * Phase 3 수정: Step 11 (Payment Processing) 구현
 * - 결제 요청 처리
 * - payment_history 테이블에 기록
 * - projects 테이블 업데이트
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase = createClient(supabaseUrl, supabaseServiceKey);

interface PaymentRequest {
  project_id: string;
  amount: number;
  payment_type: 'deposit' | 'balance';
  payment_method?: string;
  gateway_tx_id?: string;
  gateway_name?: string;
}

interface PaymentConfirmRequest {
  payment_id: string;
  status: 'confirmed' | 'failed' | 'refunded';
}

/**
 * POST /api/payments
 *
 * 결제를 생성하고 payment_history 테이블에 기록합니다.
 *
 * @example
 * ```
 * POST /api/payments
 * {
 *   "project_id": "VL-20260222-0001",
 *   "amount": 5000000,
 *   "payment_type": "deposit",
 *   "payment_method": "card",
 *   "gateway_tx_id": "tx_1234567890",
 *   "gateway_name": "stripe"
 * }
 *
 * Response:
 * {
 *   "payment_id": "uuid-...",
 *   "status": "pending",
 *   "message": "결제가 생성되었습니다."
 * }
 * ```
 */
export async function POST(req: NextRequest) {
  try {
    const body: PaymentRequest = await req.json();
    const {
      project_id,
      amount,
      payment_type,
      payment_method = 'manual',
      gateway_tx_id,
      gateway_name,
    } = body;

    // 1. 입력 검증
    if (!project_id || !amount || !payment_type) {
      return NextResponse.json(
        { error: 'project_id, amount, payment_type는 필수입니다.' },
        { status: 400 }
      );
    }

    if (amount <= 0) {
      return NextResponse.json(
        { error: '결제 금액은 0보다 커야 합니다.' },
        { status: 400 }
      );
    }

    if (!['deposit', 'balance'].includes(payment_type)) {
      return NextResponse.json(
        { error: "payment_type은 'deposit' 또는 'balance'여야 합니다." },
        { status: 400 }
      );
    }

    // 2. 프로젝트 존재 확인
    const { data: project, error: projectError } = await supabase
      .from('projects')
      .select('project_id, agreed_price, deposit_amount, deposit_paid_at, balance_paid_at')
      .eq('project_id', project_id)
      .single();

    if (projectError || !project) {
      return NextResponse.json(
        { error: '프로젝트를 찾을 수 없습니다.', details: projectError },
        { status: 404 }
      );
    }

    // 3. 결제 금액 검증
    if (payment_type === 'deposit' && amount !== project.deposit_amount) {
      return NextResponse.json(
        {
          error: `계약금은 ${project.deposit_amount}원이어야 합니다. (입력: ${amount}원)`,
        },
        { status: 400 }
      );
    }

    const expectedBalance = project.agreed_price - project.deposit_amount;
    if (payment_type === 'balance' && amount !== expectedBalance) {
      return NextResponse.json(
        {
          error: `잔금은 ${expectedBalance}원이어야 합니다. (입력: ${amount}원)`,
        },
        { status: 400 }
      );
    }

    // 4. 중복 결제 확인
    if (payment_type === 'deposit' && project.deposit_paid_at) {
      return NextResponse.json(
        { error: '계약금이 이미 결제되었습니다.' },
        { status: 400 }
      );
    }

    if (payment_type === 'balance' && project.balance_paid_at) {
      return NextResponse.json(
        { error: '잔금이 이미 결제되었습니다.' },
        { status: 400 }
      );
    }

    // 5. payment_history 테이블에 기록
    const { data: payment, error: paymentError } = await supabase
      .from('payment_history')
      .insert({
        project_id,
        amount,
        payment_type,
        payment_method,
        gateway_tx_id,
        gateway_name,
        status: 'pending',
        paid_at: new Date().toISOString(),
      })
      .select()
      .single();

    if (paymentError || !payment) {
      return NextResponse.json(
        { error: '결제 기록 생성 실패', details: paymentError },
        { status: 500 }
      );
    }

    return NextResponse.json({
      payment_id: payment.payment_id,
      status: 'pending',
      message: '결제가 생성되었습니다. 결제 확인을 위해 /api/payments/confirm을 호출하세요.',
    });
  } catch (error: any) {
    console.error('Payment creation error:', error);
    return NextResponse.json(
      { error: '결제 생성 중 오류가 발생했습니다.', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * GET /api/payments?project_id={project_id}
 *
 * 프로젝트의 결제 이력을 조회합니다.
 */
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const project_id = searchParams.get('project_id');

    if (!project_id) {
      return NextResponse.json(
        { error: 'project_id 파라미터가 필요합니다.' },
        { status: 400 }
      );
    }

    const { data: payments, error } = await supabase
      .from('payment_history')
      .select('*')
      .eq('project_id', project_id)
      .order('created_at', { ascending: false });

    if (error) {
      return NextResponse.json(
        { error: '결제 이력 조회 실패', details: error },
        { status: 500 }
      );
    }

    return NextResponse.json({ payments });
  } catch (error: any) {
    console.error('Payment history query error:', error);
    return NextResponse.json(
      { error: '결제 이력 조회 중 오류가 발생했습니다.', details: error.message },
      { status: 500 }
    );
  }
}

/**
 * PUT /api/payments
 *
 * 결제 상태를 확인/업데이트하고 projects 테이블을 업데이트합니다.
 *
 * @example
 * ```
 * PUT /api/payments
 * {
 *   "payment_id": "uuid-...",
 *   "status": "confirmed"
 * }
 * ```
 */
export async function PUT(req: NextRequest) {
  try {
    const body: PaymentConfirmRequest = await req.json();
    const { payment_id, status } = body;

    if (!payment_id || !status) {
      return NextResponse.json(
        { error: 'payment_id, status는 필수입니다.' },
        { status: 400 }
      );
    }

    if (!['confirmed', 'failed', 'refunded'].includes(status)) {
      return NextResponse.json(
        { error: "status는 'confirmed', 'failed', 'refunded' 중 하나여야 합니다." },
        { status: 400 }
      );
    }

    // 1. 결제 정보 조회
    const { data: payment, error: paymentError } = await supabase
      .from('payment_history')
      .select('*')
      .eq('payment_id', payment_id)
      .single();

    if (paymentError || !payment) {
      return NextResponse.json(
        { error: '결제 정보를 찾을 수 없습니다.', details: paymentError },
        { status: 404 }
      );
    }

    // 2. payment_history 업데이트
    const { error: updateError } = await supabase
      .from('payment_history')
      .update({
        status,
        confirmed_at: status === 'confirmed' ? new Date().toISOString() : null,
      })
      .eq('payment_id', payment_id);

    if (updateError) {
      return NextResponse.json(
        { error: '결제 상태 업데이트 실패', details: updateError },
        { status: 500 }
      );
    }

    // 3. status === 'confirmed'이면 projects 테이블 업데이트
    if (status === 'confirmed') {
      const updateFields: any = {};

      if (payment.payment_type === 'deposit') {
        updateFields.deposit_paid_at = new Date().toISOString();
      } else if (payment.payment_type === 'balance') {
        updateFields.balance_paid_at = new Date().toISOString();
      }

      const { error: projectUpdateError } = await supabase
        .from('projects')
        .update(updateFields)
        .eq('project_id', payment.project_id);

      if (projectUpdateError) {
        return NextResponse.json(
          { error: 'projects 테이블 업데이트 실패', details: projectUpdateError },
          { status: 500 }
        );
      }
    }

    return NextResponse.json({
      payment_id,
      status,
      message: `결제 상태가 '${status}'로 업데이트되었습니다.`,
    });
  } catch (error: any) {
    console.error('Payment confirmation error:', error);
    return NextResponse.json(
      { error: '결제 확인 중 오류가 발생했습니다.', details: error.message },
      { status: 500 }
    );
  }
}
