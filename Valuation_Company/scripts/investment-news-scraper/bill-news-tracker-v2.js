#!/usr/bin/env node
/**
 * Bill News Tracker v2 - 개선 버전
 * Naver API + 정규식으로 정보 추출
 */

const axios = require('axios');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const NAVER_CLIENT_ID = process.env.NAVER_CLIENT_ID;
const NAVER_CLIENT_SECRET = process.env.NAVER_CLIENT_SECRET;

const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

console.log('📰 Bill News Tracker v2 (개선 버전) 시작...\n');

// 업종 분류 키워드
const INDUSTRY_KEYWORDS = {
  'AI': ['AI', '인공지능', '머신러닝', '딥러닝'],
  '헬스케어': ['헬스케어', '바이오', '의료', '제약'],
  '핀테크': ['핀테크', '금융', '결제', '보험'],
  '이커머스': ['이커머스', '커머스', '쇼핑'],
  '모빌리티': ['모빌리티', '자동차', '물류'],
  '반도체/IT': ['반도체', '칩', '하드웨어'],
  '콘텐츠': ['게임', '웹툰', '영상'],
  '에너지': ['태양광', '배터리', '환경'],
};

function extractCompanyName(title) {
  // 패턴 1: "회사명, 투자자명..." 형식
  const match1 = title.match(/^([^,،]+)[,،]/);
  if (match1) {
    const name = match1[1].trim();
    if (name.length > 50 || /[^\wㄱ-ㅣ가-힣]/.test(name)) return null;
    return name;
  }

  // 패턴 2: 따옴표 안의 회사명
  const match2 = title.match(/'([^']+)'/);
  if (match2 && match2[1].length < 30) return match2[1].trim();

  return null;
}

function extractAmount(title) {
  const patterns = [
    /(\d+(?:,\d+)?)\s*조\s*원/,
    /(\d+(?:,\d+)?)\s*억\s*원?/,
    /(\d+(?:,\d+)?)\s*만\s*달러/,
    /(\d+(?:,\d+)?)\s*달러/,
  ];

  for (const pattern of patterns) {
    const match = title.match(pattern);
    if (match) return match[0].trim();
  }
  return null;
}

function extractStage(title) {
  const stages = ['프리시드', '시드', '프리A', '시리즈A', '시리즈B', '시리즈C', '프리IPO'];
  for (const stage of stages) {
    if (title.includes(stage)) return stage;
  }
  return 'TBD';
}

function classifyIndustry(title) {
  for (const [industry, keywords] of Object.entries(INDUSTRY_KEYWORDS)) {
    for (const keyword of keywords) {
      if (title.includes(keyword)) return industry;
    }
  }
  return 'TBD';
}

async function collectNews() {
  let collected = [];
  const keywords = ['스타트업 투자 유치', '시리즈A 펀딩', '시리즈B 펀딩', '프리A 투자', '벤처캐피탈 투자'];

  console.log(`🔍 ${keywords.length}개 키워드로 검색 중...\n`);

  for (const keyword of keywords) {
    try {
      const response = await axios.get('https://openapi.naver.com/v1/search/news.json', {
        params: { query: keyword, sort: 'date', display: 30, start: 1 },
        headers: {
          'X-Naver-Client-Id': NAVER_CLIENT_ID,
          'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        },
        timeout: 5000
      });

      for (const item of response.data.items || []) {
        const title = item.title.replace(/<\/?b>/g, '');
        const company = extractCompanyName(title);
        if (!company) continue;

        const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
        const dateStr = pubDate.toISOString().split('T')[0];

        collected.push({
          title: title,
          url: item.link,
          site: item.source,
          date: dateStr,
          company: company,
          amount: extractAmount(title),
          stage: extractStage(title),
          industry: classifyIndustry(title)
        });
      }

      process.stdout.write('.');
    } catch (err) {
      console.error(`\n⚠️ 검색 오류: ${err.message}`);
    }
  }

  console.log(`\n\n✅ 수집됨: ${collected.length}개`);
  return collected;
}

async function saveToSupabase(newsList) {
  console.log('\n💾 Supabase에 저장 중...\n');

  let saved = 0;
  for (const news of newsList) {
    try {
      const existing = await supabase
        .from('deals')
        .select('*')
        .eq('news_url', news.url)
        .limit(1);

      if (existing.data && existing.data.length > 0) {
        console.log(`⏭️  [중복] ${news.site}`);
        continue;
      }

      const record = {
        company_name: news.company,
        news_title: news.title,
        news_url: news.url,
        site_name: news.site,
        news_date: news.date,
        amount: news.amount || 'TBD',
        stage: news.stage,
        industry: news.industry
      };

      await supabase.from('deals').insert(record);
      saved++;
      console.log(`✅ [${saved}] ${news.date} | ${news.company} | ${news.amount || '-'} | ${news.industry}`);
    } catch (err) {
      console.error(`❌ 저장 실패:`, err.message);
    }
  }

  console.log(`\n✅ ${saved}개 뉴스 저장 완료!`);
  return saved;
}

async function renumberDeals() {
  console.log('\n🔢 번호 재정렬...');
  try {
    const deals = await supabase
      .from('deals')
      .select('id')
      .order('news_date', { ascending: false });

    for (let i = 0; i < deals.data.length; i++) {
      await supabase
        .from('deals')
        .update({ number: i + 1 })
        .eq('id', deals.data[i].id);
    }

    console.log(`✅ ${deals.data.length}개 레코드 재정렬 완료!\n`);
  } catch (err) {
    console.error('❌ 재정렬 실패:', err.message);
  }
}

async function main() {
  try {
    const news = await collectNews();
    const saved = await saveToSupabase(news);
    await renumberDeals();
    console.log('🎉 모든 작업 완료!\n');
    process.exit(0);
  } catch (err) {
    console.error('❌ 오류:', err.message);
    process.exit(1);
  }
}

main();
