'use client';

/**
 * Collections History Page
 * 수집 작업 이력 페이지
 */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import investmentTrackerApi, { Collection } from '@/lib/api/investment-tracker';

// 상태별 색상
const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-700',
  in_progress: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
};

// 상태 한글
const statusLabels: Record<string, string> = {
  pending: '대기 중',
  in_progress: '진행 중',
  completed: '완료',
  failed: '실패',
};

export default function CollectionsPage() {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [triggering, setTriggering] = useState(false);

  const pageSize = 10;

  useEffect(() => {
    loadCollections();
  }, [page]);

  const loadCollections = async () => {
    setLoading(true);
    try {
      const data = await investmentTrackerApi.getCollections(page, pageSize);
      setCollections(data.items);
      setTotalPages(data.total_pages);
    } catch (error) {
      console.error('Failed to load collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrigger = async () => {
    if (triggering) return;

    if (!confirm('수집을 시작하시겠습니까?')) return;

    setTriggering(true);
    try {
      await investmentTrackerApi.triggerCollection();
      alert('수집이 시작되었습니다.');
      // 잠시 후 새로고침
      setTimeout(loadCollections, 2000);
    } catch (error) {
      console.error('Failed to trigger:', error);
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
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                href="/investment-tracker"
                className="text-gray-500 hover:text-gray-700"
              >
                &larr; 대시보드
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">수집 이력</h1>
                <p className="text-sm text-gray-500">
                  매주 일요일 오전 6시 자동 실행
                </p>
              </div>
            </div>
            <button
              onClick={handleTrigger}
              disabled={triggering}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {triggering ? '시작 중...' : '수동 수집 시작'}
            </button>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {loading ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="animate-pulse">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="px-6 py-4 border-b">
                  <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        ) : collections.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            수집 이력이 없습니다.
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    수집일
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    주차
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    뉴스 수집
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    기업 발견
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    신규 기업
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    이메일 생성
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    오류
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {collections.map((collection) => (
                  <tr key={collection.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {new Date(collection.collection_date).toLocaleDateString(
                        'ko-KR',
                        {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        }
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {collection.year}년 {collection.week_number}주차
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          statusColors[collection.status]
                        }`}
                      >
                        {statusLabels[collection.status]}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {collection.total_news_crawled}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {collection.total_companies_found}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-green-600">
                      +{collection.new_companies_added}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {collection.emails_generated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                      {collection.error_count > 0 ? (
                        <span className="text-red-500 font-medium">
                          {collection.error_count}
                        </span>
                      ) : (
                        <span className="text-gray-400">0</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="mt-4 flex justify-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              이전
            </button>
            <span className="px-4 py-2">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
            >
              다음
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
