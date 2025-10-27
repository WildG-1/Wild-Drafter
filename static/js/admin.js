// ============================================================================
//  Wild Drafter – Administration locale des champions
//  Les données modifiées restent dans le navigateur. Un export permet d'envoyer
//  une proposition au serveur sans altérer la base officielle.
// ============================================================================

(() => {
  const STORAGE_KEY = window.WILD_DRAFTER?.STORAGE_KEY ?? "wild_drafter.customChampions";
  const serverChampions = window.__SERVER_CHAMPIONS__ || {};
  const reasonLabels = window.__REASON_LABELS__ || {};
  const reasonWeights = window.__REASON_WEIGHTS__ || {};
  const defaultIcon = window.__DEFAULT_ICON__ || "";

  const gridEl = document.getElementById("admin-grid");
  const addBtn = document.getElementById("add-champ");
  const saveBtn = document.getElementById("save-changes");
  const resetBtn = document.getElementById("reset-data");
  const exportBtn = document.getElementById("export-payload");
  const toggleDeleteBtn = document.getElementById("toggle-delete");

  const modalEl = document.getElementById("admin-modal");
  const cancelEl = document.getElementById("cancel-add");
  const confirmEl = document.getElementById("confirm-add");
  const nameEl = document.getElementById("champ-name");
  const iconEl = document.getElementById("champ-icon");
  const placeholderEl = document.getElementById("champ-icon-placeholder");

  if (!gridEl) return;

  const ICON_OVERRIDES = {
    "Wukong": "MonkeyKing",
    "Renata Glasc": "Renata",
    "Kha'Zix": "Khazix",
    "Cho'Gath": "Chogath",
    "Vel'Koz": "Velkoz",
    "Kai'Sa": "Kaisa",
    "LeBlanc": "Leblanc",
    "Nunu & Willump": "Nunu",
    "Dr. Mundo": "DrMundo",
    "Miss Fortune": "MissFortune",
    "Tahm Kench": "TahmKench",
    "Twisted Fate": "TwistedFate",
    "Jarvan IV": "JarvanIV",
    "Xin Zhao": "XinZhao",
    "Aurelion Sol": "AurelionSol",
    "Kog'Maw": "KogMaw",
    "Rek'Sai": "RekSai",
    "Bel'Veth": "Belveth",
    "K'Sante": "KSante",
    "Lee Sin": "LeeSin",
    "Master Yi": "MasterYi",
    "Renécton": "Renekton",
    "Dr Mundo": "DrMundo",
    "ChoGath": "Chogath",
  };

  function cloneChampions(source) {
    return JSON.parse(JSON.stringify(source || {}));
  }

  function loadLocalChampions() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null;
    } catch (error) {
      console.warn("Impossible de charger les champions locaux", error);
      return null;
    }
  }

  function buildRiotIconUrl(inputName) {
    if (!inputName) return "";
    const normalized = inputName
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/['.]/g, "")
      .replace(/\s+/g, " ")
      .trim();
    const override = ICON_OVERRIDES[normalized];
    let key = override || normalized.replace(/\s+/g, "");
    key = key.charAt(0).toUpperCase() + key.slice(1);
    return `https://ddragon.leagueoflegends.com/cdn/14.23.1/img/champion/${key}.png`;
  }

  function resolveIcon(name, meta = {}) {
    if (meta.icon && typeof meta.icon === "string" && meta.icon.trim()) {
      return meta.icon;
    }
    return buildRiotIconUrl(name) || defaultIcon;
  }

  let champions = loadLocalChampions() || cloneChampions(serverChampions);
  let deleteMode = false;
  let hasUnsavedChanges = false;

  function markUnsaved() {
    hasUnsavedChanges = true;
    saveBtn?.classList.add("unsaved");
  }

  function markSaved() {
    hasUnsavedChanges = false;
    saveBtn?.classList.remove("unsaved");
  }

  function flashSavedEffect() {
    const panel = document.querySelector(".admin-panel");
    if (!panel) return;
    panel.classList.add("saved-flash");
    setTimeout(() => panel.classList.remove("saved-flash"), 1200);
  }

  function renderGrid() {
    gridEl.innerHTML = "";
    const names = Object.keys(champions).sort((a, b) => a.localeCompare(b));

    names.forEach((name) => {
      const meta = champions[name] || {};
      const card = document.createElement("div");
      card.className = "admin-card";
      if (deleteMode) card.classList.add("delete-mode");

      const deleteBtn = document.createElement("div");
      deleteBtn.className = "admin-delete";
      deleteBtn.innerHTML = "✕";
      deleteBtn.title = "Supprimer ce champion";
      deleteBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        if (!confirm(`Supprimer ${name} ?`)) return;
        delete champions[name];
        markUnsaved();
        renderGrid();
      });
      card.appendChild(deleteBtn);

      const img = document.createElement("img");
      img.src = resolveIcon(name, meta) || defaultIcon;
      img.alt = name;
      img.referrerPolicy = "no-referrer";
      img.onerror = () => {
        img.src = defaultIcon;
        img.style.filter = "grayscale(1) brightness(0.6)";
      };
      card.appendChild(img);

      const nameDiv = document.createElement("div");
      nameDiv.className = "admin-name";
      nameDiv.textContent = name;
      card.appendChild(nameDiv);

      const tooltip = document.createElement("div");
      tooltip.className = "admin-tooltip";
      const keys = Object.keys(meta)
        .filter((key) => meta[key] === true && reasonLabels[key])
        .sort((a, b) => (reasonWeights[b] || 1) - (reasonWeights[a] || 1));

      tooltip.innerHTML = keys
        .map((key) => {
          const weight = reasonWeights[key] || 1;
          const cls = weight === 2 ? "w2" : "w1";
          return `<div class="attr-chip ${cls}">${reasonLabels[key]}</div>`;
        })
        .join("");
      card.appendChild(tooltip);

      gridEl.appendChild(card);
    });
  }

  function closeModal() {
    modalEl?.classList.add("hidden");
    modalEl?.setAttribute("hidden", "");
    nameEl.value = "";
    iconEl.value = "";
    placeholderEl.checked = false;
    modalEl?.querySelectorAll(".attr-checkbox").forEach((checkbox) => {
      checkbox.checked = false;
    });
  }

  function openModal() {
    modalEl?.classList.remove("hidden");
    modalEl?.removeAttribute("hidden");
    nameEl.focus();
  }

  function persistLocal() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(champions));
      markSaved();
      flashSavedEffect();
    } catch (error) {
      console.error("Impossible d'enregistrer localement", error);
      alert("❌ Enregistrement local impossible. Vérifie l'espace disponible.");
    }
  }

  async function exportPayload() {
    const payload = JSON.stringify(champions, null, 2);
    let copied = false;

    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(payload);
        copied = true;
        alert("📋 Payload copié dans le presse-papiers.");
      } catch (error) {
        console.warn("Copie refusée", error);
      }
    }

    if (!copied) {
      const blob = new Blob([payload], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "wild-drafter-champions.json";
      link.click();
      URL.revokeObjectURL(url);
      alert("💾 Fichier téléchargé.");
    }

    const submit = confirm("Souhaites-tu envoyer cette proposition au serveur pour revue ?");
    if (!submit) return;

    try {
      const res = await fetch("/api/champions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload,
      });
      const body = await res.json();
      if (!res.ok) throw new Error(body?.message || "Erreur serveur");
      alert(`📨 Proposition envoyée (${body.proposal}).`);
    } catch (error) {
      console.error("Échec d'envoi", error);
      alert("⚠️ Impossible d'envoyer la proposition.");
    }
  }

  function restoreDefaults() {
    if (!confirm("Restaurer la base officielle ? Tes modifications locales seront perdues.")) {
      return;
    }
    champions = cloneChampions(serverChampions);
    markUnsaved();
    persistLocal();
    renderGrid();
  }

  function registerEvents() {
    addBtn?.addEventListener("click", openModal);
    cancelEl?.addEventListener("click", closeModal);
    modalEl?.addEventListener("click", (event) => {
      if (event.target === modalEl) closeModal();
    });

    confirmEl?.addEventListener("click", () => {
      const name = nameEl.value.trim();
      if (!name) {
        alert("Nom du champion requis");
        return;
      }
      if (champions[name]) {
        alert("Un champion avec ce nom existe déjà.");
        return;
      }

      const meta = {};
      modalEl?.querySelectorAll(".attr-checkbox").forEach((checkbox) => {
        meta[checkbox.dataset.key] = checkbox.checked;
      });

      if (placeholderEl.checked) {
        meta.icon = defaultIcon;
      } else if (iconEl.value.trim()) {
        meta.icon = iconEl.value.trim();
      } else {
        meta.icon = resolveIcon(name, meta);
      }

      champions[name] = meta;
      markUnsaved();
      closeModal();
      renderGrid();
    });

    saveBtn?.addEventListener("click", persistLocal);
    resetBtn?.addEventListener("click", restoreDefaults);
    exportBtn?.addEventListener("click", exportPayload);

    toggleDeleteBtn?.addEventListener("click", () => {
      deleteMode = !deleteMode;
      toggleDeleteBtn.classList.toggle("active", deleteMode);
      toggleDeleteBtn.textContent = deleteMode
        ? "❌ Quitter mode suppression"
        : "🗑️ Mode suppression";
      renderGrid();
    });
  }

  registerEvents();
  renderGrid();
  closeModal();
  markSaved();
})();
