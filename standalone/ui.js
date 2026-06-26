(function(){
"use strict";
const E = window.AstroEngine;
const $ = id => document.getElementById(id);
const esc = s => String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const fmt = d => d.toISOString().slice(0,10);

const CITIES={
"New Delhi, India":[28.6139,77.2090,5.5],"Mumbai, India":[19.0760,72.8777,5.5],"Bengaluru, India":[12.9716,77.5946,5.5],
"Chennai, India":[13.0827,80.2707,5.5],"Kolkata, India":[22.5726,88.3639,5.5],"Hyderabad, India":[17.3850,78.4867,5.5],
"Pune, India":[18.5204,73.8567,5.5],"Ahmedabad, India":[23.0225,72.5714,5.5],"Jaipur, India":[26.9124,75.7873,5.5],
"Lucknow, India":[26.8467,80.9462,5.5],"Kanpur, India":[26.4499,80.3319,5.5],"Nagpur, India":[21.1458,79.0882,5.5],
"Indore, India":[22.7196,75.8577,5.5],"Bhopal, India":[23.2599,77.4126,5.5],"Patna, India":[25.5941,85.1376,5.5],
"Surat, India":[21.1702,72.8311,5.5],"Vadodara, India":[22.3072,73.1812,5.5],"Visakhapatnam, India":[17.6868,83.2185,5.5],
"Kochi, India":[9.9312,76.2673,5.5],"Coimbatore, India":[11.0168,76.9558,5.5],"Chandigarh, India":[30.7333,76.7794,5.5],
"Guwahati, India":[26.1445,91.7362,5.5],"Bhubaneswar, India":[20.2961,85.8245,5.5],"Varanasi, India":[25.3176,82.9739,5.5],
"Amritsar, India":[31.6340,74.8723,5.5],"Ludhiana, India":[30.9010,75.8573,5.5],"Nashik, India":[19.9975,73.7898,5.5],
"Rajkot, India":[22.3039,70.8022,5.5],"Dehradun, India":[30.3165,78.0322,5.5],"Thiruvananthapuram, India":[8.5241,76.9366,5.5],
"Karachi, Pakistan":[24.8607,67.0011,5.0],"Lahore, Pakistan":[31.5204,74.3587,5.0],"Islamabad, Pakistan":[33.6844,73.0479,5.0],
"Dhaka, Bangladesh":[23.8103,90.4125,6.0],"Kathmandu, Nepal":[27.7172,85.3240,5.75],"Colombo, Sri Lanka":[6.9271,79.8612,5.5],
"Kabul, Afghanistan":[34.5553,69.2075,4.5],"Dubai, UAE":[25.2048,55.2708,4.0],"Abu Dhabi, UAE":[24.4539,54.3773,4.0],
"Doha, Qatar":[25.2854,51.5310,3.0],"Riyadh, Saudi Arabia":[24.7136,46.6753,3.0],"Kuwait City, Kuwait":[29.3759,47.9774,3.0],
"Muscat, Oman":[23.5880,58.3829,4.0],"Tehran, Iran":[35.6892,51.3890,3.5],"Istanbul, Turkey":[41.0082,28.9784,3.0],
"London, UK":[51.5074,-0.1278,0.0],"Manchester, UK":[53.4808,-2.2426,0.0],"Dublin, Ireland":[53.3498,-6.2603,0.0],
"Paris, France":[48.8566,2.3522,1.0],"Berlin, Germany":[52.5200,13.4050,1.0],"Frankfurt, Germany":[50.1109,8.6821,1.0],
"Madrid, Spain":[40.4168,-3.7038,1.0],"Rome, Italy":[41.9028,12.4964,1.0],"Amsterdam, Netherlands":[52.3676,4.9041,1.0],
"Zurich, Switzerland":[47.3769,8.5417,1.0],"Vienna, Austria":[48.2082,16.3738,1.0],"Stockholm, Sweden":[59.3293,18.0686,1.0],
"Moscow, Russia":[55.7558,37.6173,3.0],"Cairo, Egypt":[30.0444,31.2357,2.0],"Nairobi, Kenya":[-1.2921,36.8219,3.0],
"Lagos, Nigeria":[6.5244,3.3792,1.0],"Johannesburg, South Africa":[-26.2041,28.0473,2.0],"Bangkok, Thailand":[13.7563,100.5018,7.0],
"Singapore":[1.3521,103.8198,8.0],"Kuala Lumpur, Malaysia":[3.1390,101.6869,8.0],"Jakarta, Indonesia":[-6.2088,106.8456,7.0],
"Manila, Philippines":[14.5995,120.9842,8.0],"Hong Kong":[22.3193,114.1694,8.0],"Beijing, China":[39.9042,116.4074,8.0],
"Shanghai, China":[31.2304,121.4737,8.0],"Tokyo, Japan":[35.6762,139.6503,9.0],"Seoul, South Korea":[37.5665,126.9780,9.0],
"Sydney, Australia":[-33.8688,151.2093,10.0],"Melbourne, Australia":[-37.8136,144.9631,10.0],"Perth, Australia":[-31.9505,115.8605,8.0],
"Auckland, New Zealand":[-36.8485,174.7633,12.0],"New York, USA":[40.7128,-74.0060,-5.0],"Boston, USA":[42.3601,-71.0589,-5.0],
"Washington DC, USA":[38.9072,-77.0369,-5.0],"Chicago, USA":[41.8781,-87.6298,-6.0],"Houston, USA":[29.7604,-95.3698,-6.0],
"Denver, USA":[39.7392,-104.9903,-7.0],"Los Angeles, USA":[34.0522,-118.2437,-8.0],"San Francisco, USA":[37.7749,-122.4194,-8.0],
"Seattle, USA":[47.6062,-122.3321,-8.0],"Toronto, Canada":[43.6532,-79.3832,-5.0],"Vancouver, Canada":[49.2827,-123.1207,-8.0],
"Mexico City, Mexico":[19.4326,-99.1332,-6.0],"Sao Paulo, Brazil":[-23.5505,-46.6333,-3.0],"Buenos Aires, Argentina":[-34.6037,-58.3816,-3.0],
"Santiago, Chile":[-33.4489,-70.6693,-4.0]};

document.addEventListener("DOMContentLoaded",function(){
  setupCitySearch();
  $("birthForm").addEventListener("submit",function(e){e.preventDefault();generate();});
  // Re-derive the timezone offset if the birth date changes after a city pick.
  $("dob").addEventListener("change",function(){
    if(window._selZone){const o=tzOffsetForBirth(window._selZone);if(o!=null)$("tz").value=o;}
  });
  // Show usage counter on load.
  try{updateCounter(parseInt(localStorage.getItem("astro_usage_count")||"0",10));}catch(e){}
});

function updateCounter(n){
  const el=$("usageCounter");
  if(el) el.innerHTML='<span class="counter-icon">&#9889;</span> Charts generated: <strong>'+n+'</strong>';
}

// ---- worldwide city typeahead (Open-Meteo geocoding) ----------------------
var _cityTimer=null;
function setupCitySearch(){
  const inp=$("city"), box=$("cityResults");
  inp.addEventListener("input",function(){
    window._selZone=null;
    const q=inp.value.trim();
    clearTimeout(_cityTimer);
    if(q.length<2){box.style.display="none";box.innerHTML="";return;}
    _cityTimer=setTimeout(()=>searchCities(q,inp,box),250);
  });
  document.addEventListener("click",function(e){
    if(e.target!==inp && !box.contains(e.target)){box.style.display="none";}
  });
}
function _cityLabel(c){return [c.name,c.admin1,c.country].filter(Boolean).join(", ");}
function _renderCities(list,inp,box){
  if(!list.length){box.innerHTML='<div class="city-empty">No matches &mdash; try another spelling or enter coordinates.</div>';box.style.display="block";return;}
  box.innerHTML=list.map((c,i)=>`<div class="city-opt" data-i="${i}">${esc(_cityLabel(c))}</div>`).join("");
  box.style.display="block";
  box.querySelectorAll(".city-opt").forEach(el=>el.addEventListener("click",()=>pickCity(list[+el.dataset.i],inp,box)));
}
function searchCities(q,inp,box){
  box.innerHTML='<div class="city-empty">Searching&hellip;</div>';box.style.display="block";
  fetch("https://geocoding-api.open-meteo.com/v1/search?count=8&language=en&format=json&name="+encodeURIComponent(q))
    .then(r=>r.json())
    .then(d=>_renderCities((d&&d.results)||[],inp,box))
    .catch(()=>{
      // Offline / API failure: fall back to the built-in list.
      const ql=q.toLowerCase();
      const local=Object.keys(CITIES).filter(k=>k.toLowerCase().includes(ql))
        .map(k=>({name:k,latitude:CITIES[k][0],longitude:CITIES[k][1],_off:CITIES[k][2]}));
      _renderCities(local,inp,box);
    });
}
function pickCity(c,inp,box){
  inp.value=c._off!==undefined?c.name:_cityLabel(c);
  box.style.display="none";
  $("lat").value=(+c.latitude).toFixed(4);
  $("lon").value=(+c.longitude).toFixed(4);
  if(c.timezone){window._selZone=c.timezone;const o=tzOffsetForBirth(c.timezone);if(o!=null)$("tz").value=o;}
  else if(c._off!==undefined){window._selZone=null;$("tz").value=c._off;}
}
function tzOffsetForBirth(timeZone){
  try{
    const dob=$("dob").value||"2000-01-01", tob=$("tob").value||"12:00";
    const [y,mo,d]=dob.split("-").map(Number), [h,mi]=tob.split(":").map(Number);
    const inst=new Date(Date.UTC(y,mo-1,d,h,mi));
    const dtf=new Intl.DateTimeFormat("en-US",{timeZone,hour12:false,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit"});
    const p=dtf.formatToParts(inst).reduce((a,x)=>{a[x.type]=x.value;return a;},{});
    const hh=p.hour==="24"?0:+p.hour;
    const asUTC=Date.UTC(+p.year,+p.month-1,+p.day,hh,+p.minute,+p.second);
    return Math.round((asUTC-inst.getTime())/3600000*100)/100;
  }catch(e){return null;}
}

function generate(){
  const errEl=$("formErr");errEl.textContent="";
  // Usage counter (persisted in localStorage).
  try{
    let count=parseInt(localStorage.getItem("astro_usage_count")||"0",10)+1;
    localStorage.setItem("astro_usage_count",String(count));
    updateCounter(count);
  }catch(e){/* localStorage blocked */}
  try{
    const name=$("name").value||"Seeker";
    const dob=$("dob").value, tob=$("tob").value;
    if(!dob||!tob)throw new Error("Please enter date and time of birth.");
    const cityText=$("city").value.trim();
    let lat=parseFloat($("lat").value),lon=parseFloat($("lon").value),tz=parseFloat($("tz").value);
    if([lat,lon,tz].some(v=>isNaN(v)))throw new Error("Search and select your city, or enter numeric latitude, longitude and timezone.");
    const place=cityText||(lat.toFixed(4)+", "+lon.toFixed(4));
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
  $("bestPanel").innerHTML=renderBest(rep);
  $("sbPanel").innerHTML=renderShadbala(rep);
  $("chartPanel").innerHTML=renderCharts(rep);
  $("pdfPanel").innerHTML=renderPdf(rep);
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
  h+=`</div>`;
  // Ishta/Kashta dasha-phala timeline.
  if(rep.phala){
    h+=`<h3>Ishta / Kashta Dasha-Phala Timeline</h3>
      <p class="muted">Which periods are likely benefic vs challenging, from each dasha lord's Ishta/Kashta phala.</p>
      <div class="chart-wrap ribbon-wrap">${ribbonSvg(rep.phala.mahadasha,rep.educationBest,rep.careerBest)}</div>
      <p class="chart-key"><span class="k" style="background:#34c98a"></span> benefic
        <span class="k" style="background:#e8a13a"></span> mixed
        <span class="k" style="background:#e8607a"></span> challenging
        <span class="k" style="background:#5a6ea0"></span> node &nbsp;|&nbsp; marks above = education, below = career windows.</p>
      <table class="tl-table"><thead><tr><th>Mahadasha</th><th>From</th><th>To</th><th>Ishta</th><th>Kashta</th><th>Verdict</th></tr></thead><tbody>`;
    rep.phala.mahadasha.forEach(e=>{const cls=e.verdict.toLowerCase().includes("benefic")?"pg":e.verdict.toLowerCase().includes("challeng")?"pb":"pm";
      h+=`<tr><td class="chain">${e.lord}</td><td>${e.start}</td><td>${e.end}</td><td>${e.ishta!=null?e.ishta:"-"}</td><td>${e.kashta!=null?e.kashta:"-"}</td><td class="${cls}">${esc(e.verdict)}</td></tr>`;});
    h+=`</tbody></table>`;
    if(rep.phala.antardasha.length){
      h+=`<h4>Antardashas within the current Mahadasha</h4><table class="tl-table"><thead><tr><th>Period</th><th>From</th><th>To</th><th>Verdict</th></tr></thead><tbody>`;
      rep.phala.antardasha.forEach(e=>{const cls=e.verdict.toLowerCase().includes("benefic")?"pg":e.verdict.toLowerCase().includes("challeng")?"pb":"pm";
        h+=`<tr><td class="chain">${esc(e.lord)}</td><td>${e.start}</td><td>${e.end}</td><td class="${cls}">${esc(e.verdict)}</td></tr>`;});
      h+=`</tbody></table>`;
    }
  }
  h+=`</div>`;
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

function svgBars(items,maxval,marker){const width=580,rowH=26,labelW=82,valW=46,pad=8;
  const barArea=width-labelW-valW-pad,height=items.length*rowH+8;maxval=maxval||1;
  let s=`<svg viewBox="0 0 ${width} ${height}" class="bar-svg" preserveAspectRatio="xMinYMin meet">`;
  if(marker!=null){const mx=labelW+barArea*Math.min(marker/maxval,1);s+=`<line x1="${mx.toFixed(1)}" y1="2" x2="${mx.toFixed(1)}" y2="${height-6}" class="bar-marker"/>`;}
  items.forEach((it,i)=>{const y=i*rowH+4,w=Math.max(2,barArea*Math.min(it.value/maxval,1));
    s+=`<text x="0" y="${y+15}" class="bar-label">${esc(it.label)}</text><rect x="${labelW}" y="${y+3}" width="${w.toFixed(1)}" height="${rowH-9}" rx="3" fill="${it.color}"/><text x="${(labelW+w+5).toFixed(1)}" y="${y+15}" class="bar-val">${it.value}</text>`;});
  return s+`</svg>`;}
function shadbalaSvg(sb){const items=sb.ranking.map(p=>{const s=sb.planets[p];
  const c=(s.sufficient&&s.benefic)?"#34c98a":s.sufficient?"#e8a13a":"#e8607a";return {label:p,value:s.rupas,color:c};});
  const maxv=Math.max(...sb.ranking.map(p=>sb.planets[p].rupas),1);
  const avgReq=sb.ranking.reduce((a,p)=>a+sb.planets[p].required,0)/sb.ranking.length;
  return svgBars(items,Math.round(maxv+0.5),avgReq);}
function bhavaSvg(bb){const edu=new Set([4,5,9]),car=new Set([2,10,11]);
  const items=bb.ranking.map(h=>{const s=bb.houses[h];const c=edu.has(h)?"#8b7bf0":car.has(h)?"#f4b740":"#5a6ea0";
    return {label:`H${s.house} (${s.lord.slice(0,2)})`,value:s.rupas,color:c};});
  const maxv=Math.max(...bb.ranking.map(h=>bb.houses[h].rupas),1);return svgBars(items,Math.round(maxv+0.5));}
function bestTable(title,rows){let h=`<h3>${esc(title)}</h3>`;
  if(!rows||!rows.length)return h+`<p class="muted">No clear window within the look-ahead horizon.</p>`;
  h+=`<table class="tl-table"><thead><tr><th>Window (MD-AD-PD)</th><th>From</th><th>To</th><th>Age</th><th>Dasha era</th><th>Quality</th></tr></thead><tbody>`;
  rows.forEach(e=>{const age=e.ageStart+(e.ageEnd!==e.ageStart?"&ndash;"+e.ageEnd:"");
    h+=`<tr><td class="chain">${e.chain}</td><td>${e.start}</td><td>${e.end}</td><td>${age} <small class="muted">${esc(e.lifeStage)}</small></td><td>${e.mdLord} &middot; ${esc(e.phala)}</td><td><span class="qual qual-${e.quality.toLowerCase()}">${e.quality}</span></td></tr>`;});
  return h+`</tbody></table>`;}
function renderBest(rep){return `<div class="card"><h2>&#11088; Best Periods &mdash; Dasha Phala &times; KP Windows</h2>
  <p class="muted">Where KP fructification windows (significators active) overlap a benefic Ishta/Kashta dasha era.
  <strong>Prime</strong> = benefic era + active significators; <strong>Favourable</strong> = benefic era; <strong>Workable</strong> = needs extra effort.</p>
  <p class="age-note">Native is currently <strong>${rep.currentAge}</strong> years old (${esc(rep.lifeStage)}).
  Career windows are shown from working age and tagged with the native's age at that time.</p>
  ${bestTable("Education growth",rep.educationBest)}${bestTable("Career growth",rep.careerBest)}</div>`;}

function phalaColor(v){v=(v||"").toLowerCase();
  if(v.includes("strongly benefic"))return "#1f9d6b";if(v.includes("benefic"))return "#34c98a";
  if(v.includes("challeng"))return "#e8607a";if(v.includes("mixed"))return "#e8a13a";return "#5a6ea0";}
function ribbonSvg(maha,eduBest,carBest){if(!maha||!maha.length)return "";
  const ord=s=>Math.floor(new Date(s+"T00:00:00Z").getTime()/86400000);
  const width=600,pad=8,top=34,bandH=30,height=top+bandH+30;
  const t0=ord(maha[0].start),t1=ord(maha[maha.length-1].end),span=Math.max(t1-t0,1);
  const now=Math.floor(Date.now()/86400000);
  const x=t=>pad+(width-2*pad)*(t-t0)/span;
  let s=`<svg viewBox="0 0 ${width} ${height}" class="ribbon-svg" preserveAspectRatio="xMinYMin meet">`;
  maha.forEach(m=>{const x0=x(ord(m.start)),x1=x(ord(m.end)),w=Math.max(x1-x0,1);
    s+=`<rect x="${x0.toFixed(1)}" y="${top}" width="${w.toFixed(1)}" height="${bandH}" fill="${phalaColor(m.verdict)}" stroke="#0f1020" stroke-width="0.5"/>`;
    if(w>26)s+=`<text x="${(x0+w/2).toFixed(1)}" y="${(top+bandH/2+4).toFixed(1)}" text-anchor="middle" class="ribbon-lord">${m.lord}</text>`;});
  const y0=new Date(maha[0].start).getUTCFullYear(),y1=new Date(maha[maha.length-1].end).getUTCFullYear();
  const step=(y1-y0)>12?5:2;let yr=y0-(y0%step);
  while(yr<=y1){const tx=x(ord(yr+"-01-01"));if(tx>=pad&&tx<=width-pad){
    s+=`<line x1="${tx.toFixed(1)}" y1="${top}" x2="${tx.toFixed(1)}" y2="${top+bandH}" stroke="#0f1020" stroke-width="0.5" opacity="0.4"/>`;
    s+=`<text x="${tx.toFixed(1)}" y="${(top+bandH+14).toFixed(1)}" text-anchor="middle" class="ribbon-year">${yr}</text>`;}yr+=step;}
  const qcol={prime:"#34c98a",favourable:"#8b7bf0",workable:"#e8a13a"};
  const marks=(rows,y,h)=>{(rows||[]).forEach(e=>{const mx0=x(ord(e.start)),w=Math.max(x(ord(e.end))-mx0,3);
    s+=`<rect x="${mx0.toFixed(1)}" y="${y}" width="${w.toFixed(1)}" height="${h}" rx="1.5" fill="${qcol[e.quality.toLowerCase()]||"#8b7bf0"}"><title>${esc(e.chain)} (${e.quality})</title></rect>`;});};
  marks(eduBest,top-10,7);marks(carBest,top+bandH+3,7);
  if(t0<=now&&now<=t1){const nx=x(now);
    s+=`<line x1="${nx.toFixed(1)}" y1="${top-12}" x2="${nx.toFixed(1)}" y2="${(top+bandH+12).toFixed(1)}" class="ribbon-now"/>`;
    s+=`<text x="${nx.toFixed(1)}" y="${(top-14).toFixed(1)}" text-anchor="middle" class="ribbon-now-label">now</text>`;}
  return s+`</svg>`;}

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
    ${c.linkedFields&&c.linkedFields.length?`<h3>&#11088; Collective recommendation (Education &times; Career)</h3>
      <p class="muted">Your strongest education stream linked with your strongest career field gives a more specific vocation.</p>
      <ol class="reco-list">`+c.linkedFields.map(l=>`<li><div class="reco-title">${esc(l.title)}</div><div class="reco-meta">${esc(l.educationField)} &nbsp;&times;&nbsp; ${esc(l.careerField)}</div></li>`).join("")+`</ol>`:""}
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
    <div class="chart-wrap">${shadbalaSvg(sb)}</div>
    <p class="chart-key"><span class="k g"></span> sufficient &amp; Ishta <span class="k a"></span> sufficient <span class="k r"></span> below required &nbsp;|&nbsp; dashed line = average required.</p>
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
    <h3>Ishta-Phala ranking (benefic-result potential)</h3>
    <div class="ishta-rank">${(rep.ishtaRank||[]).map((p,i)=>`<span class="ishta-chip">${i+1}. ${p}</span>`).join("")}</div>
    <h3>Bhava Bala &mdash; House Strengths</h3>
    <p class="muted">Strength of each bhava in rupas, led by the Bhavadhipati Bala (Shadbala of the house lord).
    Education houses are 4/5/9; career houses 2/10/11.</p>
    <div class="chart-wrap">${rep.bhavaBala?bhavaSvg(rep.bhavaBala):""}</div>
    <p class="chart-key"><span class="k p"></span> education (4/5/9) <span class="k y"></span> career (2/10/11) <span class="k n"></span> other</p>
    <table class="planet-table sb-table"><thead><tr><th>House</th><th>Lord</th><th>Bhavadhipati</th><th>Occupant</th><th>Aspect</th><th>Rupas</th></tr></thead><tbody>`
    +(rep.bhavaBala?rep.bhavaBala.ranking.map(hh=>{const s=rep.bhavaBala.houses[hh];
      return `<tr><td>House ${s.house}</td><td>${s.lord}</td><td>${s.bhavadhipati}</td><td>${s.occupant}</td><td>${s.drishti}</td><td><b>${s.rupas}</b></td></tr>`;}).join(""):"")
    +`</tbody></table>
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

function renderPdf(rep){
  return `<div class="card"><h2>&#128424; PDF Report</h2>
    <div class="pdf-cta">
      <p>Generate a clean, <strong>vibrantly coloured</strong> PDF of the complete report &mdash;
      every section (Overview &amp; Dasha, Education, Career, FAQ, Best Periods, Shadbala and Charts)
      is included on one printable document.</p>
      <button class="pdf-btn" onclick="printReport()">&#128424; Save / Print as PDF</button>
      <p style="font-size:.82rem;margin-top:14px;">In the print dialog choose <strong>"Save as PDF"</strong>
      and keep <strong>"Background graphics"</strong> enabled so the colours are preserved.</p>
      <div class="pdf-swatches">
        <span style="background:#6a2cf5"></span><span style="background:#9a5cff"></span>
        <span style="background:#ff7ac3"></span><span style="background:#ffc24d"></span>
        <span style="background:#16a34a"></span><span style="background:#f59e0b"></span>
      </div>
    </div></div>`;}

window.showTab=function(id,btn){
  document.querySelectorAll(".tab-panel").forEach(p=>p.classList.remove("active"));
  document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
  $(id).classList.add("active");btn.classList.add("active");
};
window.printReport=function(){window.print();};
})();
