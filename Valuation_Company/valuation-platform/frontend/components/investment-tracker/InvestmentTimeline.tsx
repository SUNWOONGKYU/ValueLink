'use client';

/**
 * Investment Round Timeline Component
 * 투자 히스토리 타임라인 컴포넌트
 */
import { InvestmentRound } from '@/lib/api/investment-tracker';

interface Props {
  rounds: InvestmentRound[];
}

// 투자 단계 한글 매핑
const stageLabels: Record<string, string> = {
  seed: '시드',
  pre_a: '프리A',
  series_a: '시리즈A',
  series_b: '시리즈B',
  series_c: '시리즈C',
  later: '시리즈C+',
};

// 투자 단계 색상
const stageColors: Record<string, string> = {
  seed: 'bg-gray-500',
  pre_a: 'bg-blue-500',
  series_a: 'bg-green-500',
  series_b: 'bg-yellow-500',
  series_c: 'bg-orange-500',
  later: 'bg-red-500',
};

export default function InvestmentTimeline({ rounds }: Props) {
  if (rounds.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        투자 라운드 정보가 없습니다.
      </div>
    );
  }

  // 날짜순 정렬 (최신순)
  const sortedRounds = [...rounds].sort((a, b) => {
    if (!a.round_date) return 1;
    if (!b.round_date) return -1;
    return new Date(b.round_date).getTime() - new Date(a.round_date).getTime();
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="font-medium text-gray-900 mb-4">투자 히스토리</h3>

      <div className="relative">
        {/* 타임라인 선 */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* 라운드 목록 */}
        <div className="space-y-6">
          {sortedRounds.map((round, index) => (
            <div key={round.id} className="relative pl-10">
              {/* 타임라인 점 */}
              <div
                className={`absolute left-2 w-5 h-5 rounded-full border-4 border-white ${
                  stageColors[round.stage] || 'bg-gray-500'
                }`}
              ></div>

              {/* 라운드 정보 */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">
                    {stageLabels[round.stage] || round.stage}
                  </span>
                  <span className="text-sm text-gray-500">
                    {round.round_date
                      ? new Date(round.round_date).toLocaleDateString('ko-KR')
                      : '날짜 미상'}
                  </span>
                </div>

                {/* 금액 정보 */}
                <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                  {round.investment_amount_krw && (
                    <div>
                      <span className="text-gray-500">투자금액: </span>
                      <span className="font-medium text-green-600">
                        {round.investment_amount_krw.toLocaleString()}억
                      </span>
                    </div>
                  )}
                  {round.valuation_post_krw && (
                    <div>
                      <span className="text-gray-500">밸류: </span>
                      <span className="font-medium">
                        {round.valuation_post_krw.toLocaleString()}억
                      </span>
                    </div>
                  )}
                </div>

                {/* 투자자 정보 */}
                {round.lead_investor && (
                  <div className="text-sm">
                    <span className="text-gray-500">리드: </span>
                    <span className="font-medium">{round.lead_investor}</span>
                  </div>
                )}

                {round.investors && round.investors.length > 0 && (
                  <div className="text-sm text-gray-600 mt-1">
                    참여: {round.investors.map((inv) => inv.name).join(', ')}
                  </div>
                )}

                {/* 출처 */}
                {round.source_url && (
                  <a
                    href={round.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:text-blue-700 mt-2 inline-block"
                  >
                    출처 보기 &rarr;
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
