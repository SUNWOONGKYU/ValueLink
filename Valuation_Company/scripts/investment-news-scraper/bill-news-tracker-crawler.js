#!/usr/bin/env node
/**
 * Bill News Tracker with Web Crawler
 * Naver API + 웹 크롤링으로 본문 수집
 * 투자자, 투자 사유 추출
 */

const axios = require('axios');
const cheerio = require('cheerio');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const NAVER_CLIENT_ID = process.env.NAVER_CLIENT_ID;
const NAVER_CLIENT_SECRET = process.env.NAVER_CLIENT_SECRET;

const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

console.log('📰 Bill News Tracker with Web Crawler 시작...\n');

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

const INVALID_PATTERNS = [
  /도청|도의회|시청|시의회|관광공사|문화원|센터|대학|대학원|학원|학교|공사|청|국|부|처|위원회|협회|기금|재단|공단/,
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

function classifyIndustry(text) {
  for (const [industry, keywords] of Object.entries(INDUSTRY_KEYWORDS)) {
    for (const keyword of keywords) {
      if (text.includes(keyword)) return industry;
    }
  }
  return 'TBD';
}

/**
 * 웹 크롤링으로 뉴스 본문 수집
 */
async function crawlNewsBody(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      },
      timeout: 5000
    });

    const $ = cheerio.load(response.data);

    // 일반적인 본문 선택자들
    let body = '';

    // 시도 1: 메타 description
    body = $('meta[property="og:description"]').attr('content') || '';
    if (body.length > 50) return body;

    // 시도 2: 주요 본문 div
    const articleSelectors = [
      'article', '.article-body', '.article-content', '.news-body',
      '.post-content', '.content', '.article', '.news_body', '.article_txt'
    ];

    for (const selector of articleSelectors) {
      const element = $(selector).first();
      if (element.length) {
        body = element.text().trim();
        if (body.length > 50) return body;
      }
    }

    // 시도 3: p 태그들 수집
    const paragraphs = [];
    $('p, span.article_text').each((i, el) => {
      const text = $(el).text().trim();
      if (text.length > 20) paragraphs.push(text);
    });

    body = paragraphs.slice(0, 10).join(' ').trim();
    return body.length > 50 ? body : null;

  } catch (err) {
    console.error(`⚠️ 크롤링 실패 (${url.substring(0, 50)}...): ${err.message}`);
    return null;
  }
}

/**
 * 본문에서 투자자 추출
 */
function extractInvestorFromBody(body) {
  if (!body) return null;

  const patterns = [
    /(.+?)(?:로부터|에서|가)\s+(?:투자|펀딩|자금)/,
    /(.+?)(\s+인베스트먼트|벤처캐피탈|벤처|펀드)(?:로부터|에서)/,
  ];

  for (const pattern of patterns) {
    const match = body.match(pattern);
    if (match) {
      const investor = match[1].trim();
      if (investor.length < 50 && investor.length > 2) {
        return investor;
      }
    }
  }

  return null;
}

/**
 * 본문에서 투자 사유 추출
 */
function extractReasonFromBody(body) {
  if (!body) return null;

  const patterns = [
    /이번\s+투자(?:는|로)?(?:는)?\s+(.+?)(?:[.。]|이\s+회사|이\s+기업)/,
    /투자\s+배경(?:은)?\s+(.+?)(?:[.。]|한편|한편으로)/,
    /이\s+(?:기업|회사|기관)(?:은|는)?\s+(.+?)(?:기술|플랫폼|서비스)/,
  ];

  for (const pattern of patterns) {
    const match = body.match(pattern);
    if (match) {
      const reason = match[1].trim();
      if (reason.length > 5 && reason.length < 100) {
        return reason;
      }
    }
  }

  // 기본 추출: 투자금액 정보 근처의 텍스트
  const idx = body.indexOf('투자');
  if (idx > -1) {
    const context = body.substring(Math.max(0, idx - 50), Math.min(body.length, idx + 100));
    return context.trim().substring(0, 80);
  }

  return null;
}

async function collectNews() {
  let collected = [];
  const keywords = ['스타트업 투자 유치', '시리즈A 펀딩', '시리즈B 펀딩'];

  console.log(`🔍 ${keywords.length}개 키워드로 검색 중...\n`);

  for (const keyword of keywords) {
    try {
      const response = await axios.get('https://openapi.naver.com/v1/search/news.json', {
        params: { query: keyword, sort: 'date', display: 20, start: 1 },
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

        if (!company || !amount) {
          process.stdout.write('·');
          continue;
        }

        // 웹 크롤링으로 본문 수집
        console.log(`\n  🔗 크롤링: ${company}...`);
        const body = await crawlNewsBody(item.link);

        if (!body) {
          process.stdout.write('✗');
          continue;
        }

        // 본문에서 투자자와 사유 추출
        const investor = extractInvestorFromBody(body);
        const reason = extractReasonFromBody(body);

        // 필수 3가지 체크: 회사명 + 투자금액 + 투자자
        if (!investor) {
          process.stdout.write('✗');
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
          industry: classifyIndustry(body),
          body: body.substring(0, 500)
        });

        process.stdout.write('✓');
      }

      // 요청 간 delay (서버 부하 방지)
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (err) {
      console.error(`\n⚠️ 검색 오류: ${err.message}`);
    }
  }

  console.log(`\n\n✅ 필터링 결과: ${collected.length}개 (필수 정보 충족)\n`);
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
      console.log(`✅ [${saved}] ${news.date} | ${news.company} | ${news.amount} | ${news.investor.substring(0, 15)}`);
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
