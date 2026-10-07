"use strict";
/* ============ progres (localStorage) ============ */
const GEO_KEY = "unghiuriProgress";
function getProgress(){
  try { return JSON.parse(localStorage.getItem(GEO_KEY)) || {}; } catch(e){ return {}; }
}
function markDone(id){
  const p = getProgress(); p[id] = true;
  try { localStorage.setItem(GEO_KEY, JSON.stringify(p)); } catch(e){}
}

/* ============ navigare între ecrane ============ */
function show(id){
  document.querySelectorAll(".screen").forEach(s=>s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
  if(window.onShow) window.onShow(id);
  if(id === "screen-end" && window.LESSON_ID) markDone(window.LESSON_ID);
  if(id === "screen-end") adaugaLinkCasa();
  window.scrollTo({top:0});
}
function adaugaLinkCasa(){
  const eb = document.querySelector("#screen-end .end-buttons");
  if(!eb || eb.querySelector(".casa-link")) return;
  const a = document.createElement("a");
  a.href = "../casa/";
  a.className = "btn-primary casa-link";
  a.style.cssText = "background:#35b653;box-shadow:0 4px 0 #1b6b2e;";
  a.textContent = "🏡 Acasă — te așteaptă un cufăr!";
  eb.appendChild(a);
}

/* ============ utilitare canvas ============ */
function canvasPos(cv, ev){
  const r = cv.getBoundingClientRect();
  const t = ev.touches ? ev.touches[0] : ev;
  return { x:(t.clientX-r.left)*cv.width/r.width, y:(t.clientY-r.top)*cv.height/r.height };
}
function clamp(v,a,b){ return Math.max(a, Math.min(b, v)); }
function extendLine(p1,p2,both){
  const dx=p2.x-p1.x, dy=p2.y-p1.y;
  const len=Math.hypot(dx,dy)||1;
  const ux=dx/len, uy=dy/len, L=2000;
  const end={x:p1.x+ux*L, y:p1.y+uy*L};
  const start= both ? {x:p1.x-ux*L, y:p1.y-uy*L} : p1;
  return [start,end];
}
function drawPoint(ctx,p,label,color){
  ctx.beginPath(); ctx.arc(p.x,p.y,10,0,7); ctx.fillStyle=color||"#e05555"; ctx.fill();
  ctx.strokeStyle="rgba(0,0,0,.25)"; ctx.lineWidth=2; ctx.stroke();
  if(label){ ctx.fillStyle="#222"; ctx.font="bold 22px Segoe UI"; ctx.fillText(label,p.x+13,p.y-13); }
}
/* drag generic: getPts() -> obiect {cheie:{x,y}}, onMove(cheie) apelat la mutare */
function enableDrag(cv, getPts, onMove, margin){
  const m = margin===undefined ? 15 : margin;
  let key = null;
  function down(ev){
    const p = canvasPos(cv,ev), pts = getPts();
    for(const k in pts){
      if(Math.hypot(p.x-pts[k].x, p.y-pts[k].y) < 34){ key=k; ev.preventDefault(); return; }
    }
  }
  function move(ev){
    if(!key) return;
    const p = canvasPos(cv,ev), pts = getPts();
    pts[key].x = clamp(p.x,m,cv.width-m);
    pts[key].y = clamp(p.y,m,cv.height-m);
    onMove(key); ev.preventDefault();
  }
  cv.addEventListener("mousedown",down); cv.addEventListener("mousemove",move);
  addEventListener("mouseup",()=>key=null);
  cv.addEventListener("touchstart",down,{passive:false});
  cv.addEventListener("touchmove",move,{passive:false});
  cv.addEventListener("touchend",()=>key=null);
}

/* ============ motor de quiz ============
   Lecția definește: window.questions = [{title, fig(), choices[], correct, hint, explain}] */
let qIndex = 0, qMistakes = 0;
function startQuiz(){ qIndex = 0; show("screen-quiz"); renderQuestion(); }
function renderQuestion(){
  const q = questions[qIndex];
  qMistakes = 0;
  document.getElementById("quiz-progress").innerHTML =
    questions.map((_,i)=>`<span class="${i<qIndex?'done':i===qIndex?'now':''}"></span>`).join("");
  document.getElementById("q-title").textContent = `Întrebarea ${qIndex+1}: ${q.title}`;
  document.getElementById("q-figure").innerHTML = q.fig ? q.fig() : "";
  document.getElementById("q-feedback").innerHTML = "";
  document.getElementById("q-next-wrap").classList.add("hidden");
  document.getElementById("q-choices").innerHTML = q.choices.map((c,i)=>
    `<button class="btn-choice" onclick="answer(${i},this)">${c}</button>`).join("");
}
function answer(i, btn){
  const q = questions[qIndex];
  const fb = document.getElementById("q-feedback");
  if(i === q.correct){
    btn.classList.add("correct");
    document.querySelectorAll("#q-choices button").forEach(b=>b.disabled=true);
    const msgs = ["Bravo! 🎉","Exact! ⭐","Super! 🦊","Corect! 💪"];
    fb.innerHTML = `<div class="feedback good">${msgs[qIndex % msgs.length]} ${q.explain}</div>`;
    document.getElementById("q-next-wrap").classList.remove("hidden");
  } else {
    btn.classList.add("wrong"); btn.disabled = true;
    qMistakes++;
    if(qMistakes === 1){
      fb.innerHTML = `<div class="feedback hint">🤔 Nu-i nimic, mai încearcă! Indiciu: ${q.hint}</div>`;
    } else {
      fb.innerHTML = `<div class="feedback explain">💡 ${q.explain}<br>Apasă acum pe răspunsul corect ca să mergem mai departe.</div>`;
      document.querySelectorAll("#q-choices button").forEach((b,bi)=>{ if(bi!==q.correct) b.disabled=true; });
    }
  }
}
function nextQuestion(){
  qIndex++;
  if(qIndex < questions.length) renderQuestion();
  else show(document.getElementById("screen-challenge") ? "screen-challenge" : "screen-end");
}

/* ============ serie de mini-întrebări (pentru provocări) ============
   items = [{q, fig?, choices[], correct, hint, explain}], onDone() la final */
function startSeries(containerId, items, onDone){
  const el = document.getElementById(containerId);
  let idx = 0, mistakes = 0;
  function render(){
    const it = items[idx];
    mistakes = 0;
    el.innerHTML = `<p style="font-size:1.15rem;font-weight:700;color:#1d4e89;">${idx+1} / ${items.length}: ${it.q}</p>
      ${it.fig||""}
      <div class="sr-choices">${it.choices.map((c,i)=>`<button class="btn-choice" data-i="${i}">${c}</button>`).join("")}</div>
      <div class="sr-fb"></div>`;
    el.querySelectorAll(".sr-choices button").forEach(b=>b.onclick=()=>pick(+b.dataset.i,b));
  }
  function pick(i,btn){
    const it = items[idx], fb = el.querySelector(".sr-fb");
    if(i === it.correct){
      btn.classList.add("correct");
      el.querySelectorAll("button").forEach(b=>b.disabled=true);
      fb.innerHTML = `<div class="feedback good">⭐ ${it.explain}</div>`;
      setTimeout(()=>{ idx++; if(idx<items.length) render(); else onDone(); }, 1400);
    } else {
      btn.classList.add("wrong"); btn.disabled = true;
      mistakes++;
      if(mistakes === 1){
        fb.innerHTML = `<div class="feedback hint">🤔 Indiciu: ${it.hint}</div>`;
      } else {
        fb.innerHTML = `<div class="feedback explain">💡 ${it.explain}<br>Apasă răspunsul corect ca să continuăm.</div>`;
        el.querySelectorAll(".sr-choices button").forEach((b,bi)=>{ if(bi!==it.correct) b.disabled=true; });
      }
    }
  }
  render();
}
