'use client';

/**
 * Company Table Component
 * 기업 목록 테이블 컴포넌트
 */
import Link from 'next/link';
import { Company } from '@/lib/api/investment-tracker';

interface Props {
  companies: Company[];
  loading?: boolean;
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
  seed: 'bg-gray-100 text-gray-700',
  pre_a: 'bg-blue-100 text-blue-700',
  series_a: 'bg-green-100 text-green-700',
  series_b: 'bg-yellow-100 text-yellow-700',
  series_c: 'bg-orange-100 text-orange-700',
  later: 'bg-red-100 text-red-700',
};

export default function CompanyTable({ companies, loading }: Props) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">기업명</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">업종</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">투자 단계</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">투자 금액</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">최근 투자일</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="animate-pulse">
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-24"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-16"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-12"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-16"></div></td>
                <td className="px-6 py-4"><div className="h-4 bg-gray-200 rounded w-20"></div></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        등록된 기업이 없습니다.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              기업명
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              업종
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              투자 단계
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              총 투자 금액
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              최근 투자일
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {companies.map((company) => (
            <tr key={company.id} className="hover:bg-gray-50 cursor-pointer">
              <td className="px-6 py-4 whitespace-nowrap">
                <Link
                  href={`/investment-tracker/companies/${company.id}`}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  {company.name_ko}
                  {company.name_en && (
                    <span className="text-gray-400 text-sm ml-2">
                      ({company.name_en})
                    </span>
                  )}
                </Link>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {company.industry || '-'}
                {company.sub_industry && (
                  <span className="text-gray-400"> / {company.sub_industry}</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {company.latest_stage ? (
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      stageColors[company.latest_stage] || 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {stageLabels[company.latest_stage] || company.latest_stage}
                  </span>
                ) : (
                  <span className="text-gray-400">-</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {company.total_funding_krw
                  ? `${company.total_funding_krw.toLocaleString()}억`
                  : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {company.latest_round_date
                  ? new Date(company.latest_round_date).toLocaleDateString('ko-KR')
                  : '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
