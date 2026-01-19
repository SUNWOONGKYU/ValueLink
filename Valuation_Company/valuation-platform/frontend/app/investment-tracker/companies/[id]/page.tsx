'use client';

/**
 * Company Detail Page
 * 기업 상세 페이지
 */
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import investmentTrackerApi, {
  Company,
  InvestmentRound,
  News,
  EmailTemplate,
} from '@/lib/api/investment-tracker';
import InvestmentTimeline from '@/components/investment-tracker/InvestmentTimeline';
import NewsCard from '@/components/investment-tracker/NewsCard';
import EmailTemplateView from '@/components/investment-tracker/EmailTemplateView';

interface CompanyDetail extends Company {
  investment_rounds: InvestmentRound[];
  news: News[];
}

export default function CompanyDetailPage() {
  const params = useParams();
  const companyId = Number(params.id);

  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [emailTemplate, setEmailTemplate] = useState<EmailTemplate | null>(null);
  const [loading, setLoading] = useState(true);
  const [emailLoading, setEmailLoading] = useState(true);

  useEffect(() => {
    if (companyId) {
      loadCompanyData();
    }
  }, [companyId]);

  const loadCompanyData = async () => {
    setLoading(true);
    setEmailLoading(true);

    try {
      const companyData = await investmentTrackerApi.getCompanyDetail(companyId);
      setCompany(companyData);
    } catch (error) {
      console.error('Failed to load company:', error);
    } finally {
      setLoading(false);
    }

    try {
      const templateData = await investmentTrackerApi.getCompanyEmailTemplate(companyId);
      setEmailTemplate(templateData);
    } catch (error) {
      // 템플릿이 없을 수 있음
      setEmailTemplate(null);
    } finally {
      setEmailLoading(false);
    }
  };

  const handleRegenerateEmail = async (feedback?: string) => {
    try {
      const newTemplate = await investmentTrackerApi.regenerateEmailTemplate(
        companyId,
        feedback
      );
      setEmailTemplate(newTemplate);
    } catch (error) {
      console.error('Failed to regenerate email:', error);
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            기업을 찾을 수 없습니다
          </h1>
          <Link
            href="/investment-tracker/companies"
            className="text-blue-600 hover:text-blue-800"
          >
            목록으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-4">
            <Link
              href="/investment-tracker/companies"
              className="text-gray-500 hover:text-gray-700"
            >
              &larr; 기업 목록
            </Link>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">
                {company.name_ko}
                {company.name_en && (
                  <span className="text-gray-400 text-lg ml-2">
                    ({company.name_en})
                  </span>
                )}
              </h1>
              <p className="text-sm text-gray-500">
                {company.industry || '업종 미상'}
                {company.sub_industry && ` / ${company.sub_industry}`}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 왼쪽: 기업 정보 + 투자 타임라인 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 기업 기본 정보 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-medium text-gray-900 mb-4">기업 정보</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">총 투자 유치</span>
                  <p className="font-medium text-lg text-green-600">
                    {company.total_funding_krw
                      ? `${company.total_funding_krw.toLocaleString()}억원`
                      : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500">최근 투자 단계</span>
                  <p className="font-medium text-lg">
                    {company.latest_stage || '-'}
                  </p>
                </div>
                <div>
                  <span className="text-gray-500">설립년도</span>
                  <p className="font-medium">{company.founded_year || '-'}</p>
                </div>
                <div>
                  <span className="text-gray-500">직원 수</span>
                  <p className="font-medium">
                    {company.employee_count ? `${company.employee_count}명` : '-'}
                  </p>
                </div>
                {company.website && (
                  <div className="col-span-2">
                    <span className="text-gray-500">웹사이트</span>
                    <p>
                      <a
                        href={company.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {company.website}
                      </a>
                    </p>
                  </div>
                )}
                {company.description && (
                  <div className="col-span-2">
                    <span className="text-gray-500">설명</span>
                    <p className="mt-1">{company.description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* 투자 타임라인 */}
            <InvestmentTimeline rounds={company.investment_rounds} />

            {/* 관련 뉴스 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-medium text-gray-900 mb-4">관련 뉴스</h3>
              {company.news.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  관련 뉴스가 없습니다.
                </p>
              ) : (
                <div className="space-y-3">
                  {company.news.map((news) => (
                    <NewsCard key={news.id} news={news} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* 오른쪽: 이메일 템플릿 */}
          <div className="lg:col-span-1">
            <EmailTemplateView
              template={emailTemplate}
              onRegenerate={handleRegenerateEmail}
              loading={emailLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
