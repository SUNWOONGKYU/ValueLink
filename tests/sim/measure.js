const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path=require('path');
const FRONT=path.resolve(__dirname,'../../Valuation_Company/valuation-platform/frontend');
(async()=>{
  const srv=spawn('node',[path.join(__dirname,'..','static-server.js'),FRONT,'8170'],{stdio:'ignore'});
  await new Promise(r=>setTimeout(r,1300));
  const b=await chromium.launch({headless:true,args:['--no-sandbox','--disable-gpu']});
  for(const m of ['dcf','tax','intrinsic','relative','asset']){
    const p=await b.newPage();
    await p.goto('http://localhost:8170/app/valuation/report-auto.html?method='+m,{waitUntil:'networkidle'});
    await p.waitForTimeout(400);
    const text=await p.evaluate(()=>document.querySelector('.doc').innerText);
    const tables=await p.$$eval('table',t=>t.length);
    const secs=await p.$$eval('section',s=>s.length);
    console.log(`${m}: ${text.replace(/\s/g,'').length} chars(공백제외) / 표 ${tables}개 / 섹션 ${secs}`);
    await p.close();
  }
  await b.close(); srv.kill();
})();
