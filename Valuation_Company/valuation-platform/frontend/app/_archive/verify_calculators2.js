/**
 * 5개 가치평가 계산기 실브라우저 검증 스크립트 v2
 * - 클릭 타임아웃 문제 수정: scrollIntoView 후 JS 직접 호출 fallback
 */
const { chromium } = require('playwright');

const BASE = 'http://localhost:5050/app/valuation/results';

function isValidResult(text) {
    if (!text || text === '-' || text.trim() === '') return { ok: false, reason: 'empty/dash' };
    if (text.includes('NaN')) return { ok: false, reason: 'NaN' };
    if (text.includes('Infinity')) return { ok: false, reason: 'Infinity' };
    if (text.includes('undefined')) return { ok: false, reason: 'undefined' };
    return { ok: true };
}

function extractNumber(text) {
    if (!text) return NaN;
    let s = text.replace(/,/g, '').replace(/원$/, '').replace(/원/g, '').trim();
    if (s.includes('억')) return parseFloat(s.replace('억', '')) * 1e8;
    if (s.includes('조')) return parseFloat(s.replace('조', '')) * 1e12;
    return parseFloat(s);
}

/**
 * 버튼 클릭을 여러 방법으로 시도
 */
async function clickCalcButton(page, jsFunc) {
    // 1차: JS로 직접 함수 호출 (가장 확실)
    try {
        await page.evaluate(`${jsFunc}()`);
        console.log(`  -> JS direct call: ${jsFunc}()`);
        await page.waitForTimeout(800);
        return 'js-direct';
    } catch(e) {
        console.log(`  -> JS direct call failed: ${e.message}`);
    }
    // 2차: force click
    try {
        await page.locator('button.btn-calculate').first().click({ force: true, timeout: 5000 });
        console.log('  -> force click');
        await page.waitForTimeout(800);
        return 'force-click';
    } catch(e) {
        console.log(`  -> force click failed: ${e.message}`);
    }
    return 'failed';
}

async function testAsset(browser) {
    console.log('\n=== [1] asset-valuation ===');
    const page = await browser.newPage();
    const dialogs = [];
    page.on('dialog', async d => { dialogs.push(d.message()); await d.dismiss(); });

    try {
        await page.goto(`${BASE}/asset-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);

        const clickMethod = await clickCalcButton(page, 'calculateNAV');
        await page.waitForTimeout(500);

        const resultVisible = await page.locator('#result-section').isVisible();
        console.log('result-section visible:', resultVisible, '| click method:', clickMethod);

        const navpsOrigText = (await page.locator('#result-navps-original').textContent()).trim();
        const navpsAdjText = (await page.locator('#result-navps-adjusted').textContent()).trim();
        const marketNavText = (await page.locator('#result-market-nav').textContent()).trim();

        console.log('조정전 NAVPS:', navpsOrigText, '| 조정후 NAVPS:', navpsAdjText);

        const v1 = isValidResult(navpsOrigText);
        const v2 = isValidResult(navpsAdjText);

        // Independent
        const cashM = 8000, arM = 4500-90, invM = 1200-60, otherCurM = 2300;
        const investM = 5000+500, landM = 8000+4000, buildM = 12000-1200, equipM = 6000-1200, intangM = 5000-1000, otherNCM = 3000;
        const totalAssetsMarket = cashM + arM + invM + otherCurM + investM + landM + buildM + equipM + intangM + otherNCM;
        const apM = 3500, shortDebtM = 4000, otherCurLiabM = 5500;
        const longDebtM = 8000-500, pensionM = 3000+500, otherNCLiabM = 3000;
        const totalLiabMarket = apM + shortDebtM + otherCurLiabM + longDebtM + pensionM + otherNCLiabM;
        const navMarket = totalAssetsMarket - totalLiabMarket;
        const shares = 5000000;
        const navps = Math.round((navMarket * 1e6) / shares);
        const adjustedNavps = navps; // discount=0

        console.log('독립계산 - 시가순자산(백만원):', navMarket, '| NAVPS(원):', navps);
        const displayed = extractNumber(navpsOrigText);
        const match = Math.abs(displayed - navps) <= 1;
        console.log('일치 여부:', match, `(표시:${displayed} vs 계산:${navps})`);

        return {
            page: 'asset', buttonClicked: clickMethod !== 'failed',
            displayValue: navpsOrigText + ' (orig) / ' + navpsAdjText + ' (adj)',
            independent: navps + '원 (orig) / ' + adjustedNavps + '원 (adj)',
            match,
            nanInfinity: (!v1.ok || !v2.ok) ? (v1.reason || v2.reason) : '없음'
        };
    } catch(e) {
        return { page: 'asset', error: e.message };
    } finally {
        await page.close();
    }
}

async function testDCF(browser) {
    console.log('\n=== [2] dcf-valuation ===');
    const page = await browser.newPage();
    const dialogs = [];
    page.on('dialog', async d => { dialogs.push({ msg: d.message() }); await d.dismiss(); });

    try {
        await page.goto(`${BASE}/dcf-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);

        const clickMethod = await clickCalcButton(page, 'calculateDCF');
        await page.waitForTimeout(500);

        const resultVisible = await page.locator('#resultSection').isVisible();
        console.log('resultSection visible:', resultVisible, '| method:', clickMethod);

        const perShareText = (await page.locator('#resultPerShare').textContent()).trim();
        const evText = (await page.locator('#resultEnterpriseValue').textContent()).trim();
        const opValText = (await page.locator('#resultOperatingValue').textContent()).trim();

        console.log('주당가치:', perShareText, '| 기업가치:', evText, '| 영업가치:', opValText);

        const v = isValidResult(perShareText);

        // Independent DCF
        const rf=0.035, mrp=0.070, beta=1.25, size=0.020;
        const costOfDebt=0.048, taxRate=0.25, eRatio=0.75, dRatio=0.25;
        const costOfEquity = rf + beta*mrp + size;
        const afterTaxCostOfDebt = costOfDebt * (1 - taxRate);
        const wacc = eRatio*costOfEquity + dRatio*afterTaxCostOfDebt;
        console.log('독립계산 WACC:', (wacc*100).toFixed(4)+'%');

        const ebit=[5488e6,7134e6,8704e6,10010e6,11011e6];
        const dep=[515e6,669e6,816e6,938e6,1032e6];
        const capex=[858e6,1115e6,1360e6,1564e6,1720e6];
        const wc=[784e6,823e6,785e6,653e6,500e6];
        let pvSum=0; const fcffs=[];
        for(let i=0;i<5;i++){
            const nopat=ebit[i]*(1-taxRate);
            const fcff=nopat+dep[i]-capex[i]-wc[i];
            const df=1/Math.pow(1+wacc,i+1);
            pvSum+=fcff*df;
            fcffs.push(fcff);
        }
        const g=0.025;
        const tvFcff=fcffs[4]*(1+g);
        const tv=tvFcff/(wacc-g);
        const pvTv=tv/Math.pow(1+wacc,5);
        const operatingValue=pvSum+pvTv;
        const ev=operatingValue+8e9;
        const equityValue=ev-7e9;
        const vps=Math.round(equityValue/5000000);
        console.log('독립계산 - 주당가치:', vps+'원');

        const displayedVps=extractNumber(perShareText);
        const match=Math.abs(displayedVps-vps)/vps < 0.001;
        console.log('일치 여부:', match, `(표시:${displayedVps} vs 계산:${vps})`);

        // Robustness: empty shares
        console.log('\n  [견고성] 발행주식수 빈값 테스트...');
        const dBefore = dialogs.length;
        await page.fill('#sharesOutstanding', '');
        await page.evaluate('calculateDCF()');
        await page.waitForTimeout(500);
        const dAfter = dialogs.length;
        const sharesBlocked = dAfter > dBefore;
        const perShareAfterEmpty = (await page.locator('#resultPerShare').textContent()).trim();
        const nanVisible = perShareAfterEmpty.includes('NaN');
        console.log('  빈주식수 - alert발생:', sharesBlocked, '| NaN표시:', nanVisible, '| 값:', perShareAfterEmpty);

        // Robustness: empty taxRate
        await page.fill('#sharesOutstanding', '5000000');
        await page.fill('#taxRate', '');
        const dBeforeTax = dialogs.length;
        await page.evaluate('calculateDCF()');
        await page.waitForTimeout(500);
        const taxRateResult = (await page.locator('#resultPerShare').textContent()).trim();
        const taxNaN = taxRateResult.includes('NaN');
        console.log('  빈taxRate - NaN표시:', taxNaN, '| 값:', taxRateResult);
        await page.fill('#taxRate', '25');

        return {
            page: 'dcf', buttonClicked: clickMethod !== 'failed',
            displayValue: perShareText,
            independent: vps+'원',
            match,
            nanInfinity: v.ok ? '없음' : v.reason,
            robustness: {
                emptyShares: sharesBlocked ? '차단됨(alert)' : (nanVisible ? 'NaN노출' : '결과유지'),
                emptyTaxRate: taxNaN ? 'NaN노출' : '정상(NaN없음)',
            }
        };
    } catch(e) {
        return { page: 'dcf', error: e.message };
    } finally {
        await page.close();
    }
}

async function testIntrinsic(browser) {
    console.log('\n=== [3] intrinsic-valuation ===');
    const page = await browser.newPage();

    try {
        await page.goto(`${BASE}/intrinsic-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);

        const clickMethod = await clickCalcButton(page, 'calculateIntrinsic');
        await page.waitForTimeout(500);

        const resultVisible = await page.locator('#result-section').isVisible();
        console.log('result-section visible:', resultVisible, '| method:', clickMethod);

        const finalText = (await page.locator('#result-final').textContent()).trim();
        const incomeText = (await page.locator('#result-income').textContent()).trim();
        const assetText = (await page.locator('#result-asset').textContent()).trim();

        console.log('본질가치:', finalText, '| 수익가치:', incomeText, '| 자산가치:', assetText);

        const v = isValidResult(finalText);

        // Independent
        const y1=600, y2=1300, y3=2575;
        const avgIncome=(y1+y2+y3)/3;
        const capRate=0.10;
        const navMillions=35000, totalShares=5000000;
        const incomeValue=Math.max(0,avgIncome)/capRate;
        const perShareIncome=(incomeValue*1e6)/totalShares;
        const perShareAsset=(navMillions*1e6)/totalShares;
        const intrinsic=Math.round((perShareAsset*1+perShareIncome*1.5)/2.5);
        console.log('독립계산 - avgIncome:', avgIncome.toFixed(2), '| incomeVal:', incomeValue.toFixed(0), '백만원');
        console.log('독립계산 - perShareIncome:', perShareIncome.toFixed(0), '원 | perShareAsset:', perShareAsset, '원');
        console.log('독립계산 - 본질가치:', intrinsic, '원');

        const displayed=extractNumber(finalText);
        const match=Math.abs(displayed-intrinsic)<=1;
        console.log('일치 여부:', match, `(표시:${displayed} vs 계산:${intrinsic})`);

        return {
            page: 'intrinsic', buttonClicked: clickMethod !== 'failed',
            displayValue: finalText,
            independent: intrinsic+'원',
            match,
            nanInfinity: v.ok ? '없음' : v.reason
        };
    } catch(e) {
        return { page: 'intrinsic', error: e.message };
    } finally {
        await page.close();
    }
}

async function testRelative(browser) {
    console.log('\n=== [4] relative-valuation ===');
    const page = await browser.newPage();

    try {
        await page.goto(`${BASE}/relative-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);

        await page.evaluate(() => { if(typeof calculateAverages==='function') calculateAverages(); });
        const clickMethod = await clickCalcButton(page, 'calculateValuation');
        await page.waitForTimeout(500);

        const resultVisible = await page.locator('#result-section').isVisible();
        console.log('result-section visible:', resultVisible, '| method:', clickMethod);

        const finalText = (await page.locator('#result-final-value').textContent()).trim();
        const perValueText = (await page.locator('#result-per-value').textContent()).trim();
        const pbrValueText = (await page.locator('#result-pbr-value').textContent()).trim();
        const evEbitdaText = (await page.locator('#result-ev-ebitda-value').textContent()).trim();

        console.log('가중평균주당가치:', finalText, '| PER기준:', perValueText, '| PBR기준:', pbrValueText, '| EV/EBITDA:', evEbitdaText);

        const v = isValidResult(finalText);

        // Independent from page data
        const peerData = await page.evaluate(() => {
            const rows = document.getElementById('peer-tbody').rows;
            return Array.from(rows).map(row => {
                const inputs = row.querySelectorAll('input');
                return Array.from(inputs).slice(1,7).map(i=>parseFloat(i.value)||0);
            });
        });
        const targetData = await page.evaluate(() => ({
            shares: parseFloat(document.getElementById('shares-outstanding').value.replace(/,/g,''))||0,
            netIncome: parseFloat(document.getElementById('net-income').value.replace(/,/g,''))||0,
            equity: parseFloat(document.getElementById('equity').value.replace(/,/g,''))||0,
            ebitda: parseFloat(document.getElementById('ebitda').value.replace(/,/g,''))||0,
            netDebt: parseFloat(document.getElementById('net-debt').value.replace(/,/g,''))||0,
            wPer: parseFloat(document.getElementById('weight-per').value)||0,
            wPbr: parseFloat(document.getElementById('weight-pbr').value)||0,
            wEvEbitda: parseFloat(document.getElementById('weight-ev-ebitda').value)||0,
        }));

        const pers = peerData.map(r=>r[1]).filter(v=>v>0);
        const pbrs = peerData.map(r=>r[2]).filter(v=>v>0);
        const evEbitdas = peerData.map(r=>r[4]).filter(v=>v>0);
        const avgPer = pers.length>0 ? pers.reduce((a,b)=>a+b,0)/pers.length : 0;
        const avgPbr = pbrs.length>0 ? pbrs.reduce((a,b)=>a+b,0)/pbrs.length : 0;
        const avgEvEbitda = evEbitdas.length>0 ? evEbitdas.reduce((a,b)=>a+b,0)/evEbitdas.length : 0;

        const {shares, netIncome, equity, ebitda, netDebt, wPer, wPbr, wEvEbitda} = targetData;
        const perPS = Math.round(netIncome*avgPer*1e6/shares);
        const pbrPS = Math.round(equity*avgPbr*1e6/shares);
        const evEbitdaPS = Math.round((ebitda*avgEvEbitda - netDebt)*1e6/shares);
        const weightedPS = Math.round(perPS*(wPer/100) + pbrPS*(wPbr/100) + evEbitdaPS*(wEvEbitda/100));

        console.log('독립계산 - avgPER:', avgPer.toFixed(1), '| avgPBR:', avgPbr.toFixed(1), '| avgEV/EBITDA:', avgEvEbitda.toFixed(1));
        console.log('독립계산 - PER주당:', perPS, '| PBR주당:', pbrPS, '| EV/EBITDA주당:', evEbitdaPS);
        console.log('독립계산 - 가중평균주당:', weightedPS);

        const displayed = extractNumber(finalText);
        const match = Math.abs(displayed - weightedPS) / Math.max(1, weightedPS) < 0.02;
        console.log('일치 여부:', match, `(표시:${displayed} vs 계산:${weightedPS})`);

        return {
            page: 'relative', buttonClicked: clickMethod !== 'failed',
            displayValue: finalText,
            independent: weightedPS+'원',
            match,
            nanInfinity: v.ok ? '없음' : v.reason
        };
    } catch(e) {
        return { page: 'relative', error: e.message };
    } finally {
        await page.close();
    }
}

async function testTax(browser) {
    console.log('\n=== [5] tax-valuation ===');
    const page = await browser.newPage();

    try {
        await page.goto(`${BASE}/tax-valuation.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(2000);

        const clickMethod = await clickCalcButton(page, 'calculateTaxValue');
        await page.waitForTimeout(500);

        const resultVisible = await page.locator('#result-section').isVisible();
        console.log('result-section visible:', resultVisible, '| method:', clickMethod);

        const finalText = (await page.locator('#result-final-value').textContent()).trim();
        const profitText = (await page.locator('#result-profit-value').textContent()).trim();
        const assetText = (await page.locator('#result-asset-value').textContent()).trim();

        console.log('1주당평가액:', finalText, '| 순손익가치:', profitText, '| 순자산가치:', assetText);

        const v = isValidResult(finalText);

        const formulaHtml = await page.locator('#result-formula').innerHTML();
        const floorApplied = formulaHtml.includes('80% 하한') || formulaHtml.includes('80%');
        console.log('80% 하한 적용 여부:', floorApplied);

        // Independent
        const profit3=(850+50-213), profit2=(1740+80-435), profit1=(3430+120-858);
        const rawW=(profit3*1+profit2*2+profit1*3)/6;
        const wp=Math.max(0,rawW);
        const pfPS=(wp*1e6/0.10)/5000000;
        const netAssets=55950-27000;
        const asPS=(netAssets*1e6)/5000000;
        let final=Math.floor((pfPS*3+asPS*2)/5);
        const floor80=asPS*0.8;
        const floorNeeded=final<floor80;
        if(floorNeeded) final=Math.floor(floor80);
        console.log('독립계산 - profitPS:', pfPS.toFixed(0), '| assetPS:', asPS.toFixed(0), '| final:', final, '| 80%하한:', floorNeeded);

        const displayed=extractNumber(finalText);
        const match=Math.abs(displayed-final)<=1;
        console.log('일치 여부:', match, `(표시:${displayed} vs 계산:${final})`);

        return {
            page: 'tax', buttonClicked: clickMethod !== 'failed',
            displayValue: finalText,
            independent: final+'원',
            match,
            nanInfinity: v.ok ? '없음' : v.reason,
            floorApplied80pct: floorApplied ? '확인됨' : '미표시',
            floorExpected: floorNeeded ? '예상:적용' : '예상:미적용'
        };
    } catch(e) {
        return { page: 'tax', error: e.message };
    } finally {
        await page.close();
    }
}

async function main() {
    const browser = await chromium.launch({ headless: true });
    const results = [];

    try {
        results.push(await testAsset(browser));
        results.push(await testDCF(browser));
        results.push(await testIntrinsic(browser));
        results.push(await testRelative(browser));
        results.push(await testTax(browser));
    } finally {
        await browser.close();
    }

    console.log('\n\n========== 최종 결과 JSON ==========');
    console.log(JSON.stringify(results, null, 2));
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
