/* ============================================================
   🔹 FICHIER : questions.js
   🔹 RÔLE : Gère l'affichage du questionnaire, la collecte des réponses,
             la progression, et la génération des résultats recommandés.
   ============================================================ */


/* ============================================================
   #1 — UTILITAIRES FETCH (GET / POST JSON)
   ------------------------------------------------------------
   Fonctions génériques pour communiquer avec le backend Flask.
   ============================================================ */

async function getJSON(url) {
  const res = await fetch(url);
  return await res.json();
}

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  return await res.json();
}


/* ============================================================
   #2 — VARIABLES GLOBALES ET ÉLÉMENTS DOM
   ------------------------------------------------------------
   Variables nécessaires pour suivre la progression du quiz
   et manipuler le DOM (barre, questions, résultats, etc.)
   ============================================================ */

let QUESTIONS = [];
let answers = {};
let idx = 0; // index de la question actuelle

// Références DOM
const qEl = document.getElementById("question");
const progressText = document.getElementById("progress-text");
const progressMeter = document.getElementById("progress-meter");
const qaBox = document.getElementById("qa-box");
const resultsBox = document.getElementById("results-box");
const resultsRoot = document.getElementById("results");
const btnYes = document.getElementById("btn-yes");
const btnNo = document.getElementById("btn-no");
const maxResultsSel = document.getElementById("max-results");


/* ============================================================
   #3 — PROGRESSION DU QUESTIONNAIRE
   ------------------------------------------------------------
   Met à jour la barre de progression et le texte associé.
   ============================================================ */

function updateProgress() {
  const total = QUESTIONS.length;
  const pct = Math.round((idx / total) * 100);
  progressMeter.style.width = pct + "%";
  const current = Math.min(idx + 1, total);
  progressText.textContent = `Question ${current} / ${total}`;
}


/* ============================================================
   #4 — AFFICHAGE D’UNE QUESTION
   ------------------------------------------------------------
   Affiche la question en cours, ou les résultats si terminé.
   ============================================================ */

function showQuestion() {
  if (idx >= QUESTIONS.length) {
    finalizeAndShowResults();
    return;
  }
  qEl.textContent = QUESTIONS[idx].text;
  updateProgress();
}


/* ============================================================
   #5 — AFFICHAGE DES RÉSULTATS
   ------------------------------------------------------------
   Génère dynamiquement les cartes champions avec leurs scores
   et raisons correspondantes.
   ============================================================ */

function renderResults(items) {
  resultsRoot.innerHTML = "";

  // Aucun résultat
  if (!items.length) {
    resultsRoot.innerHTML = `
      <div class="tip">
        Aucun résultat avec ces réponses. Essaie de relancer avec d'autres choix.
      </div>`;
    return;
  }

  // Génération des cartes
  for (const it of items) {
    const card = document.createElement("div");
    card.className = "card champion-card"; // 👈 ajout de la classe fade-in
    card.innerHTML = `
      <div class="icon-wrap">
        <img class="icon" alt="${it.champion}" src="${it.icon}">
      </div>
      <div class="meta">
        <div class="title">
          <span>${it.champion}</span>
          <span class="score">+${it.score}</span>
        </div>
        ${it.reasons?.length ? `
        <div class="reasons">
          ${it.reasons
            .sort((a, b) => b.weight - a.weight)
            .map(r => `
              <span class="reason-tag weight-${r.weight}">
                ${r.label}
              </span>
            `).join('')}
        </div>` : ""}
      </div>
    `;
    resultsRoot.appendChild(card);
  }

  // ✨ Effet fade-in progressif des cartes
  const cards = document.querySelectorAll('.champion-card');
  setTimeout(() => {
    cards.forEach((card, index) => {
      setTimeout(() => card.classList.add('visible'), index * 80);
    });
  }, 100);
}


/* ============================================================
   #6 — FINALISATION ET TRANSITION VERS LES RÉSULTATS
   ------------------------------------------------------------
   Animation de transition, récupération des résultats depuis
   le backend, affichage final des champions recommandés.
   ============================================================ */

async function finalizeAndShowResults() {
  const overlay = document.getElementById("transition-wrapper");

  // Désactive les boutons pendant la transition
  btnYes.disabled = true;
  btnNo.disabled = true;

  // Barre à 100 %
  progressMeter.style.width = "100%";
  progressMeter.classList.add("finish-glow");
  progressText.textContent = `Question ${QUESTIONS.length} / ${QUESTIONS.length}`;

  // Petite pause pour lisibilité
  await new Promise(r => setTimeout(r, 250));

  // Effet doré
  overlay.classList.add("active");
  await new Promise(r => setTimeout(r, 1000));

  // Transition vers les résultats
  qaBox.classList.add("hidden");
  resultsBox.classList.remove("hidden");
  resultsBox.classList.add("visible");

  const max_results = maxResultsSel.value;
  const data = await postJSON("/recommend", {answers, max_results});
  renderResults(data);

  // Dissipation du voile
  await new Promise(r => setTimeout(r, 600));
  overlay.classList.remove("active");

  // Réinitialise l’état visuel
  btnYes.disabled = false;
  btnNo.disabled = false;
  progressMeter.classList.remove("finish-glow");
}


/* ============================================================
   #7 — LOGIQUE DE RÉPONSE UTILISATEUR
   ------------------------------------------------------------
   Gère le clic sur "Oui" ou "Non", stocke la réponse,
   passe à la suivante ou affiche les résultats finaux.
   ============================================================ */

async function handleAnswer(value) {
  const key = QUESTIONS[idx].key;
  answers[key] = value;
  idx += 1;

  if (idx === QUESTIONS.length) {
    updateProgress();
    await finalizeAndShowResults();
    return;
  }

  showQuestion();
}


/* ============================================================
   #8 — GESTION DES ÉVÉNEMENTS UTILISATEUR
   ------------------------------------------------------------
   Boutons Oui/Non, redémarrage du quiz, changement du
   nombre max de résultats affichés.
   ============================================================ */

btnYes.addEventListener("click", () => handleAnswer(true));
btnNo.addEventListener("click", () => handleAnswer(false));

document.getElementById("brand-restart").addEventListener("click", () => {
  answers = {};
  idx = 0;
  resultsBox.classList.add("hidden");
  qaBox.classList.remove("hidden");
  progressMeter.style.width = "0%";
  updateProgress();
  showQuestion();
  window.scrollTo({top: 0, behavior: "smooth"});
});

maxResultsSel.addEventListener("change", async () => {
  if (resultsBox.classList.contains("hidden")) return;
  const max_results = maxResultsSel.value;
  const data = await postJSON("/recommend", {answers, max_results});
  renderResults(data);
});


/* ============================================================
   #9 — INITIALISATION AU CHARGEMENT DE LA PAGE
   ------------------------------------------------------------
   Charge la liste de questions depuis le backend et démarre
   le questionnaire à la première question.
   ============================================================ */

(async () => {
  QUESTIONS = await getJSON("/questions");
  idx = 0;
  answers = {};
  progressMeter.style.width = "0%";
  updateProgress();
  showQuestion();
})();
