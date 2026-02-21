#!/usr/bin/env node
/**
 * Bill News Tracker STRICT - 엄격한 필터링
 * 필수 3가지: 회사명 + 투자자 + 투자금액 모두 있어야만 저장
 */

const axios = require('axios');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const NAVER_CLIENT_ID = process.env.NAVER_CLIENT_ID;
const NAVER_CLIENT_SECRET = process.env.NAVER_CLIENT_SECRET;

const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

console.log('📰 Bill News Tracker STRICT (엄격한 필터링) 시작...\n');

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

// 필터링: 회사명처럼 보이지 않는 것들
const INVALID_PATTERNS = [
  /도청|도의회|시청|시의회|관광공사|문화원|센터|대학|대학원|학원|학교|공사|청|국|부|처|위원회|협회|기금|재단|공단|조합|조성/,
  /^[0-9]+|^[a-zA-Z]*$|^[가-힣]+\s+[가-힣]+\s+[가-힣]+/, // 순수 숫자, 영문만, 3글자 이상 단어
];

function isValidCompanyName(name) {
  if (!name || name.length > 50) return false;
  return !INVALID_PATTERNS.some(pattern => pattern.test(name));
}

function extractCompanyName(title) {
  const match = title.match(/^([^,،]+)[,،]/);
  if (match) {
    const name = match[1].trim();
    if (isValidCompanyName(name)) return name;
  }
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

function extractInvestor(title) {
  // 패턴: "~로부터", "~에게", "~의 투자"
  const patterns = [
    /(.+?)(?:로부터|에게)\s+(?:투자|펀딩)/,
    /(.+?)\s+(?:인베스트먼트|벤처|캐피탈)\s+(?:로부터|투자)/,
  ];

  for (const pattern of patterns) {
    const match = title.match(pattern);
    if (match) {
      const investor = match[1].trim();
      if (investor.length < 50 && !investor.includes('스타트업')) {
        return investor;
      }
    }
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

function extractReason(title) {
  // 투자 사유 추출: "기술 고도화", "글로벌 확장", "플랫폼 강화" 등
  const patterns = [
    /…(.+?)(?:$|[.。])/,  // "…" 이후의 내용
    /:\s*(.+?)(?:$|[.。])/,  // ":" 이후의 내용
    /\.\.\.\s*(.+?)(?:$|[.。])/,
  ];

  for (const pattern of patterns) {
    const match = title.match(pattern);
    if (match) {
      const reason = match[1].trim();
      if (reason.length > 5 && reason.length < 100) {
        return reason;
      }
    }
  }
  return null;
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
        const amount = extractAmount(title);
        const investor = extractInvestor(title);
        const reason = extractReason(title);

        // 필수 3가지 체크: 회사명 + 투자금액 + 투자자
        if (!company || !amount || !investor) {
          process.stdout.write('·');
          continue;
        }

        const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
        const dateStr = pubDate.toISOString().split('T')[0];

        collected.push({
          title: title,
          url: item.link,
          site: item.source,
          date: dateStr,
          company: company,
          amount: amount,
          investor: investor,
          reason: reason || 'TBD',
          stage: extractStage(title),
          industry: classifyIndustry(title)
        });

        process.stdout.write('✓');
      }
    } catch (err) {
      console.error(`\n⚠️ 검색 오류: ${err.message}`);
    }
  }

  console.log(`\n\n✅ 필터링 결과: ${collected.length}개 (필수 정보 3가지 충족)\n`);
  return collected;
}

async function saveToSupabase(newsList) {
  console.log('💾 Supabase에 저장 중...\n');

  let saved = 0;
  for (const news of newsList) {
    try {
      const existing = await supabase
        .from('deals')
        .select('*')
        .eq('news_url', news.url)
        .limit(1);

      if (existing.data && existing.data.length > 0) {
        console.log(`⏭️  [중복] ${news.company}`);
        continue;
      }

      const record = {
        company_name: news.company,
        news_title: news.title,
        news_url: news.url,
        site_name: news.site,
        news_date: news.date,
        amount: news.amount,
        stage: news.stage,
        investors: news.investor,
        investment_reason: news.reason,
        industry: news.industry
      };

      await supabase.from('deals').insert(record);
      saved++;
      console.log(`✅ [${saved}] ${news.date} | ${news.company} | ${news.amount} | ${news.investor.substring(0, 20)}`);
    } catch (err) {
      console.error(`❌ 저장 실패:`, err.message);
    }
  }

  console.log(`\n✅ ${saved}개 고품질 뉴스 저장 완료!\n`);
  return saved;
}

async function renumberDeals() {
  console.log('🔢 번호 재정렬...');
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
