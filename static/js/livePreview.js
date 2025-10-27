// ============================================================================
//  Live Preview — suggestions en direct pendant le questionnaire
//  Cette version partage la logique de payload local et respecte le debounce
//  pour limiter les appels réseaux.
// ============================================================================

(() => {
  const STORAGE_KEY = window.WILD_DRAFTER?.STORAGE_KEY ?? "wild_drafter.customChampions";

  const resultsList = document.getElementById("results-list");
  const livePreview = document.getElementById("live-preview");

  if (!resultsList) return;

  const placeholder = `
    <div class="live-placeholder">
      <p>Commence le questionnaire pour voir apparaître les premiers résultats.</p>
    </div>`;
  resultsList.innerHTML = placeholder;

  function getLocalPayload() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
    } catch (error) {
      console.warn("Impossible de lire le payload local", error);
      return null;
    }
  }

  let debounceHandle = null;

  async function fetchPreview(answers, maxResults) {
    const payload = getLocalPayload();
    const body = { answers, max_results: maxResults };
    if (payload) body.payload = payload;

    const res = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`Preview → ${res.status}`);
    return res.json();
  }

  function renderPreview(items) {
    resultsList.innerHTML = "";

    if (!items.length) {
      resultsList.innerHTML = "<p style='opacity:0.6'>Aucun résultat pour l’instant</p>";
      return;
    }

    items.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "champion-card";
      div.innerHTML = `
        <img src="${item.icon}" alt="${item.champion}">
        <span class="champion-name">${item.champion}</span>
        <span class="champion-score">+${item.score}</span>`;
      resultsList.appendChild(div);
      setTimeout(() => div.classList.add("visible"), index * 70);
    });
  }

  function clearPreview() {
    resultsList.innerHTML = placeholder;
  }

  function getMaxResults(options) {
    if (options?.maxResults) return Number(options.maxResults);
    const select = document.getElementById("max-results");
    return select ? Number(select.value) : 6;
  }

  async function updatePreview(answers = {}, options = {}) {
    const hasAnswer = Object.values(answers || {}).some((value) => value === true || value === false);
    if (options.reset || !hasAnswer) {
      clearPreview();
      return;
    }

    const maxResults = getMaxResults(options);

    clearTimeout(debounceHandle);
    debounceHandle = setTimeout(async () => {
      try {
        const data = await fetchPreview(answers, maxResults);
        renderPreview(data);
      } catch (error) {
        console.error("Erreur Live Preview", error);
      }
    }, 150);
  }

  window.updateLivePreview = updatePreview;

  window.addEventListener("wilddrafter:restart", () => {
    clearPreview();
  });

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && livePreview?.classList.contains("visible")) {
      updatePreview(window.liveAnswers || {});
    }
  });
})();
