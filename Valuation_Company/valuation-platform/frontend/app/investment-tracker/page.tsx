'use client';

/**
 * Investment Tracker Dashboard Page
 * 투자 트래커 대시보드 페이지
 */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import investmentTrackerApi, {
  DashboardStats as DashboardStatsType,
  Company,
  News,
} from '@/lib/api/investment-tracker';
import DashboardStats from '@/components/investment-tracker/DashboardStats';
import CompanyTable from '@/components/investment-tracker/CompanyTable';
import NewsCard from '@/components/investment-tracker/NewsCard';

export default function InvestmentTrackerDashboard() {
  const [stats, setStats] = useState<DashboardStatsType | null>(null);
  const [recentCompanies, setRecentCompanies] = useState<Company[]>([]);
  const [recentNews, setRecentNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsData, companiesData, newsData] = await Promise.all([
        investmentTrackerApi.getDashboardStats(),
        investmentTrackerApi.getCompanies(1, 5),
        investmentTrackerApi.getNews(1, 6),
      ]);

      setStats(statsData);
      setRecentCompanies(companiesData.items);
      setRecentNews(newsData.items);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerCollection = async () => {
    if (triggering) return;

    if (!confirm('주간 수집을 수동으로 시작하시겠습니까?')) return;

    setTriggering(true);
    try {
      const result = await investmentTrackerApi.triggerCollection();
      alert(`수집이 시작되었습니다. (ID: ${result.collection_id})`);
      // 잠시 후 데이터 새로고침
      setTimeout(loadDashboardData, 5000);
    } catch (error) {
      console.error('Failed to trigger collection:', error);
      alert('수집 시작에 실패했습니다.');
    } finally {
      setTriggering(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                투자 트래커
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                스타트업 투자 유치 뉴스 자동 수집 및 영업 리드 관리
              </p>
            </div>
            <button
              onClick={handleTriggerCollection}
              disabled={triggering}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {triggering ? '수집 중...' : '수동 수집 시작'}
            </button>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* 통계 카드 */}
        <section className="mb-8">
          <DashboardStats stats={stats} loading={loading} />
        </section>

        {/* 업종별/단계별 분포 */}
        {stats && (
          <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* 업종별 분포 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-medium text-gray-900 mb-4">업종별 분포</h3>
              <div className="space-y-2">
                {Object.entries(stats.industry_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 5)
                  .map(([industry, count]) => (
                    <div key={industry} className="flex items-center">
                      <span className="w-24 text-sm text-gray-600 truncate">
                        {industry}
                      </span>
                      <div className="flex-1 mx-2 h-4 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{
                            width: `${(count / stats.total_companies) * 100}%`,
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* 투자 단계별 분포 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-medium text-gray-900 mb-4">투자 단계별 분포</h3>
              <div className="space-y-2">
                {Object.entries(stats.stage_distribution)
                  .sort((a, b) => b[1] - a[1])
                  .map(([stage, count]) => (
                    <div key={stage} className="flex items-center">
                      <span className="w-20 text-sm text-gray-600">
                        {stage}
                      </span>
                      <div className="flex-1 mx-2 h-4 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500 rounded-full"
                          style={{
                            width: `${(count / stats.total_companies) * 100}%`,
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  ))}
              </div>
            </div>
          </section>
        )}

        {/* 최근 기업 */}
        <section className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              최근 발견 기업
            </h2>
            <Link
              href="/investment-tracker/companies"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              전체 보기 &rarr;
            </Link>
          </div>
          <CompanyTable companies={recentCompanies} loading={loading} />
        </section>

        {/* 최근 뉴스 */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">최근 뉴스</h2>
            <Link
              href="/investment-tracker/news"
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              전체 보기 &rarr;
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loading ? (
              [1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="bg-white rounded-lg shadow p-4 animate-pulse"
                >
                  <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                  <div className="h-5 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))
            ) : (
              recentNews.map((news) => <NewsCard key={news.id} news={news} />)
            )}
          </div>
        </section>

        {/* 네비게이션 */}
        <nav className="mt-8 pt-8 border-t">
          <div className="flex gap-4">
            <Link
              href="/investment-tracker/companies"
              className="px-4 py-2 bg-white shadow rounded-lg hover:shadow-md"
            >
              기업 목록
            </Link>
            <Link
              href="/investment-tracker/news"
              className="px-4 py-2 bg-white shadow rounded-lg hover:shadow-md"
            >
              뉴스 목록
            </Link>
            <Link
              href="/investment-tracker/collections"
              className="px-4 py-2 bg-white shadow rounded-lg hover:shadow-md"
            >
              수집 이력
            </Link>
            <Link
              href="/"
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              홈으로
            </Link>
          </div>
        </nav>
      </main>
    </div>
  );
}
