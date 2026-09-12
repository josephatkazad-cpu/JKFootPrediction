// Remplacez cette adresse par l'URL HTTPS de votre backend PythonAnywhere.
const API_BASE_URL = "https://josephatkazad2013.pythonanywhere.com";

const fixturesEl = document.getElementById("fixtures");
const statusEl = document.getElementById("status");

function isoDate(offset=0) {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return d.toISOString().slice(0,10);
}

async function loadFixtures(offset=0) {
  statusEl.textContent = "Chargement des matchs...";
  fixturesEl.innerHTML = "";
  try {
    const r = await fetch(`${API_BASE_URL}/api/fixtures?date=${isoDate(offset)}`);
    const data = await r.json();
    if (!data.ok) throw new Error(data.error || "Erreur serveur");
    statusEl.textContent = `${data.fixtures.length} match(s) trouvé(s)`;
    data.fixtures.forEach(renderFixture);
  } catch (e) {
    statusEl.textContent = `Impossible de charger les matchs : ${e.message}`;
  }
}

function renderFixture(f) {
  const card = document.createElement("article");
  card.className = "fixture";
  const time = f.starting_at ? new Date(f.starting_at).toLocaleTimeString("fr-FR", {hour:"2-digit",minute:"2-digit"}) : "--:--";
  card.innerHTML = `
    <div class="league">${f.league || "Compétition"}</div>
    <div class="teams"><strong>${f.home}</strong><span>${time}</span><strong>${f.away}</strong></div>
    <button class="analyze">Analyser →</button>
  `;
  card.querySelector(".analyze").onclick = () => analyze(f.id, card);
  fixturesEl.appendChild(card);
}

async function analyze(id, card) {
  const btn = card.querySelector(".analyze");
  btn.disabled = true;
  btn.textContent = "Analyse...";
  try {
    const r = await fetch(`${API_BASE_URL}/api/analyze/${id}`);
    const data = await r.json();
    if (!data.ok) throw new Error(data.error || "Données insuffisantes");
    showAnalysis(data.analysis, card);
  } catch(e) {
    alert(`Impossible d'analyser ce match : ${e.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyser →";
  }
}

function showAnalysis(a, card) {
  const old = card.querySelector(".analysis");
  if (old) old.remove();
  const div = document.createElement("div");
  div.className = "analysis";
  div.innerHTML = `
    <h3>Analyse</h3>
    <p>Buts attendus : ${a.expectedGoals.home} - ${a.expectedGoals.away}</p>
    <p><b>1N2 :</b> ${a["1N2"]["1"]}% / ${a["1N2"]["N"]}% / ${a["1N2"]["2"]}%</p>
    <p><b>BTTS Oui :</b> ${a.BTTS.yes}%</p>
    <p><b>Over 2,5 :</b> ${a.overUnder["over2.5"]}%</p>
    <p><b>Top scores :</b> ${a.topScores.map(x => `${x.score} (${x.probability}%)`).join(" · ")}</p>
  `;
  card.appendChild(div);
}

document.querySelectorAll(".tabs button").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll(".tabs button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    loadFixtures(btn.dataset.day === "tomorrow" ? 1 : 0);
  };
});

document.getElementById("themeBtn").onclick = () => document.body.classList.toggle("light");
loadFixtures(0);
