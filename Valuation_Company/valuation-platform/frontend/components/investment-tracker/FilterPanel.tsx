'use client';

/**
 * Filter Panel Component
 * 기업/뉴스 필터 패널 컴포넌트
 */
import { useState, useEffect } from 'react';
import { CompanyFilter } from '@/lib/api/investment-tracker';

interface Props {
  industries: string[];
  stages: Array<{ value: string; label: string }>;
  onFilter: (filter: CompanyFilter) => void;
  initialFilter?: CompanyFilter;
}

export default function FilterPanel({
  industries,
  stages,
  onFilter,
  initialFilter = {},
}: Props) {
  const [filter, setFilter] = useState<CompanyFilter>(initialFilter);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    setFilter(initialFilter);
  }, [initialFilter]);

  const handleChange = (key: keyof CompanyFilter, value: any) => {
    const newFilter = { ...filter, [key]: value || undefined };
    setFilter(newFilter);
  };

  const handleApply = () => {
    onFilter(filter);
  };

  const handleReset = () => {
    const emptyFilter: CompanyFilter = {};
    setFilter(emptyFilter);
    onFilter(emptyFilter);
  };

  return (
    <div className="bg-white rounded-lg shadow mb-4">
      {/* 검색바 (항상 표시) */}
      <div className="p-4 flex gap-4 items-center">
        <div className="flex-1">
          <input
            type="text"
            placeholder="기업명 검색..."
            value={filter.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleApply()}
            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <button
          onClick={handleApply}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          검색
        </button>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          {isExpanded ? '필터 접기' : '상세 필터'}
        </button>
      </div>

      {/* 상세 필터 (확장 시) */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t pt-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* 업종 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                업종
              </label>
              <select
                value={filter.industry || ''}
                onChange={(e) => handleChange('industry', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">전체</option>
                {industries.map((industry) => (
                  <option key={industry} value={industry}>
                    {industry}
                  </option>
                ))}
              </select>
            </div>

            {/* 투자 단계 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                투자 단계
              </label>
              <select
                value={filter.stage || ''}
                onChange={(e) => handleChange('stage', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg"
              >
                <option value="">전체</option>
                {stages.map((stage) => (
                  <option key={stage.value} value={stage.value}>
                    {stage.label}
                  </option>
                ))}
              </select>
            </div>

            {/* 최소 투자금액 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                최소 투자금액 (억)
              </label>
              <input
                type="number"
                value={filter.min_funding || ''}
                onChange={(e) => handleChange('min_funding', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="0"
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>

            {/* 최대 투자금액 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                최대 투자금액 (억)
              </label>
              <input
                type="number"
                value={filter.max_funding || ''}
                onChange={(e) => handleChange('max_funding', e.target.value ? Number(e.target.value) : undefined)}
                placeholder="무제한"
                className="w-full px-3 py-2 border rounded-lg"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-2">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              초기화
            </button>
            <button
              onClick={handleApply}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              필터 적용
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
