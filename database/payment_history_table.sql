/**
 * @task S5_FIX_PHASE3
 * @description Payment History 테이블 생성
 *
 * Phase 3 수정: Step 11 (Payment Processing) 구현
 * - 결제 이력 추적 테이블
 * - projects 테이블과 연동
 */

-- payment_history 테이블 생성
CREATE TABLE IF NOT EXISTS payment_history (
  payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,

  -- 결제 정보
  amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
  payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('deposit', 'balance')),
  payment_method VARCHAR(50),  -- 'card', 'transfer', 'cash', etc.

  -- 결제 상태
  status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'failed', 'refunded')),

  -- 결제 게이트웨이 정보 (추후 연동 시)
  gateway_tx_id VARCHAR(100),  -- 결제 게이트웨이 트랜잭션 ID
  gateway_name VARCHAR(50),    -- 'stripe', 'toss', 'kakao', etc.

  -- 시간 정보
  paid_at TIMESTAMP,           -- 실제 결제 완료 시간
  confirmed_at TIMESTAMP,      -- 결제 확인 시간
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_payment_history_project_id ON payment_history(project_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_status ON payment_history(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_payment_type ON payment_history(payment_type);
CREATE INDEX IF NOT EXISTS idx_payment_history_created_at ON payment_history(created_at DESC);

-- RLS (Row Level Security) 활성화
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;

-- RLS 정책: 관리자는 모든 결제 내역 조회 가능
CREATE POLICY payment_history_admin_read ON payment_history
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.user_id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- RLS 정책: 회계사는 자신이 담당하는 프로젝트의 결제 내역 조회 가능
CREATE POLICY payment_history_accountant_read ON payment_history
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.project_id = payment_history.project_id
      AND projects.accountant_id = auth.uid()
    )
  );

-- RLS 정책: 고객은 자신의 프로젝트 결제 내역 조회 가능
CREATE POLICY payment_history_customer_read ON payment_history
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM projects
      WHERE projects.project_id = payment_history.project_id
      AND projects.user_id = auth.uid()
    )
  );

-- RLS 정책: 관리자와 회계사는 결제 내역 생성 가능
CREATE POLICY payment_history_insert ON payment_history
  FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.user_id = auth.uid()
      AND users.role IN ('admin', 'accountant')
    )
  );

-- RLS 정책: 관리자만 결제 내역 업데이트 가능
CREATE POLICY payment_history_update ON payment_history
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.user_id = auth.uid()
      AND users.role = 'admin'
    )
  );

-- 트리거: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_payment_history_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER payment_history_updated_at_trigger
  BEFORE UPDATE ON payment_history
  FOR EACH ROW
  EXECUTE FUNCTION update_payment_history_updated_at();

-- 코멘트
COMMENT ON TABLE payment_history IS '프로젝트 결제 이력 테이블';
COMMENT ON COLUMN payment_history.payment_id IS '결제 ID (UUID)';
COMMENT ON COLUMN payment_history.project_id IS '프로젝트 ID';
COMMENT ON COLUMN payment_history.amount IS '결제 금액';
COMMENT ON COLUMN payment_history.payment_type IS '결제 유형: deposit (계약금), balance (잔금)';
COMMENT ON COLUMN payment_history.payment_method IS '결제 수단: card, transfer, cash 등';
COMMENT ON COLUMN payment_history.status IS '결제 상태: pending, confirmed, failed, refunded';
COMMENT ON COLUMN payment_history.gateway_tx_id IS '결제 게이트웨이 트랜잭션 ID';
COMMENT ON COLUMN payment_history.gateway_name IS '결제 게이트웨이명: stripe, toss, kakao 등';
COMMENT ON COLUMN payment_history.paid_at IS '실제 결제 완료 시간';
COMMENT ON COLUMN payment_history.confirmed_at IS '결제 확인 시간';
