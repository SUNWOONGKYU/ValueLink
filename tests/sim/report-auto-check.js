const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FRONT = path.resolve(__dirname,'../../Valuation_Company/valuation-platform/frontend');
const PORT=8166;
(async()=>{
  const srv=spawn('node',[path.join(__dirname,'..','static-server.js'),FRONT,String(PORT)],{stdio:'ignore'});
  await new Promise(r=>setTimeout(r,1300));
  const b=await chromium.launch({headless:true,args:['--no-sandbox','--disable-gpu']});
  const methods=['dcf','tax','intrinsic','relative','asset'];
  const fs=require('fs'); fs.mkdirSync(path.join(__dirname,'screenshots','autoreport'),{recursive:true});
  for(const m of methods){
    const p=await b.newPage({viewport:{width:900,height:1200}});
    const errs=[];
    p.on('pageerror',e=>errs.push(e.message.split('\n')[0]));
    p.on('console',e=>{if(e.type()==='error')errs.push('C:'+e.text().slice(0,80));});
    await p.goto(`http://localhost:${PORT}/app/valuation/report-auto.html?method=${m}`,{waitUntil:'networkidle',timeout:30000});
    await p.waitForTimeout(500);
    const body=await p.evaluate(()=>document.body.innerText);
    const bad=/NaN|undefined|Infinity/.test(body);
    const secCount=await p.$$eval('section',els=>els.length);
    const title=await p.$eval('.cover .ttl',el=>el.textContent).catch(()=>'(no cover)');
    const co=await p.$eval('.cover .co',el=>el.textContent).catch(()=>'?');
    await p.screenshot({path:path.join(__dirname,'screenshots','autoreport',m+'.png'),fullPage:true});
    console.log(`[${m}] 표지:"${title}" 회사:${co} 섹션:${secCount} ${bad?'❌NaN/undefined':'✅clean'} ${errs.length?'ERR:'+errs.join('|'):'에러0'}`);
    await p.close();
  }
  await b.close(); srv.kill();
})();
