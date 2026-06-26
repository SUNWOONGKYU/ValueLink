/**
 * 5개 가치평가 계산기 실브라우저 검증 스크립트
 * Playwright Chromium 사용
 */
const { chromium } = require('playwright');

const BASE = 'http://localhost:5050/app/valuation/results';

function isValidResult(text) {
    if (!text || text === '-' || text === '') return { ok: false, reason: 'empty/dash' };
    if (text.includes('NaN')) return { ok: false, reason: 'NaN' };
    if (text.includes('Infinity')) return { ok: false, reason: 'Infinity' };
    if (text.includes('undefined')) return { ok: false, reason: 'undefined' };
    return { ok: true };
}

function extractNumber(text) {
    if (!text) return NaN;
    // Remove commas, 원, 억, 조 units
    let s = text.replace(/,/g, '').replace(/원$/, '').replace(/원/g, '').trim();
    if (s.includes('억')) {
        const n = parseFloat(s.replace('억', ''));
        return n * 1e8;
    }
    if (s.includes('조')) {
        const n = parseFloat(s.replace('조', ''));
        return n * 1e12;
    }
    return parseFloat(s);
}

async function testAsset(page) {
    console.log('\n=== [1] asset-valuation ===');
    const dialogs = [];
    page.on('dialog', async d => { dialogs.push(d.message()); await d.dismiss(); });

    await page.goto(`${BASE}/asset-valuation.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    // 계산 버튼 클릭
    await page.click('button.btn-calculate');
    await page.waitForTimeout(800);

    const resultSection = await page.locator('#result-section').isVisible();
    console.log('result-section visible:', resultSection);

    const navpsOrigText = await page.locator('#result-navps-original').textContent();
    const navpsAdjText = await page.locator('#result-navps-adjusted').textContent();
    const marketNavText = await page.locator('#result-market-nav').textContent();

    console.log('조정전 NAVPS:', navpsOrigText, '| 조정후 NAVPS:', navpsAdjText, '| 시가순자산:', marketNavText);

    // Validate
    const v1 = isValidResult(navpsOrigText);
    const v2 = isValidResult(navpsAdjText);

    // Independent cross-check
    // Assets (book+adj): cash=8000+0, ar=4500-90, inv=1200-60, otherCur=2300+0
    //   invest=5000+500, land=8000+4000, building=12000-1200, equip=6000-1200, intang=5000-1000, otherNC=3000+0
    // Total assets market = 8000+4410+1140+2300 + 5500+12000+10800+4800+4000+3000
    const cashM = 8000+0, arM = 4500-90, invM = 1200-60, otherCurM = 2300+0;
    const investM = 5000+500, landM = 8000+4000, buildM = 12000-1200, equipM = 6000-1200, intangM = 5000-1000, otherNCM = 3000+0;
    const totalAssetsMarket = cashM + arM + invM + otherCurM + investM + landM + buildM + equipM + intangM + otherNCM;

    // Liabilities market
    const apM = 3500+0, shortDebtM = 4000+0, otherCurLiabM = 5500+0;
    const longDebtM = 8000-500, pensionM = 3000+500, otherNCLiabM = 3000+0;
    const totalLiabMarket = apM + shortDebtM + otherCurLiabM + longDebtM + pensionM + otherNCLiabM;

    const navMarket = totalAssetsMarket - totalLiabMarket;
    const shares = 5000000;
    const navDiscount = 0;
    const navps = Math.round((navMarket * 1e6) / shares);
    const adjustedNavps = Math.round(navps * (1 + navDiscount / 100));

    console.log('독립계산 - 시가순자산(백만원):', navMarket, '| NAVPS(원):', navps, '| 조정NAVPS:', adjustedNavps);

    const displayedNavps = extractNumber(navpsOrigText);
    const match = Math.abs(displayedNavps - navps) <= 1;

    return {
        page: 'asset',
        buttonClicked: true,
        displayValue: navpsOrigText + ' (orig) / ' + navpsAdjText + ' (adj)',
        independent: navps + '원 (orig) / ' + adjustedNavps + '원 (adj)',
        match: match,
        nanInfinity: (!v1.ok || !v2.ok) ? (v1.reason || v2.reason) : '없음',
        details: { totalAssetsMarket, totalLiabMarket, navMarket }
    };
}

async function testDCF(page) {
    console.log('\n=== [2] dcf-valuation ===');
    const dialogs = [];
    page.on('dialog', async d => { dialogs.push({ msg: d.message() }); await d.dismiss(); });

    await page.goto(`${BASE}/dcf-valuation.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    await page.click('button.btn-calculate');
    await page.waitForTimeout(1000);

    const resultVisible = await page.locator('#resultSection').isVisible();
    console.log('resultSection visible:', resultVisible);

    const perShareText = await page.locator('#resultPerShare').textContent();
    const evText = await page.locator('#resultEnterpriseValue').textContent();
    const opValText = await page.locator('#resultOperatingValue').textContent();

    console.log('주당가치:', perShareText, '| 기업가치:', evText, '| 영업가치:', opValText);

    const v1 = isValidResult(perShareText);
    console.log('NaN/Inf check:', v1);

    // Independent DCF calculation
    const rf = 0.035, mrp = 0.070, beta = 1.25, size = 0.020;
    const costOfDebt = 0.048, taxRate = 0.25;
    const eRatio = 0.75, dRatio = 0.25;
    const costOfEquity = rf + beta * mrp + size; // 0.035+0.0875+0.02 = 0.1425
    const afterTaxCostOfDebt = costOfDebt * (1 - taxRate); // 0.048*0.75=0.036
    const ratioSum = eRatio + dRatio; // 1.0
    const eW = eRatio / ratioSum;
    const dW = dRatio / ratioSum;
    const wacc = eW * costOfEquity + dW * afterTaxCostOfDebt;
    console.log('독립계산 WACC:', (wacc*100).toFixed(2) + '%');

    const ebit = [5488e6, 7134e6, 8704e6, 10010e6, 11011e6];
    const dep  = [515e6,  669e6,  816e6,  938e6,   1032e6];
    const capex= [858e6,  1115e6, 1360e6, 1564e6,  1720e6];
    const wc   = [784e6,  823e6,  785e6,  653e6,   500e6];
    const g = 0.025;
    const nonOpAssets = 8e9;
    const ibd = 7e9;
    const shares = 5000000;

    let pvSum = 0;
    const fcffs = [];
    for (let i = 0; i < 5; i++) {
        const nopat = ebit[i] * (1 - taxRate);
        const fcff = nopat + dep[i] - capex[i] - wc[i];
        const df = 1 / Math.pow(1 + wacc, i + 1);
        const pv = fcff * df;
        pvSum += pv;
        fcffs.push({ fcff, pv });
        console.log(`  Year ${i+1}: FCFF=${(fcff/1e8).toFixed(2)}억, PV=${(pv/1e8).toFixed(2)}억`);
    }
    const lastFcff = fcffs[4].fcff;
    const tvFcff = lastFcff * (1 + g);
    const tv = tvFcff / (wacc - g);
    const pvTv = tv / Math.pow(1 + wacc, 5);
    const operatingValue = pvSum + pvTv;
    const ev = operatingValue + nonOpAssets;
    const equityValue = ev - ibd;
    const vps = Math.round(equityValue / shares);

    console.log('독립계산 - 영업가치:', (operatingValue/1e8).toFixed(1)+'억', '| EV:', (ev/1e8).toFixed(1)+'억', '| 주당가치:', vps+'원');

    const displayedVps = extractNumber(perShareText);
    const match = Math.abs(displayedVps - vps) / vps < 0.001; // 0.1% 허용

    // Robustness: empty shares test
    console.log('\n  [견고성] 발행주식수 빈값 테스트...');
    const dialogsBefore = dialogs.length;
    await page.fill('#sharesOutstanding', '');
    await page.click('button.btn-calculate');
    await page.waitForTimeout(600);
    const dialogsAfter = dialogs.length;
    const sharesEmptyBlocked = dialogsAfter > dialogsBefore;
    const perShareAfterEmpty = await page.locator('#resultPerShare').textContent();
    const nanInResult = perShareAfterEmpty.includes('NaN');
    console.log('  빈주식수 - dialog 발생:', sharesEmptyBlocked, '| 결과NaN:', nanInResult);

    // Robustness: empty taxRate test
    await page.fill('#sharesOutstanding', '5000000');
    await page.fill('#taxRate', '');
    const dialogsBeforeTax = dialogs.length;
    await page.click('button.btn-calculate');
    await page.waitForTimeout(600);
    const taxRateResult = await page.locator('#resultPerShare').textContent();
    const taxNaN = taxRateResult.includes('NaN');
    console.log('  빈taxRate - 결과NaN:', taxNaN, '| value:', taxRateResult);
    // Restore
    await page.fill('#taxRate', '25');

    return {
        page: 'dcf',
        buttonClicked: true,
        displayValue: perShareText,
        independent: vps + '원',
        match: match,
        nanInfinity: v1.ok ? '없음' : v1.reason,
        robustness: {
            emptyShares: sharesEmptyBlocked ? '차단됨(alert)' : (nanInResult ? 'NaN노출' : '결과미변경'),
            emptyTaxRate: taxNaN ? 'NaN노출' : '정상(NaN없음)',
        },
        details: { wacc: (wacc*100).toFixed(2)+'%', vps }
    };
}

async function testIntrinsic(page) {
    console.log('\n=== [3] intrinsic-valuation ===');

    await page.goto(`${BASE}/intrinsic-valuation.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    await page.click('button.btn-calculate');
    await page.waitForTimeout(800);

    const resultVisible = await page.locator('#result-section').isVisible();
    console.log('result-section visible:', resultVisible);

    const finalText = await page.locator('#result-final').textContent();
    const incomeText = await page.locator('#result-income').textContent();
    const assetText = await page.locator('#result-asset').textContent();

    console.log('본질가치:', finalText, '| 수익가치:', incomeText, '| 자산가치:', assetText);

    const v = isValidResult(finalText);

    // Independent calculation
    // totalShares=5000000, capRate=10%, navMillions=35000
    // income years (백만원): 600, 1300, 2575 → avg = (600+1300+2575)/3 = 1491.67
    const y1=600, y2=1300, y3=2575;
    const avgIncome = (y1+y2+y3) / 3;
    const capRate = 0.10;
    const navMillions = 35000;
    const totalShares = 5000000;

    const incomeValue = Math.max(0, avgIncome) / capRate; // 14916.67 백만원
    const perShareIncome = (incomeValue * 1e6) / totalShares; // 2983.33원
    const perShareAsset = (navMillions * 1e6) / totalShares;  // 7000원
    const intrinsic = Math.round((perShareAsset * 1 + perShareIncome * 1.5) / 2.5);

    console.log('독립계산 - avgIncome:', avgIncome.toFixed(2), '| incomeVal:', incomeValue.toFixed(0), '백만원');
    console.log('독립계산 - perShareIncome:', perShareIncome.toFixed(0), '원 | perShareAsset:', perShareAsset, '원');
    console.log('독립계산 - 본질가치:', intrinsic, '원');

    const displayed = extractNumber(finalText);
    const match = Math.abs(displayed - intrinsic) <= 1;

    return {
        page: 'intrinsic',
        buttonClicked: true,
        displayValue: finalText,
        independent: intrinsic + '원',
        match: match,
        nanInfinity: v.ok ? '없음' : v.reason,
    };
}

async function testRelative(page) {
    console.log('\n=== [4] relative-valuation ===');

    await page.goto(`${BASE}/relative-valuation.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    // calculateAverages 먼저 실행
    await page.evaluate(() => { if (typeof calculateAverages === 'function') calculateAverages(); });
    await page.click('button.btn-calculate');
    await page.waitForTimeout(800);

    const resultVisible = await page.locator('#result-section').isVisible();
    console.log('result-section visible:', resultVisible);

    const finalText = await page.locator('#result-final-value').textContent();
    const perValueText = await page.locator('#result-per-value').textContent();
    const pbrValueText = await page.locator('#result-pbr-value').textContent();

    console.log('가중평균주당가치:', finalText, '| PER기준:', perValueText, '| PBR기준:', pbrValueText);

    const v = isValidResult(finalText);

    // Read peer data from page to do independent calc
    const peerData = await page.evaluate(() => {
        const tbody = document.getElementById('peer-tbody');
        const rows = tbody.rows;
        const result = [];
        for (let row of rows) {
            const inputs = row.querySelectorAll('input');
            const vals = Array.from(inputs).slice(1, 7).map(i => parseFloat(i.value) || 0);
            result.push(vals); // [marketcap, per, pbr, psr, evEbitda, evSales]
        }
        return result;
    });

    // Get target company data
    const targetData = await page.evaluate(() => ({
        shares: parseFloat(document.getElementById('shares-outstanding').value.replace(/,/g,'')) || 0,
        netIncome: parseFloat(document.getElementById('net-income').value.replace(/,/g,'')) || 0,
        equity: parseFloat(document.getElementById('equity').value.replace(/,/g,'')) || 0,
        revenue: parseFloat(document.getElementById('revenue').value.replace(/,/g,'')) || 0,
        ebitda: parseFloat(document.getElementById('ebitda').value.replace(/,/g,'')) || 0,
        netDebt: parseFloat(document.getElementById('net-debt').value.replace(/,/g,'')) || 0,
        weightPer: parseFloat(document.getElementById('weight-per').value) || 0,
        weightPbr: parseFloat(document.getElementById('weight-pbr').value) || 0,
        weightEvEbitda: parseFloat(document.getElementById('weight-ev-ebitda').value) || 0,
        calcMethod: document.getElementById('calc-method').value,
    }));

    console.log('Target data:', JSON.stringify(targetData));
    console.log('Peer rows:', peerData.length);

    // Independent: compute mean PER, PBR, EV/EBITDA
    const pers = peerData.map(r => r[1]).filter(v => v > 0);
    const pbrs = peerData.map(r => r[2]).filter(v => v > 0);
    const evEbitdas = peerData.map(r => r[4]).filter(v => v > 0);

    const avgPer = pers.length > 0 ? pers.reduce((a,b)=>a+b,0)/pers.length : 0;
    const avgPbr = pbrs.length > 0 ? pbrs.reduce((a,b)=>a+b,0)/pbrs.length : 0;
    const avgEvEbitda = evEbitdas.length > 0 ? evEbitdas.reduce((a,b)=>a+b,0)/evEbitdas.length : 0;

    const shares = targetData.shares;
    const mcPer = targetData.netIncome * avgPer;
    const perPS = shares > 0 ? Math.round(mcPer * 1e6 / shares) : 0;
    const mcPbr = targetData.equity * avgPbr;
    const pbrPS = shares > 0 ? Math.round(mcPbr * 1e6 / shares) : 0;
    const evEbitdaEV = targetData.ebitda * avgEvEbitda;
    const mcEvEbitda = evEbitdaEV - targetData.netDebt;
    const evEbitdaPS = shares > 0 ? Math.round(mcEvEbitda * 1e6 / shares) : 0;

    const wPer = targetData.weightPer / 100;
    const wPbr = targetData.weightPbr / 100;
    const wEvEbitda = targetData.weightEvEbitda / 100;
    const weightedPS = Math.round(perPS * wPer + pbrPS * wPbr + evEbitdaPS * wEvEbitda);

    console.log('독립계산 - avgPER:', avgPer.toFixed(1), '| avgPBR:', avgPbr.toFixed(1), '| avgEV/EBITDA:', avgEvEbitda.toFixed(1));
    console.log('독립계산 - PER주당:', perPS, '| PBR주당:', pbrPS, '| EV/EBITDA주당:', evEbitdaPS);
    console.log('독립계산 - 가중평균주당:', weightedPS);

    const displayed = extractNumber(finalText);
    const match = Math.abs(displayed - weightedPS) / Math.max(1, weightedPS) < 0.02; // 2% 허용(PSR 0 제외 시 차이 가능)

    return {
        page: 'relative',
        buttonClicked: true,
        displayValue: finalText,
        independent: weightedPS + '원',
        match: match,
        nanInfinity: v.ok ? '없음' : v.reason,
    };
}

async function testTax(page) {
    console.log('\n=== [5] tax-valuation ===');

    await page.goto(`${BASE}/tax-valuation.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    await page.click('button.btn-calculate');
    await page.waitForTimeout(800);

    const resultVisible = await page.locator('#result-section').isVisible();
    console.log('result-section visible:', resultVisible);

    const finalText = await page.locator('#result-final-value').textContent();
    const profitText = await page.locator('#result-profit-value').textContent();
    const assetText = await page.locator('#result-asset-value').textContent();

    console.log('1주당평가액:', finalText, '| 순손익가치:', profitText, '| 순자산가치:', assetText);

    const v = isValidResult(finalText);

    // Check floor note
    const formulaHtml = await page.locator('#result-formula').innerHTML();
    const floorApplied = formulaHtml.includes('80% 하한');
    console.log('80% 하한 적용 여부:', floorApplied);

    // Independent calculation
    const income3=850, nontax3=50, tax3=213;
    const income2=1740, nontax2=80, tax2=435;
    const income1=3430, nontax1=120, tax1=858;
    const profit3 = income3 + nontax3 - tax3; // 687
    const profit2 = income2 + nontax2 - tax2; // 1385
    const profit1 = income1 + nontax1 - tax1; // 2692
    const rawWeighted = (profit3*1 + profit2*2 + profit1*3) / 6;
    const weightedProfit = Math.max(0, rawWeighted);
    const discountRate = 0.10;
    const shares = 5000000;
    const totalProfitValue = (weightedProfit * 1e6) / discountRate;
    const profitValuePS = totalProfitValue / shares;

    const totalAssets = 55950, totalLiabilities = 27000;
    const netAssets = totalAssets - totalLiabilities; // 28950
    const assetValuePS = (netAssets * 1e6) / shares;

    // General: (3*profit + 2*asset) / 5
    let finalValue = Math.floor((profitValuePS * 3 + assetValuePS * 2) / 5);
    const assetFloor = assetValuePS * 0.8;
    const floorNeeded = finalValue < assetFloor;
    if (floorNeeded) finalValue = Math.floor(assetFloor);

    console.log('독립계산 - profit3/2/1:', profit3, profit2, profit1);
    console.log('독립계산 - weightedProfit:', rawWeighted.toFixed(2), '백만원 | 1주당순손익가치:', profitValuePS.toFixed(0)+'원');
    console.log('독립계산 - netAssets:', netAssets, '백만원 | 1주당순자산가치:', assetValuePS.toFixed(0)+'원');
    console.log('독립계산 - finalValue:', finalValue, '원 | 80%하한필요:', floorNeeded);

    const displayed = extractNumber(finalText);
    const match = Math.abs(displayed - finalValue) <= 1;

    return {
        page: 'tax',
        buttonClicked: true,
        displayValue: finalText,
        independent: finalValue + '원',
        match: match,
        nanInfinity: v.ok ? '없음' : v.reason,
        floorApplied80pct: floorApplied ? '확인됨' : '미표시',
        floorExpected: floorNeeded ? '예상:적용' : '예상:미적용',
    };
}

async function main() {
    const browser = await chromium.launch({ headless: true });
    const results = [];

    try {
        // asset
        {
            const page = await browser.newPage();
            try { results.push(await testAsset(page)); } catch(e) { results.push({ page:'asset', error: e.message }); }
            await page.close();
        }
        // dcf
        {
            const page = await browser.newPage();
            try { results.push(await testDCF(page)); } catch(e) { results.push({ page:'dcf', error: e.message }); }
            await page.close();
        }
        // intrinsic
        {
            const page = await browser.newPage();
            try { results.push(await testIntrinsic(page)); } catch(e) { results.push({ page:'intrinsic', error: e.message }); }
            await page.close();
        }
        // relative
        {
            const page = await browser.newPage();
            try { results.push(await testRelative(page)); } catch(e) { results.push({ page:'relative', error: e.message }); }
            await page.close();
        }
        // tax
        {
            const page = await browser.newPage();
            try { results.push(await testTax(page)); } catch(e) { results.push({ page:'tax', error: e.message }); }
            await page.close();
        }
    } finally {
        await browser.close();
    }

    console.log('\n\n========== 최종 결과 요약 ==========');
    console.log(JSON.stringify(results, null, 2));
}

main().catch(e => { console.error('FATAL:', e); process.exit(1); });
