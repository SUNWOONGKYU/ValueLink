#!/usr/bin/env node
/**
 * Bill News Tracker - 투자 뉴스 수집 커맨드
 * 명령어: npm run bill-news-tracker
 * 또는: node bill-news-tracker.js
 */

const axios = require('axios');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const NAVER_CLIENT_ID = process.env.NAVER_CLIENT_ID;
const NAVER_CLIENT_SECRET = process.env.NAVER_CLIENT_SECRET;

const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

console.log('📰 Bill News Tracker 시작...\n');

// 투자 관련 정확한 키워드
const KEYWORDS = [
  '스타트업 투자 유치',
  '시리즈A 펀딩',
  '시리즈B 펀딩',
  '프리A 투자',
  '벤처캐피탈 투자',
  '시드 펀딩',
  '기업가치평가 투자',
  '창업 자금조달'
];

// 필터링할 엉뚱한 키워드 (제거)
const EXCLUDE_KEYWORDS = [
  '정치', '드라마', '영화', '스포츠', '연예', '미스트롯',
  '비트코인', '암호화폐', '해킹', '범죄', '사망', '논란',
  '대북', '국방', '전쟁', '군사', '무기', '미사일'
];

// 투자 관련 회사명 키워드
const COMPANY_KEYWORDS = [
  '스타트업', '벤처기업', '테크기업', '에드테크', 'AI기업',
  '핀테크', '헬스케어', '바이오', '팕', '클린테크',
  '호텔', '배달', '커머스', '마켓플레이스'
];

async function collectNews() {
  let collected = [];

  console.log(`🔍 ${KEYWORDS.length}개 키워드로 검색 중...\n`);

  for (const keyword of KEYWORDS) {
    try {
      const response = await axios.get('https://openapi.naver.com/v1/search/news.json', {
        params: {
          query: keyword,
          sort: 'date',
          display: 30,
          start: 1
        },
        headers: {
          'X-Naver-Client-Id': NAVER_CLIENT_ID,
          'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
        },
        timeout: 5000
      });

      for (const item of response.data.items || []) {
        // 제외 키워드 필터링
        const isExcluded = EXCLUDE_KEYWORDS.some(ex => 
          item.title.includes(ex) || (item.description && item.description.includes(ex))
        );
        
        if (isExcluded) continue;

        // 투자 관련 키워드 포함 확인
        const hasKeyword = COMPANY_KEYWORDS.some(kw => 
          item.title.includes(kw)
        );

        if (!hasKeyword) continue;

        // 발행 날짜 파싱
        const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
        const dateStr = pubDate.toISOString().split('T')[0];

        collected.push({
          title: item.title.replace(/<\/?b>/g, ''),
          url: item.link,
          site: item.source,
          date: dateStr
        });
      }

      process.stdout.write('.');
    } catch (err) {
      console.error(`\n⚠️ 검색 오류 (${keyword}):`, err.message);
    }
  }

  console.log(`\n\n✅ 수집됨: ${collected.length}개`);
  return collected;
}

async function extractCompanyName(title) {
  // 패턴 1: "회사명, 투자자로부터 투자"
  if (title.includes(',')) {
    return title.split(',')[0].trim();
  }

  // 패턴 2: "회사명이 시리즈A 펀딩"
  for (const keyword of ['시리즈', '펀딩', '투자', '유치']) {
    const idx = title.indexOf(keyword);
    if (idx > 0) {
      return title.substring(0, idx).trim();
    }
  }

  // 패턴 3: 첫 번째 단어
  return title.split(' ')[0].trim();
}

async function saveToSupabase(newsList) {
  console.log('\n💾 Supabase에 저장 중...\n');

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
        console.log(`⏭️  [중복] ${news.site}`);
        continue;
      }

      const company = await extractCompanyName(news.title);

      const record = {
        company_name: company,
        news_title: news.title,
        news_url: news.url,
        site_name: news.site,
        news_date: news.date,
        industry: 'TBD',
        stage: 'TBD'
      };

      await supabase.from('deals').insert(record);
      saved++;
      console.log(`✅ [${saved}] ${news.date} | ${company.substring(0, 20)} | ${news.site}`);
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
