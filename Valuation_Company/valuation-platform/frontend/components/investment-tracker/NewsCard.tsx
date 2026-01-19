'use client';

/**
 * News Card Component
 * 뉴스 카드 컴포넌트
 */
import { News } from '@/lib/api/investment-tracker';

interface Props {
  news: News;
  onClick?: () => void;
}

// 소스별 색상
const sourceColors: Record<string, string> = {
  naver: 'bg-green-100 text-green-700',
  platum: 'bg-blue-100 text-blue-700',
  venturesquare: 'bg-purple-100 text-purple-700',
};

export default function NewsCard({ news, onClick }: Props) {
  return (
    <div
      className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      {/* 헤더: 소스 뱃지 + 날짜 */}
      <div className="flex items-center justify-between mb-2">
        <span
          className={`px-2 py-0.5 text-xs rounded-full ${
            sourceColors[news.source] || 'bg-gray-100 text-gray-700'
          }`}
        >
          {news.source.toUpperCase()}
        </span>
        <span className="text-xs text-gray-400">
          {news.published_at
            ? new Date(news.published_at).toLocaleDateString('ko-KR')
            : '-'}
        </span>
      </div>

      {/* 제목 */}
      <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">
        {news.title}
      </h3>

      {/* AI 요약 */}
      {news.ai_summary && (
        <p className="text-sm text-gray-600 line-clamp-3 mb-2">
          {news.ai_summary}
        </p>
      )}

      {/* AI 추출 데이터 */}
      {news.ai_extracted_data && (
        <div className="flex flex-wrap gap-1 mt-2">
          {news.ai_extracted_data.investment_amount && (
            <span className="px-2 py-0.5 bg-yellow-50 text-yellow-700 text-xs rounded">
              {news.ai_extracted_data.investment_amount}억
            </span>
          )}
          {news.ai_extracted_data.stage && (
            <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
              {news.ai_extracted_data.stage}
            </span>
          )}
          {news.ai_extracted_data.industry && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded">
              {news.ai_extracted_data.industry}
            </span>
          )}
        </div>
      )}

      {/* 링크 */}
      <div className="mt-3 pt-2 border-t border-gray-100">
        <a
          href={news.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-500 hover:text-blue-700"
          onClick={(e) => e.stopPropagation()}
        >
          원문 보기 &rarr;
        </a>
      </div>
    </div>
  );
}
