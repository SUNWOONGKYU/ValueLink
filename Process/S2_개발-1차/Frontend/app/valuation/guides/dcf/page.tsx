/**
 * @task S2F3
 * @description DCF (현금흐름할인법) 가이드 페이지 - Server Component
 */

import type { Metadata } from 'next'
import GuideTemplate from '@/components/guide-template'

export const metadata: Metadata = {
  title: 'DCF 현금흐름할인법 안내 - ValueLink',
  description:
    'DCF(Discounted Cash Flow) 평가법의 개념, WACC 계산, FCF 추정, 터미널 가치 산출까지 실무 중심으로 안내합니다.',
  keywords: [
    'DCF',
    '현금흐름할인법',
    '기업가치평가',
    'WACC',
    'FCF',
    '터미널가치',
    'Discounted Cash Flow',
    '할인율',
    '비상장주식',
  ],
  openGraph: {
    title: 'DCF 현금흐름할인법 안내 - ValueLink',
    description:
      'DCF 평가법의 핵심 원리부터 실무 계산 예시까지 상세히 안내합니다.',
    type: 'article',
    locale: 'ko_KR',
  },
}

export default async function DcfGuidePage() {
  return (
    <GuideTemplate
      methodName="dcf"
      title="DCF 현금흐름할인법"
      description="기업이 미래에 창출할 현금흐름을 현재가치로 환산하여 기업가치를 평가하는 방법입니다. 기업가치평가 실무에서 가장 광범위하게 사용되는 방법론입니다."
    >
      {/* 개요 */}
      <section>
        <h2 id="overview">개요</h2>
        <p>
          <strong>DCF(Discounted Cash Flow) 평가법</strong>은 기업이나 자산이
          미래에 창출할 현금흐름을 현재가치로 환산하여 가치를 평가하는 방법입니다.
          DCF의 핵심은 <strong>화폐의 시간가치(Time Value of Money)</strong>{' '}
          원리입니다. 오늘의 100만원과 5년 후의 100만원은 가치가 다릅니다. 오늘
          받은 100만원은 투자하여 수익을 낼 수 있고, 인플레이션과 위험도 고려해야
          하기 때문입니다.
        </p>
        <p>
          DCF가 필요한 이유는 크게 세 가지입니다. 첫째, 주가나 시장 분위기와
          무관하게 기업의 <strong>내재가치(Intrinsic Value)</strong>를 발견할 수
          있습니다. 둘째, VC/PE 투자 타당성 검증, M&A 가격 협상, IPO 공모가 산정
          등 <strong>투자 의사결정의 근거</strong>로 활용됩니다. 셋째,
          자본시장법상 외부평가의견서 제출, 상증세법상 보충적 평가방법 등{' '}
          <strong>법적/제도적 요구사항</strong>을 충족합니다.
        </p>
      </section>

      {/* 핵심 공식 */}
      <section>
        <h2 id="formula">핵심 공식</h2>
        <pre>
          <code>
{`기업가치(Enterprise Value)
  = Sum[ FCF(t) / (1 + WACC)^t ] + Terminal Value / (1 + WACC)^n

여기서:
  FCF  = Free Cash Flow (잉여현금흐름)
  WACC = Weighted Average Cost of Capital (가중평균자본비용)
  TV   = Terminal Value (추정기간 이후 영속가치)
  n    = 추정기간 (통상 5~10년)`}
          </code>
        </pre>
      </section>

      {/* 5단계 프로세스 */}
      <section>
        <h2 id="process">DCF 평가 5단계 프로세스</h2>
        <ol>
          <li>
            <strong>1단계: 재무제표 수집 및 과거 실적 분석</strong> - 최소 3~5개년
            재무제표를 확보하고, 비경상적 항목을 제거하는 정규화(Normalization)를
            수행합니다.
          </li>
          <li>
            <strong>2단계: 미래 현금흐름 추정 (FCF 계산)</strong> - NOPLAT,
            감가상각비, CapEx, 순운전자본 변동을 반영하여 FCFF를 산출합니다.
          </li>
          <li>
            <strong>3단계: 할인율 산정 (WACC 계산)</strong> - 자기자본비용과
            타인자본비용의 가중평균으로 할인율을 결정합니다.
          </li>
          <li>
            <strong>4단계: Terminal Value 계산</strong> - 추정기간 이후 영속가치를
            영구성장모형 또는 Exit Multiple 방식으로 산출합니다.
          </li>
          <li>
            <strong>5단계: 현재가치 할인 및 기업가치/주식가치 도출</strong> -
            기업가치에서 순부채를 차감하고 비영업자산을 가산하여 자기자본가치를
            산출합니다.
          </li>
        </ol>
      </section>

      {/* FCFF 계산 */}
      <section>
        <h2 id="fcff">FCFF (잉여현금흐름) 계산</h2>
        <p>
          FCFF는 기업이 영업활동으로 창출한 현금 중, 운영 유지에 필요한 투자를
          하고 남은 &quot;주주와 채권자 모두에게 배분 가능한 현금&quot;입니다.
        </p>
        <pre>
          <code>
{`FCFF = NOPLAT + 감가상각비 - 자본적지출(CapEx) - 순운전자본 증가액

여기서:
  NOPLAT = EBIT x (1 - 실효세율)    [세후영업이익]
  CapEx  = 유형자산 및 무형자산 취득액
  ΔNWC   = 영업관련 유동자산 - 영업관련 유동부채의 변동액`}
          </code>
        </pre>
      </section>

      {/* WACC 계산 */}
      <section>
        <h2 id="wacc">WACC (가중평균자본비용) 계산</h2>
        <p>
          WACC는 기업이 자금을 조달하는 데 드는 가중평균비용으로, DCF 평가의 핵심
          할인율입니다.
        </p>
        <pre>
          <code>
{`WACC = (E/V) x Re + (D/V) x Rd x (1 - T)

여기서:
  Re  = 자기자본비용 (CAPM: Rf + Beta x ERP + SRP)
  Rd  = 타인자본비용
  T   = 실효세율
  E/V = 자기자본 비중
  D/V = 타인자본 비중`}
          </code>
        </pre>
        <h3>자기자본비용 (CAPM)</h3>
        <p>
          자기자본비용은 CAPM(Capital Asset Pricing Model)을 사용하여
          산정합니다. 무위험이자율(Rf), 베타(Beta), 시장위험프리미엄(ERP)을 결정하며,
          비상장사의 경우 유사 상장사의 베타를 참고하여 Unlevered Beta를 계산한 후
          대상 기업의 자본구조로 Re-levering합니다.
        </p>
      </section>

      {/* Terminal Value */}
      <section>
        <h2 id="terminal-value">Terminal Value (영구가치)</h2>
        <p>
          Terminal Value는 명시적 추정기간 이후 기업이 창출하는 모든 미래
          현금흐름의 현재가치로, DCF 기업가치의 60~80%를 차지할 정도로
          중요합니다.
        </p>
        <h3>영구성장모형 (Gordon Growth Model)</h3>
        <pre>
          <code>
{`TV = FCF(n+1) / (WACC - g)

여기서:
  FCF(n+1) = 추정 마지막 해 다음 년도의 현금흐름
  g        = 영구성장률 (일반적으로 0~2%)`}
          </code>
        </pre>
        <p>
          영구성장률은 보수적으로 설정하는 것이 원칙이며, 명목 GDP 성장률을
          초과할 수 없습니다.
        </p>
        <h3>Exit Multiple 방식</h3>
        <pre>
          <code>{`TV = EBITDA(n) x Exit Multiple`}</code>
        </pre>
        <p>
          VC/PE 투자나 경기순환 산업에서 사용되며, Gordon Model과 병행하여 범위
          제시 용도로 활용됩니다.
        </p>
      </section>

      {/* 계산 예시 */}
      <section>
        <h2 id="example">계산 예시: 제조업체 A사</h2>
        <p>
          평가기준일 2024년 12월 31일, 발행주식수 200만주인 제조업체 A사의 DCF
          평가 사례입니다.
        </p>

        <h3>1. FCFF 추정 (2025년 기준)</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>금액</th>
              <th>산출 근거</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>EBIT</td>
              <td>238억원</td>
              <td>매출 1,080억 x 영업이익률 22%</td>
            </tr>
            <tr>
              <td>NOPLAT</td>
              <td>182억원</td>
              <td>238억 x (1 - 0.233)</td>
            </tr>
            <tr>
              <td>감가상각비</td>
              <td>54억원</td>
              <td>매출액의 5%</td>
            </tr>
            <tr>
              <td>CapEx</td>
              <td>99억원</td>
              <td>매출액의 9.2%</td>
            </tr>
            <tr>
              <td>순운전자본 증가액</td>
              <td>13억원</td>
              <td>NWC 16.6% x 매출 증가 80억</td>
            </tr>
            <tr>
              <td>
                <strong>FCFF</strong>
              </td>
              <td>
                <strong>124억원</strong>
              </td>
              <td>182 + 54 - 99 - 13</td>
            </tr>
          </tbody>
        </table>

        <h3>2. WACC 산정</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>값</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>자기자본비용 (Re)</td>
              <td>12.4% (Rf 3.5% + Beta 1.05 x ERP 8.5%)</td>
            </tr>
            <tr>
              <td>타인자본비용 (Rd)</td>
              <td>5.0%</td>
            </tr>
            <tr>
              <td>자기자본 비중</td>
              <td>82%</td>
            </tr>
            <tr>
              <td>타인자본 비중</td>
              <td>18%</td>
            </tr>
            <tr>
              <td>
                <strong>WACC</strong>
              </td>
              <td>
                <strong>10.9%</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>3. 최종 가치 산출</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>금액</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>추정기간 FCFF 현재가치 합계</td>
              <td>517억원</td>
            </tr>
            <tr>
              <td>Terminal Value 현재가치</td>
              <td>1,179억원</td>
            </tr>
            <tr>
              <td>기업가치 (EV)</td>
              <td>1,696억원</td>
            </tr>
            <tr>
              <td>(-) 순부채</td>
              <td>650억원</td>
            </tr>
            <tr>
              <td>(+) 비영업자산</td>
              <td>120억원</td>
            </tr>
            <tr>
              <td>
                <strong>자기자본가치</strong>
              </td>
              <td>
                <strong>1,166억원</strong>
              </td>
            </tr>
            <tr>
              <td>
                <strong>주당가치</strong>
              </td>
              <td>
                <strong>58,300원</strong>
              </td>
            </tr>
          </tbody>
        </table>
        <p>
          WACC와 영구성장률의 변동에 따른 민감도 분석을 통해 A사의
          자기자본가치는 1,050억원 ~ 1,300억원 범위로 평가되며, 주당가치로는
          52,500원 ~ 65,000원 범위입니다.
        </p>
      </section>

      {/* 장단점 */}
      <section>
        <h2 id="pros-cons">장단점</h2>
        <h3>장점</h3>
        <ul>
          <li>
            기업의 현금창출능력에 기반한 <strong>내재가치</strong> 산출 가능
          </li>
          <li>미래지향적 평가로 성장 가능성 반영</li>
          <li>이론적 엄밀성이 높아 학계와 실무 모두에서 인정</li>
          <li>민감도 분석을 통한 가치 범위 제시 가능</li>
        </ul>
        <h3>단점</h3>
        <ul>
          <li>미래 현금흐름 추정의 불확실성</li>
          <li>WACC, 영구성장률 등 가정에 민감</li>
          <li>계산이 복잡하고 전문성 요구</li>
          <li>
            초기 스타트업(현금흐름 마이너스), 경기순환 극심 산업에는 부적합
          </li>
        </ul>
      </section>

      {/* 적용 사례 */}
      <section>
        <h2 id="use-cases">적용 사례</h2>
        <ul>
          <li>
            <strong>M&A 가격 결정:</strong> Stand-alone 가치와 시너지 가치를
            반영하여 인수가격을 결정
          </li>
          <li>
            <strong>스타트업 투자 (Series A):</strong> VC Method와 DCF를 병행하여
            Exit 시점의 기업가치를 추정하고 투자 타당성 검증
          </li>
          <li>
            <strong>손상평가 (Impairment):</strong> 자산의 사용가치를 재평가하고
            손상차손 인식
          </li>
          <li>
            <strong>IPO 공모가 산정:</strong> 상장 시 적정 기업가치를 산출하여
            공모가 밴드 설정
          </li>
        </ul>
      </section>
    </GuideTemplate>
  )
}
