'use client';

/**
 * Dashboard Statistics Component
 * 대시보드 통계 카드 컴포넌트
 */
import { DashboardStats as DashboardStatsType } from '@/lib/api/investment-tracker';

interface Props {
  stats: DashboardStatsType | null;
  loading?: boolean;
}

export default function DashboardStats({ stats, loading }: Props) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const statCards = [
    {
      title: '전체 기업',
      value: stats.total_companies.toLocaleString(),
      subtext: `이번 주 +${stats.this_week_new_companies}`,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: '총 투자 금액',
      value: `${stats.total_funding_krw.toLocaleString()}억`,
      subtext: '누적 투자 유치',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: '수집 뉴스',
      value: stats.total_news.toLocaleString(),
      subtext: `이번 주 +${stats.this_week_new_news}`,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: '최근 수집',
      value: stats.last_collection_date
        ? new Date(stats.last_collection_date).toLocaleDateString('ko-KR')
        : '없음',
      subtext: stats.last_collection_status || '',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((card) => (
        <div
          key={card.title}
          className={`${card.bgColor} rounded-lg shadow p-6`}
        >
          <p className="text-sm text-gray-500 mb-1">{card.title}</p>
          <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
          <p className="text-xs text-gray-400 mt-1">{card.subtext}</p>
        </div>
      ))}
    </div>
  );
}
