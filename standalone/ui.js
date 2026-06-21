(function(){
"use strict";
const E = window.AstroEngine;
const $ = id => document.getElementById(id);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const fmt = d => d.toISOString().slice(0,10);

const CITIES={
  "New Delhi, India":[28.6139,77.2090,5.5],"Mumbai, India":[19.0760,72.8777,5.5],
  "Bengaluru, India":[12.9716,77.5946,5.5],"Chennai, India":[13.0827,80.2707,5.5],
  "Kolkata, India":[22.5726,88.3639,5.5],"Hyderabad, India":[17.3850,78.4867,5.5],
  "Pune, India":[18.5204,73.8567,5.5],"London, UK":[51.5074,-0.1278,0.0],
  "New York, USA":[40.7128,-74.0060,-5.0],"Dubai, UAE":[25.2048,55.2708,4.0],
  "Singapore":[1.3521,103.8198,8.0],"Sydney, Australia":[-33.8688,151.2093,11.0]};

document.addEventListener("DOMContentLoaded",function(){
  const sel=$("city");
  Object.keys(CITIES).sort().forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;sel.appendChild(o);});
  $("birthForm").addEventListener("submit",function(e){e.preventDefault();generate();});
});

function generate(){
  const errEl=$("formErr");errEl.textContent="";
  try{
    const name=$("name").value||"Seeker";
    const dob=$("dob").value, tob=$("tob").value;
    if(!dob||!tob)throw new Error("Please enter date and time of birth.");
    const city=$("city").value;
    let lat,lon,tz,place;
    if(city&&CITIES[city]){[lat,lon,tz]=CITIES[city];place=city;}
    else{lat=parseFloat($("lat").value);lon=parseFloat($("lon").value);tz=parseFloat($("tz").value);
      if([lat,lon,tz].some(v=>isNaN(v)))throw new Error("Choose a city, or enter numeric latitude, longitude and timezone.");
      place=lat.toFixed(4)+", "+lon.toFixed(4);}
    const [y,mo,d]=dob.split("-").map(Number);const [h,mi]=tob.split(":").map(Number);
    const birth={name,year:y,month:mo,day:d,hour:h,minute:mi,lat,lon,tz,place};
    const rep=E.buildReport(birth);
    render(rep);
    $("reportArea").style.display="block";
    $("reportArea").scrollIntoView({behavior:"smooth"});
  }catch(ex){errEl.textContent=ex.message||String(ex);}
}

function render(rep){
  const b=rep.birth;
  const kpA=rep.kpCh.ascLordship, parA=rep.parCh.ascLordship;
  $("repHead").innerHTML=
    `<h1>Advice for ${esc(b.name)}</h1>
     <p class="meta">Born ${b.year}-${String(b.month).padStart(2,"0")}-${String(b.day).padStart(2,"0")} at
       ${String(b.hour).padStart(2,"0")}:${String(b.minute).padStart(2,"0")} &middot; ${esc(b.place)} &middot; UTC${b.tz>=0?"+":""}${b.tz}</p>
     <p class="meta"><strong>KP Lagna:</strong> ${kpA.sign} (sub-lord ${kpA.subLord}) &nbsp;|&nbsp;
       <strong>Parashara Lagna:</strong> ${parA.sign}</p>
     <p class="print-only meta">Report generated ${new Date().toISOString().slice(0,10)} &middot; KP (Krishnamurti/Placidus) + Parashara (Lahiri/whole-sign)</p>`;

  $("ovPanel").innerHTML=renderOverview(rep);
  $("eduPanel").innerHTML=renderEducation(rep);
  $("carPanel").innerHTML=renderCareer(rep);
  $("faqPanel").innerHTML=renderFaq(rep);
  $("sbPanel").innerHTML=renderShadbala(rep);
  $("chartPanel").innerHTML=renderCharts(rep);
}

function renderOverview(rep){
  const c=rep.current;
  let h=`<div class="card"><h2>&#9775; Current Vimshottari Dasha (3 levels)</h2>
    <div class="dasha-chips">
      <div class="chip md"><span>Mahadasha</span><b>${c.md||"-"}</b><small>${esc(c.mdPeriod)}</small></div>
      <div class="chip ad"><span>Antardasha</span><b>${c.ad||"-"}</b><small>${esc(c.adPeriod)}</small></div>
      <div class="chip pd"><span>Pratyantardasha</span><b>${c.pd||"-"}</b><small>${esc(c.pdPeriod)}</small></div>
    </div>
    <h3>Upcoming Mahadashas</h3><div class="timeline-bar">`;
  rep.upcoming.forEach(md=>{h+=`<div class="tl-seg"><b>${md.lord}</b><small>${fmt(md.start)} &ndash; ${fmt(md.end)}</small></div>`;});
  h+=`</div></div>`;
  const t=rep.transit;
  h+=`<div class="card"><h2>&#127756; Transit (Gochar) Triggers <small class="muted">as of ${t.asOf}</small></h2>
    <p class="muted">Dashas show what is promised; these slow-planet transits confirm when results mature.</p>
    <div class="transit-grid">`;
  for(const p in t.positions){const tp=t.positions[p];
    h+=`<div class="tr-card"><b>${p}</b><span>${tp.sign}</span><small>${tp.houseFromLagna}H Lagna &middot; ${tp.houseFromMoon}H Moon</small></div>`;}
  h+=`</div><ul class="trigger-list">
    <li><strong>Education:</strong> ${esc(t.educationTrigger)}</li>
    <li><strong>Career:</strong> ${esc(t.careerTrigger)}</li>
    <li><strong>Saturn / Moon:</strong> ${esc(t.sadeSati)}</li>`;
  t.notes.forEach(n=>h+=`<li>${esc(n)}</li>`);
  h+=`</ul></div>`;
  return h;
}

function recoList(items){let h=`<ol class="reco-list">`;const max=items.length?items[0].score:1;
  items.forEach(r=>{h+=`<li><div class="reco-title">${esc(r.title)}</div>
    <div class="reco-meta">drivers: ${esc(r.drivers.join(", "))} &middot; weight ${r.score}</div>
    <div class="bar"><span style="width:${Math.round(r.score/max*100)}%"></span></div></li>`;});
  return h+`</ol>`;}

function vargaBlock(v,summary,kind){if(!v)return "";
  let head=`<div class="vk"><span>Varga Lagna</span><b>${v.ascSign}</b><small>lord ${v.ascLord}</small></div>`;
  if(kind==="career"){head+=`<div class="vk"><span>10th</span><b>${v.focusSign}</b><small>lord ${v.focusLord}</small></div>
    <div class="vk"><span>In 10th</span><b>${v.planetsInFocus.length?esc(v.planetsInFocus.join(", ")):"&mdash;"}</b></div>`;}
  else{head+=`<div class="vk"><span>Mercury</span><b>H${v.keyPlacements.Mercury}</b><small>intellect</small></div>
    <div class="vk"><span>Jupiter</span><b>H${v.keyPlacements.Jupiter}</b><small>wisdom</small></div>`;}
  head+=`<div class="vk"><span>Strength</span><b>${Math.round(v.strength*100)}%</b></div>`;
  let notes=v.notes.map(n=>`<li>${esc(n)}</li>`).join("");
  return `<h3>Divisional chart analysis &mdash; ${v.name}</h3><div class="varga">
    <div class="varga-head">${head}</div>
    ${v.vargottama.length?`<p class="vargottama">&#11088; Vargottama (extra-strong): <strong>${esc(v.vargottama.join(", "))}</strong></p>`:""}
    <p>${esc(summary)}</p><ul class="varga-notes">${notes}</ul>
    <p class="varga-fields">Fields reinforced by this varga: <strong>${esc(v.fieldPlanets.join(", "))}</strong></p></div>`;}

function remedyBlock(rems){if(!rems.length)return "";
  let h=`<h3>Remedial suggestions (upaya)</h3><div class="remedy-list">`;
  rems.forEach(r=>{const m=r.measures;
    h+=`<div class="remedy"><div class="rem-head"><b>${r.planet}</b><span>${esc(r.reason)}</span></div>
      <div class="rem-body">
        <span><em>Deity:</em> ${esc(m.deity)}</span><span><em>Mantra:</em> ${esc(m.mantra)}</span>
        <span><em>Charity:</em> ${esc(m.charity)}</span><span><em>Day:</em> ${esc(m.day)}</span>
        <span><em>Gemstone:</em> ${esc(m.gem)}</span><span><em>Lifestyle:</em> ${esc(m.lifestyle)}</span>
      </div></div>`;});
  return h+`</div><p class="disclaimer">Gemstones should be worn only after consulting a qualified astrologer. Mantra, charity and lifestyle measures are safe for everyone.</p>`;}

function notesCols(left,leftTitle,right,rightTitle,yogas,yogaLabel){
  const li=a=>a.map(n=>`<li>${esc(n)}</li>`).join("");
  return `<div class="two-col"><div><h4>${leftTitle}</h4><ul>${li(left)}</ul></div>
    <div><h4>${rightTitle}</h4><ul>${li(right)}</ul>
    ${yogas&&yogas.length?`<p class="yoga-line">${yogaLabel}: ${esc(yogas.join(", "))}</p>`:""}</div></div>`;}

function sbNotesBlock(notes){if(!notes||!notes.length)return "";
  return `<h3>Planetary strength (Shadbala)</h3><ul class="sb-notes">`+notes.map(n=>`<li>${esc(n)}</li>`).join("")+`</ul>`;}

function renderEducation(rep){const e=rep.education;
  return `<div class="card"><h2>&#127891; Education Guidance</h2>
    <div class="verdict-row">
      <span class="badge ${e.promised?"good":"warn"}">Education promise: ${e.promised?"Strong":"Moderate"}</span>
      <span class="badge ${e.higherEducation?"good":"warn"}">Higher education: ${e.higherEducation?"Likely":"With effort"}</span>
      <span class="badge info">${esc(e.strengthSummary)}</span></div>
    <h3>Recommended streams</h3>${recoList(e.streams)}
    ${notesCols(e.kpNotes,"KP basis",e.parNotes,"Parashara basis",e.yogas,"Education yogas")}
    ${vargaBlock(e.varga,e.vargaSummary,"education")}
    ${sbNotesBlock(e.shadbalaNotes)}
    ${remedyBlock(rep.eduRemedies)}</div>`;}

function renderCareer(rep){const c=rep.career;
  return `<div class="card"><h2>&#128188; Career Guidance</h2>
    <div class="verdict-row"><span class="badge good">${esc(c.earningRating)}</span>
      <span class="badge good">Satisfaction: ${esc(c.satisfactionRating)}</span></div>
    <p class="lean"><strong>Job vs Business:</strong> ${esc(c.jobVsBusiness)}</p>
    <h3>Recommended career fields (earning + satisfaction)</h3>${recoList(c.fields)}
    <div class="two-col"><div><h4>Earning</h4><p class="muted">${esc(c.earningExplanation)}</p></div>
      <div><h4>Satisfaction</h4><p class="muted">${esc(c.satisfactionExplanation)}</p></div></div>
    ${notesCols(c.kpNotes,"KP notes",c.parNotes,"Parashara notes",c.yogas,"Career yogas")}
    ${vargaBlock(c.varga,c.vargaSummary,"career")}
    ${sbNotesBlock(c.shadbalaNotes)}
    ${remedyBlock(rep.careerRemedies)}</div>`;}

function renderShadbala(rep){const sb=rep.shadbala;if(!sb)return "";
  let h=`<div class="card"><h2>&#9878; Shadbala &mdash; Six-fold Planetary Strength</h2>
    <p class="muted">Strength in <em>rupas</em> (a planet needs its required minimum to deliver its promise).
    Ishta = benefic result, Kashta = strained. Motion (speed/direction) feeds Cheshta Bala; declination feeds Ayana Bala.</p>
    <table class="planet-table sb-table"><thead><tr>
      <th>Planet</th><th>Sthana</th><th>Dig</th><th>Kala</th><th>Cheshta</th><th>Naisarg.</th><th>Drik</th>
      <th>Rupas</th><th>Req</th><th>Status</th><th>Result</th><th>Motion</th><th>Decl.</th></tr></thead><tbody>`;
  sb.ranking.forEach(p=>{const s=sb.planets[p];
    h+=`<tr><td>${p}</td><td>${s.sthana}</td><td>${s.dig}</td><td>${s.kala}</td><td>${s.cheshta}</td>
      <td>${s.naisargika}</td><td>${s.drik}</td><td><b>${s.rupas}</b></td><td>${s.required}</td>
      <td class="${s.sufficient?'ok':'low'}">${s.sufficient?'sufficient':'below'}</td>
      <td class="${s.benefic?'ok':'low'}">${s.benefic?'Ishta':'Kashta'}</td>
      <td>${esc(s.motion)}</td><td>${Math.abs(s.declination).toFixed(1)}&deg;${s.declination>=0?'N':'S'}</td></tr>`;});
  return h+`</tbody></table>
    <p class="disclaimer">Computed for the seven classical grahas (Rahu/Ketu have no Shadbala). Browser edition:
    Cheshta uses speed/retrogression and Ayana uses declination; sunrise-based Kala sub-balas may differ slightly from the server build.</p></div>`;}

function renderFaq(rep){let h=`<div class="card"><h2>&#10067; Frequently Asked Questions</h2>
    <p class="muted">Each answer combines the KP promise with the 3-level Vimshottari dasha timing.</p>`;
  rep.faqs.forEach(a=>{
    let tl="";
    if(a.timeline.length){tl=`<table class="tl-table"><thead><tr><th>Dasha (MD-AD-PD)</th><th>From</th><th>To</th><th>Why</th></tr></thead><tbody>`;
      a.timeline.forEach(w=>{tl+=`<tr><td class="chain">${w.chain}</td><td>${fmt(w.start)}</td><td>${fmt(w.end)}</td><td class="why">${esc(w.note)}</td></tr>`;});
      tl+=`</tbody></table>`;}
    else tl=`<p class="muted">No clear dasha window within the look-ahead horizon.</p>`;
    h+=`<details class="faq-item"><summary><span class="q">${esc(a.question)}</span><span class="v">${esc(a.verdict)}</span></summary>
      <div class="faq-body"><p>${esc(a.summary)}</p>${tl}
      <div class="basis"><p><strong>KP:</strong> ${esc(a.kp)}</p><p><strong>Parashara:</strong> ${esc(a.par)}</p></div></div></details>`;});
  return h+`</div>`;}

function planetTable(chart){
  let h=`<table class="planet-table"><thead><tr><th>Planet</th><th>Sign</th><th>Deg</th><th>H</th>
    <th>Nakshatra</th><th>Pada</th><th>Star</th><th>Sub</th><th>D-9</th><th>D-10</th><th>D-24</th></tr></thead><tbody>`;
  E.PLANETS.forEach(n=>{const p=chart.planets[n],L=p.lordship;
    h+=`<tr><td>${n} ${p.retro?"R":""}</td><td>${p.sign}</td><td>${p.degInSign.toFixed(2)}</td><td>${p.house}</td>
      <td>${L.nak}</td><td>${L.pada}</td><td>${L.starLord}</td><td>${L.subLord}</td>
      <td>${E.navamsaSign(p.longitude)}</td><td>${E.dasamsaSign(p.longitude)}</td><td>${E.siddhamsaSign(p.longitude)}</td></tr>`;});
  return h+`</tbody></table>`;}

function renderCharts(rep){
  return `<div class="card"><h2>&#128302; Planetary Positions</h2>
    <div class="chart-tables">
      <div><h3>KP chart (Krishnamurti / Placidus)</h3>${planetTable(rep.kpCh)}</div>
      <div><h3>Parashara chart (Lahiri / whole-sign)</h3>${planetTable(rep.parCh)}</div></div>
    <p class="disclaimer">Browser edition: positions use the astronomy-engine model and match Swiss Ephemeris to ~0.004&deg;.
    Rahu/Ketu use the mean lunar node (may differ slightly from a true-node calculation).</p></div>`;}

window.showTab=function(id,btn){
  document.querySelectorAll(".tab-panel").forEach(p=>p.classList.remove("active"));
  document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
  $(id).classList.add("active");btn.classList.add("active");
};
window.printReport=function(){window.print();};
})();
