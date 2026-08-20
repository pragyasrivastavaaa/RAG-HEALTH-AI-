const user = requireAuth();
if (user) { renderNavUser(); document.getElementById('patientInput').value = user.name; }

let scoreLineChart = null;
const paramCharts  = {};

async function loadTrends() {
    const name = document.getElementById('patientInput').value.trim();
    if (!name) { showToast('Enter a patient name', 'error'); return; }

    document.getElementById('loadingState').style.display  = 'block';
    document.getElementById('noTrends').style.display      = 'none';
    document.getElementById('trendsContent').style.display = 'none';

    try {
        const res  = await apiFetch(`/trends/${encodeURIComponent(name)}`);
        if (!res) return;
        document.getElementById('loadingState').style.display = 'none';

        if (res.status === 404) {
            document.getElementById('noTrendsMsg').textContent = `No reports found for "${name}"`;
            document.getElementById('noTrends').style.display  = 'block';
            return;
        }

        const data = await res.json();
        if (data.total_reports < 2) {
            document.getElementById('noTrendsMsg').textContent = `Only 1 report found for "${name}". Upload more to see trends.`;
            document.getElementById('noTrends').style.display  = 'block';
            return;
        }

        renderTrends(data);

    } catch(e) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('noTrendsMsg').textContent    = 'Error loading trends. Make sure Flask is running.';
        document.getElementById('noTrends').style.display     = 'block';
    }
}

function renderTrends(data) {
    const lng    = data.longitudinal;
    const params = lng.parameters || {};
    const scores = lng.scores_over_time || [];
    const dates  = lng.report_dates || [];

    // Summary bar
    document.getElementById('summaryTitle').textContent = `${data.patient_name} — ${data.total_reports} Reports`;
    document.getElementById('summarySub').textContent   = `${lng.date_range?.from} → ${lng.date_range?.to}`;

    const overall = lng.overall_trend || 'stable';
    const badge   = document.getElementById('overallBadge');
    const cls     = overall==='improving'?'ob-improving':overall==='worsening'?'ob-worsening':'ob-stable';
    const label   = overall==='improving'?'↑ Overall Improving':overall==='worsening'?'↓ Overall Worsening':'→ Stable';
    badge.innerHTML = `<span class="overall-badge ${cls}">${label}</span>`;

    // Score line chart
    if (scoreLineChart) scoreLineChart.destroy();
    const sCtx = document.getElementById('scoreLineChart').getContext('2d');
    scoreLineChart = new Chart(sCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Health Score',
                data:  scores,
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0,212,170,0.08)',
                borderWidth: 2.5,
                pointBackgroundColor: '#00d4aa',
                pointRadius: 5,
                tension: 0.35,
                fill: true
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend:{display:false}, tooltip:{ backgroundColor:'#111827', borderColor:'rgba(255,255,255,0.1)', borderWidth:1 } },
            scales: {
                x: { ticks:{color:'#8892a4',font:{size:11}}, grid:{color:'rgba(255,255,255,0.04)'} },
                y: { min:0, max:100, ticks:{color:'#8892a4',font:{size:11}}, grid:{color:'rgba(255,255,255,0.04)'} }
            }
        }
    });

    // Parameter trend cards
    const grid = document.getElementById('paramsGrid');
    grid.innerHTML = '';
    Object.values(paramCharts).forEach(c => c.destroy());

    Object.entries(params).forEach(([key, p], i) => {
        const card = document.createElement('div');
        card.className = `param-card ${p.trend==='stable_normal'?'improving':p.trend}`;
        card.style.animationDelay = (i*0.05)+'s';
        card.style.animation = 'fadeUp 0.4s ease both';

        const changeStr = p.change_from_first >= 0 ? `+${p.change_from_first}` : `${p.change_from_first}`;
        const pctStr    = p.change_pct >= 0 ? `+${p.change_pct}%` : `${p.change_pct}%`;
        const badgeCls  = p.trend==='improving'||p.trend==='stable_normal' ? 'badge-improving' : p.trend==='worsening' ? 'badge-worsening' : 'badge-stable';

        card.innerHTML = `
          <div class="param-top">
            <div class="param-name">${p.display_name}</div>
            <span class="badge ${badgeCls}">${p.trend_label}</span>
          </div>
          <div class="param-chart-wrap"><canvas id="pc_${key}"></canvas></div>
          <div class="param-meta">
            <span>First: ${p.first} ${p.unit}</span>
            <span>Latest: ${p.latest} ${p.unit}</span>
            <span style="color:${p.change_from_first>=0?'var(--warn)':'var(--green)'}">${changeStr} (${pctStr})</span>
          </div>`;

        grid.appendChild(card);

        // Draw mini sparkline
        requestAnimationFrame(() => {
            const ctx    = document.getElementById(`pc_${key}`)?.getContext('2d');
            if (!ctx) return;
            const color  = p.trend==='improving'||p.trend==='stable_normal' ? '#00d4aa' : p.trend==='worsening' ? '#ff4d6d' : '#ffb347';
            paramCharts[key] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: p.dates,
                    datasets: [{
                        data: p.values,
                        borderColor: color,
                        backgroundColor: color+'18',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: color,
                        tension: 0.35,
                        fill: true
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend:{display:false}, tooltip:{ backgroundColor:'#111827', borderColor:'rgba(255,255,255,0.1)', borderWidth:1 } },
                    scales: {
                        x: { ticks:{color:'#8892a4',font:{size:9},maxRotation:0}, grid:{display:false} },
                        y: { ticks:{color:'#8892a4',font:{size:9},maxTicksLimit:4}, grid:{color:'rgba(255,255,255,0.04)'} }
                    }
                }
            });
        });
    });

    document.getElementById('trendsContent').style.display = 'block';
}

// Auto-load if user is logged in
window.addEventListener('DOMContentLoaded', () => {
    if (user) loadTrends();
});