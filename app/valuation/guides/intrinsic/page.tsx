/**
 * @task S2F3
 * @description 내재가치평가 (자본시장법) 가이드 페이지 - Server Component
 */

import type { Metadata } from 'next'
import GuideTemplate from '@/components/guide-template'

export const metadata: Metadata = {
  title: '내재가치평가 (자본시장법) 안내 - ValueLink',
  description:
    '자본시장법에 따른 본질가치 평가법의 개념, 자산가치와 수익가치의 가중평균, 자본환원율 산정, 계산 예시까지 실무 중심으로 안내합니다.',
  keywords: [
    '본질가치',
    '내재가치',
    '자본시장법',
    '수익환원법',
    '순자산가치법',
    '주식매수청구권',
    '합병비율',
    'Intrinsic Value',
    '비상장주식',
  ],
  openGraph: {
    title: '내재가치평가 (자본시장법) 안내 - ValueLink',
    description:
      '자본시장법에서 정한 본질가치 평가법으로, 자산가치 40%와 수익가치 60%를 가중평균합니다.',
    type: 'article',
    locale: 'ko_KR',
  },
}

export default async function IntrinsicGuidePage() {
  return (
    <GuideTemplate
      methodName="intrinsic"
      title="내재가치평가 (자본시장법)"
      description="자본시장법에서 정한 법적 평가 방법으로, 기업의 자산가치와 수익가치를 법정 비율(40:60)로 가중평균하여 계산합니다. 주식매수청구권, M&A, Pre-IPO 등 법적 의무 상황에서 필수적으로 수행됩니다."
    >
      {/* 개요 */}
      <section>
        <h2 id="overview">개요</h2>
        <p>
          <strong>본질가치(Intrinsic Value)</strong>는 자본시장과 금융투자업에
          관한 법률 시행령 제176조의5 및 제176조의6에 근거한 법적 평가
          방법입니다. 기업의 자산가치와 수익가치를 정해진 비율로 가중평균하여
          계산합니다.
        </p>
        <p>
          핵심은 <strong>자산가치 40% + 수익가치 60%</strong>의 가중구조입니다.
          계속기업(going concern) 관점에서 수익가치에 더 높은 가중치를 부여하며,
          법령으로 고정되어 있어 평가자의 자의적 판단을 배제합니다.
        </p>
      </section>

      {/* 핵심 공식 */}
      <section>
        <h2 id="formula">핵심 공식</h2>
        <pre>
          <code>
{`본질가치 = (자산가치 x 1 + 수익가치 x 1.5) / 2.5

또는 동일하게:

본질가치 = 자산가치 x 40% + 수익가치 x 60%`}
          </code>
        </pre>
      </section>

      {/* 6단계 프로세스 */}
      <section>
        <h2 id="process">본질가치 평가 6단계 프로세스</h2>
        <ol>
          <li>
            <strong>1단계:</strong> 재무제표 수집 및 기초 분석 (3개년 확보,
            정규화)
          </li>
          <li>
            <strong>2단계:</strong> 자산가치 계산 (순자산가치법)
          </li>
          <li>
            <strong>3단계:</strong> 수익가치 계산 (수익환원법)
          </li>
          <li>
            <strong>4단계:</strong> 본질가치 산출 (가중평균)
          </li>
          <li>
            <strong>5단계:</strong> 평가 범위 제시 및 교차 검증
          </li>
          <li>
            <strong>6단계:</strong> 법적 요구사항 준수 및 보고서 작성
          </li>
        </ol>
      </section>

      {/* 수익가치 */}
      <section>
        <h2 id="income-value">수익가치 계산 (수익환원법)</h2>
        <pre>
          <code>{`수익가치 = 정상수익 / 자본환원율`}</code>
        </pre>
        <h3>정상수익 산정</h3>
        <p>
          직전 3개 사업연도 순이익을 가중평균합니다. 최근 연도에 더 높은
          가중치를 부여합니다.
        </p>
        <pre>
          <code>
{`정상수익 = (N-2년 순이익 x 1 + N-1년 순이익 x 2 + N년 순이익 x 3) / 6`}
          </code>
        </pre>
        <p>
          일회성 손익(자산처분이익, 보험차익, 소송비용 등)은 제거하여 기업의
          정상적인 수익력을 반영합니다.
        </p>

        <h3>자본환원율 산정</h3>
        <ul>
          <li>
            <strong>방법 1:</strong> 무위험수익률 + 업종별 위험프리미엄 + 중소기업
            규모프리미엄
          </li>
          <li>
            <strong>방법 2:</strong> CAPM(자본자산가격결정모형) 활용
          </li>
          <li>
            <strong>방법 3:</strong> 업종별 평균 자본비용 적용 (한국은행 등)
          </li>
        </ul>
        <p>
          실무에서는 여러 방법을 계산하여 범위를 확인하고, 보수적인 값(높은
          환원율)을 선택하는 것이 일반적입니다.
        </p>
      </section>

      {/* 자산가치 */}
      <section>
        <h2 id="asset-value">자산가치 계산 (순자산가치법)</h2>
        <pre>
          <code>{`1주당 자산가치 = 조정 순자산가치 / 발행주식총수`}</code>
        </pre>
        <p>
          장부상 순자산에 대해 자산 항목별 시장가치 재평가(토지, 건물, 기계장치,
          투자자산, 무형자산 등), 부채 항목별 시장가치 재평가(장기차입금 현재가치,
          전환사채 분리평가), 비계상 항목(자체 개발 무형자산, 우발부채) 반영을
          수행합니다.
        </p>
      </section>

      {/* 가중평균 */}
      <section>
        <h2 id="weighted-average">본질가치 산출 (가중평균)</h2>
        <pre>
          <code>
{`1주당 본질가치 = (1주당 자산가치 x 1 + 1주당 수익가치 x 1.5) / 2.5

= 1주당 자산가치 x 40% + 1주당 수익가치 x 60%`}
          </code>
        </pre>
        <p>
          이 공식은 수익가치에 더 높은 가중치(60%)를 부여하여 기업의 계속기업
          관점을 반영합니다.
        </p>
      </section>

      {/* 계산 예시 */}
      <section>
        <h2 id="example">계산 예시: (주)테크밸리</h2>
        <p>
          비상장 제조기업, M&A(합병) 추진 중, 반대주주 주식매수청구권 대비,
          발행주식수 100만주.
        </p>

        <h3>1. 자산가치</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>금액</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>조정 총자산</td>
              <td>172억원</td>
            </tr>
            <tr>
              <td>조정 총부채</td>
              <td>75억원</td>
            </tr>
            <tr>
              <td>
                <strong>순자산</strong>
              </td>
              <td>
                <strong>97억원</strong>
              </td>
            </tr>
            <tr>
              <td>
                <strong>1주당 자산가치</strong>
              </td>
              <td>
                <strong>9,700원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>2. 수익가치</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>값</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>3년 가중평균 정상수익</td>
              <td>10.67억원</td>
            </tr>
            <tr>
              <td>자본환원율</td>
              <td>11.5%</td>
            </tr>
            <tr>
              <td>
                <strong>수익가치</strong>
              </td>
              <td>
                <strong>93억원</strong>
              </td>
            </tr>
            <tr>
              <td>
                <strong>1주당 수익가치</strong>
              </td>
              <td>
                <strong>9,300원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>3. 본질가치 산출</h3>
        <pre>
          <code>
{`본질가치 = 97억 x 40% + 93억 x 60% = 38.8억 + 55.8억 = 94.6억원

1주당 본질가치 = 94.6억 / 100만주 = 9,460원`}
          </code>
        </pre>
        <p>
          민감도 분석: 자본환원율 1%p 상승 시 본질가치 약 6% 하락. 적정 가치
          범위는 9,000원 ~ 10,000원, 중심값 9,460원.
        </p>
      </section>

      {/* 장단점 */}
      <section>
        <h2 id="pros-cons">장단점</h2>
        <h3>장점</h3>
        <ul>
          <li>법적 강제성이 있어 법원과 감독기관이 인정하는 객관적 기준</li>
          <li>표준화된 방법론으로 자의적 판단 배제</li>
          <li>자산가치와 수익가치를 균형있게 반영</li>
          <li>분쟁 발생 시 객관적 해결 근거 제공</li>
        </ul>
        <h3>단점</h3>
        <ul>
          <li>과거 실적 기반이라 미래 성장성 반영 제한</li>
          <li>자본환원율 설정에 따라 수익가치가 크게 변동</li>
          <li>법정 비율이 고정되어 산업 특성 반영 제한</li>
          <li>외부평가기관 선정 등 법적 절차 비용 발생</li>
        </ul>
      </section>

      {/* 적용 사례 */}
      <section>
        <h2 id="use-cases">적용 사례</h2>
        <ul>
          <li>
            <strong>주식매수청구권 행사:</strong> 합병, 분할, 영업양도 등에서
            반대주주의 주식매수가격 산정
          </li>
          <li>
            <strong>상장사 간 합병:</strong> 합병비율 산정 및
            외부평가의견서 작성
          </li>
          <li>
            <strong>Pre-IPO 기업가치 산정:</strong> 제3자 배정 증자 시
            발행가액의 적정성 입증
          </li>
          <li>
            <strong>주식교환 M&A:</strong> 교환비율 산정을 위한 본질가치
            활용
          </li>
        </ul>
      </section>
    </GuideTemplate>
  )
}
