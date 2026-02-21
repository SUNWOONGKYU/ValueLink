#!/usr/bin/env node
/**
 * Bill News Tracker Enhanced - 5대 언론사 크롤링 + Naver API
 * 필수 3가지 필터링: 회사명 + 투자자 + (투자금액 또는 사유)
 *
 * 명령어: npm run deal-news-tracker (또는 이 파일 직접 실행)
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

console.log('📰 Bill News Tracker Enhanced (5대 언론사 + Naver API) 시작...\n');

// ============================================================
// Step 1: 5대 언론기관 (daily_auto_collect.py의 로직 차용)
// ============================================================

const MEDIA_SITES = [
  {
    id: 9,
    name: '벤처스퀘어',
    url: 'https://www.venturesquare.net/category/news/',
    article_selector: 'article.post',
    title_selector: 'h5 a',
    link_selector: 'h5 a',
  },
  {
    id: 11,
    name: '스타트업투데이',
    url: 'https://www.startuptoday.kr/news/articleList.html',
    article_selector: 'div.article-list-content',
    title_selector: 'h4.titles',
    link_selector: 'a',
  },
  {
    id: 13,
    name: '아웃스탠딩',
    url: 'https://outstanding.kr/',
    article_selector: 'article',
    title_selector: 'h2 a',
    link_selector: 'h2 a',
  },
  {
    id: 10,
    name: '플래텀',
    url: 'https://platum.kr/',
    article_selector: 'article',
    title_selector: 'h2 a',
    link_selector: 'h2 a',
  },
];

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

// ============================================================
// 필터링 및 추출 함수들
// ============================================================

function isValidCompanyName(name) {
  if (!name || name.length > 50) return false;
  const invalidPatterns = /도청|도의회|시청|시의회|관광공사|문화원|센터|대학|대학원|학원|학교|공사|청|국|부|처|위원회|협회|기금|재단|공단/;
  return !invalidPatterns.test(name);
}

function extractCompanyName(title) {
  // 패턴 1: "회사명, 투자자로부터" 형식
  const match = title.match(/^([^,،]+)[,،]/);
  if (match) {
    const name = match[1].trim();
    if (isValidCompanyName(name)) return name;
  }

  // 패턴 2: "회사명이 시리즈A" 형식
  for (const keyword of ['시리즈', '펀딩', '투자', '유치', '라운드']) {
    const idx = title.indexOf(keyword);
    if (idx > 0) {
      const name = title.substring(0, idx).trim();
      if (isValidCompanyName(name)) return name;
    }
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
    /(.+?)(?:가|가)\s+(?:주도|리드)/,
  ];

  for (const pattern of patterns) {
    const match = title.match(pattern);
    if (match) {
      const investor = match[1].trim();
      if (investor.length < 50 && investor.length > 1 && !investor.includes('스타트업')) {
        return investor;
      }
    }
  }
  return null;
}

function extractReason(title) {
  // 투자 사유 추출: "기술 고도화", "글로벌 확장" 등
  const patterns = [
    /…(.+?)(?:$|[.。])/,
    /:\s*(.+?)(?:$|[.。])/,
    /\.{3}\s*(.+?)(?:$|[.。])/,
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

// ============================================================
// 5대 언론사 웹 크롤링
// ============================================================

async function crawlMediaSites() {
  console.log('🔍 Step 1: 5대 언론사 웹 크롤링...\n');

  let allArticles = [];

  for (const site of MEDIA_SITES) {
    console.log(`  📰 ${site.name} 크롤링 중...`);

    try {
      const response = await axios.get(site.url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000
      });

      if (response.status !== 200) {
        console.log(`    ❌ HTTP ${response.status}`);
        continue;
      }

      const $ = cheerio.load(response.data);
      const articles = $(site.article_selector).slice(0, 20);

      let siteCount = 0;

      articles.each((i, el) => {
        try {
          const titleEl = $(el).find(site.title_selector);

          let linkEl;
          if (site.link_selector === 'self') {
            linkEl = $(el);
          } else {
            linkEl = $(el).find(site.link_selector);
          }

          if (!titleEl.length || !linkEl.length) return;

          let title = titleEl.text().trim();
          let url = linkEl.attr('href') || '';

          // 상대 경로 처리
          if (url.startsWith('/')) {
            const basePath = site.url.split('?')[0].split('/').slice(0, -1).join('/');
            url = basePath + url;
          }

          if (!url.startsWith('http')) return;

          // 투자 키워드 필터
          const investKeywords = ['투자', '유치', '펀딩', '시리즈', 'Series', '라운드'];
          if (!investKeywords.some(kw => title.includes(kw))) {
            process.stdout.write('·');
            return;
          }

          allArticles.push({
            site_id: site.id,
            site_name: site.name,
            title: title,
            url: url,
            source: 'media'
          });

          siteCount++;
          process.stdout.write('✓');
        } catch (err) {
          process.stdout.write('✗');
        }
      });

      console.log(`\n    ✅ ${siteCount}개 발견`);

    } catch (error) {
      console.log(`    ❌ 크롤링 오류: ${error.message.substring(0, 40)}`);
    }

    // 요청 간 대기
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  console.log(`\n  📊 총 ${allArticles.length}개 기사 수집\n`);
  return allArticles;
}

// ============================================================
// Naver API 보충 수집
// ============================================================

async function collectFromNaverAPI() {
  console.log('🔍 Step 2: Naver API 보충 수집...\n');

  let collected = [];
  const keywords = ['스타트업 투자 유치', '시리즈A 펀딩', '벤처캐피탈 투자'];

  for (const keyword of keywords) {
    try {
      const response = await axios.get('https://openapi.naver.com/v1/search/news.json', {
        params: {
          query: keyword,
          sort: 'date',
          display: 20,
          start: 1
        },
        headers: {
          'X-Naver-Client-Id': NAVER_CLIENT_ID,
          'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        },
        timeout: 5000
      });

      for (const item of response.data.items || []) {
        const title = item.title.replace(/<\/?b>/g, '');

        collected.push({
          site_id: 0,
          site_name: item.source,
          title: title,
          url: item.link,
          source: 'naver'
        });

        process.stdout.write('.');
      }

    } catch (err) {
      console.log(`\n  ⚠️ Naver API 오류: ${err.message.substring(0, 30)}`);
    }

    await new Promise(resolve => setTimeout(resolve, 500));
  }

  console.log(`\n  ✅ Naver API로부터 ${collected.length}개 추가\n`);
  return collected;
}

// ============================================================
// 필터링 및 저장
// ============================================================

async function processAndSave(articles) {
  console.log('💾 Step 3: 필터링 및 저장...\n');

  const required3 = [];
  let passed = 0;
  let filtered = 0;

  for (const article of articles) {
    const title = article.title;
    const company = extractCompanyName(title);
    const amount = extractAmount(title);
    const investor = extractInvestor(title);
    const reason = extractReason(title);

    // 필수 조건: 회사명 + 투자자 + (투자금액 또는 사유)
    if (!company || !investor) {
      process.stdout.write('·');
      filtered++;
      continue;
    }

    // 투자금액 또는 투자사유 중 하나 필요
    if (!amount && !reason) {
      process.stdout.write('·');
      filtered++;
      continue;
    }

    passed++;
    process.stdout.write('✓');

    const pubDate = article.pubDate ? new Date(article.pubDate) : new Date();
    const dateStr = pubDate.toISOString().split('T')[0];

    required3.push({
      title: title,
      url: article.url,
      site: article.site_name,
      date: dateStr,
      company: company,
      amount: amount || 'N/A',
      investor: investor,
      reason: reason || 'N/A',
      stage: extractStage(title),
      industry: classifyIndustry(title),
      source: article.source
    });
  }

  console.log(`\n\n✅ 필터링 결과: ${passed}개 (필수 3가지 충족), ${filtered}개 제외\n`);
  return required3;
}

async function saveToSupabase(newsList) {
  console.log('💾 Supabase에 저장 중...\n');

  let saved = 0;

  for (const news of newsList) {
    try {
      // 중복 확인
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
      console.log(`✅ [${saved}] ${news.date} | ${news.company} | ${news.investor.substring(0, 20)}`);

    } catch (err) {
      console.error(`❌ 저장 실패: ${err.message}`);
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

// ============================================================
// 메인 실행
// ============================================================

async function main() {
  try {
    // Step 1: 5대 언론사 크롤링
    const mediaArticles = await crawlMediaSites();

    // Step 2: Naver API 보충
    const naverArticles = await collectFromNaverAPI();

    // 모두 병합
    const allArticles = [...mediaArticles, ...naverArticles];

    if (allArticles.length === 0) {
      console.log('⚠️ 수집된 기사 없음\n');
      process.exit(0);
    }

    // Step 3: 필터링
    const filtered = await processAndSave(allArticles);

    if (filtered.length > 0) {
      // Step 4: Supabase 저장
      await saveToSupabase(filtered);

      // Step 5: 번호 재정렬
      await renumberDeals();
    }

    console.log('🎉 모든 작업 완료!\n');
    process.exit(0);

  } catch (err) {
    console.error('❌ 오류:', err.message);
    process.exit(1);
  }
}

main();
