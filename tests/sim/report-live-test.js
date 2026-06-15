const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path=require('path');
const FRONT=path.resolve(__dirname,'../../Valuation_Company/valuation-platform/frontend');
(async()=>{
  const srv=spawn('node',[path.join(__dirname,'..','static-server.js'),FRONT,'8171'],{stdio:'ignore'});
  await new Promise(r=>setTimeout(r,1300));
  const b=await chromium.launch({headless:true,args:['--no-sandbox','--disable-gpu']});
  // 1) 계산기에서 입력 변경 후 보고서 버튼 → 라이브 반영 확인 (DCF)
  const ctx=await b.newContext();
  const cp=await ctx.newPage();
  await cp.goto('http://localhost:8171/app/valuation/results/dcf-valuation.html',{waitUntil:'networkidle'});
  await cp.evaluate(()=>{document.getElementById('companyName').value='테스트구조화';document.getElementById('sharesOutstanding').value='20000000';document.getElementById('ebit1').value='9000000000';});
  // 버튼 클릭 대신 직접 함수 호출(새창 대신 동일 컨텍스트 검증)
  await cp.evaluate(()=>{var o={};document.querySelectorAll('input,select,textarea').forEach(e=>{if(e.id)o[e.id]=e.value;});localStorage.setItem('vl_report_fields_dcf',JSON.stringify(o));});
  const rp=await ctx.newPage();
  const errs=[];rp.on('pageerror',e=>errs.push(e.message.split('\n')[0]));
  await rp.goto('http://localhost:8171/app/valuation/report-auto.html?method=dcf',{waitUntil:'networkidle'});
  await rp.waitForTimeout(400);
  const txt=await rp.evaluate(()=>document.querySelector('.doc').innerText);
  const hasCo=txt.includes('테스트구조화');
  const hasChart=await rp.$$eval('svg',s=>s.length);
  const shareLine=(txt.match(/발행주식수[^\n]*/)||[''])[0];
  console.log('라이브 회사명 반영:',hasCo?'✅':'❌');
  console.log('라이브 주식수(2천만) 반영:', /20,000,000/.test(txt)?'✅':'❌', '|', shareLine.slice(0,40));
  console.log('차트(SVG):', hasChart>0?'✅ '+hasChart+'개':'❌');
  console.log('에러:', errs.length?errs.join('|'):'0');
  await ctx.close();
  // 2) 라이브 없이 샘플 fallback
  const sp=await b.newPage();
  await sp.goto('http://localhost:8171/app/valuation/report-auto.html?method=tax',{waitUntil:'networkidle'});
  await sp.waitForTimeout(300);
  const t2=await sp.evaluate(()=>document.querySelector('.doc').innerText);
  console.log('샘플 fallback(tax 한울푸드):', t2.includes('한울푸드')?'✅':'❌');
  await b.close();srv.kill();
})();
