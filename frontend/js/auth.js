const API = 'http://127.0.0.1:5000/api';

function getToken()  { return localStorage.getItem('rag_token'); }
function getUser()   { try{ return JSON.parse(localStorage.getItem('rag_user')); }catch{ return null; } }
function setSession(token, user){ localStorage.setItem('rag_token', token); localStorage.setItem('rag_user', JSON.stringify(user)); }
function clearSession(){ localStorage.removeItem('rag_token'); localStorage.removeItem('rag_user'); localStorage.removeItem('rag_result'); localStorage.removeItem('rag_report_id'); }

function authHeaders(noContentType){
    const t = getToken();
    if(noContentType) return t ? {'Authorization':'Bearer '+t} : {};
    return t ? {'Authorization':'Bearer '+t,'Content-Type':'application/json'} : {'Content-Type':'application/json'};
}

function requireAuth(){
    const t=getToken(), u=getUser();
    if(!t||!u){ window.location.href='login.html'; return null; }
    return u;
}

function renderNavUser(){
    const u=getUser(); if(!u) return;
    const nu=document.getElementById('navUser'), nn=document.getElementById('navUserName');
    if(nu) nu.style.display='flex';
    if(nn) nn.textContent=u.name;
}

async function logout(){
    try{ await fetch(API+'/logout',{method:'POST',headers:authHeaders()}); }catch(e){}
    clearSession();
    window.location.href='login.html';
}

function showToast(msg,type='success'){
    const t=document.getElementById('toast'); if(!t) return;
    t.textContent=msg; t.className='toast '+type+' show';
    setTimeout(()=>t.classList.remove('show'),3200);
}

async function apiFetch(url, options={}){
    const headers = {...authHeaders(), ...(options.headers||{})};
    try{
        const res = await fetch(API+url, {...options, headers});
        if(res.status===401){ clearSession(); window.location.href='login.html'; return null; }
        return res;
    }catch(e){
        console.error('Network error:', e);
        return null;
    }
}