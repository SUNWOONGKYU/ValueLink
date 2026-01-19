'use client';

/**
 * Companies List Page
 * 기업 목록 페이지
 */
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import investmentTrackerApi, {
  Company,
  CompanyFilter,
} from '@/lib/api/investment-tracker';
import CompanyTable from '@/components/investment-tracker/CompanyTable';
import FilterPanel from '@/components/investment-tracker/FilterPanel';

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<CompanyFilter>({});
  const [industries, setIndustries] = useState<string[]>([]);
  const [stages, setStages] = useState<Array<{ value: string; label: string }>>([]);

  const pageSize = 20;

  useEffect(() => {
    loadMetadata();
  }, []);

  useEffect(() => {
    loadCompanies();
  }, [page, filter]);

  const loadMetadata = async () => {
    try {
      const [industriesData, stagesData] = await Promise.all([
        investmentTrackerApi.getIndustries(),
        investmentTrackerApi.getStages(),
      ]);
      setIndustries(industriesData.industries);
      setStages(stagesData.stages);
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  };

  const loadCompanies = useCallback(async () => {
    setLoading(true);
    try {
      const data = await investmentTrackerApi.getCompanies(page, pageSize, filter);
      setCompanies(data.items);
      setTotalPages(data.total_pages);
      setTotal(data.total);
    } catch (error) {
      console.error('Failed to load companies:', error);
    } finally {
      setLoading(false);
    }
  }, [page, filter]);

  const handleFilter = (newFilter: CompanyFilter) => {
    setFilter(newFilter);
    setPage(1); // 필터 변경 시 첫 페이지로
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
              <h1 className="text-2xl font-bold text-gray-900">기업 목록</h1>
              <p className="text-sm text-gray-500">
                총 {total.toLocaleString()}개 기업
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* 필터 */}
        <FilterPanel
          industries={industries}
          stages={stages}
          onFilter={handleFilter}
          initialFilter={filter}
        />

        {/* 기업 테이블 */}
        <CompanyTable companies={companies} loading={loading} />

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
