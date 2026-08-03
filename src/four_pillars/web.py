from __future__ import annotations


def render_home() -> str:
    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Four Pillars · 사주 리포트</title>
  <style>
    :root{--navy:#17263f;--blue:#315a84;--coral:#d16f58;--teal:#4f8f8a;--gold:#c5a165;--page:#fbfaf6;--surface:#fff;--muted:#667283;--line:#d9d7cf;--danger:#a43c30}
    *{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--navy);font-family:"Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif;line-height:1.55}
    header{background:var(--navy);color:#fff;padding:26px clamp(20px,5vw,72px)}header p{margin:4px 0;color:#dbe6f3}header a{color:#fff}
    main{max-width:1180px;margin:0 auto;padding:32px clamp(18px,4vw,48px) 64px;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(320px,.95fr);gap:24px;align-items:start}
    .panel{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 14px 40px #17263f10}.panel h2{margin-top:0}.step{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:var(--coral);color:#fff;font-weight:700;margin-right:8px}
    form{display:grid;grid-template-columns:1fr 1fr;gap:16px}.wide{grid-column:1/-1}label{display:grid;gap:6px;font-weight:650;font-size:.92rem}input,select,textarea,button{font:inherit}input,select,textarea{width:100%;padding:11px 12px;border:1px solid #aeb6c1;border-radius:9px;background:#fff;color:var(--navy)}textarea{min-height:90px;resize:vertical}.hint{font-size:.79rem;color:var(--muted);font-weight:400}
    .actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:4px}button,.button{border:0;border-radius:999px;padding:11px 18px;font-weight:750;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}.primary{background:var(--blue);color:#fff}.secondary{background:#e7f0ef;color:#245f5a}.ghost{background:#eef2f6;color:var(--navy)}button:disabled{opacity:.55;cursor:not-allowed}
    #status{min-height:28px;padding:10px 0;color:var(--muted)}#status.error{color:var(--danger)}.chart-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}.pillar{background:#eaf1f7;border-top:4px solid var(--blue);border-radius:8px;padding:14px;text-align:center}.pillar strong{font-size:1.35rem;display:block}.warning{background:#fff2ed;border-left:5px solid var(--coral);padding:12px 14px;border-radius:6px;margin-top:10px}.boundary{font-size:.85rem;color:var(--muted)}
    .downloads{display:flex;gap:9px;flex-wrap:wrap;margin-top:12px}.downloads a{background:#f2efe8;color:var(--navy);border:1px solid var(--line);padding:9px 13px;border-radius:8px;text-decoration:none;font-weight:700}.privacy{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:15px;margin-top:18px}
    pre{white-space:pre-wrap;word-break:break-word;max-height:380px;overflow:auto;background:#111d31;color:#eaf1f7;padding:14px;border-radius:10px;font-size:.78rem}
    @media(max-width:850px){main{grid-template-columns:1fr}form{grid-template-columns:1fr}.wide{grid-column:auto}}@media(max-width:480px){.chart-grid{grid-template-columns:repeat(2,1fr)}.panel{padding:18px}}
    @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
  </style>
</head>
<body>
<header>
  <strong>FOUR PILLARS</strong>
  <h1>계산을 먼저 확인하고, 해석을 파일로 받으세요.</h1>
  <p>만세력 계산과 AI 해석을 분리합니다. 경계 경고와 계산 fingerprint를 확인한 뒤 NVIDIA NIM 보고서를 생성합니다. <a href="/docs">API 문서</a></p>
</header>
<main>
  <section class="panel" aria-labelledby="input-title">
    <h2 id="input-title"><span class="step">1</span>출생 정보 입력</h2>
    <form id="report-form">
      <label>이름 또는 보고서 호칭<input id="subject" name="subject" maxlength="80" required value="최혜지"></label>
      <label>성별<select id="gender"><option value="unspecified">미지정 · 대운 양방향</option><option value="female" selected>여성</option><option value="male">남성</option></select></label>
      <label>생년월일<input id="birth-date" type="date" required value="1990-06-15"></label>
      <label>출생 시각<input id="birth-time" type="time" step="60" value="08:30"><span class="hint">모르면 비워 두면 시주를 확정하지 않습니다.</span></label>
      <label>달력<select id="calendar"><option value="solar">양력</option><option value="lunar">한국 음력</option></select></label>
      <label>시간대<input id="timezone" value="Asia/Seoul" required><span class="hint">IANA 이름을 입력합니다.</span></label>
      <label>분석 연도<input id="annual-year" type="number" min="1900" max="2200" value="2026" required></label>
      <label>분석 월<input id="monthly-month" type="month" value="2026-08" required></label>
      <label class="wide">상황 메모<textarea id="context" maxlength="4000" placeholder="직업·관계·생활에서 구체적으로 살펴볼 맥락을 적을 수 있습니다. 메모는 계산값을 바꾸지 않습니다."></textarea></label>
      <label class="wide">API 키 <input id="api-key" type="password" autocomplete="off" placeholder="운영 환경에서 인증을 켠 경우에만 입력"><span class="hint">브라우저 메모리에만 두며 저장하지 않습니다.</span></label>
      <div class="actions wide"><button class="primary" type="button" id="calculate">계산 먼저 확인</button><button class="secondary" type="submit" id="generate" disabled>확인한 계산으로 보고서 생성</button><button class="ghost" type="reset">입력 초기화</button></div>
    </form>
    <p class="privacy">생년월일시와 상황 메모는 민감정보가 될 수 있습니다. 운영자는 TLS, 접근제어, 보존기간, 삭제 정책을 설정해야 합니다.</p>
  </section>
  <aside class="panel" aria-labelledby="result-title">
    <h2 id="result-title"><span class="step">2</span>계산 검토와 작업 상태</h2>
    <div id="status" role="status" aria-live="polite">출생 정보를 입력한 뒤 계산을 확인하세요.</div>
    <div id="chart" hidden></div>
    <div id="job" hidden><h3>보고서 작업</h3><p id="job-state"></p><div class="downloads" id="downloads"></div></div>
    <details><summary>원본 JSON 보기</summary><pre id="raw">아직 계산하지 않았습니다.</pre></details>
  </aside>
</main>
<script>
const form=document.querySelector('#report-form'), statusBox=document.querySelector('#status'), chartBox=document.querySelector('#chart'), raw=document.querySelector('#raw'), generate=document.querySelector('#generate'), jobBox=document.querySelector('#job'), stateBox=document.querySelector('#job-state'), downloads=document.querySelector('#downloads');
let reviewed=null, pollTimer=null;
function headers(){const key=document.querySelector('#api-key').value;return {'Content-Type':'application/json',...(key?{'X-API-Key':key}:{})}}
function birthPayload(){const d=document.querySelector('#birth-date').value,t=document.querySelector('#birth-time').value;return {birth:`${d}T${t||'12:00'}:00`,timezone:document.querySelector('#timezone').value,gender:document.querySelector('#gender').value,calendar:document.querySelector('#calendar').value,lunar_leap_month:false,birth_time_known:Boolean(t),time_basis:'civil',day_boundary:'midnight'}}
function message(text,error=false){statusBox.textContent=text;statusBox.className=error?'error':''}
async function api(path,options={}){const response=await fetch(path,{...options,headers:{...headers(),...(options.headers||{})}});if(!response.ok){let detail=`HTTP ${response.status}`;try{const body=await response.json();detail=body.detail||detail}catch{}throw new Error(typeof detail==='string'?detail:JSON.stringify(detail))}return response.status===204?null:response.json()}
function renderChart(chart){const items=[['연주',chart.year],['월주',chart.month],['일주',chart.day],['시주',chart.hour]];chartBox.innerHTML=`<div class="chart-grid">${items.map(([label,p])=>`<div class="pillar"><span>${label}</span><strong>${p?p.hanja:'미확정'}</strong><small>${p?p.korean:''}</small></div>`).join('')}</div><p class="boundary">절기 구간: ${chart.current_jie.name_ko} ${new Date(chart.current_jie.occurs_at).toLocaleString()} → ${chart.next_jie.name_ko} ${new Date(chart.next_jie.occurs_at).toLocaleString()}</p><p class="boundary">계산 fingerprint: ${chart.fingerprint}</p>${chart.boundary_warnings.map(w=>`<div class="warning">${w}</div>`).join('')}`;chartBox.hidden=false;raw.textContent=JSON.stringify(chart,null,2)}
async function calculate(){try{message('만세력과 절기 경계를 계산하고 있습니다…');reviewed=await api('/v1/chart',{method:'POST',body:JSON.stringify(birthPayload())});renderChart(reviewed);generate.disabled=false;message('계산을 확인했습니다. 같은 입력으로 보고서를 생성할 수 있습니다.')}catch(error){reviewed=null;generate.disabled=true;message(error.message,true)}}
async function poll(id){clearTimeout(pollTimer);try{const job=await api(`/v1/reports/${id}`);stateBox.textContent=`상태: ${job.status}${job.error?` · ${job.error}`:''}`;if(job.status==='completed'){downloads.innerHTML=['report.pdf','report.html','report.json','chart.json','manifest.json'].map(name=>`<a href="/v1/reports/${id}/artifacts/${name}">${name}</a>`).join('');message('보고서 생성이 완료되었습니다.');return}if(['failed','quality_failed'].includes(job.status)){message('보고서를 완료하지 못했습니다. 상태와 오류를 확인하세요.',true);return}pollTimer=setTimeout(()=>poll(id),2000)}catch(error){message(error.message,true)}}
document.querySelector('#calculate').addEventListener('click',calculate);
form.addEventListener('reset',()=>{setTimeout(()=>{reviewed=null;generate.disabled=true;chartBox.hidden=true;jobBox.hidden=true;raw.textContent='아직 계산하지 않았습니다.';message('입력을 초기화했습니다.')},0)});
form.addEventListener('submit',async event=>{event.preventDefault();if(!reviewed){await calculate();if(!reviewed)return}try{const [year,month]=document.querySelector('#monthly-month').value.split('-').map(Number);message('보고서 작업을 등록하고 있습니다…');const job=await api('/v1/reports',{method:'POST',body:JSON.stringify({subject_name:document.querySelector('#subject').value,birth:birthPayload(),annual_year:Number(document.querySelector('#annual-year').value),monthly_year:year,monthly_month:month,user_context:document.querySelector('#context').value})});jobBox.hidden=false;downloads.innerHTML='';stateBox.textContent=`상태: ${job.status}`;poll(job.id)}catch(error){message(error.message,true)}});
</script>
</body></html>"""
