"""Render the self-contained browser studio used to review calculations and request reports."""

from __future__ import annotations


def render_home() -> str:
    """Return the accessible single-page Korean report studio as static HTML."""
    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Four Pillars · 사주 리포트</title>
  <style>
    :root{--navy:#17263f;--blue:#315a84;--coral:#d16f58;--teal:#4f8f8a;--gold:#c5a165;--page:#fbfaf6;--surface:#fff;--muted:#667283;--line:#d9d7cf;--danger:#a43c30;--success:#256f5b}
    *{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--navy);font-family:"Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif;line-height:1.55}
    header{background:var(--navy);color:#fff;padding:26px clamp(20px,5vw,72px)}header p{margin:4px 0;color:#dbe6f3}header a{color:#fff}
    main{max-width:1180px;margin:0 auto;padding:32px clamp(18px,4vw,48px) 64px;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(320px,.95fr);gap:24px;align-items:start}
    .panel{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:0 14px 40px #17263f10}.panel h2{margin-top:0}.step{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:var(--coral);color:#fff;font-weight:700;margin-right:8px}
    form{display:grid;grid-template-columns:1fr 1fr;gap:16px}.wide{grid-column:1/-1}label{display:grid;gap:6px;font-weight:650;font-size:.92rem}input,select,textarea,button{font:inherit}input,select,textarea{width:100%;padding:11px 12px;border:1px solid #aeb6c1;border-radius:9px;background:#fff;color:var(--navy)}textarea{min-height:90px;resize:vertical}.hint{font-size:.79rem;color:var(--muted);font-weight:400}
    .actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:4px}button,.button{border:0;border-radius:999px;padding:11px 18px;font-weight:750;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}.primary{background:var(--blue);color:#fff}.secondary{background:#e7f0ef;color:#245f5a}.ghost{background:#eef2f6;color:var(--navy)}button:disabled{opacity:.55;cursor:not-allowed}
    #status{min-height:28px;padding:10px 0;color:var(--muted)}#status.error{color:var(--danger)}.chart-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}.pillar{background:#eaf1f7;border-top:4px solid var(--blue);border-radius:8px;padding:14px;text-align:center}.pillar strong{font-size:1.35rem;display:block}.warning{background:#fff2ed;border-left:5px solid var(--coral);padding:12px 14px;border-radius:6px;margin-top:10px}.boundary{font-size:.85rem;color:var(--muted)}
    .downloads{display:flex;gap:9px;flex-wrap:wrap;margin-top:12px}.downloads a,.downloads button,.artifact-link{background:#f2efe8;color:var(--navy);border:1px solid var(--line);padding:9px 13px;border-radius:8px;text-decoration:none;font-weight:700}.privacy{font-size:.82rem;color:var(--muted);border-top:1px solid var(--line);padding-top:15px;margin-top:18px}
    .history-panel{grid-column:1/-1}.history-head{display:flex;align-items:flex-end;justify-content:space-between;gap:20px}.history-head h2{margin-bottom:4px}.history-helper{margin:0;color:var(--muted);font-size:.86rem}.history-controls{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap}.history-controls label{min-width:180px}.history-controls button{min-height:44px}.history-list{display:grid;gap:10px;margin-top:14px}.history-item{border:1px solid var(--line);border-radius:12px;padding:16px;display:grid;gap:11px;background:var(--surface)}.history-top,.history-bottom,.history-identity,.history-actions,.history-footer{display:flex;align-items:center;gap:10px}.history-top,.history-bottom{justify-content:space-between}.history-identity{min-width:0}.history-id{font-weight:750;overflow-wrap:anywhere}.history-time,.history-detail,.history-helper{color:var(--muted)}.history-time{font-size:.78rem;white-space:nowrap}.history-detail{font-size:.84rem;margin:0}.history-chip{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:5px 10px;font-size:.72rem;font-weight:800;white-space:nowrap}.status-queued{background:#f6f1e6;color:#735c2f}.status-running{background:#eaf1f7;color:var(--blue)}.status-completed{background:#e7f0ef;color:var(--success)}.status-failed,.status-quality_failed{background:#fff2ed;color:var(--danger)}.history-actions{flex-wrap:wrap;justify-content:flex-end}.history-footer{justify-content:center;flex-wrap:wrap;margin-top:14px}.history-empty{margin:0;padding:18px;text-align:center;color:var(--muted);background:#f7f6f1;border-radius:10px}.history-meta{font-size:.78rem;color:var(--muted)}#history-status{min-height:28px;padding-top:10px;color:var(--muted)}#history-status.error{color:var(--danger)}
    pre{white-space:pre-wrap;word-break:break-word;max-height:380px;overflow:auto;background:#111d31;color:#eaf1f7;padding:14px;border-radius:10px;font-size:.78rem}
    @media(max-width:850px){main{grid-template-columns:1fr}form{grid-template-columns:1fr}.wide{grid-column:auto}.history-head,.history-top,.history-bottom{align-items:stretch;flex-direction:column}.history-controls{align-items:stretch}.history-controls label{min-width:0;flex:1}.history-controls button,.history-actions button,.artifact-link{width:100%}.history-actions{justify-content:stretch}.history-time{white-space:normal}}
    @media(max-width:480px){.chart-grid{grid-template-columns:repeat(2,1fr)}.panel{padding:18px}.history-controls{display:grid;grid-template-columns:1fr}.history-item{padding:14px}}
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
  <section class="panel history-panel" id="history" aria-labelledby="history-title">
    <div class="history-head">
      <div>
        <h2 id="history-title"><span class="step">3</span>최근 보고서 작업</h2>
        <p class="history-helper">이름·생년월일·상황 메모는 표시하지 않습니다. 서버가 공개한 상태와 파일만 확인합니다.</p>
      </div>
      <div class="history-controls">
        <label>상태<select id="history-filter"><option value="">전체 상태</option><option value="queued">대기</option><option value="running">실행 중</option><option value="completed">완료</option><option value="failed">실패</option><option value="quality_failed">품질 실패</option></select></label>
        <button class="secondary" type="button" id="history-refresh">새로고침</button>
      </div>
    </div>
    <div id="history-status" role="status" aria-live="polite">최근 작업을 불러오고 있습니다.</div>
    <div class="history-list" id="history-list"></div>
    <div class="history-footer"><button class="ghost" type="button" id="history-more" hidden>이전 작업 더 불러오기</button><span class="history-meta">최신순 · 한 번에 20개</span></div>
  </section>
</main>
<script>
const form=document.querySelector('#report-form'), statusBox=document.querySelector('#status'), chartBox=document.querySelector('#chart'), raw=document.querySelector('#raw'), generate=document.querySelector('#generate'), jobBox=document.querySelector('#job'), stateBox=document.querySelector('#job-state'), downloads=document.querySelector('#downloads'), apiKey=document.querySelector('#api-key'), historyFilter=document.querySelector('#history-filter'), historyRefresh=document.querySelector('#history-refresh'), historyStatus=document.querySelector('#history-status'), historyList=document.querySelector('#history-list'), historyMore=document.querySelector('#history-more');
let reviewed=null, reportKey=null, pollTimer=null, historyCursor=null, historyLoading=false, historyRequest=0;
const historyLimit=20, statusLabels={queued:'대기',running:'실행 중',completed:'완료',failed:'실패',quality_failed:'품질 실패'};
function headers(){const key=apiKey.value;return {'Content-Type':'application/json',...(key?{'X-API-Key':key}:{})}}
function birthPayload(){const d=document.querySelector('#birth-date').value,t=document.querySelector('#birth-time').value;return {birth:`${d}T${t||'12:00'}:00`,timezone:document.querySelector('#timezone').value,gender:document.querySelector('#gender').value,calendar:document.querySelector('#calendar').value,lunar_leap_month:false,birth_time_known:Boolean(t),time_basis:'civil',day_boundary:'midnight'}}
function message(text,error=false){statusBox.textContent=text;statusBox.className=error?'error':''}
function historyMessage(text,error=false){historyStatus.textContent=text;historyStatus.className=error?'error':''}
async function api(path,options={}){const response=await fetch(path,{...options,headers:{...headers(),...(options.headers||{})}});if(!response.ok){let detail=`HTTP ${response.status}`;try{const body=await response.json();detail=body.detail||detail}catch{}const error=new Error(typeof detail==='string'?detail:JSON.stringify(detail));error.status=response.status;throw error}return response.status===204?null:response.json()}
function addText(parent,tag,text,className=''){const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;parent.appendChild(node);return node}
function renderChart(chart){chartBox.replaceChildren();const grid=document.createElement('div');grid.className='chart-grid';[['연주',chart.year],['월주',chart.month],['일주',chart.day],['시주',chart.hour]].forEach(([label,pillar])=>{const card=document.createElement('div');card.className='pillar';addText(card,'span',label);addText(card,'strong',pillar?pillar.hanja:'미확정');addText(card,'small',pillar?pillar.korean:'');grid.appendChild(card)});chartBox.appendChild(grid);addText(chartBox,'p',`절기 구간: ${chart.current_jie.name_ko} ${new Date(chart.current_jie.occurs_at).toLocaleString()} → ${chart.next_jie.name_ko} ${new Date(chart.next_jie.occurs_at).toLocaleString()}`,'boundary');addText(chartBox,'p',`계산 fingerprint: ${chart.fingerprint}`,'boundary');chart.boundary_warnings.forEach(warning=>addText(chartBox,'div',warning,'warning'));chartBox.hidden=false;raw.textContent=JSON.stringify(chart,null,2)}
async function downloadArtifact(jobId,name){try{const response=await fetch(`/v1/reports/${jobId}/artifacts/${name}`,{headers:headers()});if(!response.ok){let detail=`HTTP ${response.status}`;try{const body=await response.json();detail=body.detail||detail}catch{}throw new Error(typeof detail==='string'?detail:JSON.stringify(detail))}const blob=await response.blob(),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),0)}catch(error){message(error.message,true);historyMessage(error.message,true)}}
function artifactButton(parent,jobId,name){const button=document.createElement('button');button.type='button';button.className='artifact-link';button.textContent=name;button.addEventListener('click',()=>downloadArtifact(jobId,name));parent.appendChild(button);return button}
function renderCurrentArtifacts(job){downloads.replaceChildren();job.artifacts.forEach(name=>artifactButton(downloads,job.id,name))}
async function calculate(){try{message('만세력과 절기 경계를 계산하고 있습니다…');reviewed=await api('/v1/chart',{method:'POST',body:JSON.stringify(birthPayload())});renderChart(reviewed);generate.disabled=false;message('계산을 확인했습니다. 같은 입력으로 보고서를 생성할 수 있습니다.')}catch(error){reviewed=null;generate.disabled=true;message(error.message,true)}}
async function poll(id){clearTimeout(pollTimer);try{const job=await api(`/v1/reports/${id}`);jobBox.hidden=false;stateBox.textContent=`상태: ${statusLabels[job.status]||job.status}${job.error?` · ${job.error}`:''}`;if(job.status==='completed'){renderCurrentArtifacts(job);message('보고서 생성이 완료되었습니다.');loadHistory({reset:true});return}if(['failed','quality_failed'].includes(job.status)){downloads.replaceChildren();message('보고서를 완료하지 못했습니다. 상태와 오류를 확인하세요.',true);loadHistory({reset:true});return}pollTimer=setTimeout(()=>poll(id),2000)}catch(error){message(error.message,true)}}
function shortJobId(id){return id.length>18?`${id.slice(0,8)}…${id.slice(-4)}`:id}
function historyTime(value){try{return new Intl.DateTimeFormat('ko-KR',{dateStyle:'medium',timeStyle:'short'}).format(new Date(value))}catch{return value}}
function boundedHistoryDetail(value){const detail=String(value||'작업을 완료하지 못했습니다.');return detail.length>240?`${detail.slice(0,239)}…`:detail}
function setHistoryLoading(loading){historyLoading=loading;historyRefresh.disabled=loading;historyFilter.disabled=loading;historyMore.disabled=loading}
function scrollToCurrentJob(){const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;window.scrollTo({top:jobBox.getBoundingClientRect().top+window.scrollY-24,behavior:reduced?'auto':'smooth'})}
function restoreActiveJob(job){jobBox.hidden=false;downloads.replaceChildren();stateBox.textContent=`상태: ${statusLabels[job.status]||job.status}${job.error?` · ${boundedHistoryDetail(job.error)}`:''}`;if(['queued','running'].includes(job.status)){message('선택한 보고서 작업의 상태를 확인하고 있습니다.');poll(job.id)}else if(job.status==='completed'){renderCurrentArtifacts(job);message('완료된 보고서 파일을 선택할 수 있습니다.')}else{message('선택한 작업의 오류를 확인하세요.',true)}scrollToCurrentJob()}
function renderHistoryItem(job){const item=document.createElement('article');item.className='history-item';const top=document.createElement('div');top.className='history-top';const identity=document.createElement('div');identity.className='history-identity';const chip=addText(identity,'span',statusLabels[job.status]||job.status,`history-chip status-${job.status}`);chip.setAttribute('aria-label',`작업 상태 ${statusLabels[job.status]||job.status}`);const id=addText(identity,'code',shortJobId(job.id),'history-id');id.title=job.id;top.appendChild(identity);const time=addText(top,'time',historyTime(job.created_at),'history-time');time.dateTime=job.created_at;item.appendChild(top);const bottom=document.createElement('div');bottom.className='history-bottom';let detail='대기 중인 작업입니다.';if(job.status==='running')detail='보고서를 생성하고 있습니다.';if(job.status==='completed')detail=job.artifacts.length?`사용 가능한 파일 ${job.artifacts.length}개`:'완료되었지만 공개된 파일이 없습니다.';if(['failed','quality_failed'].includes(job.status))detail=boundedHistoryDetail(job.error);addText(bottom,'p',detail,'history-detail');const actions=document.createElement('div');actions.className='history-actions';if(job.status==='completed'){job.artifacts.forEach(name=>artifactButton(actions,job.id,name))}else if(['queued','running'].includes(job.status)){const button=document.createElement('button');button.type='button';button.className='ghost';button.textContent='상태 보기';button.addEventListener('click',()=>restoreActiveJob(job));actions.appendChild(button)}bottom.appendChild(actions);item.appendChild(bottom);historyList.appendChild(item)}
async function loadHistory({reset=false}={}){const requestId=++historyRequest;if(reset){historyCursor=null;historyList.replaceChildren();historyMore.hidden=true}const cursor=historyCursor;setHistoryLoading(true);historyMessage(reset?'최근 작업을 불러오고 있습니다.':'이전 작업을 더 불러오고 있습니다.');const params=new URLSearchParams({limit:String(historyLimit)});if(historyFilter.value)params.set('status',historyFilter.value);if(!reset&&cursor)params.set('cursor',cursor);try{const payload=await api(`/v1/reports?${params.toString()}`);if(requestId!==historyRequest)return;if(reset)historyList.replaceChildren();payload.items.forEach(renderHistoryItem);historyCursor=payload.next_cursor;historyMore.hidden=!historyCursor;if(!historyList.children.length){addText(historyList,'p','표시할 최근 작업이 없습니다.','history-empty');historyMessage('표시할 최근 작업이 없습니다.')}else if(reset){historyMessage(`${payload.items.length}개의 최근 작업을 불러왔습니다.`)}else{historyMessage(payload.items.length?`${payload.items.length}개의 이전 작업을 추가했습니다.`:'더 표시할 작업이 없습니다.')}}catch(error){if(requestId!==historyRequest)return;if(reset)historyList.replaceChildren();historyCursor=null;historyMore.hidden=true;let text=error.message;if(error.status===401)text='API 키가 필요한 환경입니다. 키를 입력한 뒤 새로고침하세요.';if(error.status===501)text='현재 저장소는 최근 작업 조회를 지원하지 않습니다.';historyMessage(text,true)}finally{if(requestId===historyRequest)setHistoryLoading(false)}}
document.querySelector('#calculate').addEventListener('click',calculate);
historyFilter.addEventListener('change',()=>loadHistory({reset:true}));
historyRefresh.addEventListener('click',()=>loadHistory({reset:true}));
historyMore.addEventListener('click',()=>loadHistory({reset:false}));
apiKey.addEventListener('change',()=>loadHistory({reset:true}));
form.addEventListener('input',event=>{if(event.target.id==='api-key')return;reviewed=null;reportKey=null;generate.disabled=true;chartBox.hidden=true;raw.textContent='입력이 변경되어 계산을 다시 확인해야 합니다.';message('입력이 변경되었습니다. 계산을 다시 확인하세요.')});
form.addEventListener('reset',()=>{setTimeout(()=>{reviewed=null;reportKey=null;generate.disabled=true;chartBox.hidden=true;jobBox.hidden=true;raw.textContent='아직 계산하지 않았습니다.';message('입력을 초기화했습니다.')},0)});
form.addEventListener('submit',async event=>{event.preventDefault();if(!reviewed){await calculate();if(!reviewed)return}try{const [year,month]=document.querySelector('#monthly-month').value.split('-').map(Number);if(!reportKey)reportKey=crypto.randomUUID();message('보고서 작업을 등록하고 있습니다…');const job=await api('/v1/reports',{method:'POST',headers:{'Idempotency-Key':`"${reportKey}"`},body:JSON.stringify({subject_name:document.querySelector('#subject').value,birth:birthPayload(),annual_year:Number(document.querySelector('#annual-year').value),monthly_year:year,monthly_month:month,user_context:document.querySelector('#context').value})});reportKey=null;jobBox.hidden=false;downloads.replaceChildren();stateBox.textContent=`상태: ${statusLabels[job.status]||job.status}`;await loadHistory({reset:true});poll(job.id)}catch(error){message(error.message,true)}});
loadHistory({reset:true});
</script>
</body></html>"""
