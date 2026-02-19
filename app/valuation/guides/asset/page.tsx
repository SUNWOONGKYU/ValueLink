/**
 * @task S2F3
 * @description 자산가치평가 가이드 페이지 - Server Component
 */

import type { Metadata } from 'next'
import GuideTemplate from '@/components/guide-template'

export const metadata: Metadata = {
  title: '자산가치평가 안내 - ValueLink',
  description:
    '자산가치평가(Asset-Based Valuation)의 개념, 유형자산/무형자산 평가, 부채 공제, 순자산가치(NAV) 산출까지 실무 중심으로 안내합니다.',
  keywords: [
    '자산가치평가',
    'NAV',
    '순자산가치',
    '청산가치',
    'SOTP',
    '감정평가',
    'Asset-Based Valuation',
    '비상장주식',
  ],
  openGraph: {
    title: '자산가치평가 안내 - ValueLink',
    description:
      '기업 보유 자산의 시장가치에서 부채를 차감하여 순자산가치를 산출하는 자산가치평가를 안내합니다.',
    type: 'article',
    locale: 'ko_KR',
  },
}

export default async function AssetGuidePage() {
  return (
    <GuideTemplate
      methodName="asset"
      title="자산가치평가"
      description="기업이 보유한 자산의 시장가치에서 부채를 차감하여 순자산가치를 산출하는 평가방법입니다. '지금 이 기업을 해체하면 얼마의 가치가 있는가?'라는 현재 중심의 질문에 답합니다."
    >
      {/* 개요 */}
      <section>
        <h2 id="overview">개요</h2>
        <p>
          <strong>자산가치평가(Asset-Based Valuation)</strong>는 기업이 보유한
          자산의 시장가치에서 부채를 차감하여 기업의 순자산가치를 산출하는
          평가방법입니다. DCF가 미래의 현금창출능력에 초점을 맞춘다면,
          자산가치평가는 현재 보유 자산의 가치를 직접 평가합니다.
        </p>
        <pre>
          <code>{`순자산가치(NAV) = 자산의 시장가치 - 부채의 시장가치`}</code>
        </pre>
        <p>
          자산가치평가에서는 <strong>청산가치(Liquidation Value)</strong>와{' '}
          <strong>계속기업가치(Going Concern Value)</strong>를 구분합니다.
          청산가치는 자산을 급하게 처분할 때의 가치로 20-70% 할인이 적용되며,
          계속기업가치는 영업 지속을 전제로 한 가치입니다.
        </p>
      </section>

      {/* 6단계 프로세스 */}
      <section>
        <h2 id="process">자산가치 평가 6단계 프로세스</h2>
        <ol>
          <li>
            <strong>1단계:</strong> 재무상태표 확보 및 기초 분석
          </li>
          <li>
            <strong>2단계:</strong> 자산 항목별 시장가치 재평가
          </li>
          <li>
            <strong>3단계:</strong> 부채 항목별 시장가치 재평가
          </li>
          <li>
            <strong>4단계:</strong> 우발부채 및 비계상 항목 반영
          </li>
          <li>
            <strong>5단계:</strong> 비영업자산 식별 및 분리 평가
          </li>
          <li>
            <strong>6단계:</strong> 순자산가치 및 주당가치 산출
          </li>
        </ol>
      </section>

      {/* 유형자산 평가 */}
      <section>
        <h2 id="tangible-assets">유형자산 평가</h2>
        <h3>토지</h3>
        <ul>
          <li>
            <strong>1순위:</strong> 공인감정평가법인의 감정평가액 (가장 신뢰도
            높음)
          </li>
          <li>
            <strong>2순위:</strong> 인근 유사 토지의 실거래가 비교
          </li>
          <li>
            <strong>3순위:</strong> 개별공시지가에 현실화율과 할증률 적용
          </li>
        </ul>

        <h3>건물</h3>
        <pre>
          <code>{`건물 시장가치 = 재조달원가 - 감가상각 누계액`}</code>
        </pre>

        <h3>기계장치 및 설비</h3>
        <ul>
          <li>중고시장 거래가 참고 (KOAMI 등)</li>
          <li>신품 가격에 감가상각률과 경과년수 적용</li>
          <li>청산가치: 장부가액에 회수율(30~50%) 적용</li>
        </ul>

        <h3>재고자산</h3>
        <pre>
          <code>{`순실현가능가치(NRV) = 예상 판매가격 - 판매비용`}</code>
        </pre>
      </section>

      {/* 무형자산 평가 */}
      <section>
        <h2 id="intangible-assets">무형자산 평가</h2>
        <h3>특허권 및 상표권: 로열티 면제법</h3>
        <pre>
          <code>
{`무형자산 가치 = Sum[ 예상매출액 x 로열티율 x (1 - 세율) / (1 + 할인율)^t ]`}
          </code>
        </pre>

        <h3>브랜드 가치: 초과수익 환원법</h3>
        <pre>
          <code>{`브랜드 가치 = 초과 수익 / 자본화율`}</code>
        </pre>

        <h3>영업권 (Goodwill)</h3>
        <pre>
          <code>{`영업권 회수가능액 = Max(순공정가치, 사용가치)`}</code>
        </pre>
      </section>

      {/* 부채 공제 */}
      <section>
        <h2 id="debt">부채 시장가치 재평가</h2>
        <h3>단기부채</h3>
        <p>
          만기 1년 이내 단기부채는 일반적으로 장부가액을 시장가치로 간주합니다.
        </p>

        <h3>장기부채</h3>
        <pre>
          <code>
{`시장가치 = Sum[ 연간이자 / (1 + 시장이자율)^t ] + 원금 / (1 + 시장이자율)^n`}
          </code>
        </pre>

        <h3>전환사채 (CB)</h3>
        <p>
          부채 요소와 전환권 가치를 분리하여 평가합니다. 전환권은
          Black-Scholes 옵션가격 모형으로 산정합니다.
        </p>

        <h3>우발부채</h3>
        <pre>
          <code>
{`예상 부채 = 소송 청구액 x 패소 확률 x (1 / (1 + 할인율)^예상기간)`}
          </code>
        </pre>
      </section>

      {/* 계산 예시 */}
      <section>
        <h2 id="example">계산 예시: (주)한국부동산개발</h2>
        <p>
          평가기준일 2025년 3월 31일, 발행주식수 100만주, 재무상태표상 순자산
          150억원.
        </p>

        <h3>자산 재평가</h3>
        <table>
          <thead>
            <tr>
              <th>자산 항목</th>
              <th>장부가액</th>
              <th>시장가치</th>
              <th>증감</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>토지</td>
              <td>80억원</td>
              <td>200억원</td>
              <td>+120억원</td>
            </tr>
            <tr>
              <td>건물</td>
              <td>50억원</td>
              <td>60억원</td>
              <td>+10억원</td>
            </tr>
            <tr>
              <td>기계설비</td>
              <td>30억원</td>
              <td>20억원</td>
              <td>-10억원</td>
            </tr>
            <tr>
              <td>상장주식</td>
              <td>20억원</td>
              <td>35억원</td>
              <td>+15억원</td>
            </tr>
            <tr>
              <td>기타</td>
              <td>120억원</td>
              <td>116억원</td>
              <td>-4억원</td>
            </tr>
            <tr>
              <td>
                <strong>자산 총계</strong>
              </td>
              <td>
                <strong>300억원</strong>
              </td>
              <td>
                <strong>431억원</strong>
              </td>
              <td>
                <strong>+131억원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>부채 재평가</h3>
        <table>
          <thead>
            <tr>
              <th>부채 항목</th>
              <th>장부가액</th>
              <th>시장가치</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>단기차입금</td>
              <td>50억원</td>
              <td>50억원</td>
            </tr>
            <tr>
              <td>장기차입금</td>
              <td>70억원</td>
              <td>65억원</td>
            </tr>
            <tr>
              <td>매입채무</td>
              <td>30억원</td>
              <td>30억원</td>
            </tr>
            <tr>
              <td>우발부채 (소송)</td>
              <td>-</td>
              <td>10억원</td>
            </tr>
            <tr>
              <td>
                <strong>부채 총계</strong>
              </td>
              <td>
                <strong>150억원</strong>
              </td>
              <td>
                <strong>155억원</strong>
              </td>
            </tr>
          </tbody>
        </table>

        <h3>최종 산출</h3>
        <table>
          <thead>
            <tr>
              <th>항목</th>
              <th>금액</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>조정 자산 총계</td>
              <td>431억원</td>
            </tr>
            <tr>
              <td>조정 부채 총계</td>
              <td>155억원</td>
            </tr>
            <tr>
              <td>
                <strong>순자산가치(NAV)</strong>
              </td>
              <td>
                <strong>276억원</strong>
              </td>
            </tr>
            <tr>
              <td>
                <strong>주당 순자산가치</strong>
              </td>
              <td>
                <strong>27,600원</strong>
              </td>
            </tr>
          </tbody>
        </table>
        <p>
          장부가 대비 순자산가치가 84% 상승하였으며, 주로 토지 가치 상승과 보유
          상장주식 평가이익에 기인합니다.
        </p>
      </section>

      {/* 장단점 */}
      <section>
        <h2 id="pros-cons">장단점</h2>
        <h3>장점</h3>
        <ul>
          <li>객관성과 검증가능성이 높음 (감정평가, 시장가격 기반)</li>
          <li>미래 예측이 필요 없어 불확실성이 낮음</li>
          <li>기업가치의 하한선(Floor Value) 제시에 유용</li>
          <li>자산집약적 산업에서 가장 정확한 평가 가능</li>
        </ul>
        <h3>단점</h3>
        <ul>
          <li>무형자산(브랜드, 고객관계, 조직역량) 평가가 어려움</li>
          <li>계속기업 관점의 초과 수익(영업권) 미반영</li>
          <li>감정평가 시점과 실제 거래 시점의 차이 발생 가능</li>
          <li>IT, 바이오, 서비스업처럼 무형자산 중심 산업에 부적합</li>
        </ul>
      </section>

      {/* 적용 사례 */}
      <section>
        <h2 id="use-cases">적용 사례</h2>
        <ul>
          <li>
            <strong>부동산 보유 기업 평가:</strong> 부동산 가치 상승을 반영하여
            영업이익 기반 평가보다 현실적인 가치 도출
          </li>
          <li>
            <strong>부실기업 청산가치 산정:</strong> 미래 현금흐름 예측이
            불가능한 기업의 채권자/주주 회수 가능액 산정
          </li>
          <li>
            <strong>지주회사 SOTP 평가:</strong> 각 자회사 가치를 개별 평가한 후
            합산하고 지주회사 할인(10~30%) 적용
          </li>
        </ul>
      </section>
    </GuideTemplate>
  )
}
