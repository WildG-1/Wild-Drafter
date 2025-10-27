/* ===========================================================================
   Wild Drafter – Questionnaire principal (réécriture 2025)
   Gère la navigation dans les questions, les réponses utilisateurs et
   l'affichage des recommandations finales.
   ======================================================================== */

(() => {
  const STORAGE_KEY = window.WILD_DRAFTER?.STORAGE_KEY ?? "wild_drafter.customChampions";

  const qEl = document.getElementById("question");
  const progressText = document.getElementById("progress-text");
  const progressMeter = document.getElementById("progress-meter");
  const qaBox = document.getElementById("qa-box");
  const resultsBox = document.getElementById("results-box");
  const resultsRoot = document.getElementById("results");
  const btnYes = document.getElementById("btn-yes");
  const btnNo = document.getElementById("btn-no");
  const maxResultsSel = document.getElementById("max-results");

  const state = {
    questions: [],
    index: 0,
    answers: {},
  };

  function getLocalPayload() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
    } catch (error) {
      console.warn("Impossible de charger le payload local", error);
      return null;
    }
  }

  async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`GET ${url} → ${res.status}`);
    return res.json();
  }

  async function postRecommendations(maxResults) {
    const payload = getLocalPayload();
    const body = {
      answers: state.answers,
      max_results: maxResults,
    };
    if (payload) {
      body.payload = payload;
    }

    const res = await fetch("/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`POST /recommend → ${res.status}`);
    return res.json();
  }

  function updateProgress() {
    const total = state.questions.length || Q_COUNT || 1;
    const current = Math.min(state.index + 1, total);
    const ratio = Math.round((state.index / total) * 100);
    progressMeter.style.width = `${ratio}%`;
    progressText.textContent = `Question ${current} / ${total}`;
  }

  function renderResults(items) {
    resultsRoot.innerHTML = "";

    if (!items.length) {
      resultsRoot.innerHTML = `
        <div class="tip">
          Aucun résultat avec ces réponses. Essaie de relancer avec d'autres choix.
        </div>`;
      return;
    }

    items.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "card champion-card";
      card.innerHTML = `
        <div class="icon-wrap">
          <img class="icon" alt="${item.champion}" src="${item.icon}">
        </div>
        <div class="meta">
          <div class="title">
            <span>${item.champion}</span>
            <span class="score">+${item.score}</span>
          </div>
          ${item.reasons?.length ? `
          <div class="reasons">
            ${item.reasons
              .map((reason) => `
                <span class="reason-tag weight-${reason.weight}">
                  ${reason.label}
                </span>`)
              .join("")}
          </div>` : ""}
        </div>`;
      resultsRoot.appendChild(card);

      setTimeout(() => card.classList.add("visible"), index * 80);
    });
  }

  async function finalizeQuiz() {
    btnYes.disabled = true;
    btnNo.disabled = true;

    progressMeter.style.width = "100%";
    progressMeter.classList.add("finish-glow");
    progressText.textContent = `Question ${state.questions.length} / ${state.questions.length}`;

    await new Promise((resolve) => setTimeout(resolve, 250));

    const overlay = document.getElementById("transition-wrapper");
    overlay?.classList.add("active");
    await new Promise((resolve) => setTimeout(resolve, 1000));

    qaBox.classList.add("hidden");
    resultsBox.classList.remove("hidden");
    resultsBox.classList.add("visible");

    const maxResults = Number(maxResultsSel.value || 6);
    const data = await postRecommendations(maxResults);
    renderResults(data);

    await new Promise((resolve) => setTimeout(resolve, 600));
    overlay?.classList.remove("active");

    btnYes.disabled = false;
    btnNo.disabled = false;
    progressMeter.classList.remove("finish-glow");
  }

  function showQuestion() {
    if (state.index >= state.questions.length) {
      finalizeQuiz();
      return;
    }

    const current = state.questions[state.index];
    qEl.textContent = current.text;
    updateProgress();

    window.currentQuestionKey = current.key;
  }

  function syncLivePreview(options = {}) {
    if (typeof window.updateLivePreview === "function") {
      window.updateLivePreview(state.answers, options);
    }
    window.liveAnswers = { ...state.answers };
  }

  async function handleAnswer(value) {
    const question = state.questions[state.index];
    if (!question) return;

    state.answers[question.key] = value;
    syncLivePreview();

    state.index += 1;
    if (state.index >= state.questions.length) {
      await finalizeQuiz();
      return;
    }

    showQuestion();
  }

  function resetQuiz() {
    state.index = 0;
    state.answers = {};
    resultsBox.classList.add("hidden");
    qaBox.classList.remove("hidden");
    resultsRoot.innerHTML = "";
    progressMeter.style.width = "0%";
    updateProgress();
    showQuestion();
    syncLivePreview({ reset: true });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function registerEvents() {
    btnYes?.addEventListener("click", () => handleAnswer(true));
    btnNo?.addEventListener("click", () => handleAnswer(false));

    maxResultsSel?.addEventListener("change", async () => {
      const maxResults = Number(maxResultsSel.value || 6);
      if (!resultsBox.classList.contains("hidden")) {
        const data = await postRecommendations(maxResults);
        renderResults(data);
      }
      syncLivePreview({ maxResults });
    });

    window.addEventListener("wilddrafter:restart", () => {
      resetQuiz();
    });
  }

  (async () => {
    registerEvents();
    state.questions = await getJSON("/questions");
    resetQuiz();
  })().catch((error) => console.error("Initialisation questionnaire impossible", error));
})();
