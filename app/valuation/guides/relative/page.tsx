/**
 * @task S2F3
 * @description 상대가치평가 가이드 페이지 - Server Component
 */

import type { Metadata } from 'next'
import GuideTemplate from '@/components/guide-template'

export const metadata: Metadata = {
  title: '상대가치평가 안내 - ValueLink',
  description:
    '상대가치평가(Relative Valuation)의 개념, 비교기업 선정, PER/PBR/EV_EBITDA 멀티플 계산, 비상장할인까지 실무 중심으로 안내합니다.',
  keywords: [
    '상대가치평가',
    'Relative Valuation',
    'PER',
    'PBR',
    'EV/EBITDA',
    'PSR',
    '멀티플',
    '비교기업분석',
    '비상장주식',
  ],
  openGraph: {
    title: '상대가치평가 안내 - ValueLink',
    description:
      '유사기업의 시장 배수를 활용한 상대가치평가의 핵심 원리와 계산 예시를 안내합니다.',
    type: 'article',
    locale: 'ko_KR',
  },
}

export default async function RelativeGuidePage() {
  return (
    <GuideTemplate
      methodName="relative"
      title="상대가치평가"
      description="비슷한 기업이 시장에서 어떻게 평가받는지를 기준으로 대상 기업의 가치를 추정하는 방법입니다. 멀티플(배수)을 활용하여 시장의 평가 기준을 반영합니다."
    >
      {/* 개요 */}
      <section>
        <h2 id="overview">개요</h2>
        <p>
          <strong>상대가치평가(Relative Valuation)</strong>는 비슷한 기업이
          시장에서 어떻게 평가받는지를 기준으로 대상 기업의 가치를 추정하는
          방법입니다. 핵심은 <strong>멀티플(Multiples)</strong>, 즉 가치평가
          배수입니다. PER이 15배라는 것은 투자자들이 1원의 이익을 내는 기업에
          15원을 지불할 의향이 있다는 의미입니다.
        </p>
        <p>
          DCF는 이론적으로 완벽하지만, 실제로는 시장이 다르게 평가할 수
          있습니다. 상대가치평가는 바로 이 시장의 시각을 반영합니다. 가장 큰
          장점은 속도입니다. DCF는 며칠이 걸리지만 상대가치평가는 비교기업 몇 개만
          찾으면 몇 시간 안에 가능합니다.
        </p>
      </section>

      {/* 6단계 프로세스 */}
      <section>
        <h2 id="process">상대가치 평가 6단계 프로세스</h2>
        <ol>
          <li>
            <strong>1단계:</strong> 평가 대상기업 재무제표 수집 및 정규화
          </li>
          <li>
            <strong>2단계:</strong> 비교가능 기업군(Peer Group) 선정
          </li>
          <li>
            <strong>3단계:</strong> 비교기업의 멀티플 계산
          </li>
          <li>
            <strong>4단계:</strong> 이상치 제거 및 대표값 산출
          </li>
          <li>
            <strong>5단계:</strong> 대상기업 특성 반영 조정
          </li>
          <li>
            <strong>6단계:</strong> 최종 가치 산출 및 범위 제시
          </li>
        </ol>
      </section>

      {/* 비교기업 선정 */}
      <section>
        <h2 id="peer-selection">비교기업 선정 기준</h2>
        <p>비교기업 선정 시 다음 5가지 기준을 확인해야 합니다.</p>
        <ol>
          <li>
            <strong>산업 동질성 (가장 중요):</strong> KSIC 소분류(4자리) 또는
            중분류(3자리) 동일, 사업 모델 유사성
          </li>
          <li>
            <strong>매출 규모 유사성:</strong> 대상기업 매출의 &plusmn;50% 범위
            내
          </li>
          <li>
            <strong>성장성 유사성:</strong> 최근 3년 평균 매출 성장률
            &plusmn;10%p 이내
          </li>
          <li>
            <strong>수익성 패턴:</strong> 영업이익률이 비슷한 기업 우선
          </li>
          <li>
            <strong>지리적/시장 환경:</strong> 코스피 vs 코스닥, 국내 vs 글로벌
          </li>
        </ol>
        <p>
          최소 3개 이상, 이상적으로 5~7개의 비교기업을 최종 선정합니다. 10개
          이상은 비효율적입니다.
        </p>
      </section>

      {/* 멀티플 종류 */}
      <section>
        <h2 id="multiples">주요 멀티플 종류</h2>

        <h3>PER (주가수익비율)</h3>
        <pre>
          <code>{`PER = 시가총액 / 당기순이익`}</code>
        </pre>
        <p>
          투자자들이 1원 순이익에 대해 얼마를 지불할 의향이 있는지를 나타냅니다.
          안정적 수익 기업, 성숙 산업에 적합하며, 적자 기업에는 부적합합니다.
        </p>

        <h3>PBR (주가순자산비율)</h3>
        <pre>
          <code>{`PBR = 시가총액 / 자기자본 (순자산)`}</code>
        </pre>
        <p>
          기업의 순자산 1원당 시장이 얼마를 지불하는지를 나타냅니다. 금융업,
          부동산, 자본집약 산업에 적합합니다.
        </p>

        <h3>PSR (주가매출액비율)</h3>
        <pre>
          <code>{`PSR = 시가총액 / 매출액`}</code>
        </pre>
        <p>
          매출 1원당 시가총액을 나타내며, 적자 스타트업이나 고성장 IT/바이오,
          SaaS에 유용합니다.
        </p>

        <h3>EV/EBITDA</h3>
        <pre>
          <code>
{`EV = 시가총액 + 순부채
순부채 = 총차입금 - 현금성자산
EV/EBITDA = EV / EBITDA`}
          </code>
        </pre>
        <p>
          부채 수준 차이를 제거하여 순수한 영업가치만 비교할 수 있습니다.
          제조업, 인프라, M&A 평가에 적합합니다.
        </p>
      </section>

      {/* 비상장할인 */}
      <section>
        <h2 id="discount">이상치 제거 및 대표값</h2>
        <p>
          비교기업 멀티플에서 통계적 이상치를 제거하고 대표값을 산출합니다.
        </p>
        <ul>
          <li>
            <strong>통계적 방법:</strong> 평균 &plusmn; 2 x 표준편차 밖 제거
          </li>
          <li>
            <strong>백분위 제거:</strong> 상위 10%, 하위 10% 제거 (실무에서 가장
            보편적)
          </li>
          <li>
            <strong>정성적 판단:</strong> M&A, 회계 정책 변경 등으로 왜곡된 기업
            제외
          </li>
        </ul>
        <p>
          기본적으로 이상치 제거 후 <strong>산술평균</strong>을 사용하고,{' '}
          <strong>중위값</strong>으로 검증하며, 상장사 평가 시{' '}
          <strong>가중평균</strong>을 고려합니다.
        </p>
      </section>

      {/* 계산 예시 */}
      <section>
        <h2 id="example">계산 예시: (주)뷰티코리아</h2>
        <p>
          화장품 ODM 제조 비상장사, 코스닥 IPO 준비 중, 평가기준일 2024년 12월
          31일, 발행주식수 200만주.
        </p>

        <h3>A사 재무 현황 (2024년)</h3>
        <table>
          <thead>
            <tr>
              <th>구분</th>
              <th>금액 (억원)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>매출액</td>
              <td>1,500</td>
            </tr>
            <tr>
              <td>영업이익</td>
              <td>170</td>
            </tr>
            <tr>
              <td>당기순이익</td>
              <td>150</td>
            </tr>
            <tr>
              <td>EBITDA</td>
              <td>200</td>
            </tr>
            <tr>
              <td>자기자본</td>
              <td>800</td>
            </tr>
            <tr>
              <td>순부채</td>
              <td>100</td>
            </tr>
          </tbody>
        </table>

        <h3>멀티플 적용 결과</h3>
        <table>
          <thead>
            <tr>
              <th>방식</th>
              <th>멀티플</th>
              <th>시가총액</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>PER 방식</td>
              <td>17배</td>
              <td>2,550억원</td>
            </tr>
            <tr>
              <td>PBR 방식</td>
              <td>2.2배</td>
              <td>1,760억원</td>
            </tr>
            <tr>
              <td>EV/EBITDA 방식</td>
              <td>16.5배</td>
              <td>3,200억원</td>
            </tr>
          </tbody>
        </table>

        <p>
          가중치(PER 50%, PBR 20%, EV/EBITDA 30%)를 적용한 통합 가치는 약
          2,587억원이며, 최종 가치 범위는 2,300억원 ~ 2,900억원, 주당
          130,000원입니다.
        </p>
      </section>

      {/* 장단점 */}
      <section>
        <h2 id="pros-cons">장단점</h2>
        <h3>장점</h3>
        <ul>
          <li>시장의 평가 기준을 직접 반영하여 현실적</li>
          <li>DCF 대비 빠른 산출이 가능</li>
          <li>투자자 커뮤니케이션에 효과적</li>
          <li>교차 검증 용도로 활용 가치 높음</li>
        </ul>
        <h3>단점</h3>
        <ul>
          <li>완벽히 비슷한 비교기업이 없을 수 있음</li>
          <li>시장 전체가 과열/침체 시 멀티플 왜곡</li>
          <li>비교기업 선정의 자의성</li>
          <li>회계정책 차이 미반영 시 오차 발생</li>
        </ul>
      </section>

      {/* 적용 사례 */}
      <section>
        <h2 id="use-cases">적용 사례</h2>
        <ul>
          <li>
            <strong>IPO 공모가 산정:</strong> 코스닥 상장 비교기업의 멀티플을
            활용하여 희망공모가 산정
          </li>
          <li>
            <strong>상장기업 주가 적정성 분석:</strong> 글로벌 경쟁사와의 멀티플
            비교를 통해 저평가 여부 판단
          </li>
          <li>
            <strong>산업별 특화 멀티플:</strong> SaaS는 EV/ARR, 커머스는
            EV/GMV 등 산업 특성에 맞는 멀티플 활용
          </li>
        </ul>
      </section>
    </GuideTemplate>
  )
}
