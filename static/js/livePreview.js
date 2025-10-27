// ============================================================
//  🔹 FICHIER : livePreview.js
//  🔹 RÔLE : Met à jour la colonne Live Preview en temps réel
//            mais ne l'affiche que lorsqu'on le demande
// ============================================================

// État global partagé avec questions.js
window.liveAnswers = window.liveAnswers || {};
const resultsList = document.getElementById("results-list");
const livePreview = document.getElementById("live-preview");

// --- Message d'intro (si aucun contenu encore affiché) ---
if (resultsList && !resultsList.children.length) {
  resultsList.innerHTML = `
    <div class="live-placeholder">
      <p>Commencez le questionnaire pour voir apparaître les premiers résultats</p>
    </div>
  `;
}

// === Anti-spam d’appels réseau ===
let livePreviewTimeout = null;

// ============================================================
//  🧠 FONCTION PRINCIPALE — Mise à jour du contenu du Live Preview
// ============================================================
async function updateLivePreview() {
  if (!resultsList) return;

  clearTimeout(livePreviewTimeout);
  livePreviewTimeout = setTimeout(async () => {
    try {
      const maxSel = document.getElementById("max-results");
      const max = maxSel ? Number(maxSel.value) : 6;

      const res = await fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          answers: window.liveAnswers,
          max_results: max,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // 🔄 Vide le contenu actuel
      resultsList.innerHTML = "";

      // --- Cas : aucun résultat ---
      if (!data.length) {
        resultsList.innerHTML =
          "<p style='opacity:0.6'>Aucun résultat pour l’instant</p>";
        return;
      }

      // --- Création fluide des cartes champions ---
      data.forEach((it, index) => {
        const div = document.createElement("div");
        div.className = "champion-card";

        // 🔧 Fallback icône : si aucune URL dans la base, on prend Data Dragon
        const cleanName = (it.champion || "")
          .replace(/[\s'\.]/g, "")
          .replace("Wukong", "MonkeyKing")
          .replace("LeBlanc", "Leblanc")
          .replace("Cho'Gath", "Chogath")
          .replace("Bel'Veth", "Belveth")
          .replace("Jarvan IV", "JarvanIV");

        const iconUrl =
          it.icon && it.icon.startsWith("http")
            ? it.icon
            : `https://ddragon.leagueoflegends.com/cdn/14.23.1/img/champion/${cleanName}.png`;

        div.innerHTML = `
          <img src="${iconUrl}" alt="${it.champion}">
          <span class="champion-name">${it.champion}</span>
          <span class="champion-score">+${it.score}</span>
        `;
        resultsList.appendChild(div);

        // ✨ Apparition fluide progressive
        setTimeout(() => div.classList.add("visible"), index * 70);
      });
    } catch (err) {
      console.error("Erreur Live Preview :", err);
    }
  }, 120);
}

// ============================================================
//  🖱️ SYNCHRONISATION DES CLICS "OUI" / "NON"
// ============================================================
document.addEventListener("click", (e) => {
  if (e.target.id !== "btn-yes" && e.target.id !== "btn-no") return;

  const key = window.currentQuestionKey;
  if (!key) return;

  // ✅ Stocke les réponses sous forme de booléens
  window.liveAnswers[key] = e.target.id === "btn-yes";

  // 🔁 Met à jour les données (sans afficher le panneau)
  updateLivePreview();
});

// ============================================================
//  🎚️ AFFICHAGE MANUEL DU LIVE PREVIEW
// ============================================================
const togglePreviewBtn = document.getElementById("toggle-preview");

if (togglePreviewBtn && livePreview) {
  togglePreviewBtn.addEventListener("click", () => {
    livePreview.classList.toggle("visible");
  });
}
