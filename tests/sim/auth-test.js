const { chromium } = require('playwright');
const BASE='https://valuelink-platform.vercel.app/app';
const email=`vltest${Date.now()}@example.com`, pw='Test1234!@#';
(async()=>{
  const b=await chromium.launch({headless:true,args:['--no-sandbox','--disable-gpu']});
  const p=await b.newPage();
  const errs=[],net=[],dlgs=[];
  p.on('pageerror',e=>errs.push('PAGEERR: '+e.message.split('\n')[0]));
  p.on('console',e=>{if(e.type()==='error')errs.push('CONSOLE: '+e.text().slice(0,120));});
  p.on('dialog',d=>{dlgs.push(d.message().split('\n')[0]);d.accept().catch(()=>{});});
  p.on('response',r=>{const u=r.url();if(/auth\/v1\/(signup|token)|rest\/v1\/(users|customers)/.test(u))net.push(r.request().method()+' '+(u.split('.co/')[1]||u).split('?')[0]+' -> '+r.status());});
  const fill=async(id,v)=>{const el=await p.$('#'+id);if(el&&await el.isVisible().catch(()=>false)){await el.fill(v).catch(()=>{});return true;}return false;};

  console.log('=== 1) signup ('+email+') ===');
  await p.goto(BASE+'/register.html',{waitUntil:'networkidle',timeout:45000});
  await p.waitForTimeout(800);
  // 역할 선택(고객) — 단계형 폼
  await p.evaluate(()=>{const r=document.getElementById('roleCustomer')||document.querySelector('input[name="role"]');if(r){r.checked=true;r.click();r.dispatchEvent(new Event('change',{bubbles:true}));}});
  await p.waitForTimeout(800);
  await fill('userName','테스트유저'); await fill('userEmail',email);
  await fill('userPassword',pw); await fill('userPasswordConfirm',pw);
  await fill('companyName','테스트컴퍼니'); await fill('companyNameEn','TestCompany'); await fill('ceoName','김대표');
  // 보이는 모든 입력 채우기 + 셀렉트 첫 유효옵션 선택
  await p.evaluate(()=>{
    document.querySelectorAll('input').forEach(e=>{ if(e.offsetParent===null)return; const t=e.type;
      if(t==='text'&&!e.value)e.value='테스트'; else if(t==='tel'&&!e.value)e.value='01012345678';
      else if(t==='number'&&!e.value)e.value='10'; else if(t==='url'&&!e.value)e.value='https://test.com';
      if(t==='text'||t==='tel'||t==='number'||t==='url')e.dispatchEvent(new Event('input',{bubbles:true})); });
    document.querySelectorAll('select').forEach(s=>{ if(s.offsetParent===null)return; const opt=[...s.options].find(o=>o.value&&o.value!=='');
      if(opt){s.value=opt.value;s.dispatchEvent(new Event('change',{bubbles:true}));} });
    document.querySelectorAll('input[type=checkbox]').forEach(c=>{ if(c.offsetParent!==null&&(/약관|동의|개인정보|terms|agree/i.test((c.id||'')+(c.name||''))))c.checked=true; });
  });
  // 고객 필수 필드 직접 주입(숨김 섹션 포함) — 백엔드 경로 검증용
  await p.evaluate(()=>{const set=(id,v)=>{const e=document.getElementById(id);if(e)e.value=v;};
    set('companyName','테스트컴퍼니');set('companyNameEn','TestCompany');set('businessNumber','1234567890');set('ceoName','김대표');set('industry','IT');set('phone','021234567');});
  await p.evaluate(()=>{ if(typeof submitRegistration==='function') return submitRegistration(); const btn=[...document.querySelectorAll('button')].find(x=>/가입|등록|제출/.test(x.textContent)); if(btn)btn.click(); });
  await p.waitForTimeout(4000);
  console.log('  JS에러:', errs.length?errs.join(' | '):'없음');
  console.log('  네트워크:', net.length?net.join(' | '):'(auth호출 없음)');
  console.log('  alert:', dlgs.length?dlgs.join(' | '):'(없음)');
  const body1=await p.evaluate(()=>document.body.innerText);
  console.log('  화면문구:', (body1.match(/확인 메일|가입.{0,10}완료|이메일을? 확인|오류|실패|already|등록/g)||[]).slice(0,4).join(' / ')||'(특이문구 없음)');

  console.log('');
  console.log('=== 2) login (신규=미확인 예상) ===');
  net.length=0;dlgs.length=0;errs.length=0;
  await p.goto(BASE+'/login.html',{waitUntil:'networkidle',timeout:45000});
  await p.waitForTimeout(600);
  await fill('email',email); await fill('password',pw);
  await p.click('#loginBtn',{timeout:5000}).catch(()=>{});
  await p.waitForTimeout(3000);
  console.log('  JS에러:', errs.length?errs.join(' | '):'없음');
  console.log('  네트워크:', net.length?net.join(' | '):'(없음)');
  console.log('  alert:', dlgs.length?dlgs.join(' | '):'(없음)');
  const body2=await p.evaluate(()=>document.body.innerText);
  console.log('  화면문구:', (body2.match(/확인.{0,6}메일|미확인|confirm|비밀번호|일치하지|오류|실패/g)||[]).slice(0,4).join(' / ')||'(특이문구 없음)');
  await b.close();
})();
