const fs = require("fs");
const path = require("path");

const lib = fs.readFileSync("node_modules/astronomy-engine/astronomy.browser.min.js","utf8");
const engine = fs.readFileSync("engine.js","utf8");
const ui = fs.readFileSync("ui.js","utf8");
const css = fs.readFileSync("styles.css","utf8");

const body = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Astro Adviser - Education &amp; Career (KP + Parashara)</title>
<meta name="description" content="Astrological adviser for education and career using KP and Parashara systems with 3-level Vimshottari dashas and divisional charts. Developed by Dr. Anil Sabaji.">
<style>
${css}
</style>
</head>
<body>
<header class="site-header"><div class="wrap">
  <span class="brand"><span class="logo">&#9789;</span> Astro Adviser</span>
  <span class="tagline">Education &amp; Career &middot; KP + Parashara &middot; Vimshottari Dasha &middot; Vargas</span>
</div></header>

<main class="wrap">
  <section class="hero no-print">
    <h1>Find your right education &amp; career path</h1>
    <p>A fully in-browser astrological adviser using <strong>both the KP (Krishnamurti Paddhati) and Parashara</strong>
    systems, <strong>3-level Vimshottari dashas</strong> (Mahadasha &rarr; Antardasha &rarr; Pratyantardasha) and the
    <strong>divisional charts</strong> (D-9, D-10 career, D-24 education). Get field recommendations for good
    <em>earning</em> and <em>satisfaction</em>, timelines, FAQs, remedies and transit triggers &mdash; then print a colourful PDF.</p>
  </section>

  <section class="card no-print" id="inputCard">
    <h2>Enter birth details</h2>
    <form id="birthForm" class="grid-form">
      <div class="field"><label for="name">Name</label><input type="text" id="name" placeholder="Your name" value="Seeker"></div>
      <div class="field"><label for="dob">Date of birth</label><input type="date" id="dob" value="1990-08-15" required></div>
      <div class="field"><label for="tob">Time of birth (24h, local)</label><input type="time" id="tob" value="10:30" required></div>
      <div class="field"><label for="city">City (quick pick)</label><select id="city"><option value="">-- choose, or enter coordinates --</option></select></div>
      <fieldset class="coords"><legend>Or enter exact coordinates</legend>
        <div class="field"><label for="lat">Latitude</label><input type="text" id="lat" placeholder="28.6139"></div>
        <div class="field"><label for="lon">Longitude</label><input type="text" id="lon" placeholder="77.2090"></div>
        <div class="field"><label for="tz">Timezone (hrs from UTC)</label><input type="text" id="tz" placeholder="5.5"></div>
      </fieldset>
      <div class="actions"><button type="submit">Generate advice &rarr;</button></div>
    </form>
    <p class="err" id="formErr"></p>
    <p class="hint">Tip: pick a city for instant coordinates &amp; timezone, or type your own. Everything is computed locally in your browser &mdash; nothing is uploaded.</p>
  </section>

  <section id="reportArea" style="display:none;">
    <div class="card report-head" id="repHead"></div>
    <div class="tabs no-print">
      <button class="tab active" onclick="showTab('ovPanel',this)">Overview &amp; Dasha</button>
      <button class="tab" onclick="showTab('eduPanel',this)">Education</button>
      <button class="tab" onclick="showTab('carPanel',this)">Career</button>
      <button class="tab" onclick="showTab('faqPanel',this)">FAQ</button>
      <button class="tab" onclick="showTab('chartPanel',this)">Charts</button>
      <button class="tab" onclick="printReport()" title="Open the print dialog and choose 'Save as PDF'">&#128424; Print / Save PDF</button>
    </div>
    <h2 class="print-only" style="margin:6px 0;">Complete Education &amp; Career Report</h2>
    <div class="tab-panel active" id="ovPanel"></div>
    <div class="tab-panel" id="eduPanel"></div>
    <div class="tab-panel" id="carPanel"></div>
    <div class="tab-panel" id="faqPanel"></div>
    <div class="tab-panel" id="chartPanel"></div>
  </section>
</main>

<footer class="site-footer"><div class="wrap">
  <p class="dev-credit">Developed by Dr. Anil Sabaji, email: <a href="mailto:anilsabaji@gmail.com">anilsabaji@gmail.com</a></p>
  <p class="foot-note">Computed entirely in your browser with the astronomy-engine model (sidereal). KP uses the Krishnamurti
  ayanamsa with Placidus cusps; Parashara uses the Lahiri ayanamsa with whole-sign houses. For guidance and self-reflection only.</p>
</div></footer>

<script>
${lib}
</script>
<script>
${engine}
</script>
<script>
${ui}
</script>
</body>
</html>
`;

const outDir = process.argv[2] || ".";
const outPath = path.join(outDir, "index.html");
fs.writeFileSync(outPath, body);
console.log("Wrote", outPath, (body.length/1024).toFixed(0)+"KB");
