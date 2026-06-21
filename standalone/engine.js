/* =========================================================================
 * Astro Adviser - browser engine (KP + Parashara, Vimshottari, Vargas)
 * Pure JS. Depends on a global `Astronomy` (astronomy-engine).
 * Sidereal positions validated against Swiss Ephemeris to ~0.004 deg.
 * ========================================================================= */
(function (root) {
"use strict";
const Astronomy = root.Astronomy;

// ---- basic math -----------------------------------------------------------
const D2R = Math.PI / 180, R2D = 180 / Math.PI;
const norm360 = x => ((x % 360) + 360) % 360;

// ---- constants ------------------------------------------------------------
const SUN="Sun",MOON="Moon",MARS="Mars",MERCURY="Mercury",JUPITER="Jupiter",
      VENUS="Venus",SATURN="Saturn",RAHU="Rahu",KETU="Ketu";
const PLANETS=[SUN,MOON,MARS,MERCURY,JUPITER,VENUS,SATURN,RAHU,KETU];
const PSHORT={Sun:"Su",Moon:"Mo",Mars:"Ma",Mercury:"Me",Jupiter:"Ju",Venus:"Ve",Saturn:"Sa",Rahu:"Ra",Ketu:"Ke",Ascendant:"Asc"};
const SIGNS=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
const SIGN_LORD={Aries:MARS,Taurus:VENUS,Gemini:MERCURY,Cancer:MOON,Leo:SUN,Virgo:MERCURY,Libra:VENUS,Scorpio:MARS,Sagittarius:JUPITER,Capricorn:SATURN,Aquarius:SATURN,Pisces:JUPITER};
const MOVABLE=new Set(["Aries","Cancer","Libra","Capricorn"]);
const FIXED=new Set(["Taurus","Leo","Scorpio","Aquarius"]);
const NAKSHATRAS=["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"];
const VIM_ORDER=[KETU,VENUS,SUN,MOON,MARS,RAHU,JUPITER,SATURN,MERCURY];
const VIM_YEARS={Ketu:7,Venus:20,Sun:6,Moon:10,Mars:7,Rahu:18,Jupiter:16,Saturn:19,Mercury:17};
const TOTAL_VIM=120, DAYS_PER_YEAR=365.25;
const NAK_LORDS=[]; for(let i=0;i<27;i++) NAK_LORDS.push(VIM_ORDER[i%9]);
const NAK_SPAN=360/27, PADA_SPAN=NAK_SPAN/4;

const EXALT={Sun:["Aries",10],Moon:["Taurus",3],Mars:["Capricorn",28],Mercury:["Virgo",15],Jupiter:["Cancer",5],Venus:["Pisces",27],Saturn:["Libra",20]};
const DEBIL={Sun:"Libra",Moon:"Scorpio",Mars:"Cancer",Mercury:"Pisces",Jupiter:"Capricorn",Venus:"Virgo",Saturn:"Aries"};
const OWN={Sun:["Leo"],Moon:["Cancer"],Mars:["Aries","Scorpio"],Mercury:["Gemini","Virgo"],Jupiter:["Sagittarius","Pisces"],Venus:["Taurus","Libra"],Saturn:["Capricorn","Aquarius"]};
const MOOLA={Sun:"Leo",Moon:"Taurus",Mars:"Aries",Mercury:"Virgo",Jupiter:"Sagittarius",Venus:"Libra",Saturn:"Aquarius"};
const REL={Sun:{Moon:"f",Mars:"f",Jupiter:"f",Mercury:"n",Venus:"e",Saturn:"e"},
  Moon:{Sun:"f",Mercury:"f",Mars:"n",Jupiter:"n",Venus:"n",Saturn:"n"},
  Mars:{Sun:"f",Moon:"f",Jupiter:"f",Venus:"n",Saturn:"n",Mercury:"e"},
  Mercury:{Sun:"f",Venus:"f",Moon:"e",Mars:"n",Jupiter:"n",Saturn:"n"},
  Jupiter:{Sun:"f",Moon:"f",Mars:"f",Saturn:"n",Mercury:"e",Venus:"e"},
  Venus:{Mercury:"f",Saturn:"f",Mars:"n",Jupiter:"n",Sun:"e",Moon:"e"},
  Saturn:{Mercury:"f",Venus:"f",Jupiter:"n",Sun:"e",Moon:"e",Mars:"e"}};

const EDU_POS=[4,5,9,11], EDU_NEG=[3,8,12];
const CAR_POS=[2,6,10,11], CAR_NEG=[5,8,12];
const KENDRA=new Set([1,4,7,10]), TRIKONA=new Set([1,5,9]);

const PLANET_CAREER={
  Sun:["Government / civil services","Administration & leadership","Politics","Medicine (physician)","Power / energy sector","Pharmaceuticals","Public administration"],
  Moon:["Healthcare & nursing","Hospitality","Food & beverages / dairy","Psychology & counselling","Public relations","Marine / shipping","Real estate"],
  Mars:["Engineering (mechanical/civil)","Defence / police / army","Surgery","Sports & athletics","Real estate & construction","Manufacturing","Metallurgy"],
  Mercury:["Information technology & software","Accounting & finance","Writing, editing & journalism","Mathematics & data science","Commerce & trading","Communications & telecom","Teaching","Business analysis"],
  Jupiter:["Teaching & academia","Law & judiciary","Banking & finance","Advisory / consulting","Religion & spirituality","Economics","Publishing","Wealth management"],
  Venus:["Arts, design & fashion","Music, film & entertainment","Luxury & beauty industry","Interior & graphic design","Hospitality & tourism","Diplomacy","Media & advertising"],
  Saturn:["Mining & oil","Agriculture","Manufacturing & heavy industry","Civil & structural work","Logistics & supply chain","Social work","Law enforcement"],
  Rahu:["Aviation & aeronautics","Foreign / overseas assignments","Software & emerging technology","Photography & cinematography","Electronics","Stock markets","Pharma research"],
  Ketu:["Research & investigation","Spirituality & healing","Medicine / alternative medicine","Mathematics","Computing","Forensics","Occult sciences"]};
const PLANET_EDU={
  Sun:["Medicine","Public administration / political science","Management"],
  Moon:["Psychology","Nursing & healthcare","Hotel management","Liberal arts"],
  Mars:["Engineering","Defence studies","Surgery / dentistry","Physical education"],
  Mercury:["Commerce & accountancy","Computer science / IT","Mathematics & statistics","Journalism & mass communication","Business administration"],
  Jupiter:["Law","Economics","Teaching / education","Philosophy","Finance & banking"],
  Venus:["Fine arts & design","Fashion technology","Music / performing arts","Architecture","Media studies"],
  Saturn:["Civil engineering","Geology / mining","Agriculture","Social sciences","Labour / industrial studies"],
  Rahu:["Aeronautical engineering","Computer / data science","Foreign languages","Photography / film","Electronics & communication"],
  Ketu:["Pure sciences & research","Mathematics","Pharmacy","Spiritual / vedic studies","Forensic science"]};
const SIGN_FIELDS={
  Aries:["Engineering","Defence","Sports","Entrepreneurship"],Taurus:["Finance & banking","Arts","Agriculture","Luxury goods"],
  Gemini:["IT & communication","Writing","Trade","Teaching"],Cancer:["Healthcare","Hospitality","Real estate","Public-facing roles"],
  Leo:["Administration","Government","Entertainment","Leadership roles"],Virgo:["Accounting","Analysis","Healthcare","Editing & research"],
  Libra:["Law","Design","Diplomacy","Fashion & beauty"],Scorpio:["Research","Medicine / surgery","Investigation","Defence"],
  Sagittarius:["Teaching","Law","Finance","Travel / philosophy"],Capricorn:["Administration","Engineering","Mining","Long-term enterprise"],
  Aquarius:["Technology & innovation","Social work","Science","Networking roles"],Pisces:["Arts","Spirituality","Pharma / healthcare","Marine / overseas work"]};

const REMEDY_DB={
  Sun:{deity:"Surya / Lord Rama",mantra:"Om Hraam Hreem Hraum Sah Suryaya Namah (Sunday, sunrise)",gem:"Ruby (gold, ring finger) - only if Sun is a functional benefic",charity:"Donate wheat, jaggery or copper on Sundays",day:"Sunday",lifestyle:"Offer water to the rising Sun; respect father and elders."},
  Moon:{deity:"Chandra / Parvati / Shiva",mantra:"Om Shraam Shreem Shraum Sah Chandraya Namah (Monday)",gem:"Natural pearl (silver, little finger)",charity:"Donate rice, milk or white clothes on Mondays",day:"Monday",lifestyle:"Keep a calm routine; respect mother."},
  Mars:{deity:"Hanuman / Kartikeya",mantra:"Om Kraam Kreem Kraum Sah Bhaumaya Namah (Tuesday)",gem:"Red coral (gold/copper, ring finger)",charity:"Donate red lentils or sweets on Tuesdays",day:"Tuesday",lifestyle:"Channel energy through sport; recite Hanuman Chalisa."},
  Mercury:{deity:"Lord Vishnu / Ganesha",mantra:"Om Braam Breem Braum Sah Budhaya Namah (Wednesday)",gem:"Emerald (gold, little finger)",charity:"Donate green gram or green cloth on Wednesdays",day:"Wednesday",lifestyle:"Feed birds; practise writing and study daily."},
  Jupiter:{deity:"Brihaspati / Guru",mantra:"Om Graam Greem Graum Sah Gurave Namah (Thursday)",gem:"Yellow sapphire (gold, index finger)",charity:"Donate turmeric, chana dal or yellow items on Thursdays",day:"Thursday",lifestyle:"Respect teachers; study scriptures; serve the learned."},
  Venus:{deity:"Lakshmi / Shukra",mantra:"Om Draam Dreem Draum Sah Shukraya Namah (Friday)",gem:"Diamond / white sapphire",charity:"Donate white sweets, curd or perfume on Fridays",day:"Friday",lifestyle:"Cultivate art and aesthetics; maintain cleanliness."},
  Saturn:{deity:"Shani / Hanuman",mantra:"Om Praam Preem Praum Sah Shanaye Namah (Saturday)",gem:"Blue sapphire (test first) / amethyst as a safe substitute",charity:"Donate black sesame, mustard oil or serve labourers on Saturdays",day:"Saturday",lifestyle:"Be disciplined and patient; serve the elderly."},
  Rahu:{deity:"Durga / Bhairava",mantra:"Om Bhraam Bhreem Bhraum Sah Rahave Namah",gem:"Hessonite (gomed) - test first",charity:"Donate mustard oil or blankets on Saturdays",day:"Saturday",lifestyle:"Avoid short-cuts; meditate to steady the mind."},
  Ketu:{deity:"Ganesha / Lord Shiva",mantra:"Om Sraam Sreem Sraum Sah Ketave Namah",gem:"Cat's eye (lehsunia) - test first",charity:"Donate multi-coloured cloth or feed dogs",day:"Tuesday",lifestyle:"Practise spirituality and detachment."}};

// ---- ayanamsa -------------------------------------------------------------
function decimalYear(d){const y=d.getUTCFullYear();const s=Date.UTC(y,0,1),n=Date.UTC(y+1,0,1);return y+(d.getTime()-s)/(n-s);}
function lahiri(d){return 23.8569+0.0139552*(decimalYear(d)-2000.0);}
function kpAyan(d){return lahiri(d)-0.0970;}
function obliquity(d){const T=Astronomy.MakeTime(d).tt/36525;return 23.439291-0.0130042*T-0.00000016*T*T+0.000000504*T*T*T;}

// ---- planetary longitudes -------------------------------------------------
function geoEclLon(body,date){
  if(body===SUN) return norm360(Astronomy.SunPosition(date).elon);
  if(body===MOON) return norm360(Astronomy.EclipticGeoMoon(date).lon);
  const vec=Astronomy.GeoVector(Astronomy.Body[body],date,true);
  const rot=Astronomy.Rotation_EQJ_ECT(vec.t);
  const e=Astronomy.RotateVector(rot,vec);
  return norm360(Math.atan2(e.y,e.x)*R2D);
}
function meanNode(d){const T=Astronomy.MakeTime(d).tt/36525;
  let om=125.0445479-1934.1362891*T+0.0020754*T*T+T*T*T/467441-T*T*T*T/60616000;return norm360(om);}
function wrapDiff(a,b){let d=a-b;if(d>180)d-=360;if(d<-180)d+=360;return d;}
function speedOf(body,date){const h=0.5;
  const a=geoEclLon(body,new Date(date.getTime()+h*86400000));
  const b=geoEclLon(body,new Date(date.getTime()-h*86400000));
  return wrapDiff(a,b)/(2*h);}
function geoVec(body,date){
  if(body===SUN) return Astronomy.GeoVector(Astronomy.Body.Sun,date,true);
  if(body===MOON) return Astronomy.GeoVector(Astronomy.Body.Moon,date,true);
  return Astronomy.GeoVector(Astronomy.Body[body],date,true);}
function declOf(body,date){const v=geoVec(body,date);
  const r=Math.sqrt(v.x*v.x+v.y*v.y+v.z*v.z);return Math.asin(v.z/r)*R2D;}
function nodeDecl(lonTropical,date){const eps=obliquity(date);
  return Math.asin(Math.sin(eps*D2R)*Math.sin(lonTropical*D2R))*R2D;}
function isRetro(body,date){if(body===SUN||body===MOON)return false;return speedOf(body,date)<0;}

// ---- lordships ------------------------------------------------------------
function subdivide(offset,length,startLord){
  const si=VIM_ORDER.indexOf(startLord); let cur=0;
  for(let i=0;i<9;i++){const lord=VIM_ORDER[(si+i)%9];
    const pl=length*VIM_YEARS[lord]/TOTAL_VIM;
    if(offset<cur+pl||i===8) return [lord,cur,pl];
    cur+=pl;}
  return [startLord,0,length];
}
function lordships(longitude){
  const lon=norm360(longitude);
  const signIndex=Math.floor(lon/30), sign=SIGNS[signIndex];
  const nakIndex=Math.floor(lon/NAK_SPAN), nak=NAKSHATRAS[nakIndex], starLord=NAK_LORDS[nakIndex];
  const nakOffset=lon-nakIndex*NAK_SPAN, pada=Math.floor(nakOffset/PADA_SPAN)+1;
  const [subLord,subStart,subLen]=subdivide(nakOffset,NAK_SPAN,starLord);
  const [subSubLord]=subdivide(nakOffset-subStart,subLen,subLord);
  return {sign,signLord:SIGN_LORD[sign],nak,nakIndex,pada,starLord,subLord,subSubLord};
}

// ---- vargas ---------------------------------------------------------------
function navamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),dg=lon-si*30,part=Math.floor(dg/(30/9));
  let start; if(si%3===0)start=si; else if(si%3===1)start=(si+8)%12; else start=(si+4)%12;
  return SIGNS[(start+part)%12];}
function dasamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),dg=lon-si*30,part=Math.floor(dg/3);
  const start=(si%2===0)?si:(si+8)%12; return SIGNS[(start+part)%12];}
function siddhamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),dg=lon-si*30,part=Math.floor(dg/(30/24));
  const start=(si%2===0)?SIGNS.indexOf("Leo"):SIGNS.indexOf("Cancer"); return SIGNS[(start+part)%12];}
function horaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),dg=lon-si*30,odd=(si%2===0);
  return odd?(dg<15?"Leo":"Cancer"):(dg<15?"Cancer":"Leo");}
function drekkanaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),part=Math.floor((lon-si*30)/10);
  return SIGNS[(si+part*4)%12];}
function saptamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),part=Math.floor((lon-si*30)/(30/7));
  const start=(si%2===0)?si:(si+6)%12;return SIGNS[(start+part)%12];}
function dwadasamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),part=Math.floor((lon-si*30)/2.5);
  return SIGNS[(si+part)%12];}
const TRIMSA_ODD=[[5,"Aries"],[10,"Aquarius"],[18,"Sagittarius"],[25,"Gemini"],[30,"Libra"]];
const TRIMSA_EVEN=[[5,"Taurus"],[12,"Virgo"],[20,"Pisces"],[25,"Capricorn"],[30,"Scorpio"]];
function trimsamsaSign(lon){lon=norm360(lon);const si=Math.floor(lon/30),dg=lon-si*30;
  const t=(si%2===0)?TRIMSA_ODD:TRIMSA_EVEN;for(const [lim,s] of t)if(dg<lim)return s;return t[t.length-1][1];}
const DIVFN={9:navamsaSign,10:dasamsaSign,24:siddhamsaSign};
const VARGA_NAMES={1:"Rasi (D-1)",9:"Navamsa (D-9)",10:"Dasamsa (D-10)",24:"Chaturvimsamsa (D-24)"};

function buildVarga(chart,division){
  const fn=DIVFN[division];
  const ascSign=fn(chart.ascendant), ai=SIGNS.indexOf(ascSign);
  const planets={};
  for(const n of PLANETS){const s=fn(chart.planets[n].longitude),si=SIGNS.indexOf(s);
    planets[n]={name:n,sign:s,signIndex:si,house:((si-ai)%12+12)%12+1};}
  const houseSigns=[]; for(let i=0;i<12;i++)houseSigns.push(SIGNS[(ai+i)%12]);
  return {division,name:VARGA_NAMES[division],ascSign,ascIndex:ai,planets,houseSigns,
    signOfHouse:h=>houseSigns[h-1], lordOfHouse:h=>SIGN_LORD[houseSigns[h-1]],
    planetsInHouse:h=>PLANETS.filter(n=>planets[n].house===h), houseOfPlanet:n=>planets[n].house};
}
function vargottama(chart){const d9=buildVarga(chart,9);
  return PLANETS.filter(n=>chart.planets[n].sign===d9.planets[n].sign);}

// ---- chart ----------------------------------------------------------------
function placidusCusps(date,latDeg,lonDeg,ayan){
  const gast=Astronomy.SiderealTime(date), ramc=norm360(gast*15+lonDeg);
  const eps=obliquity(date), phi=latDeg*D2R;
  const raToLon=a=>norm360(Math.atan2(Math.sin(a*D2R),Math.cos(a*D2R)*Math.cos(eps*D2R))*R2D);
  const decl=l=>Math.asin(Math.sin(eps*D2R)*Math.sin(l*D2R))*R2D;
  const mc=norm360(Math.atan2(Math.sin(ramc*D2R),Math.cos(ramc*D2R)*Math.cos(eps*D2R))*R2D);
  const asc=norm360(Math.atan2(Math.cos(ramc*D2R),-(Math.sin(ramc*D2R)*Math.cos(eps*D2R)+Math.tan(phi)*Math.sin(eps*D2R)))*R2D);
  function diurnal(frac){let a=ramc+frac*60;for(let i=0;i<30;i++){const d=decl(raToLon(a));let c=-Math.tan(phi)*Math.tan(d*D2R);c=Math.max(-1,Math.min(1,c));a=ramc+frac*Math.acos(c)*R2D;}return norm360(raToLon(a)-ayan);}
  function nocturnal(frac){let a=ramc+120;for(let i=0;i<30;i++){const d=decl(raToLon(a));let c=-Math.tan(phi)*Math.tan(d*D2R);c=Math.max(-1,Math.min(1,c));const NSA=180-Math.acos(c)*R2D;a=ramc+180-frac*NSA;}return norm360(raToLon(a)-ayan);}
  const c={};c[1]=norm360(asc-ayan);c[10]=norm360(mc-ayan);
  c[11]=diurnal(1/3);c[12]=diurnal(2/3);c[2]=nocturnal(2/3);c[3]=nocturnal(1/3);
  c[4]=norm360(c[10]+180);c[5]=norm360(c[11]+180);c[6]=norm360(c[12]+180);
  c[7]=norm360(c[1]+180);c[8]=norm360(c[2]+180);c[9]=norm360(c[3]+180);
  return {cusps:c,asc:norm360(asc-ayan)};
}
function placidusHouse(lon,cuspArr){lon=norm360(lon);
  for(let i=0;i<12;i++){const s=norm360(cuspArr[i]),e=norm360(cuspArr[(i+1)%12]);let span=norm360(e-s);if(span===0)span=360;
    if(norm360(lon-s)<span)return i+1;}return 1;}

function computeChart(ephDate,latDeg,lonDeg,system){
  const ayan=(system==="KP")?kpAyan(ephDate):lahiri(ephDate);
  const planets={};
  for(const n of PLANETS){
    let lon,retro,speed=0,decl=0;
    if(n===KETU){lon=norm360(planets[RAHU].longitude+180);retro=true;speed=planets[RAHU].speed;decl=-planets[RAHU].declination;}
    else if(n===RAHU){const trop=meanNode(ephDate);lon=norm360(trop-ayan);retro=true;speed=0.0;decl=nodeDecl(trop,ephDate);}
    else{lon=norm360(geoEclLon(n,ephDate)-ayan);speed=speedOf(n,ephDate);retro=speed<0;decl=declOf(n,ephDate);}
    const si=Math.floor(lon/30);
    planets[n]={name:n,longitude:lon,sign:SIGNS[si],signIndex:si,degInSign:lon-si*30,retro,speed,declination:decl,lordship:lordships(lon)};
  }
  let ascendant,cusps,houseSigns,mc;
  const gast=Astronomy.SiderealTime(ephDate),ramc=norm360(gast*15+lonDeg),eps=obliquity(ephDate),phi=latDeg*D2R;
  mc=norm360(Math.atan2(Math.sin(ramc*D2R),Math.cos(ramc*D2R)*Math.cos(eps*D2R))*R2D-ayan);
  if(system==="KP"){
    const pl=placidusCusps(ephDate,latDeg,lonDeg,ayan);ascendant=pl.asc;
    const arr=[];for(let h=1;h<=12;h++)arr.push(pl.cusps[h]);
    cusps=[];for(let h=1;h<=12;h++)cusps.push({num:h,longitude:pl.cusps[h],sign:SIGNS[Math.floor(pl.cusps[h]/30)],lordship:lordships(pl.cusps[h])});
    houseSigns=cusps.map(c=>c.sign);
    for(const n of PLANETS)planets[n].house=placidusHouse(planets[n].longitude,arr);
  } else {
    ascendant=norm360(Math.atan2(Math.cos(ramc*D2R),-(Math.sin(ramc*D2R)*Math.cos(eps*D2R)+Math.tan(phi)*Math.sin(eps*D2R)))*R2D-ayan);
    const ai=Math.floor(ascendant/30);
    houseSigns=[];for(let i=0;i<12;i++)houseSigns.push(SIGNS[(ai+i)%12]);
    cusps=[];for(let i=0;i<12;i++){const clon=((ai+i)%12)*30;cusps.push({num:i+1,longitude:clon,sign:houseSigns[i],lordship:lordships(clon)});}
    for(const n of PLANETS)planets[n].house=((planets[n].signIndex-ai)%12+12)%12+1;
  }
  const chart={system,ayanamsa:ayan,ascendant,midheaven:mc,ascLordship:lordships(ascendant),planets,cusps,houseSigns,_ephDate:ephDate,_lat:latDeg,_lon:lonDeg};
  chart.signOfHouse=h=>chart.houseSigns[h-1];
  chart.lordOfHouse=h=>SIGN_LORD[chart.houseSigns[h-1]];
  chart.houseOfSign=s=>chart.houseSigns.indexOf(s)+1;
  chart.planetsInHouse=h=>PLANETS.filter(n=>chart.planets[n].house===h).map(n=>chart.planets[n]);
  return chart;
}

// ---- dasha ----------------------------------------------------------------
const addYears=(date,y)=>new Date(date.getTime()+y*DAYS_PER_YEAR*86400000);
const seqFrom=lord=>{const i=VIM_ORDER.indexOf(lord);const o=[];for(let k=0;k<9;k++)o.push(VIM_ORDER[(i+k)%9]);return o;};
function moonBalance(moonLon){const ni=Math.floor(norm360(moonLon)/NAK_SPAN);const lord=NAK_LORDS[ni];
  const off=norm360(moonLon)-ni*NAK_SPAN;const frac=off/NAK_SPAN;return {lord,frac,balance:VIM_YEARS[lord]*(1-frac)};}
function buildDashaTree(moonLon,birth,spanYears=120){
  const {lord:startLord,balance}=moonBalance(moonLon);
  const fullFirst=VIM_YEARS[startLord];
  let cursor=addYears(birth,-(fullFirst-balance));
  let idx=VIM_ORDER.indexOf(startLord),total=0;const tree=[];
  while(total<spanYears+fullFirst){
    const lord=VIM_ORDER[idx%9],my=VIM_YEARS[lord],mdEnd=addYears(cursor,my);
    const md={lord,level:1,start:cursor,end:mdEnd,children:[]};
    let adCur=cursor;
    for(const adLord of seqFrom(lord)){
      const ay=my*VIM_YEARS[adLord]/TOTAL_VIM,adEnd=addYears(adCur,ay);
      const ad={lord:adLord,level:2,start:adCur,end:adEnd,children:[]};
      let pdCur=adCur;
      for(const pdLord of seqFrom(adLord)){const py=ay*VIM_YEARS[pdLord]/TOTAL_VIM,pdEnd=addYears(pdCur,py);
        ad.children.push({lord:pdLord,level:3,start:pdCur,end:pdEnd});pdCur=pdEnd;}
      md.children.push(ad);adCur=adEnd;
    }
    tree.push(md);cursor=mdEnd;total+=my;idx++;
  }
  return tree;
}
function findRunning(tree,when){let md=null,ad=null,pd=null;
  for(const m of tree){if(m.start<=when&&when<m.end){md=m;for(const a of m.children){if(a.start<=when&&when<a.end){ad=a;for(const p of a.children){if(p.start<=when&&when<p.end){pd=p;break;}}break;}}break;}}
  return {md,ad,pd};}
const fmtDate=d=>d.toISOString().slice(0,10);
function fmtPeriod(md,ad,pd){const parts=[];if(md)parts.push(md.lord);if(ad)parts.push(ad.lord);if(pd)parts.push(pd.lord);
  const last=pd||ad||md;return parts.join("-")+(last?` (${fmtDate(last.start)} to ${fmtDate(last.end)})`:"");}

// ---- KP analysis ----------------------------------------------------------
const NODES=new Set([RAHU,KETU]);
const ownedHouses=(ch,p)=>{const o=[];for(let h=1;h<=12;h++)if(ch.lordOfHouse(h)===p)o.push(h);return o;};
const planetsInStarOf=(ch,lord)=>PLANETS.filter(n=>ch.planets[n].lordship.starLord===lord);
function nodeAgents(ch,node){const p=ch.planets[node];
  const conj=PLANETS.filter(o=>o!==node&&!NODES.has(o)&&ch.planets[o].signIndex===p.signIndex);
  const agents=conj.slice();agents.push(p.lordship.starLord);if(conj.length===0)agents.push(p.lordship.signLord);
  const seen=new Set(),out=[];for(const a of agents)if(!seen.has(a)){seen.add(a);out.push(a);}return out;}
function housesSignifiedBy(ch,planet){const houses=new Set();const p=ch.planets[planet];
  const sl=p.lordship.starLord,slp=ch.planets[sl];houses.add(slp.house);ownedHouses(ch,sl).forEach(h=>houses.add(h));
  houses.add(p.house);ownedHouses(ch,planet).forEach(h=>houses.add(h));
  if(NODES.has(planet))for(const ag of nodeAgents(ch,planet)){houses.add(ch.planets[ag].house);ownedHouses(ch,ag).forEach(h=>houses.add(h));}
  return houses;}
function significatorsOfHouse(ch,house){
  const occ=ch.planetsInHouse(house).map(p=>p.name);const lord=ch.lordOfHouse(house);
  const A=[];for(const o of occ)for(const pl of planetsInStarOf(ch,o))if(!A.includes(pl))A.push(pl);
  const B=occ.slice();const C=planetsInStarOf(ch,lord);const Dd=[lord];
  for(const node of NODES){if(ch.planets[node].house===house&&!B.includes(node))B.push(node);}
  const ordered=[];for(const g of [A,B,C,Dd])for(const pl of g)if(!ordered.includes(pl))ordered.push(pl);
  return {house,A,B,C,D:Dd,ordered};}
function significatorGrades(ch,houses){const score={};for(const h of houses){const s=significatorsOfHouse(ch,h);
  [[4,s.A],[3,s.B],[2,s.C],[1,s.D]].forEach(([g,grp])=>grp.forEach(pl=>{score[pl]=Math.max(score[pl]||0,g);}));}return score;}
function significatorsOfHouses(ch,houses){const sc=significatorGrades(ch,houses);
  return Object.keys(sc).sort((a,b)=>(sc[b]-sc[a])||(PLANETS.indexOf(a)-PLANETS.indexOf(b)));}
const cuspalSubLord=(ch,h)=>ch.cusps[h-1].lordship.subLord;
function strongSignificators(ch,houses,minGrade=3){const g=significatorGrades(ch,houses);
  const strong=new Set(Object.keys(g).filter(p=>g[p]>=minGrade));houses.forEach(h=>strong.add(cuspalSubLord(ch,h)));
  return [...strong].sort((a,b)=>((g[b]||2)-(g[a]||2))||(PLANETS.indexOf(a)-PLANETS.indexOf(b)));}
function analyseCsl(ch,house,pos,neg){const csl=cuspalSubLord(ch,house);const sig=[...housesSignifiedBy(ch,csl)].sort((a,b)=>a-b);
  const posHit=pos.filter(h=>sig.includes(h)),negHit=neg.filter(h=>sig.includes(h));
  const fav=posHit.length>=1&&posHit.length>=negHit.length;
  return {house,subLord:csl,signifies:sig,favorable:fav,
    note:`CSL of house ${house} is ${csl}; it signifies houses [${sig.join(", ")}]. Positive: [${posHit.join(", ")||"none"}]; cautionary: [${negHit.join(", ")||"none"}].`};}
function kpJudgeEducation(ch){const sig=significatorsOfHouses(ch,EDU_POS);
  const f=[analyseCsl(ch,4,EDU_POS,EDU_NEG),analyseCsl(ch,5,EDU_POS,EDU_NEG),analyseCsl(ch,9,[9,11,4,5],[8,12,3]),analyseCsl(ch,11,EDU_POS,EDU_NEG)];
  const promised=f.filter(x=>x.favorable).length>=2;const he=f[2].favorable&&f[3].favorable;
  const fieldPlanets=significatorsOfHouses(ch,[4,5]).slice(0,4);
  const notes=[he?"9th & 11th cuspal sub-lords support higher / specialised education and successful completion.":"Higher-education yoga is moderate; completion may need extra effort or a supportive dasha."];
  return {promised,significators:sig,csl:f,higherEducation:he,fieldPlanets,notes};}
function kpJudgeCareer(ch){const sig=significatorsOfHouses(ch,CAR_POS);
  const f=[analyseCsl(ch,10,CAR_POS,CAR_NEG),analyseCsl(ch,6,[6,10,2,11],[5,12]),analyseCsl(ch,2,[2,6,10,11],[8,12]),analyseCsl(ch,11,CAR_POS,CAR_NEG)];
  const promised=f.filter(x=>x.favorable).length>=2;
  const csl10=housesSignifiedBy(ch,cuspalSubLord(ch,10)),csl6=housesSignifiedBy(ch,cuspalSubLord(ch,6));
  const comb=new Set([...csl10,...csl6]);const job=comb.has(6),biz=comb.has(7);
  let note;if(job&&!biz)note="Service / salaried employment is favoured (strong 6th-house link).";
  else if(biz&&!job)note="Independent business / self-employment is favoured (strong 7th-house link).";
  else if(job&&biz)note="Both service and business are possible; a job first, then independent work, is common.";
  else note="Career mode is mixed; the running dasha will tilt it toward service or enterprise.";
  const earnSig=significatorsOfHouses(ch,[2,11]);const strongEarn=[JUPITER,VENUS,MERCURY].some(p=>earnSig.slice(0,4).includes(p));
  const eleven=analyseCsl(ch,11,[2,6,10,11],[8,12]);
  const earning=(eleven.favorable&&strongEarn)?"Strong":(eleven.favorable||strongEarn)?"Good":"Moderate";
  const fieldPlanets=significatorsOfHouses(ch,[10,6]).slice(0,4);
  return {promised,significators:sig,csl:f,job,biz,earning,fieldPlanets,notes:[note]};}

// ---- Parashara ------------------------------------------------------------
const relation=(p,lord)=>p===lord?"own":((REL[p]||{})[lord]||"n");
function dignityState(p,sign){if(NODES.has(p))return ["Node (acts via dispositor)",0.5];
  const lord=SIGN_LORD[sign];
  if(EXALT[p]&&EXALT[p][0]===sign)return ["Exalted",1.0];
  if(DEBIL[p]===sign)return ["Debilitated",0.1];
  if(MOOLA[p]===sign)return ["Moolatrikona",0.9];
  if(OWN[p]&&OWN[p].includes(sign))return ["Own sign",0.85];
  const r=relation(p,lord);if(r==="f")return ["Friendly sign",0.65];if(r==="e")return ["Enemy sign",0.3];return ["Neutral sign",0.5];}
function dignityOf(ch,p){const [s,sc]=dignityState(p,ch.planets[p].sign);return {planet:p,sign:ch.planets[p].sign,state:s,score:sc,retro:ch.planets[p].retro};}
function allDignities(ch){const d={};for(const p of PLANETS)d[p]=dignityOf(ch,p);return d;}
function lordPlacement(ch,house){const lord=ch.lordOfHouse(house);const p=ch.planets[lord];
  return {house,lord,placedInHouse:p.house,placedInSign:p.sign,dignity:dignityOf(ch,lord).state};}
const conj=(ch,a,b)=>ch.planets[a].house===ch.planets[b].house;
function detectYogas(ch){const y=[];
  if(conj(ch,SUN,MERCURY))y.push({name:"Budha-Aditya Yoga",detail:"Sun and Mercury together sharpen intellect and communication."});
  const diff=((ch.planets[JUPITER].house-ch.planets[MOON].house)%12+12)%12+1;
  if([1,4,7,10].includes(diff))y.push({name:"Gaja-Kesari Yoga",detail:"Jupiter in a kendra from the Moon grants intelligence and repute."});
  const good=new Set([...KENDRA,...TRIKONA,2]);
  if([MERCURY,JUPITER,VENUS].every(x=>good.has(ch.planets[x].house)))y.push({name:"Saraswati Yoga",detail:"Mercury, Jupiter and Venus in supportive houses - learning, arts and eloquence."});
  const maha={Mars:"Ruchaka",Mercury:"Bhadra",Jupiter:"Hamsa",Venus:"Malavya",Saturn:"Sasa"};
  for(const p in maha){const d=dignityOf(ch,p);if(KENDRA.has(ch.planets[p].house)&&["Exalted","Own sign","Moolatrikona"].includes(d.state))
    y.push({name:`${maha[p]} Yoga (Mahapurusha)`,detail:`${p} is strong in a kendra - leadership and success.`});}
  const wl=new Set([ch.lordOfHouse(2),ch.lordOfHouse(11)]);const gh=new Set([...wl].map(l=>ch.planets[l].house));
  if([2,5,9,10,11].some(h=>gh.has(h)))y.push({name:"Dhana Yoga",detail:"Wealth-house lords linked to gain/fortune houses - steady earning."});
  const kl=new Set([...KENDRA].map(h=>ch.lordOfHouse(h))),tl=new Set([...TRIKONA].map(h=>ch.lordOfHouse(h)));
  let raja=false;for(const k of kl)for(const t of tl)if(k!==t&&conj(ch,k,t))raja=true;
  if(raja)y.push({name:"Raja Yoga",detail:"A kendra lord and trikona lord combine - rise in status and success."});
  return y;}
function analyseDasamsa(ch){const d10=buildVarga(ch,10),vg=vargottama(ch);const notes=[];
  const tenthSign=d10.signOfHouse(10),tenthLord=d10.lordOfHouse(10),pit=d10.planetsInHouse(10),ascLord=d10.lordOfHouse(1),pl1=d10.planetsInHouse(1);
  notes.push(`D-10 Lagna is ${d10.ascSign} (lord ${ascLord}); its 10th house is ${tenthSign} (lord ${tenthLord}).`);
  notes.push(pit.length?`Planet(s) in the D-10 10th house: ${pit.join(", ")} - the clearest signature of the profession.`:"No planet in the D-10 10th house; the 10th lord and lagna lord carry the signification.");
  let strong=0;const key={};for(const k of [SUN,SATURN,MERCURY,JUPITER]){key[k]=d10.houseOfPlanet(k);
    const ds=dignityState(k,d10.planets[k].sign)[1];if(ds>=0.65||KENDRA.has(d10.houseOfPlanet(k))||TRIKONA.has(d10.houseOfPlanet(k)))strong++;}
  if(vg.length)notes.push(`Vargottama: ${vg.join(", ")} - particularly reliable results.`);
  const field=[];for(const p of [...pit,tenthLord,ascLord,...pl1])if(!field.includes(p))field.push(p);
  for(const k of [SUN,SATURN,MERCURY,JUPITER])if(vg.includes(k)&&!field.includes(k))field.push(k);
  const strength=Math.round((strong/4*0.6+(pit.length?1:0.5)*0.2+((vg.includes(ascLord)||vg.includes(tenthLord))?0.2:0))*1000)/1000;
  return {division:10,name:"Dasamsa (D-10)",ascSign:d10.ascSign,ascLord,focusHouse:10,focusSign:tenthSign,focusLord:tenthLord,
    planetsInFocus:pit,keyPlacements:key,vargottama:vg,fieldPlanets:field.slice(0,5),strength,notes};}
function analyseSiddhamsa(ch){const d24=buildVarga(ch,24),vg=vargottama(ch);const notes=[];
  const ascLord=d24.lordOfHouse(1);const learners=[];[1,4,5,9].forEach(h=>d24.planetsInHouse(h).forEach(p=>learners.push(p)));
  const meH=d24.houseOfPlanet(MERCURY),juH=d24.houseOfPlanet(JUPITER);
  notes.push(`D-24 Lagna is ${d24.ascSign} (lord ${ascLord}).`);
  notes.push(`In the D-24, Mercury is in house ${meH} and Jupiter in house ${juH} (1/4/5/9/10 strengthen academics).`);
  const uniqLearn=[...new Set(learners)];if(uniqLearn.length)notes.push(`Planet(s) in the D-24 learning houses (1/4/5/9): ${uniqLearn.join(", ")}.`);
  const good=new Set([...KENDRA,...TRIKONA]);let strong=0;
  for(const [k,h] of [[MERCURY,meH],[JUPITER,juH]]){if(good.has(h))strong++;if(dignityState(k,d24.planets[k].sign)[1]>=0.65)strong++;}
  const strength=Math.round((Math.min(strong,4)/4*0.7+Math.min(uniqLearn.length,3)/3*0.3)*1000)/1000;
  const field=[];for(const [k,h] of [[MERCURY,meH],[JUPITER,juH]])if(good.has(h)||h===10)field.push(k);
  if(!field.includes(ascLord))field.push(ascLord);for(const p of uniqLearn)if(!field.includes(p)&&!NODES.has(p))field.push(p);
  return {division:24,name:"Chaturvimsamsa (D-24)",ascSign:d24.ascSign,ascLord,focusHouse:1,focusSign:d24.ascSign,focusLord:ascLord,
    planetsInFocus:uniqLearn,keyPlacements:{Mercury:meH,Jupiter:juH},vargottama:vg,fieldPlanets:field.slice(0,5),strength,notes};}
function parJudgeEducation(ch){const notes=[];const eduLords=[2,4,5,9].map(h=>lordPlacement(ch,h));
  const dig=allDignities(ch);const good=new Set([...KENDRA,...TRIKONA,2,11]);
  if(eduLords.some(lp=>[4,5].includes(lp.house)&&good.has(lp.placedInHouse)))notes.push("Education-house lord(s) occupy supportive houses, giving a stable foundation.");
  const me=dig[MERCURY].score,ju=dig[JUPITER].score;
  if(me>=0.8)notes.push("Mercury (intellect) is strong - quick grasp of logic, numbers and analysis.");else if(me<=0.3)notes.push("Mercury is weak - exams may need extra discipline; Mercury remedies help.");
  if(ju>=0.8)notes.push("Jupiter (wisdom) is strong - favours higher studies, philosophy, teaching, law or finance.");
  const yogas=detectYogas(ch).filter(y=>["Saraswati Yoga","Budha-Aditya Yoga","Gaja-Kesari Yoga"].includes(y.name));
  const d24=analyseSiddhamsa(ch);notes.push(`Education varga D-24 strength is ${d24.strength}; `+d24.notes[1]);
  const lordScore=eduLords.filter(lp=>good.has(lp.placedInHouse)).length/4;
  const score=Math.round(((me+ju)/2*0.4+lordScore*0.25+Math.min(yogas.length,2)*0.075+d24.strength*0.2)*1000)/1000;
  const field=[];for(const c of [MERCURY,JUPITER])if(dig[c].score>=0.6)field.push(c);
  for(const lp of eduLords)if([4,5].includes(lp.house)&&!field.includes(lp.lord))field.push(lp.lord);
  for(const p of d24.fieldPlanets)if(!field.includes(p))field.push(p);
  return {eduLords,karaka:{Mercury:dig[MERCURY].state,Jupiter:dig[JUPITER].state},yogas,score,fieldPlanets:field.slice(0,5),notes,varga:d24};}
function parJudgeCareer(ch){const notes=[];const tenthSign=ch.signOfHouse(10),tenthLord=lordPlacement(ch,10);
  const pit=ch.planetsInHouse(10).map(p=>p.name);const dig=allDignities(ch);
  const d10=analyseDasamsa(ch);let jp=0,bp=0;
  if(MOVABLE.has(tenthSign))jp++;if(FIXED.has(tenthSign))bp++;
  if(pit.includes(SATURN)||pit.includes(SUN))jp++;if(pit.includes(MARS)||pit.includes(MERCURY)||pit.includes(RAHU))bp++;
  if(dig[ch.lordOfHouse(6)].score>=0.6)jp++;if(dig[ch.lordOfHouse(7)].score>=0.6)bp++;
  const lean=jp>bp?"Job / service":bp>jp?"Business / self-employment":"Both (job then independent work)";
  const yogas=detectYogas(ch).filter(y=>["Raja Yoga","Dhana Yoga"].includes(y.name)||y.name.includes("Mahapurusha"));
  const good=new Set([...KENDRA,...TRIKONA,2,11]);const second=lordPlacement(ch,2),eleventh=lordPlacement(ch,11);
  let w=0;w+=good.has(second.placedInHouse)?0.25:0;w+=good.has(eleventh.placedInHouse)?0.25:0;
  w+=0.25*Math.max(dig[JUPITER].score,dig[VENUS].score);w+=detectYogas(ch).some(y=>y.name==="Dhana Yoga")?0.25:0;
  const wealth=Math.round(w*1000)/1000;
  const field=pit.slice();if(!field.includes(tenthLord.lord))field.push(tenthLord.lord);
  const sk=[SUN,SATURN,MERCURY,JUPITER].reduce((a,b)=>dig[b].score>dig[a].score?b:a);if(!field.includes(sk))field.push(sk);
  for(const p of d10.fieldPlanets)if(!field.includes(p))field.push(p);
  notes.push(`The 10th house (${tenthSign}) and its lord ${tenthLord.lord} (in house ${tenthLord.placedInHouse}, ${tenthLord.dignity}) set the professional tone.`);
  if(pit.length)notes.push(`Planet(s) in the 10th: ${pit.join(", ")} - these strongly colour the work.`);
  d10.notes.forEach(n=>notes.push(n));
  return {tenthSign,tenthLord,planetsInTenth:pit,karaka:{Sun:dig[SUN].state,Saturn:dig[SATURN].state,Mercury:dig[MERCURY].state,Jupiter:dig[JUPITER].state},
    yogas,jobLean:lean,wealth,fieldPlanets:field.slice(0,6),notes,varga:d10};}

// ---- Shadbala (six-fold strength) -----------------------------------------
const SB_PLANETS=[SUN,MOON,MARS,MERCURY,JUPITER,VENUS,SATURN];
const NAISARGIKA_SB={Sun:60,Moon:51.43,Venus:42.86,Jupiter:34.29,Mercury:25.71,Mars:17.14,Saturn:8.57};
const REQUIRED_RUPAS={Sun:6.5,Moon:6.0,Mars:5.0,Mercury:7.0,Jupiter:6.5,Venus:5.5,Saturn:5.0};
const MEAN_SPEED={Sun:0.9856,Moon:13.176,Mars:0.524,Mercury:1.383,Jupiter:0.083,Venus:1.602,Saturn:0.0335};
const SAPTAVARGA=[[1,l=>SIGNS[Math.floor(norm360(l)/30)]],[2,horaSign],[3,drekkanaSign],[7,saptamsaSign],[9,navamsaSign],[12,dwadasamsaSign],[30,trimsamsaSign]];
const SAPTA_VIRUPA={moolatrikona:45,own:30,great_friend:22.5,friend:15,neutral:7.5,enemy:3.75,great_enemy:1.875};
const KENDRA_SB=new Set([1,4,7,10]),PANAPHARA_SB=new Set([2,5,8,11]);
const SB_BENEFIC=new Set([JUPITER,VENUS,MERCURY,MOON]);
const WD_LORD=[SUN,MOON,MARS,MERCURY,JUPITER,VENUS,SATURN];
const CHALDEAN=[SATURN,JUPITER,MARS,SUN,VENUS,MERCURY,MOON];
const SPECIAL_ASP={Mars:[4,8],Jupiter:[5,9],Saturn:[3,10]};

function angDist(a,b){let d=Math.abs(norm360(a)-norm360(b))%360;return d<=180?d:360-d;}
function permanentRel(p,lord){if(p===lord)return 2;const r=(REL[p]||{})[lord]||"n";return {f:1,n:0,e:-1}[r];}
function temporaryRel(ch,p,other){const rel=((ch.planets[other].signIndex-ch.planets[p].signIndex)%12+12)%12+1;return [2,3,4,10,11,12].includes(rel)?1:-1;}
function compoundRel(ch,p,lord){if(p===lord)return "own";const s=permanentRel(p,lord)+temporaryRel(ch,p,lord);
  return s>=2?"great_friend":s===1?"friend":s===0?"neutral":s===-1?"enemy":"great_enemy";}
function ucchaBala(planet,lon){if(!EXALT[planet])return 0;const [s,d]=EXALT[planet];
  const ex=SIGNS.indexOf(s)*30+d;return angDist(lon,norm360(ex+180))/3;}
function saptavargajaBala(ch,planet){let t=0;for(const [,fn] of SAPTAVARGA){const sign=fn(ch.planets[planet].longitude);
  if(MOOLA[planet]===sign)t+=SAPTA_VIRUPA.moolatrikona;else t+=SAPTA_VIRUPA[compoundRel(ch,planet,SIGN_LORD[sign])];}return t;}
function ojhayugmaBala(ch,planet){let v=0;const rasiOdd=ch.planets[planet].signIndex%2===0;
  const navOdd=SIGNS.indexOf(navamsaSign(ch.planets[planet].longitude))%2===0;
  const wantOdd=[SUN,MARS,JUPITER,MERCURY,SATURN].includes(planet);
  if(rasiOdd===wantOdd)v+=15;if(navOdd===wantOdd)v+=15;return v;}
function kendradiBala(h){return KENDRA_SB.has(h)?60:PANAPHARA_SB.has(h)?30:15;}
function drekkanaBala(planet,lon){const part=Math.floor((norm360(lon)%30)/10);
  if([SUN,JUPITER,MARS].includes(planet)&&part===0)return 15;
  if([SATURN,MERCURY].includes(planet)&&part===1)return 15;
  if([MOON,VENUS].includes(planet)&&part===2)return 15;return 0;}
function digBala(ch,planet){const asc=ch.ascendant,mc=ch.midheaven,nadir=norm360(mc+180),desc=norm360(asc+180);
  const weak={Sun:nadir,Mars:nadir,Moon:mc,Venus:mc,Jupiter:desc,Mercury:desc,Saturn:asc}[planet];
  return angDist(ch.planets[planet].longitude,weak)/3;}
function ayanaBalaSB(planet,decl){const north=[SUN,MARS,JUPITER,VENUS,MERCURY].includes(planet);
  const delta=north?decl:-decl;return Math.max(0,Math.min(60,1.2766*(23.45+delta)));}
function sunSidereal(date){return norm360(geoEclLon(SUN,date)-lahiri(date));}
function searchRise(start,dir,lat,lon){try{const obs=new Astronomy.Observer(lat,lon,0);
  const ev=Astronomy.SearchRiseSet(Astronomy.Body.Sun,obs,dir,start,2);return ev?ev.date:null;}catch(e){return null;}}
function lastEvent(date,dir,lat,lon){let r=searchRise(new Date(date.getTime()-1.5*86400000),dir,lat,lon),last=null;
  for(let i=0;i<5&&r;i++){if(r<=date)last=r;else break;r=searchRise(new Date(r.getTime()+3600000),dir,lat,lon);}return last;}
function nextEvent(date,dir,lat,lon){return searchRise(date,dir,lat,lon);}

function kalaBala(ch,planet,sunLon,moonLon){
  const date=ch._ephDate,lat=ch._lat,lon=ch._lon;
  // Nathonnatha via Sun hour angle.
  const gst=Astronomy.SiderealTime(date),lst=((gst+lon/15)%24+24)%24;
  const sunVec=geoVec(SUN,date);const raSun=norm360(Math.atan2(sunVec.y,sunVec.x)*R2D);
  // RA from EQJ vector approx; convert using of-date not critical for HA fold.
  let ha=norm360(lst*15-raSun);const haFold=ha<=180?ha:360-ha;
  const dayS=(180-haFold)/3,nightS=haFold/3;
  let nath=planet===MERCURY?60:[SUN,JUPITER,VENUS].includes(planet)?dayS:nightS;
  // Paksha.
  const elong=angDist(moonLon,sunLon);let paksha=SB_BENEFIC.has(planet)?elong/3:(180-elong)/3;
  if(planet===MOON)paksha*=2;
  // Sunrise/sunset for tribhaga + hora.
  let tribhaga=0,hora=0,sr=lastEvent(date,+1,lat,lon),ss=lastEvent(date,-1,lat,lon),nsr=nextEvent(date,+1,lat,lon);
  if(sr&&nsr){
    const isDay=ss&&sr<=date&&date<ss&&ss>sr;
    if(isDay){const third=Math.min(2,Math.floor((date-sr)/((ss-sr)/3)));const ruler=[MERCURY,SUN,SATURN][third];
      if(planet===ruler||planet===JUPITER)tribhaga=60;}
    else{const start=ss&&date>=ss?ss:lastEvent(new Date(date.getTime()-86400000),-1,lat,lon)||ss;
      if(start){const third=Math.min(2,Math.max(0,Math.floor((date-start)/Math.max((nsr-start)/3,1))));const ruler=[MOON,VENUS,MARS][third];
        if(planet===ruler||planet===JUPITER)tribhaga=60;}else if(planet===JUPITER)tribhaga=60;}
    const horaLen=(nsr-sr)/24;let idx=horaLen>0?Math.floor((date-sr)/horaLen):0;idx=Math.max(0,Math.min(23,idx));
    const wd=sr.getUTCDay();const dayLord=WD_LORD[wd];const hl=CHALDEAN[(CHALDEAN.indexOf(dayLord)+idx)%7];
    if(planet===hl)hora=60;
  } else if(planet===JUPITER)tribhaga=60;
  // Vara.
  const wdBirth=(sr&&sr<=date?sr:date).getUTCDay();let vara=planet===WD_LORD[wdBirth]?45:0;
  // Abda / Masa via solar ingress.
  let abda=0,masa=0;const curSign=Math.floor(sunSidereal(date)/30);let j=new Date(date);
  for(let i=0;i<40;i++){if(Math.floor(sunSidereal(j)/30)!==curSign)break;j=new Date(j.getTime()-86400000);}
  const masaLord=WD_LORD[new Date(j.getTime()+86400000).getUTCDay()];if(planet===masaLord)masa=30;
  j=new Date(date);for(let i=0;i<380;i++){if(Math.floor(sunSidereal(j)/30)===0&&Math.floor(sunSidereal(new Date(j.getTime()-86400000))/30)===11)break;j=new Date(j.getTime()-86400000);}
  const abdaLord=WD_LORD[j.getUTCDay()];if(planet===abdaLord)abda=15;
  const ayana=ayanaBalaSB(planet,ch.planets[planet].declination);
  return {nathonnatha:nath,paksha,tribhaga,abda,masa,vara,hora,ayana,yuddha:0,
    total(){return nath+paksha+tribhaga+abda+masa+vara+hora+ayana;}};
}
function cheshtaBala(ch,planet,kala){if(planet===SUN)return kala.ayana;if(planet===MOON)return kala.paksha;
  const p=ch.planets[planet];if(p.retro)return 60;const mean=MEAN_SPEED[planet];const frac=mean?p.speed/mean:1;
  if(frac<=0)return 60;return Math.max(5,Math.min(60,(1.5-frac)/1.5*60));}
function motionState(ch,planet){const p=ch.planets[planet];if(planet===SUN||planet===MOON)return "Direct (luminary)";
  if(p.retro)return "Retrograde (Vakra) - very high motional strength";const frac=Math.abs(p.speed)/MEAN_SPEED[planet];
  if(frac<0.2)return "Near-stationary (Vikala) - strong";if(frac>1.3)return "Fast / direct (Sheeghra)";return "Direct (normal speed)";}
function drikBala(ch,planet){const th=ch.planets[planet].house;let v=0;
  for(const o of SB_PLANETS){if(o===planet)continue;const oh=ch.planets[o].house;const rel=((th-oh)%12+12)%12+1;
    const asp=[7].concat(SPECIAL_ASP[o]||[]);if(asp.includes(rel))v+=SB_BENEFIC.has(o)?15:-15;}return v/4;}
function computeShadbala(ch){const sunLon=ch.planets[SUN].longitude,moonLon=ch.planets[MOON].longitude;const planets={};
  for(const planet of SB_PLANETS){const p=ch.planets[planet];
    const ub=ucchaBala(planet,p.longitude),sv=saptavargajaBala(ch,planet),oj=ojhayugmaBala(ch,planet),kd=kendradiBala(p.house),dk=drekkanaBala(planet,p.longitude);
    const sthana=ub+sv+oj+kd+dk;const dig=digBala(ch,planet);const kala=kalaBala(ch,planet,sunLon,moonLon);
    const ch_=cheshtaBala(ch,planet,kala);const nb=NAISARGIKA_SB[planet];const dr=drikBala(ch,planet);
    const total=sthana+dig+kala.total()+ch_+nb+dr;const rupas=total/60;const required=REQUIRED_RUPAS[planet];
    const ishta=Math.sqrt(Math.max(ub,0)*Math.max(ch_,0)),kashta=Math.sqrt(Math.max(60-ub,0)*Math.max(60-ch_,0));
    const r1=x=>Math.round(x*10)/10;
    planets[planet]={planet,sthana:r1(sthana),dig:r1(dig),kala:r1(kala.total()),cheshta:r1(ch_),naisargika:r1(nb),drik:r1(dr),
      total:r1(total),rupas:Math.round(rupas*100)/100,required,ratio:Math.round(rupas/required*100)/100,sufficient:rupas>=required,
      ishta:r1(ishta),kashta:r1(kashta),benefic:ishta>=kashta,speed:Math.round(p.speed*1e4)/1e4,retrograde:p.retro,
      declination:Math.round(p.declination*100)/100,motion:motionState(ch,planet),
      sub:{uccha:r1(ub),saptavargaja:r1(sv),ojhayugma:r1(oj),kendradi:r1(kd),drekkana:r1(dk),nathonnatha:r1(kala.nathonnatha),
        paksha:r1(kala.paksha),tribhaga:r1(kala.tribhaga),abda:r1(kala.abda),masa:r1(kala.masa),vara:r1(kala.vara),hora:r1(kala.hora),ayana:r1(kala.ayana)}};
  }
  const ranking=Object.keys(planets).sort((a,b)=>planets[b].rupas-planets[a].rupas);
  return {planets,ranking};}
function strengthFactor(sb,planet){const ps=sb.planets[planet];if(!ps)return 1.0;
  let f=0.6+0.6*Math.min(ps.ratio,1.6)/1.6;if(ps.benefic)f+=0.1;if(ps.retrograde)f+=0.05;return Math.round(Math.min(1.4,Math.max(0.6,f))*1000)/1000;}
function statusLine(sb,planet){const ps=sb.planets[planet];if(!ps)return `${planet}: node - Shadbala not applicable.`;
  const dir=ps.declination>=0?"N":"S";
  return `${planet}: Shadbala ${ps.rupas} rupas (${ps.sufficient?"sufficient":"below"} the ${ps.required} required), ${ps.benefic?"Ishta/benefic":"Kashta/strained"}; ${ps.motion}; declination ${Math.abs(ps.declination).toFixed(1)}\u00b0${dir}.`;}

// ---- Bhava Bala (house strengths) + Ishta/Kashta phala -------------------
function bhavaDrishti(ch,house){let v=0;for(const o of SB_PLANETS){const oh=ch.planets[o].house;const rel=((house-oh)%12+12)%12+1;
  if(rel===1)continue;const asp=[7].concat(SPECIAL_ASP[o]||[]);if(asp.includes(rel))v+=SB_BENEFIC.has(o)?20:-20;}return v;}
function computeBhavaBala(ch,sb){const r1=x=>Math.round(x*10)/10;const houses={};
  for(let h=1;h<=12;h++){const lord=ch.lordOfHouse(h);const bhavadhipati=sb.planets[lord]?sb.planets[lord].total:300;
    const occ=0.10*ch.planetsInHouse(h).filter(n=>sb.planets[n]).reduce((a,n)=>a+sb.planets[n].total,0);
    const drishti=bhavaDrishti(ch,h);const total=bhavadhipati+occ+drishti;
    houses[h]={house:h,lord,bhavadhipati:r1(bhavadhipati),occupant:r1(occ),drishti:r1(drishti),total:r1(total),rupas:Math.round(total/60*100)/100};}
  const ranking=Object.keys(houses).map(Number).sort((a,b)=>houses[b].rupas-houses[a].rupas);
  return {houses,ranking,groupStrength:hs=>hs.reduce((a,h)=>a+houses[h].rupas,0)/hs.length};}
function houseStrengthLabel(r){return r>=9?"very strong":r>=7?"strong":r>=5?"moderate":"weak";}
function periodPhala(sb,lord){const ps=sb.planets[lord];if(!ps)return {ishta:null,kashta:null,verdict:"Variable (node - acts via its dispositor)"};
  let v;if(ps.ishta>=ps.kashta&&ps.ishta>=40)v="Strongly benefic";else if(ps.ishta>=ps.kashta)v="Benefic / supportive";
  else if(ps.kashta-ps.ishta>15)v="Challenging";else v="Mixed";return {ishta:ps.ishta,kashta:ps.kashta,verdict:v};}
function ishtaRanking(sb){return Object.keys(sb.planets).sort((a,b)=>sb.planets[b].ishta-sb.planets[a].ishta);}
function dashaPhala(tree,sb,now,count){count=count||7;const maha=[];let curMd=null;
  for(const md of tree){if(md.end<now)continue;const ph=periodPhala(sb,md.lord);
    maha.push({lord:md.lord,start:fmtDate(md.start),end:fmtDate(md.end),ishta:ph.ishta,kashta:ph.kashta,verdict:ph.verdict});
    if(md.start<=now&&now<md.end)curMd=md;if(maha.length>=count)break;}
  const antar=[];if(curMd)for(const ad of curMd.children){if(ad.end<now)continue;const ph=periodPhala(sb,ad.lord);
    antar.push({lord:curMd.lord+"-"+ad.lord,start:fmtDate(ad.start),end:fmtDate(ad.end),ishta:ph.ishta,kashta:ph.kashta,verdict:ph.verdict});}
  return {mahadasha:maha,antardasha:antar};}
function ageYears(birth,d){const m=d.getUTCMonth()+1,day=d.getUTCDate();
  return d.getUTCFullYear()-birth.year-((m<birth.month||(m===birth.month&&day<birth.day))?1:0);}
function lifeStage(a){return a<18?"Student years":a<25?"Early career / entry":a<35?"Career building":a<50?"Career peak":a<60?"Senior / consolidation":"Retirement / advisory";}
function bestPeriods(kpCh,tree,sb,now,domain,birth){const houses=domain==="education"?[4,9,11]:[2,10,11];
  let fromDate=now;
  if(domain==="career"){const ws=new Date(Date.UTC(birth.year+16,birth.month-1,birth.day));if(ws>now)fromDate=ws;}
  const wins=fructificationWindows(kpCh,tree,houses,fromDate,18,6,2);
  return wins.map(w=>{const r=findRunning(tree,w.start);const lord=r.md?r.md.lord:null;
    const ph=lord?periodPhala(sb,lord):{ishta:null,kashta:null,verdict:"-"};
    const benefic=ph.ishta!=null&&ph.ishta>=ph.kashta;const prime=benefic&&ph.verdict.toLowerCase().includes("benefic");
    const a0=ageYears(birth,w.start),a1=ageYears(birth,w.end);
    return {chain:w.chain,start:fmtDate(w.start),end:fmtDate(w.end),mdLord:lord,phala:ph.verdict,
      quality:prime?"Prime":benefic?"Favourable":"Workable",ageStart:a0,ageEnd:a1,lifeStage:lifeStage(a0)};});}

// ---- advice fusion --------------------------------------------------------
function weightedPlanets(sources){const score={};for(const [planets,weight] of sources)
  planets.forEach((p,i)=>{score[p]=(score[p]||0)+weight*(1-0.12*i);});return score;}
function rankFields(scores,mapping,signHint,top=6){const fs={},fd={};
  for(const planet in scores)for(const fld of (mapping[planet]||[])){fs[fld]=(fs[fld]||0)+scores[planet];(fd[fld]=fd[fld]||new Set()).add(PSHORT[planet]||planet);}
  if(signHint)for(const fld of (SIGN_FIELDS[signHint]||[]))for(const ex in fs)if(ex.toLowerCase().includes(fld.split(" ")[0].toLowerCase())){fs[ex]+=0.4;(fd[ex]=fd[ex]||new Set()).add(signHint);}
  return Object.keys(fs).sort((a,b)=>fs[b]-fs[a]).slice(0,top).map(fld=>({title:fld,score:Math.round(fs[fld]*1000)/1000,drivers:[...fd[fld]].sort()}));}
function applyStrength(scores,sb){if(!sb)return scores;const out={};for(const p in scores)out[p]=scores[p]*strengthFactor(sb,p);return out;}
function adviseEducation(kpCh,parCh,sb){const k=kpJudgeEducation(kpCh),p=parJudgeEducation(parCh);
  if(!sb)sb=computeShadbala(parCh);
  const vw=0.6+0.6*(p.varga?p.varga.strength:0);
  let scores=weightedPlanets([[k.fieldPlanets,1.0],[k.significators.slice(0,4),0.6],[p.fieldPlanets,1.0],[p.varga?p.varga.fieldPlanets:[],vw]]);
  scores=applyStrength(scores,sb);
  const streams=rankFields(scores,PLANET_EDU,kpCh.signOfHouse(4));
  const me=sb.planets[MERCURY],ju=sb.planets[JUPITER];
  const karakaRatio=(me&&ju)?(Math.min(me.ratio,1.6)+Math.min(ju.ratio,1.6))/2/1.6:0.5;
  const blended=p.score*0.65+karakaRatio*0.35;
  const strength=blended>=0.7?"Strong - good academic potential":blended>=0.5?"Above average - steady learner":"Moderate - benefits from focus and remedies";
  const keyPlanets=Object.keys(scores).sort((a,b)=>scores[b]-scores[a]).slice(0,4);
  const noteP=[];for(const c of [MERCURY,JUPITER].concat(keyPlanets))if(!noteP.includes(c)&&sb.planets[c])noteP.push(c);
  const sbNotes=noteP.slice(0,4).map(x=>statusLine(sb,x));
  const weak=[MERCURY,JUPITER].filter(x=>sb.planets[x]&&!sb.planets[x].sufficient);
  if(weak.length)sbNotes.push(`Learning karaka(s) ${weak.join(", ")} are below the required Shadbala - remedies and disciplined effort are advised.`);
  let vs="";if(p.varga){const v=p.varga;vs=`D-24 (Chaturvimsamsa), the education varga, has Lagna ${v.ascSign} (lord ${v.ascLord}). Mercury sits in its ${v.keyPlacements.Mercury}th house and Jupiter in the ${v.keyPlacements.Jupiter}th, giving a divisional academic strength of ${v.strength}. `+(v.vargottama.length?`Vargottama: ${v.vargottama.join(", ")}. `:"");}
  return {promised:k.promised,higherEducation:k.higherEducation,streams,strengthSummary:strength,keyPlanets,
    kpNotes:k.notes,parNotes:p.notes,yogas:p.yogas.map(y=>y.name),varga:p.varga,vargaSummary:vs,shadbalaNotes:sbNotes};}
const EARN_MAP={Strong:3,Good:2,Moderate:1};
function satisfaction(parCh,p,fieldPlanets){const dig=allDignities(parCh);
  const fifth=lordPlacement(parCh,5),ninth=lordPlacement(parCh,9);const good=new Set([1,4,5,7,9,10,11]);
  let align=0;if(good.has(fifth.placedInHouse))align++;if(good.has(ninth.placedInHouse))align++;
  const digs=fieldPlanets.slice(0,4).filter(fp=>dig[fp]).map(fp=>dig[fp].score);const avg=digs.length?digs.reduce((a,b)=>a+b,0)/digs.length:0.5;
  const score=align/2*0.5+avg*0.5;
  const rating=score>=0.7?"High - work is likely to feel meaningful":score>=0.5?"Good - reasonable contentment with the right field":"Variable - depends on choosing aligned work";
  const expl=`The 5th lord (${fifth.lord}) sits in house ${fifth.placedInHouse} and the 9th lord (${ninth.lord}) in house ${ninth.placedInHouse}; career-driving planets carry an average dignity of ${Math.round(avg*100)/100}. This points to: ${rating.toLowerCase()}.`;
  return [rating,expl];}
function consensusMode(kpMode,parMode){const kj=kpMode.includes("Job")||kpMode==="Both",kb=kpMode.includes("Business")||kpMode==="Both";
  const pj=parMode.includes("Job")||parMode.includes("Both"),pb=parMode.includes("Business")||parMode.includes("Both");
  const job=kj&&pj,biz=kb&&pb;
  if(job&&!biz)return `Service / salaried job is favoured. (KP: ${kpMode}; Parashara: ${parMode}.)`;
  if(biz&&!job)return `Independent business / self-employment is favoured. (KP: ${kpMode}; Parashara: ${parMode}.)`;
  if(kj&&pb&&!kb)return `KP leans to a job while Parashara leans to business - a salaried start followed by an independent venture. (KP: ${kpMode}; Parashara: ${parMode}.)`;
  if(kb&&pj&&!kj)return `KP leans to business while Parashara leans to a job - structured employment first, enterprise later. (KP: ${kpMode}; Parashara: ${parMode}.)`;
  return `Both job and business are workable; the running dasha decides the emphasis. (KP: ${kpMode}; Parashara: ${parMode}.)`;}
function adviseCareer(kpCh,parCh,sb){const k=kpJudgeCareer(kpCh),p=parJudgeCareer(parCh);
  if(!sb)sb=computeShadbala(parCh);
  const vw=0.7+0.7*(p.varga?p.varga.strength:0);
  let scores=weightedPlanets([[k.fieldPlanets,1.0],[k.significators.slice(0,4),0.6],[p.fieldPlanets,1.1],[p.varga?p.varga.fieldPlanets:[],vw]]);
  scores=applyStrength(scores,sb);
  const fields=rankFields(scores,PLANET_CAREER,parCh.signOfHouse(10));
  const kpEarn=EARN_MAP[k.earning]||1,parEarn=p.wealth>=0.7?3:p.wealth>=0.4?2:1;
  const wealthPlanets=new Set([parCh.lordOfHouse(2),parCh.lordOfHouse(11),JUPITER,VENUS]);
  const wp=[...wealthPlanets].filter(x=>sb.planets[x]).map(x=>sb.planets[x].ratio);
  const wealthStrength=wp.length?wp.reduce((a,b)=>a+b,0)/wp.length:1.0;
  const sbEarn=wealthStrength>=1.15?3:wealthStrength>=0.9?2:1;
  const comb=(kpEarn+parEarn+sbEarn)/3;
  const earning=comb>=2.5?"High earning potential":comb>=1.75?"Good / comfortable earning":"Moderate earning - grows with the right dasha";
  const earnExpl=`KP rates earning capacity as '${k.earning}' (2nd, 11th significators & 11th CSL); Parashara wealth score is ${p.wealth}; the wealth-giving planets average ${Math.round(wealthStrength*100)/100}x their required Shadbala. Together: ${earning.toLowerCase()}.`;
  let [sr,se]=satisfaction(parCh,p,Object.keys(scores));
  const beneficField=Object.keys(scores).slice(0,4).filter(x=>sb.planets[x]&&sb.planets[x].benefic);
  if(beneficField.length>=2&&!sr.startsWith("High"))se+=` The leading career planets (${beneficField.join(", ")}) give Ishta (benefic) results in Shadbala, supporting genuine satisfaction.`;
  const kpMode=(k.job&&!k.biz)?"Job / service":(k.biz&&!k.job)?"Business / self-employment":"Both";
  const jvb=consensusMode(kpMode,p.jobLean);
  const keyPlanets=Object.keys(scores).sort((a,b)=>scores[b]-scores[a]).slice(0,4);
  const tenthLord=parCh.lordOfHouse(10);const noteP=[];
  for(const c of [tenthLord].concat(keyPlanets))if(!noteP.includes(c)&&sb.planets[c])noteP.push(c);
  const sbNotes=noteP.slice(0,4).map(x=>statusLine(sb,x));
  const strongest=sb.ranking[0];
  sbNotes.push(`The strongest planet overall is ${strongest} (${sb.planets[strongest].rupas} rupas); its periods and the fields it governs tend to deliver the best results.`);
  let vs="";if(p.varga){const v=p.varga;const pf=v.planetsInFocus.length?v.planetsInFocus.join(", "):"no planet (10th lord & lagna lord carry it)";
    vs=`D-10 (Dasamsa), the career varga, has Lagna ${v.ascSign} (lord ${v.ascLord}) and a 10th house of ${v.focusSign} (lord ${v.focusLord}). Planets in its 10th: ${pf}. Divisional career strength ${v.strength}. `+(v.vargottama.length?`Vargottama: ${v.vargottama.join(", ")}. `:"");}
  return {promised:k.promised,fields,earningRating:earning,earningExplanation:earnExpl,satisfactionRating:sr,satisfactionExplanation:se,
    jobVsBusiness:jvb,keyPlanets,kpNotes:k.notes,parNotes:p.notes,yogas:p.yogas.map(y=>y.name),varga:p.varga,vargaSummary:vs,shadbalaNotes:sbNotes};}

// ---- FAQ ------------------------------------------------------------------
function fructificationWindows(kpCh,tree,houses,fromDate,horizonYears=25,maxWin=4,requireLevels=2){
  const sig=new Set(strongSignificators(kpCh,houses));
  const endDate=new Date(fromDate.getTime()+horizonYears*365.25*86400000);const wins=[];
  for(const md of tree){if(md.end<fromDate||md.start>endDate)continue;const ms=sig.has(md.lord);
    for(const ad of md.children){if(ad.end<fromDate||ad.start>endDate)continue;const as=sig.has(ad.lord);
      for(const pd of ad.children){if(pd.end<fromDate||pd.start>endDate)continue;const ps=sig.has(pd.lord);
        const c=ms+as+ps;if(c<requireLevels)continue;
        const q=c===3?"a precise, strongly favourable window":"a favourable window";
        wins.push({chain:`${md.lord}-${ad.lord}-${pd.lord}`,start:new Date(Math.max(pd.start.getTime(),fromDate.getTime())),end:pd.end,
          note:`Dasha of ${md.lord} (major), ${ad.lord} (sub) and ${pd.lord} (sub-sub): ${c} of 3 running lords are significators of houses [${houses.join(", ")}] - ${q}.`});
        if(wins.length>=maxWin)return wins;}}}
  return wins;}
const daysAgo=(now,d)=>new Date(now.getTime()-d*86400000);
function buildFaqs(kpCh,parCh,tree,now){
  const out=[];
  const ke=kpJudgeEducation(kpCh),pe=parJudgeEducation(parCh),kc=kpJudgeCareer(kpCh);
  const verdictFrom=(prom,str)=>prom&&str>=0.6?"Yes - clearly supported":prom?"Likely - supported with effort":str>=0.6?"Possible - timing & effort matter":"Challenging - needs remedies and effort";
  // higher education
  out.push({question:"Will I pursue / complete higher education?",verdict:verdictFrom(ke.higherEducation,pe.score),
    summary:"Higher education is read from the 4th (schooling), 9th (higher learning) and 11th (fulfilment). "+(ke.higherEducation?"The chart supports advanced study.":"Moderate support; persistence is key."),
    timeline:fructificationWindows(kpCh,tree,[4,9,11],daysAgo(now,365*8),20),kp:ke.csl[2].note,
    par:`Jupiter is ${pe.karaka.Jupiter}, Mercury is ${pe.karaka.Mercury}; education strength score ${pe.score}.`});
  out.push({question:"When is the most favourable time for my education?",verdict:"Timing windows below",
    summary:"Study flourishes when the dasha lords signify the 4th, 5th and 11th houses.",
    timeline:fructificationWindows(kpCh,tree,[4,5,11],daysAgo(now,365*10),22),kp:"Dashas of the strong significators of houses 4, 5 and 11.",par:"Cross-check with Mercury / Jupiter sub-periods."});
  out.push({question:"Will I study abroad?",verdict:(housesSignifiedBy(kpCh,cuspalSubLord(kpCh,9)).has(12))?"Likely":"Only with a strong foreign dasha",
    summary:"Foreign education needs the 9th (higher study, distant places) linked to the 12th (foreign residence).",
    timeline:fructificationWindows(kpCh,tree,[9,12],daysAgo(now,365*5),18),kp:analyseCsl(kpCh,9,[9,12,3],[4,8]).note,par:"Rahu connected to 9/12 strongly supports overseas study."});
  out.push({question:"Will I clear competitive exams / get selected?",verdict:analyseCsl(kpCh,6,[6,10,11],[8,12]).favorable?"Yes during the windows below":"Competitive; choose the windows",
    summary:"Winning competition is shown by the 6th (defeating rivals) with the 10th/11th (success and reward).",
    timeline:fructificationWindows(kpCh,tree,[6,10,11],daysAgo(now,365*3),15),kp:analyseCsl(kpCh,6,[6,10,11],[8,12]).note,par:"A strong Mars/Saturn and well-placed 6th lord help in entrance exams."});
  out.push({question:"When will I get a job / start earning?",verdict:kc.promised?"Yes - in the windows below":"Possible with effort",
    summary:"A job / first income comes when the dasha lords signify the 6th (service), 10th (profession) and 11th (income).",
    timeline:fructificationWindows(kpCh,tree,[6,10,11],daysAgo(now,365*6),18),kp:kc.csl[0].note,par:"The 10th lord, 6th lord periods and Saturn (service karaka) time the start of regular work."});
  const sunSig=housesSignifiedBy(kpCh,SUN);const govt=sunSig.has(6)||sunSig.has(10);
  out.push({question:"Will I get a government job?",verdict:govt?"Supported":"Private sector is more likely",
    summary:"Government service is read from the Sun (authority) connected to the 6th/10th. "+(govt?"The Sun links to service/profession here.":"The Sun is not strongly tied to service here."),
    timeline:fructificationWindows(kpCh,tree,[1,6,10],daysAgo(now,365*6),18),kp:`Sun signifies houses [${[...sunSig].sort((a,b)=>a-b).join(", ")}]; a 6/10 link favours government work.`,par:"A strong Sun and Saturn for discipline mark government service."});
  const ca=adviseCareer(kpCh,parCh);
  out.push({question:"Should I do a job or business?",verdict:ca.jobVsBusiness.split(".")[0],summary:ca.jobVsBusiness,
    timeline:fructificationWindows(kpCh,tree,[7,10,11],daysAgo(now,365*4),18),kp:"Service ties to the 6th; business to the 7th. The 10th CSL's links decide the mode.",par:"Reading of the 10th sign, planets in the 10th and the 6th vs 7th lord strength."});
  out.push({question:"When will I get promotion / career growth?",verdict:"Growth windows below",
    summary:"Rise in status and salary comes in dashas of the 10th (status), 11th (gains) and 2nd (income) significators.",
    timeline:fructificationWindows(kpCh,tree,[10,11,2],daysAgo(now,180),15),kp:"Conjoined dasha of the strong significators of houses 2, 10 and 11.",par:"A Raja/Dhana-yoga planet's dasha brings the most visible promotion."});
  out.push({question:"When is a good time to change job / switch careers?",verdict:"Change windows below",
    summary:"A change of work is favoured when the dasha activates the 9th (change, fortune) with the 10th and 6th.",
    timeline:fructificationWindows(kpCh,tree,[9,10,6],daysAgo(now,180),15),kp:"Dashas of significators of the 6th, 9th and 10th houses mark the switch.",par:"Movement of the 10th lord and activation of the 9th indicate a constructive change."});
  const csl10=housesSignifiedBy(kpCh,cuspalSubLord(kpCh,10));const foreign=csl10.has(7)||csl10.has(12);
  out.push({question:"Will I have a foreign career / settle abroad?",verdict:foreign?"Likely":"Mainly domestic, with travel",
    summary:"Working abroad needs the 10th/7th tied to the 12th (foreign residence). "+(foreign?"That link is present.":"That link is weak."),
    timeline:fructificationWindows(kpCh,tree,[7,10,12],daysAgo(now,365*4),18),kp:`10th CSL ${cuspalSubLord(kpCh,10)} signifies houses [${[...csl10].sort((a,b)=>a-b).join(", ")}]; a 12th/7th link points to overseas work.`,par:"Rahu, the 12th lord and 7th lord connected to the 10th support a foreign career."});
  out.push({question:"When will my income / wealth increase?",verdict:"Wealth windows below",
    summary:"Income peaks in dashas of the 2nd (accumulated wealth) and 11th (gains) significators.",
    timeline:fructificationWindows(kpCh,tree,[2,11],daysAgo(now,180),15),kp:"Dashas of the strong significators of the 2nd and 11th houses.",par:"Dasha of a Dhana-yoga planet, or of Jupiter/Venus when well placed, brings the clearest financial growth."});
  return out;}

// ---- remedies -------------------------------------------------------------
function remediesFor(parCh,kpCh,domain){const dig=allDignities(parCh);
  const karakas=domain==="education"?[MERCURY,JUPITER]:[SUN,SATURN,MERCURY,JUPITER];
  const houses=domain==="education"?EDU_POS:CAR_POS;
  const sig=significatorsOfHouses(kpCh,houses).slice(0,5);
  const cand=[];for(const p of [...karakas,...sig])if(!cand.includes(p)&&REMEDY_DB[p])cand.push(p);
  const out=[];for(const planet of cand){const d=dig[planet];let reason=null;
    if(d.state==="Debilitated")reason=`${planet} is debilitated in ${d.sign} - strengthening it helps.`;
    else if(d.state==="Enemy sign")reason=`${planet} sits in an enemy sign (${d.sign}); pacifying it helps.`;
    else if(d.score<=0.35)reason=`${planet} is weak (dignity score ${d.score}).`;
    else if(NODES.has(planet)&&sig.slice(0,3).includes(planet))reason=`${planet} is a strong ${domain} significator; a calming remedy keeps results steady.`;
    if(reason)out.push({planet,reason,measures:REMEDY_DB[planet]});}
  if(!out.length){const best=karakas.reduce((a,b)=>dig[b].score>dig[a].score?b:a);
    out.push({planet:best,reason:`All key ${domain} planets are reasonably strong; honouring ${best} sustains and enhances results.`,measures:REMEDY_DB[best]});}
  return out;}

// ---- transits -------------------------------------------------------------
const ASPECTS={Jupiter:[5,7,9],Saturn:[3,7,10],Mars:[4,7,8],Rahu:[5,7,9],Ketu:[5,7,9]};
const SLOW=[JUPITER,SATURN,RAHU,KETU];
function influenced(houseOcc,planet){const out=new Set([houseOcc]);for(const a of (ASPECTS[planet]||[]))out.add((houseOcc-1+(a-1))%12+1);return [...out].sort((x,y)=>x-y);}
function buildTransitReport(natalPar,nowDate,nowEph){const trip=computeChart(nowEph,natalPar._lat,natalPar._lon,"Parashara");
  const ai=Math.floor(natalPar.ascendant/30),mi=natalPar.planets[MOON].signIndex;const pos={};
  for(const p of SLOW){const tp=trip.planets[p];const hl=((tp.signIndex-ai)%12+12)%12+1,hm=((tp.signIndex-mi)%12+12)%12+1;
    pos[p]={planet:p,sign:tp.sign,houseFromLagna:hl,houseFromMoon:hm,influences:influenced(hl,p)};}
  const dbl=houses=>{const ju=new Set(pos[JUPITER].influences),sa=new Set(pos[SATURN].influences);return houses.filter(h=>ju.has(h)&&sa.has(h));};
  const eduHits=dbl([4,5,9]);const edu=eduHits.length?`Jupiter and Saturn jointly influence house(s) [${eduHits.join(", ")}] - a strong window to start or complete important studies / exams.`:(()=>{const j=[4,5,9].filter(h=>pos[JUPITER].influences.includes(h));return j.length?`Jupiter currently supports education house(s) [${j.join(", ")}].`:"No major Jupiter/Saturn trigger on education houses now; rely on the dasha windows.";})();
  const carHits=dbl([10,6,11,2]);const car=carHits.length?`Jupiter and Saturn jointly influence house(s) [${carHits.join(", ")}] - a classic double-transit trigger for a job change, promotion or new venture.`:(()=>{const j=[10,6,11,2].filter(h=>pos[JUPITER].influences.includes(h)),s=[10,6,11,2].filter(h=>pos[SATURN].influences.includes(h));return `Jupiter touches career house(s) [${j.join(", ")}]; Saturn touches [${s.join(", ")}]. Use these with the dasha timeline.`;})();
  const hm=pos[SATURN].houseFromMoon;const ss=hm===12?"Sade Sati - first (rising) phase is active.":hm===1?"Sade Sati - peak (janma) phase is active.":hm===2?"Sade Sati - last (setting) phase is active.":hm===8?"Ashtama Shani (Saturn in the 8th from Moon) - go steady.":"No Sade Sati currently.";
  const notes=[];if(ss.includes("active"))notes.push("During Sade Sati, prefer consolidation over risky moves; discipline and service mitigate it.");
  const jm=pos[JUPITER].houseFromMoon;if([2,5,7,9,11].includes(jm))notes.push(`Transit Jupiter is in the ${jm}th from your Moon - generally favourable for growth.`);
  return {asOf:fmtDate(nowDate),positions:pos,sadeSati:ss,educationTrigger:edu,careerTrigger:car,notes};}

// ---- orchestrator ---------------------------------------------------------
function upcomingMahadashas(tree,now,count=6){const out=[];for(const md of tree){if(md.end<now)continue;out.push(md);if(out.length>=count)break;}return out;}
function buildReport(birth){
  // birth: {name, year, month(1-12), day, hour, minute, lat, lon, tz, place}
  const wall=new Date(Date.UTC(birth.year,birth.month-1,birth.day,birth.hour,birth.minute));
  const eph=new Date(wall.getTime()-birth.tz*3600*1000);
  const now=new Date();const nowWall=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth(),now.getUTCDate()));
  const kpCh=computeChart(eph,birth.lat,birth.lon,"KP");
  const parCh=computeChart(eph,birth.lat,birth.lon,"Parashara");parCh._lat=birth.lat;parCh._lon=birth.lon;
  const tree=buildDashaTree(parCh.planets[MOON].longitude,wall);
  const {md,ad,pd}=findRunning(tree,nowWall);
  const shadbala=computeShadbala(parCh);
  const education=adviseEducation(kpCh,parCh,shadbala);
  const career=adviseCareer(kpCh,parCh,shadbala);
  const bhavaBala=computeBhavaBala(parCh,shadbala);
  const phala=dashaPhala(tree,shadbala,nowWall,7);
  const ishtaRank=ishtaRanking(shadbala);
  const educationBest=bestPeriods(kpCh,tree,shadbala,nowWall,"education",birth);
  const careerBest=bestPeriods(kpCh,tree,shadbala,nowWall,"career",birth);
  const currentAge=ageYears(birth,nowWall);const stage=lifeStage(currentAge);
  career.shadbalaNotes.push(`Age context: the native is currently ${currentAge} years old (${stage}); the career windows below are shown from working age and tagged with the age at that time.`);
  const eduHS=bhavaBala.groupStrength([4,5,9]);
  education.shadbalaNotes.push(`Bhava Bala: the education houses (4th, 5th, 9th) average ${Math.round(eduHS*100)/100} rupas - ${houseStrengthLabel(eduHS)}.`);
  const carHS=bhavaBala.groupStrength([2,10,11]);
  career.shadbalaNotes.push(`Bhava Bala: the career houses (2nd, 10th, 11th) average ${Math.round(carHS*100)/100} rupas - ${houseStrengthLabel(carHS)}.`);
  const faqs=buildFaqs(kpCh,parCh,tree,nowWall);
  const yogas=detectYogas(parCh);
  const eduRemedies=remediesFor(parCh,kpCh,"education");
  const careerRemedies=remediesFor(parCh,kpCh,"career");
  const transit=buildTransitReport(parCh,nowWall,now);
  return {birth,kpCh,parCh,tree,
    current:{md:md?md.lord:null,ad:ad?ad.lord:null,pd:pd?pd.lord:null,
      mdPeriod:md?fmtPeriod(md):"-",adPeriod:ad?fmtPeriod(md,ad):"-",pdPeriod:pd?fmtPeriod(md,ad,pd):"-"},
    upcoming:upcomingMahadashas(tree,nowWall,6),education,career,faqs,yogas,eduRemedies,careerRemedies,transit,shadbala,bhavaBala,phala,ishtaRank,educationBest,careerBest,currentAge,lifeStage:stage};
}

root.AstroEngine={buildReport,computeChart,computeShadbala,PLANETS,PSHORT,navamsaSign,dasamsaSign,siddhamsaSign,norm360};
})(typeof window!=="undefined"?window:globalThis);
