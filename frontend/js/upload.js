// All DOM elements
const dropArea    = document.getElementById('dropArea');
const fileInput   = document.getElementById('fileInput');
const fileSelected= document.getElementById('fileSelected');
const fileNameEl  = document.getElementById('fileName');
const fileSizeEl  = document.getElementById('fileSize');
const fileRemove  = document.getElementById('fileRemove');
const uploadBtn   = document.getElementById('uploadBtn');
const btnText     = document.getElementById('btnText');
const progressWrap= document.getElementById('progressWrap');
const progressFill= document.getElementById('progressFill');
const progressLabel=document.getElementById('progressLabel');

let selectedFile = null;

function fmt(b){ return b<1024?b+' B':b<1048576?(b/1024).toFixed(1)+' KB':(b/1048576).toFixed(1)+' MB'; }

function setFile(f){
    selectedFile=f;
    fileNameEl.textContent=f.name;
    fileSizeEl.textContent=fmt(f.size);
    fileSelected.classList.add('show');
    uploadBtn.disabled=false;
    btnText.textContent='Analyse Report';
}

function clearFile(){
    selectedFile=null; fileInput.value='';
    fileSelected.classList.remove('show');
    uploadBtn.disabled=true;
    btnText.textContent='Select a file to analyse';
}

function setProgress(pct, label){
    progressWrap.classList.add('show');
    progressFill.style.width=pct+'%';
    progressLabel.textContent=label;
}

fileInput.addEventListener('change', ()=>{ if(fileInput.files[0]) setFile(fileInput.files[0]); });
fileRemove.addEventListener('click', (e)=>{ e.stopPropagation(); clearFile(); });
dropArea.addEventListener('dragover',  (e)=>{ e.preventDefault(); dropArea.classList.add('dragging'); });
dropArea.addEventListener('dragleave', ()=>dropArea.classList.remove('dragging'));
dropArea.addEventListener('drop', (e)=>{
    e.preventDefault(); dropArea.classList.remove('dragging');
    if(e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
});

uploadBtn.addEventListener('click', async (event)=>{
    event.preventDefault();
    console.log('Upload button clicked');
    if(!selectedFile) {
        console.log('No file selected — opening file picker');
        fileInput.click();
        return;
    }

    console.log('Starting upload process for file:', selectedFile.name);

    // Test server connectivity first
    try {
        console.log('Testing server connectivity...');
        const testRes = await fetch('http://127.0.0.1:5000/', { method: 'GET' });
        console.log('Server test response:', testRes.status);
        if (!testRes.ok) {
            throw new Error('Flask server not responding. Please start: cd backend && flask run');
        }
    } catch (error) {
        console.error('Server connectivity test failed:', error);
        alert('Cannot connect to server. Please ensure Flask is running:\n\ncd backend\nflask run');
        return;
    }

    uploadBtn.disabled=true;
    btnText.innerHTML='<span class="spinner"></span> Uploading...';
    setProgress(15, 'Uploading file...');

    try{
        // STEP 1: Upload file
        const fd = new FormData();
        fd.append('file', selectedFile);
        console.log('FormData created with file:', selectedFile.name, 'size:', selectedFile.size);

        const token = getToken();
        const uploadHeaders = token ? {'Authorization':'Bearer '+token} : {};

        console.log('Uploading to:', API+'/upload');
        const uploadRes = await fetch(API+'/upload', {
            method: 'POST',
            headers: uploadHeaders,
            body: fd
        });

        console.log('Upload response status:', uploadRes.status);

        if(!uploadRes.ok){
            const e = await uploadRes.json();
            throw new Error(e.error || 'Upload failed: '+uploadRes.status);
        }

        const uploadData = await uploadRes.json();
        const reportId   = uploadData.report_id;
        console.log('Upload OK, report_id:', reportId);

        // STEP 2: Analyze
        setProgress(40, 'Running RAG analysis... (may take 30-60 seconds)');
        btnText.innerHTML='<span class="spinner"></span> Analysing...';

        const analyzeHeaders = token ? {'Authorization':'Bearer '+token} : {};

        console.log('Analyzing report:', reportId);
        const analyzeRes = await fetch(API+'/analyze/'+reportId, {
            method:  'POST',
            headers: analyzeHeaders
        });

        console.log('Analyze response status:', analyzeRes.status);

        if(!analyzeRes.ok){
            const e = await analyzeRes.json();
            throw new Error(e.error || 'Analysis failed: '+analyzeRes.status);
        }

        const result = await analyzeRes.json();
        console.log('Analysis result keys:', Object.keys(result));

        if(result.warning){
            setProgress(100, 'Done');
            alert('No lab values found in this file.\n\nPlease use sample_blood_report.pdf\n(Run: python create_sample_report.py)');
            uploadBtn.disabled=false;
            btnText.textContent='Analyse Report';
            progressWrap.classList.remove('show');
            return;
        }

        // STEP 3: Save and redirect
        setProgress(100, 'Analysis complete!');
        localStorage.setItem('rag_result', JSON.stringify(result));
        localStorage.setItem('rag_report_id', String(reportId));
        saveLocalHistory(reportId, result);

        // Create anonymous session if not logged in
        if (!getToken()) {
            setSession('guest-token', { name: 'Guest', user_id: null });
            console.log('Created anonymous session for dashboard access');
        }
        
        console.log('Saved to localStorage, redirecting to dashboard...');
        setTimeout(()=>{ window.location.href='dashboard.html'; }, 1000);

    }catch(err){
        console.error('Upload/Analyze error:', err);
        alert('Error: '+err.message+'\n\nCheck browser console (F12) for details.\nMake sure Flask is running on port 5000.');
        uploadBtn.disabled=false;
        btnText.textContent='Analyse Report';
        progressWrap.classList.remove('show');
    }
});

function saveLocalHistory(reportId, result) {
    const history = JSON.parse(localStorage.getItem('rag_history') || '[]');
    const existing = history.find(item => item.id === reportId);
    const record = {
        id: reportId,
        filename: result.filename || `Report ${reportId}`,
        patient_name: result.patient_name || null,
        uploaded_at: new Date().toISOString(),
        health_score: result.health_score ?? null,
        result: result
    };
    if (existing) {
        Object.assign(existing, record);
    } else {
        history.unshift(record);
    }
    localStorage.setItem('rag_history', JSON.stringify(history.slice(0, 20)));
}
