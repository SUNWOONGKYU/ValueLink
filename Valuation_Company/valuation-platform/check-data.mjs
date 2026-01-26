/**
 * Supabase 데이터 확인 스크립트
 */

import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://arxrfetgaitkgiiqabap.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeHJmZXRnYWl0a2dpaXFhYmFwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3ODk1OTgsImV4cCI6MjA4NDM2NTU5OH0.BTnuv0sYr2MGe1c-gk8PWCviwkFyIiymfKp5Jhzwbo0';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function checkData() {
    try {
        console.log('📊 Supabase 데이터 확인 중...\n');

        const { data, error } = await supabase
            .from('valuation_reports')
            .select('company_name, valuation_method, valuation_amount_display')
            .order('id');

        if (error) {
            console.error('❌ 오류:', error);
            return;
        }

        if (!data || data.length === 0) {
            console.log('⚠️  데이터가 없습니다.');
            return;
        }

        console.log(`✅ 총 ${data.length}개 기업 등록됨:\n`);
        data.forEach((row, index) => {
            console.log(`   ${index + 1}. ${row.company_name} (${row.valuation_method}): ${row.valuation_amount_display}`);
        });

        console.log('\n🎉 데이터 확인 완료!\n');

    } catch (error) {
        console.error('❌ 예외 발생:', error.message);
    }
}

checkData();
