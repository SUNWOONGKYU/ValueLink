'use client';

/**
 * News List Page
 * 뉴스 목록 페이지
 */
import { useState, useEffect } from 'react';
import Link from 'next/link';
import investmentTrackerApi, { News } from '@/lib/api/investment-tracker';
import NewsCard from '@/components/investment-tracker/NewsCard';

export default function NewsPage() {
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [source, setSource] = useState('');

  const pageSize = 18;

  useEffect(() => {
    loadNews();
  }, [page, source]);

  const loadNews = async () => {
    setLoading(true);
    try {
      const data = await investmentTrackerApi.getNews(page, pageSize, {
        source: source || undefined,
        search: search || undefined,
      });
      setNews(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load news:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadNews();
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/investment-tracker"
              className="text-gray-500 hover:text-gray-700"
            >
              &larr; 대시보드
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">뉴스 목록</h1>
              <p className="text-sm text-gray-500">
                총 {total.toLocaleString()}개 뉴스
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* 필터 */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 flex gap-4 items-center">
          <input
            type="text"
            placeholder="제목/내용 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={source}
            onChange={(e) => {
              setSource(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="">전체 소스</option>
            <option value="naver">네이버</option>
            <option value="platum">플래텀</option>
          </select>
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            검색
          </button>
        </div>

        {/* 뉴스 그리드 */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="bg-white rounded-lg shadow p-4 animate-pulse"
              >
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                <div className="h-5 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : news.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            뉴스가 없습니다.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {news.map((item) => (
              <NewsCard key={item.id} news={item} />
            ))}
          </div>
        )}

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center gap-2">
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
