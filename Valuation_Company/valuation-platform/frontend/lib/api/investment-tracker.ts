/**
 * Investment Tracker API Client
 * 스타트업 투자 트래커 API 호출
 */
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_URL = `${API_BASE}/api/v1/investment-tracker`;

// Types
export interface Company {
  id: number;
  name_ko: string;
  name_en: string | null;
  industry: string | null;
  sub_industry: string | null;
  website: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  founded_year: number | null;
  employee_count: number | null;
  description: string | null;
  latest_stage: string | null;
  latest_round_date: string | null;
  total_funding_krw: number | null;
  is_active: boolean;
  first_discovered_at: string;
  created_at: string;
  updated_at: string;
}

export interface InvestmentRound {
  id: number;
  company_id: number;
  stage: string;
  round_date: string | null;
  investment_amount_krw: number | null;
  valuation_pre_krw: number | null;
  valuation_post_krw: number | null;
  lead_investor: string | null;
  investors: Array<{ name: string; type: string }> | null;
  remarks: string | null;
  source_url: string | null;
  created_at: string;
}

export interface News {
  id: number;
  company_id: number | null;
  collection_id: number | null;
  source: string;
  source_url: string;
  title: string;
  content: string | null;
  published_at: string | null;
  author: string | null;
  ai_summary: string | null;
  ai_extracted_data: Record<string, any> | null;
  is_processed: boolean;
  processing_error: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplate {
  id: number;
  company_id: number;
  subject: string;
  body: string;
  template_type: string;
  generation_prompt: string | null;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Collection {
  id: number;
  collection_date: string;
  week_number: number;
  year: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  started_at: string | null;
  completed_at: string | null;
  total_news_crawled: number;
  total_companies_found: number;
  new_companies_added: number;
  emails_generated: number;
  error_count: number;
  error_log: Record<string, any>[] | null;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_companies: number;
  total_news: number;
  total_funding_krw: number;
  this_week_new_companies: number;
  this_week_new_news: number;
  industry_distribution: Record<string, number>;
  stage_distribution: Record<string, number>;
  last_collection_date: string | null;
  last_collection_status: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CompanyFilter {
  industry?: string;
  stage?: string;
  min_funding?: number;
  max_funding?: number;
  search?: string;
  is_active?: boolean;
}

// API Functions
export const investmentTrackerApi = {
  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await axios.get(`${API_URL}/dashboard/stats`);
    return response.data;
  },

  // Companies
  async getCompanies(
    page = 1,
    pageSize = 20,
    filter?: CompanyFilter
  ): Promise<PaginatedResponse<Company>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (filter) {
      if (filter.industry) params.set('industry', filter.industry);
      if (filter.stage) params.set('stage', filter.stage);
      if (filter.min_funding) params.set('min_funding', filter.min_funding.toString());
      if (filter.max_funding) params.set('max_funding', filter.max_funding.toString());
      if (filter.search) params.set('search', filter.search);
      if (filter.is_active !== undefined) params.set('is_active', filter.is_active.toString());
    }

    const response = await axios.get(`${API_URL}/companies?${params}`);
    return response.data;
  },

  async getCompanyDetail(companyId: number): Promise<Company & {
    investment_rounds: InvestmentRound[];
    news: News[];
  }> {
    const response = await axios.get(`${API_URL}/companies/${companyId}`);
    return response.data;
  },

  async getCompanyEmailTemplate(companyId: number): Promise<EmailTemplate> {
    const response = await axios.get(`${API_URL}/companies/${companyId}/email-template`);
    return response.data;
  },

  async regenerateEmailTemplate(
    companyId: number,
    feedback?: string
  ): Promise<EmailTemplate> {
    const response = await axios.post(
      `${API_URL}/companies/${companyId}/email-template/regenerate`,
      null,
      { params: { feedback } }
    );
    return response.data;
  },

  // News
  async getNews(
    page = 1,
    pageSize = 20,
    filter?: { source?: string; company_id?: number; search?: string }
  ): Promise<PaginatedResponse<News>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (filter) {
      if (filter.source) params.set('source', filter.source);
      if (filter.company_id) params.set('company_id', filter.company_id.toString());
      if (filter.search) params.set('search', filter.search);
    }

    const response = await axios.get(`${API_URL}/news?${params}`);
    return response.data;
  },

  async getNewsDetail(newsId: number): Promise<News> {
    const response = await axios.get(`${API_URL}/news/${newsId}`);
    return response.data;
  },

  // Collections
  async getCollections(page = 1, pageSize = 10): Promise<PaginatedResponse<Collection>> {
    const response = await axios.get(`${API_URL}/collections`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async getCollectionDetail(collectionId: number): Promise<Collection> {
    const response = await axios.get(`${API_URL}/collections/${collectionId}`);
    return response.data;
  },

  async triggerCollection(
    sources?: string[],
    maxPages = 3
  ): Promise<{ collection_id: number; status: string; message: string }> {
    const response = await axios.post(`${API_URL}/collections/trigger`, {
      sources,
      max_pages: maxPages,
    });
    return response.data;
  },

  // Utilities
  async getIndustries(): Promise<{ industries: string[] }> {
    const response = await axios.get(`${API_URL}/industries`);
    return response.data;
  },

  async getStages(): Promise<{ stages: Array<{ value: string; label: string }> }> {
    const response = await axios.get(`${API_URL}/stages`);
    return response.data;
  },
};

export default investmentTrackerApi;
