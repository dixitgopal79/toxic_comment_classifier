const $ = (s) => document.querySelector(s);
const API = "";
const $$ = (s) => [...document.querySelectorAll(s)];
let lastRequestId = null;

function showView(id){
  $$(".view").forEach(v => v.classList.toggle("active", v.id === id));
  $$(".nav-btn").forEach(b => b.classList.toggle("active", b.dataset.view === id));
  if(id === "dashboard") loadStats();
  if(id === "history") loadHistory("all");
}
$$(".nav-btn").forEach(b => b.addEventListener("click", () => showView(b.dataset.view)));

$("#themeBtn").addEventListener("click", () => document.body.classList.toggle("light"));
$("#comment").addEventListener("input", e => $("#charCount").textContent = `${e.target.value.length} / 5000`);
$$(".examples button").forEach(b => b.addEventListener("click", () => {
  $("#comment").value = b.dataset.example;
  $("#comment").dispatchEvent(new Event("input"));
}));

async function analyze(){
  const text = $("#comment").value.trim();
  if(!text) return showError("Please enter a comment first.");
  $("#error").classList.add("hidden");
  $("#btnText").textContent = "Analyzing...";
  $("#spinner").classList.remove("hidden");
  $("#analyzeBtn").disabled = true;
  try{
    const res = await fetch("/api/predict", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({text})
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || "Prediction failed");
    lastRequestId = data.request_id;
    renderResult(data);
  }catch(err){ showError(err.message); }
  finally{
    $("#btnText").textContent = "Analyze comment";
    $("#spinner").classList.add("hidden");
    $("#analyzeBtn").disabled = false;
  }
}
$("#analyzeBtn").addEventListener("click", analyze);
$("#comment").addEventListener("keydown", e => { if(e.ctrlKey && e.key === "Enter") analyze(); });

function showError(msg){ $("#error").textContent = msg; $("#error").classList.remove("hidden"); }

function renderResult(d){
  $("#emptyResult").classList.add("hidden");
  $("#resultContent").classList.remove("hidden");
  const score = Math.round(d.confidence*100);
  $("#mainConfidence").textContent = score + "%";
  $("#overallText").textContent = d.overall_toxic ? "Toxic signal detected" : "No toxic signal";
  $("#modelVersion").textContent = d.model_version;
  const badge = $("#riskBadge");
  badge.textContent = d.risk_level;
  badge.className = "badge " + d.risk_level.toLowerCase();
  const ring = $(".score-ring");
  ring.style.background = `radial-gradient(circle,var(--card) 56%,transparent 58%),conic-gradient(var(--accent) ${score*3.6}deg,var(--line) ${score*3.6}deg)`;
  const list = $("#labelScores");
  list.innerHTML = Object.entries(d.scores).map(([label, val]) => `
    <div class="label-line">
      <span>${label.replaceAll("_"," ")}</span>
      <div class="bar"><i style="width:${Math.round(val*100)}%"></i></div>
      <b>${Math.round(val*100)}%</b>
    </div>`).join("");
}

async function health(){
  try{
    const d = await (await fetch("/health")).json();
    $("#systemStatus").textContent = d.status === "ok" ? "System operational" : "Model needs attention";
  }catch{ $("#systemStatus").textContent = "Backend unavailable"; }
}
async function loadStats(){
  try{
    const d = await (await fetch("/api/stats")).json();
    if(d.connected === false) throw new Error("MongoDB unavailable");
    $("#mTotal").textContent = d.total_predictions;
    $("#mToxic").textContent = d.toxic_predictions;
    $("#mRate").textContent = d.toxic_rate + "%";
    $("#mFeedback").textContent = d.feedback_accuracy == null ? "—" : d.feedback_accuracy + "%";
    $("#systemPanel").innerHTML = `
      <div class="system-item"><span>Database</span><b>● Connected</b></div>
      <div class="system-item"><span>Predictions stored</span><b>${d.total_predictions}</b></div>
      <div class="system-item"><span>Feedback records</span><b>${d.feedback_count}</b></div>`;
  }catch{
    $("#systemPanel").innerHTML = `<div class="system-item"><span>Database</span><b>● Unavailable</b></div>`;
  }
}
$("#refreshStats").addEventListener("click", loadStats);

async function loadHistory(filter="all"){
  const list = $("#historyList");
  list.innerHTML = `<div class="empty">Loading...</div>`;
  let url = "/api/history?limit=50";
  if(filter === "toxic") url += "&toxic_only=true";
  if(filter === "safe") url += "&toxic_only=false";
  try{
    const res = await fetch(url);
    const rows = await res.json();
    if(!res.ok) throw new Error(rows.detail || "History unavailable");
    if(!rows.length){ list.innerHTML = `<div class="empty">No predictions yet.</div>`; return; }
    list.innerHTML = rows.map(r => `
      <div class="history-row">
        <div class="history-text" title="${escapeHtml(r.text)}">${escapeHtml(r.text)}</div>
        <div class="history-risk">${r.risk_level}</div>
        <div class="history-date">${new Date(r.created_at).toLocaleDateString()}</div>
        <div>${r.overall_toxic ? "⚠ Toxic" : "✓ Safe"}</div>
      </div>`).join("");
  }catch(err){ list.innerHTML = `<div class="empty">${err.message}</div>`; }
}
function escapeHtml(s){ return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }
$$(".filter").forEach(b => b.addEventListener("click", () => {
  $$(".filter").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  loadHistory(b.dataset.filter);
}));
$("#refreshHistory").addEventListener("click", () => loadHistory("all"));

async function feedback(correct){
  if(!lastRequestId) return;
  try{
    await fetch("/api/feedback", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({request_id:lastRequestId, correct, note:"User feedback"})
    });
  }catch{}
}
$("#yesBtn").addEventListener("click", () => feedback(true));
$("#noBtn").addEventListener("click", () => feedback(false));

health();
setInterval(health, 30000);


document.addEventListener("keydown", (event) => {
  if (event.key === "/" && document.activeElement.tagName !== "TEXTAREA" &&
      document.activeElement.tagName !== "INPUT") {
    event.preventDefault();
    $("#comment").focus();
  }
});

async function loadAnalytics(){
  try{
    const d = await (await fetch("/api/analytics")).json();
    if(d.total !== undefined){
      console.log("Analytics", d);
    }
  }catch{}
}
loadAnalytics();
