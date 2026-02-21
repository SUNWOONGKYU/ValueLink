/**
 * @task S2F3
 * @description 세법상 평가 (상속세법) 가이드 페이지 - Server Component
 */

import type { Metadata } from 'next'
import GuideTemplate from '@/components/guide-template'

export const metadata: Metadata = {
  title: '세법상 평가 (상속세법) 안내 - ValueLink',
  description:
    '상속세 및 증여세법에 따른 비상장주식 평가법의 개념, 순손익가치와 순자산가치의 가중평균(60:40), 할인/할증, 계산 예시까지 실무 중심으로 안내합니다.',
  keywords: [
    '상증세법',
    '상속세',
    '증여세',
    '비상장주식 평가',
    '순손익가치',
    '순자산가치',
    '가업승계',
    '최대주주 할증',
    '소액주주 할인',
  ],
  openGraph: {
    title: '세법상 평가 (상속세법) 안내 - ValueLink',
    description:
      '상속세 및 증여세법에 따른 비상장주식 평가법으로, 순손익가치 60%와 순자산가치 40%를 가중평균합니다.',
    type: 'article',
    locale: 'ko_KR',
  },
}

export default async function TaxGuidePage() {
  return (
    <GuideTemplate
      methodName="tax"
      title="세법상 평가 (상속세법)"
      description="상속세 및 증여세법 시행령 제54조에 근거하여, 비상장주식의 가치를 순손익가치 60%와 순자산가치 40%로 가중평균하는 법정 평가 방법입니다. 상속세/증여세 과세 목적으로 사용됩니다."
    >
      {/* 개요 */}
      <section>
        <h2 id="overview">개요</h2>
        <p>
          <strong>상증세법 평가법</strong>은 상속세 및 증여세법에 따라
          비상장주식의 가치를 평가하는 법정 방법입니다. 핵심 계산 구조는{' '}
          <strong>순손익가치 60%와 순자산가치 40%를 가중평균</strong>하는
          방식입니다. 순손익가치에 3의 가중치를, 순자산가치에 2의 가중치를
          부여합니다.
        </p>
        <p>
          비상장주식 평가의 목적은 시장가격이 형성되지 않는 비상장기업의 주식을
          상속하거나 증여할 때, 과세당국과 납세자가 합의할 수 있는 공정한 기준을
          제공하는 것입니다.
        </p>
      </section>

      {/* 핵심 공식 */}
      <section>
        <h2 id="formula">핵심 공식</h2>
        <pre>
          <code>
{`평가액 = (순손익가치 x 3 + 순자산가치 x 2) / 5

또는 동일하게:

평가액 = 순손익가치 x 60% + 순자산가치 x 40%`}
          </code>
        </pre>
      </section>

      {/* 순손익가치 */}
      <section>
        <h2 id="income-value">순손익가치 계산</h2>
        <h3>각 사업연도 순손익액</h3>
        <p>
          순손익액은 회계상 당기순이익이 아닌{' '}
          <strong>세무조정 후 각 사업연도 소득금액</strong>입니다. 법인세
          신고서의 세무조정계산서를 통해 손금불산입, 익금불산입, 손금산입,
          익금산입 항목을 반영합니다. 일회성/비정상적 손익은 제거합니다.
        </p>

        <h3>3년 평균 순손익</h3>
        <p>
          직전 3개 사업연도의 최종 순손익액을{' '}
          <strong>단순산술평균</strong>합니다. (자본시장법과 달리 가중평균이
          아님에 주의)
        </p>

        <h3>1주당 순손익가치</h3>
        <pre>
          <code>
{`1주당 순손익액 = 3년 평균 순손익 / 발행주식총수

1주당 순손익가치 = 1주당 순손익액 / 할인율(10%)`}
          </code>
        </pre>
        <p>
          할인율은 현행 상속세 및 증여세법 시행령 제54조에 따라{' '}
          <strong>10%</strong>를 적용합니다. (국세청 고시로 변경 가능)
        </p>
      </section>

      {/* 순자산가치 */}
      <section>
        <h2 id="asset-value">순자산가치 계산</h2>
        <p>
          평가기준일 현재 재무상태표의 자산/부채를 세법상 시가로 재평가합니다.
        </p>
        <table>
          <thead>
            <tr>
              <th>자산 항목</th>
              <th>평가 기준</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>토지</td>
              <td>개별공시지가 또는 감정평가액</td>
            </tr>
            <tr>
              <td>건물</td>
              <td>국세청 기준시가 또는 감정평가액</td>
            </tr>
            <tr>
              <td>상장주식</td>
              <td>평가기준일 전후 2개월 평균 종가</td>
            </tr>
            <tr>
              <td>비상장주식</td>
              <td>상증세법 재귀적 적용</td>
            </tr>
            <tr>
              <td>채권</td>
              <td>액면가에 잔존기간별 할인율 적용</td>
            </tr>
            <tr>
              <td>매출채권</td>
              <td>장부가액 - 대손추산액</td>
            </tr>
            <tr>
              <td>재고자산</td>
              <td>순실현가능가치 또는 장부가액</td>
            </tr>
          </tbody>
        </table>
        <pre>
          <code>
{`순자산 시가 = Sum(자산 항목별 시가) - Sum(부채 항목별 시가) - 우발부채

1주당 순자산가치 = 순자산 시가 / 발행주식총수`}
          </code>
        </pre>
      </section>

      {/* 가중평가 */}
      <section>
        <h2 id="weighted-average">1주당 평가액 산출 (가중평균)</h2>
        <pre>
          <code>
{`1주당 평가액 = (1주당 순손익가치 x 3 + 1주당 순자산가치 x 2) / 5`}
          </code>
        </pre>
      </section>

      {/* 할인/할증 */}
      <section>
        <h2 id="adjustment">할인 / 할증 적용</h2>
        <h3>20% 할증 (최대주주)</h3>
        <p>
          최대주주 및 그 특수관계인이 보유한 주식은 경영권 프리미엄을 반영하여
          20% 할증됩니다. 지분율 합계가 50% 초과하거나 경영권 행사가 명백한
          경우에 적용됩니다.
        </p>
        <pre>
          <code>{`할증 후 평가액 = 1주당 평가액 x 1.20`}</code>
        </pre>

        <h3>20% 할인 (소액주주)</h3>
        <p>다음 중 하나를 충족하는 소액주주 보유 주식에 적용됩니다.</p>
        <ul>
          <li>해당 주주 및 특수관계인 지분율 합계가 3% 미만</li>
          <li>보유 주식 시가총액이 15억원 미만 (2024년 기준)</li>
        </ul>
        <pre>
          <code>{`할인 후 평가액 = 1주당 평가액 x 0.80`}</code>
        </pre>
      </section>

      {/* 계산 예시 */}
      <section>
        <h2 id="example">계산 예시: A제조(주) 상속세 신고용 평가</h2>
        <p>
          제조업, 12월 결산, 평가기준일 2024년 12월 31일, 발행주식수 100만주,
          피상속인 보유 지분 40%(최대주주).
        </p>

        <h3>1. 순손익가치 계산</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>값</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>3년 평균 순손익 (세무조정 후)</td>
              <td>19.33억원</td>
            </tr>
            <tr>
              <td>발행주식총수</td>
              <td>100만주</td>
            </tr>
            <tr>
              <td>1주당 순손익액</td>
              <td>1,933원</td>
            </tr>
            <tr>
              <td>할인율</td>
              <td>10%</td>
            </tr>
            <tr>
              <td>
                <strong>1주당 순손익가치</strong>
              </td>
              <td>
                <strong>19,330원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>2. 순자산가치 계산</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>값</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>순자산 시가 (세법상 재평가 후)</td>
              <td>134억원</td>
            </tr>
            <tr>
              <td>
                <strong>1주당 순자산가치</strong>
              </td>
              <td>
                <strong>13,400원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>3. 1주당 평가액</h3>
        <pre>
          <code>
{`1주당 평가액 = (19,330 x 3 + 13,400 x 2) / 5
             = (57,990 + 26,800) / 5
             = 16,958원`}
          </code>
        </pre>

        <h3>4. 할증 적용 (최대주주)</h3>
        <pre>
          <code>
{`1주당 최종 평가액 = 16,958 x 1.20 = 20,350원`}
          </code>
        </pre>

        <h3>5. 상속세 산정</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>금액</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>총 평가액 (20,350원 x 40만주)</td>
              <td>81.4억원</td>
            </tr>
            <tr>
              <td>과세표준 (공제 적용 후)</td>
              <td>85.4억원</td>
            </tr>
            <tr>
              <td>
                <strong>상속세</strong>
              </td>
              <td>
                <strong>38.1억원</strong>
              </td>
            </tr>
            <tr>
              <td>가업상속공제 적용 시</td>
              <td>0.7억원</td>
            </tr>
          </tbody>
        </table>
      </section>

      {/* 장단점 */}
      <section>
        <h2 id="pros-cons">장단점</h2>
        <h3>장점</h3>
        <ul>
          <li>법적 근거가 명확하여 세무조사 시 정당한 평가로 인정</li>
          <li>표준화된 계산식으로 평가의 객관성 확보</li>
          <li>수익가치(60%)와 자산가치(40%)를 균형있게 반영</li>
          <li>할인/할증 규정으로 주주 구조 반영 가능</li>
        </ul>
        <h3>단점</h3>
        <ul>
          <li>과거 3년 실적 평균 기반으로 미래 성장성 반영 제한</li>
          <li>보수적 평가 경향 (특히 성장기업의 경우)</li>
          <li>할인율(10%)이 고정되어 시장 상황 변화 미반영</li>
          <li>세무조정 과정이 복잡하여 전문가 필요</li>
        </ul>
      </section>

      {/* 적용 사례 */}
      <section>
        <h2 id="use-cases">적용 사례</h2>
        <ul>
          <li>
            <strong>가업승계 주식 증여:</strong> 부모가 자녀에게 경영권 승계를
            위해 주식을 증여할 때, 상증세법 평가액으로 세금 부담 계산 및
            가업상속공제 전략 수립
          </li>
          <li>
            <strong>경영자 사망 시 상속세 산정:</strong> 비상장주식의 상속세
            과세표준 산정
          </li>
          <li>
            <strong>소액주주 할인 전략:</strong> 각 자녀의 지분율을 3% 미만으로
            조정하여 20% 할인 적용으로 증여세 절감
          </li>
          <li>
            <strong>특수관계인 간 거래:</strong> 정상가액 산정의 기준 (평가액
            &plusmn;30% 범위 내 시가 인정)
          </li>
        </ul>
      </section>

      {/* 주의사항 */}
      <section>
        <h2 id="caution">주의사항</h2>
        <ul>
          <li>
            <strong>세무조정 누락:</strong> 반드시 세무조정 후 순손익을
            사용해야 합니다 (회계상 당기순이익 사용 불가)
          </li>
          <li>
            <strong>비정상 손익 미제거:</strong> 일회성 자산처분이익 등은
            제거하여 정상 수익력을 반영
          </li>
          <li>
            <strong>시가 인정 범위:</strong> 평가액의 &plusmn;30% 범위를
            벗어나는 거래는 세무조사 대상이 될 수 있음
          </li>
          <li>
            <strong>전문가 협업:</strong> 세무사 및 회계사와의 협업이
            필수적이며, 국세청 유권해석 확인 권장
          </li>
        </ul>
      </section>
    </GuideTemplate>
  )
}
