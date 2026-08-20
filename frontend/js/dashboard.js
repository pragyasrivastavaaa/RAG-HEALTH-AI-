const user = getUser();  // May be null for guest uploads
if (user) renderNavUser();

let globalData = null, chatHistory = [], chatOpen = false, currentReportId = null;

window.addEventListener('DOMContentLoaded', () => {
    currentReportId = localStorage.getItem('rag_report_id');
    const raw = localStorage.getItem('rag_result');
    if (!raw) { document.getElementById('noData').style.display='block'; return; }
    let data;
    try { data = JSON.parse(raw); } catch { document.getElementById('noData').style.display='block'; return; }
    if (!data.findings && currentReportId) { refetch(parseInt(currentReportId)); return; }
    document.getElementById('dashContent').style.display = 'block';
    render(data);
});

async function refetch(id) {
    const res  = await apiFetch(`/analyze/${id}`, { method:'POST' });
    if (!res) return;
    const data = await res.json();
    if (data.findings) { localStorage.setItem('rag_result', JSON.stringify(data)); document.getElementById('dashContent').style.display='block'; render(data); }
    else document.getElementById('noData').style.display='block';
}

function render(data) {
    globalData = data;
    const score    = data.health_score ?? 0;
    const findings = data.findings     || [];
    const conds    = data.conditions   || [];
    const diet     = data.diet_plan    || {};
    const rag      = data.rag_analysis || {};
    const first    = data.patient_first|| null;
    const abnormal = findings.filter(f => f.status !== 'Normal').length;

    const hour = new Date().getHours();
    const greet = hour<12?'Good morning':hour<17?'Good afternoon':'Good evening';
    document.getElementById('greetHi').innerHTML  = first ? `${greet}, <span>${first}</span>! 👋` : `${greet}! 👋`;
    document.getElementById('greetSub').textContent = first
        ? `Here is your personalised RAG health analysis, ${first}.`
        : 'Here is your personalised RAG health analysis.';

    countUp('stScore',    score);
    countUp('stParams',   data.parameters_found || findings.length);
    countUp('stAbnormal', abnormal);
    countUp('stConds',    conds.length);

    drawScoreRing(score);
    document.getElementById('scoreNum').textContent = score;
    const {label,desc,color} = scoreInfo(score, first);
    document.getElementById('scoreTitle').textContent = label;
    document.getElementById('scoreDesc').textContent  = desc;
    document.getElementById('scoreNum').style.color   = color;

    if (rag.analysis) {
        document.getElementById('ragBox').style.display = 'block';
        document.getElementById('ragText').textContent  = rag.analysis;
        const src = document.getElementById('ragSources');
        (rag.sources||[]).slice(0,3).forEach(s => {
            const pill = document.createElement('span');
            pill.className   = 'rag-source-pill';
            pill.textContent = s.source;
            src.appendChild(pill);
        });
    }

    drawLabChart(findings);
    renderFindings(findings);
    renderDiet(diet);
    document.getElementById('chatFab').style.display = 'flex';
    initChat(first, score, abnormal);
}

function scoreInfo(score, name) {
    const you = name || 'Your';
    if (score >= 80) return { label:'Good Health',           color:'var(--green)', desc:`${you}'s parameters are mostly within normal range. Keep up the healthy habits.` };
    if (score >= 55) return { label:'Moderate Concern',      color:'var(--warn)',  desc:`${you} has some parameters needing attention. Follow the plan below and see a doctor.` };
    return               { label:'Needs Urgent Attention', color:'var(--red)',   desc:`Multiple abnormal values detected. Please consult a doctor promptly.` };
}

function drawScoreRing(score) {
    const ctx   = document.getElementById('scoreChart').getContext('2d');
    const color = score>=80?'#00d4aa':score>=55?'#ffb347':'#ff4d6d';
    new Chart(ctx, { type:'doughnut', data:{ datasets:[{ data:[score,100-score], backgroundColor:[color,'rgba(255,255,255,0.05)'], borderWidth:0, circumference:280, rotation:-140 }] }, options:{ cutout:'78%', responsive:false, plugins:{ legend:{display:false}, tooltip:{enabled:false} }, animation:{duration:1200,easing:'easeOutQuart'} } });
}

function drawLabChart(findings) {
    if (!findings.length) return;
    const items   = findings.slice(0,12);
    const labels  = items.map(f => f.display_name.split('(')[0].trim());
    const values  = items.map(f => f.value);
    const mins    = items.map(f => f.normal_min);
    const maxs    = items.map(f => f.normal_max);
    const colors  = items.map(f => f.status==='Normal'?'rgba(0,212,170,0.7)':f.status==='High'?'rgba(255,77,109,0.7)':'rgba(255,179,71,0.7)');
    const bcolors = items.map(f => f.status==='Normal'?'#00d4aa':f.status==='High'?'#ff4d6d':'#ffb347');
    new Chart(document.getElementById('labChart').getContext('2d'), {
        type:'bar',
        data:{ labels, datasets:[{ label:'Value', data:values, backgroundColor:colors, borderColor:bcolors, borderWidth:1.5, borderRadius:5 }] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{display:false}, tooltip:{ backgroundColor:'#111827', borderColor:'rgba(255,255,255,0.1)', borderWidth:1, callbacks:{ afterBody:(items)=>{ const i=items[0].dataIndex; return [`Normal: ${mins[i]} – ${maxs[i]}`]; } } } }, scales:{ x:{ticks:{color:'#8892a4',font:{size:10},maxRotation:40},grid:{color:'rgba(255,255,255,0.04)'}}, y:{ticks:{color:'#8892a4',font:{size:11}},grid:{color:'rgba(255,255,255,0.04)'}} }, animation:{duration:1000} }
    });
}

function renderFindings(findings) {
    const list = document.getElementById('findingsList');
    list.innerHTML = '';
    findings.forEach((f,i) => {
        const pct = Math.min(100, f.normal_max>0?(f.value/(f.normal_max*1.5))*100:50);
        const bc  = f.status==='Normal'?'bar-n':f.status==='High'?'bar-h':'bar-l';
        const bgc = f.status==='Normal'?'badge-normal':f.status==='High'?'badge-high':'badge-low';
        const row = document.createElement('div');
        row.className = 'finding-row';
        row.style.animationDelay = (i*0.04)+'s';
        row.innerHTML = `<div class="finding-name">${f.display_name}</div><div class="finding-bar-wrap"><div class="finding-bar-bg"><div class="finding-bar-fill ${bc}" style="width:0%" data-w="${pct}"></div></div></div><div class="finding-val">${f.value} <span style="font-size:0.72rem;color:var(--text3)">${f.unit}</span></div><span class="badge ${bgc}">${f.status}</span>`;
        list.appendChild(row);
    });
    requestAnimationFrame(() => document.querySelectorAll('.finding-bar-fill').forEach(b => b.style.width = b.dataset.w+'%'));
}

function renderDiet(plan) {
    const dl = document.getElementById('dietList'), ll = document.getElementById('lifeList');
    dl.innerHTML = ll.innerHTML = '';
    (plan.diet||[]).forEach((item,i) => { const el=document.createElement('div'); el.className='tip-item'; el.style.animationDelay=(i*0.05)+'s'; el.innerHTML=`<span class="tip-dot td"></span><span>${item.tip}</span>`; dl.appendChild(el); });
    (plan.lifestyle||[]).forEach((item,i) => { const el=document.createElement('div'); el.className='tip-item'; el.style.animationDelay=(i*0.05)+'s'; el.innerHTML=`<span class="tip-dot tl"></span><span>${item.tip}</span>`; ll.appendChild(el); });
}

function countUp(id, target) {
    const el=document.getElementById(id), dur=1100, start=performance.now();
    function step(now) { const t=Math.min((now-start)/dur,1),e=1-Math.pow(1-t,3); el.textContent=Math.round(e*target); if(t<1)requestAnimationFrame(step); }
    requestAnimationFrame(step);
}

function initChat(first, score, abnormal) {
    const msg = first
        ? `Hi ${first}! 👋 Health score: ${score}/100 with ${abnormal} abnormal values. My answers are grounded in WHO medical guidelines via RAG. Ask me anything!`
        : `Hello! 👋 Health score: ${score}/100. Ask me anything about your report — I use WHO guidelines to answer.`;
    addBot(msg);
    const chips = ['What should I eat?','What are my biggest concerns?','Explain my score','Should I see a doctor?'];
    const wrap  = document.getElementById('chatChips');
    chips.forEach(s => { const c=document.createElement('span'); c.className='chip'; c.textContent=s; c.onclick=()=>{ document.getElementById('chatInput').value=s; sendMsg(); }; wrap.appendChild(c); });
}

function toggleChat() { chatOpen=!chatOpen; document.getElementById('chatPanel').classList.toggle('open',chatOpen); if(chatOpen) setTimeout(()=>document.getElementById('chatInput').focus(),80); }

function addBot(text) { const m=document.createElement('div'); m.className='msg msg-bot'; m.textContent=text; const msgs=document.getElementById('chatMsgs'); msgs.appendChild(m); msgs.scrollTop=msgs.scrollHeight; }
function addUser(text){ const m=document.createElement('div'); m.className='msg msg-user'; m.textContent=text; const msgs=document.getElementById('chatMsgs'); msgs.appendChild(m); msgs.scrollTop=msgs.scrollHeight; }

async function sendMsg() {
    const input=document.getElementById('chatInput'), send=document.getElementById('chatSend');
    const msg=input.value.trim(); if(!msg) return;
    document.getElementById('chatChips').style.display='none';
    addUser(msg); chatHistory.push({role:'user',content:msg}); input.value=''; send.disabled=true;
    const typing=document.createElement('div'); typing.className='msg msg-bot'; typing.id='typing'; typing.textContent='...';
    document.getElementById('chatMsgs').appendChild(typing); document.getElementById('chatMsgs').scrollTop=99999;
    try {
        const res  = await apiFetch('/chat', { method:'POST', body:JSON.stringify({ message:msg, report_id:currentReportId?parseInt(currentReportId):null, patient_name:globalData?.patient_first||null, history:chatHistory.slice(-6) }) });
        document.getElementById('typing')?.remove();
        if (!res) return;
        const data = await res.json();
        const reply= data.reply || 'Sorry, something went wrong.';
        addBot(reply); chatHistory.push({role:'assistant',content:reply});
    } catch { document.getElementById('typing')?.remove(); addBot('Could not reach server. Make sure Flask is running.'); }
    send.disabled=false; input.focus();
}