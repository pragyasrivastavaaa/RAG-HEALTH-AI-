const user = getUser();
if (user) renderNavUser();

async function loadHistory() {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const grid = document.getElementById('reportsGrid');

    try {
        let reports = [];
        if (user) {
            const res = await apiFetch('/reports');
            if (!res) {
                loadingState.innerHTML = `<p style="color:var(--red)">Failed to load reports. Make sure Flask is running.</p>`;
                return;
            }
            const data = await res.json();
            reports = data.reports || [];
        } else {
            const historyItems = JSON.parse(localStorage.getItem('rag_history') || '[]');
            reports = historyItems.map(item => ({
                id: item.id,
                filename: item.filename,
                patient_name: item.patient_name,
                uploaded_at: item.uploaded_at,
                health_score: item.health_score
            }));
        }

        loadingState.style.display = 'none';
        if (!reports.length) {
            emptyState.style.display = 'block';
            return;
        }

        grid.innerHTML = '';
        reports.forEach((r, i) => {
            const score = r.health_score ?? null;
            const sc = score === null ? '' : score >= 80 ? 'good' : score >= 55 ? 'warn' : 'bad';
            const scc = score === null ? '' : score >= 80 ? 'score-good' : score >= 55 ? 'score-warn' : 'score-bad';
            const date = new Date(r.uploaded_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
            const card = document.createElement('div');
            card.className = `report-card ${sc}`;
            card.style.animationDelay = `${i * 0.07}s`;
            card.innerHTML = `
                <div class="report-top">
                    <div class="report-icon">📄</div>
                    <div><div class="report-score ${scc}">${score !== null ? score : '—'}</div><div class="report-score-label">/ 100</div></div>
                </div>
                <div class="report-name" title="${r.filename}">${r.filename}</div>
                <div class="report-date">${r.patient_name || 'Unknown patient'} · ${date}</div>
                <div class="report-footer">
                    <span class="report-meta">Report #${r.id}</span>
                    <span style="font-size:0.78rem;color:var(--accent2)">View →</span>
                </div>`;
            card.addEventListener('click', () => loadReport(r.id));
            grid.appendChild(card);
        });
    } catch (e) {
        loadingState.innerHTML = `<p style="color:var(--red)">Failed to load. Make sure Flask is running.</p>`;
    }
}

async function loadReport(reportId) {
    const currentUser = getUser();
    if (!currentUser) {
        const history = JSON.parse(localStorage.getItem('rag_history') || '[]');
        const item = history.find(h => h.id === reportId);
        if (item) {
            localStorage.setItem('rag_result', JSON.stringify(item.result));
            localStorage.setItem('rag_report_id', reportId);
            window.location.href = 'dashboard.html';
            return;
        }
    }

    const res = await apiFetch(`/report/${reportId}`);
    if (!res) return;
    const data = await res.json();
    if (data.error) {
        showToast('Could not load report', 'error');
        return;
    }

    if (!data.interpretation) {
        const ar = await apiFetch(`/analyze/${reportId}`, { method: 'POST' });
        if (!ar) return;
        const ad = await ar.json();
        localStorage.setItem('rag_result', JSON.stringify(ad));
    } else {
        localStorage.setItem('rag_result', JSON.stringify({
            filename: data.filename,
            patient_name: data.patient_name,
            patient_first: data.patient_name?.split(' ')[0] || null,
            health_score: data.health_score,
            findings: data.interpretation,
            conditions: (data.interpretation || []).map(f => f.condition).filter(Boolean).filter((v, i, a) => a.indexOf(v) === i),
            diet_plan: data.diet_plan,
            parameters_found: data.raw_values ? Object.keys(data.raw_values).length : 0,
            rag_analysis: data.rag_analysis || {}
        }));
    }
    localStorage.setItem('rag_report_id', reportId);
    window.location.href = 'dashboard.html';
}

loadHistory();