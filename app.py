# ================================================================
#  app.py — Application principale Flask pour LoL Wild's Picks
# ================================================================

from flask import Flask, render_template, request, jsonify
import json, os
from champions import CHAMPIONS


# ================================================================
#  ⚙️ CONFIGURATION DE L’APPLICATION
# ================================================================

app = Flask(__name__)


# ================================================================
#  🧩 QUESTIONS (utilisées pour évaluer les besoins de la draft)
# ================================================================

QUESTIONS = [
    ("L’équipe ennemie est-elle AD heavy ?", "heavy_ad", 1),
    ("L’équipe ennemie est-elle AP heavy ?", "heavy_ap", 1),
    ("Besoin d'engage ?", "need_engage", 1),
    ("Besoin de CC ?", "need_cc", 1),
    ("Frontline nécessaire ?", "frontline", 1),
    ("Peeling nécessaire ?", "peeling", 1),
    ("Solo invade ?", "invade", 1),
    ("Besoin de scaling ?", "scaling", 1),
    ("Besoin d'early game strong ?", "early_game", 1),
    ("Beaucoup de melee alliés ?", "ally_melee", 2),
    ("Y a-t-il des sacs à PV ?", "hp_tanks", 2),
    ("Beaucoup d'auto-attackers ?", "aa_heavy", 2),
    ("ADC peut bénéficier d'un enchanteur ?", "enchanter_adc", 2),
    ("Faut-il lock une target ?", "lock_target", 2),
    ("Beaucoup de ranges ?", "range_heavy", 2),
]


# ================================================================
#  🏷️ LIBELLÉS LISIBLES (pour l’affichage des raisons)
# ================================================================

REASON_LABELS = {
    "heavy_ad": "vs AD heavy",
    "heavy_ap": "vs AP heavy",
    "need_engage": "Engage",
    "need_cc": "CC",
    "frontline": "Frontline",
    "peeling": "Peeling",
    "invade": "Solo invade",
    "scaling": "Scaling",
    "early_game": "Early game",
    "ally_melee": "Synergie melee",
    "hp_tanks": "vs HP tanks",
    "aa_heavy": "vs AAs",
    "enchanter_adc": "Boost ADC",
    "lock_target": "Target locker",
    "range_heavy": "vs ranges",
}


# ================================================================
#  🧮 SYSTÈME DE SCORING DES CHAMPIONS
# ================================================================

def score_with_answers(meta: dict, answers: dict):
    """Calcule le score d’un champion selon les réponses utilisateur."""
    score = 0
    reasons = []

    for text, key, weight in QUESTIONS:
        ans = bool(answers.get(key, False))
        if ans and meta.get(key, False):
            score += weight
            label = REASON_LABELS.get(key, text)
            reasons.append({"key": key, "label": label, "weight": weight})

    return score, reasons


# ================================================================
#  🌐 ROUTES UTILISATEUR (frontend)
# ================================================================

@app.route("/", methods=["GET"])
def index():
    """Page d’accueil principale."""
    return render_template("index.html", q_count=len(QUESTIONS))


@app.route("/questions", methods=["GET"])
def get_questions():
    """Renvoie la liste complète des questions au format JSON."""
    return jsonify([{"text": q[0], "key": q[1], "weight": q[2]} for q in QUESTIONS])


@app.route("/recommend", methods=["POST"])
def recommend():
    """Renvoie une liste de champions recommandés selon les réponses."""
    data = request.get_json(force=True) or {}
    answers = data.get("answers", {})
    max_results = int(data.get("max_results", 6))

    scored = []
    for champ, meta in CHAMPIONS.items():
        s, reasons = score_with_answers(meta, answers)
        if s > 0:
            # ✅ Vérifie que l’icône est une URL Riot valide
            icon = meta.get("icon")
            if not icon or not str(icon).startswith("http"):
                icon = None

            scored.append({
                "champion": champ,
                "score": s,
                "reasons": reasons[:5],
                "icon": icon,
                "tags": [k for k, v in meta.items() if isinstance(v, bool) and v],
            })

    # Tri décroissant selon le score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(scored[:max_results])


# ================================================================
#  🔐 ADMINISTRATION (interface / sauvegarde)
# ================================================================

DATA_FILE = "champions.json"

# --- Chargement initial des champions depuis le fichier local ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        CHAMPIONS.update(json.load(f))


@app.route("/admin")
def admin():
    """Page d’administration des champions."""
    return render_template("admin.html", champions=CHAMPIONS, reason_labels=REASON_LABELS)


@app.route("/api/champions", methods=["GET"])
def api_get_champions():
    """API : renvoie la base complète des champions."""
    return jsonify(CHAMPIONS)


@app.route("/api/champions", methods=["POST"])
def api_save_champions():
    """API : sauvegarde les modifications sur les champions."""
    data = request.get_json(force=True) or {}

    # --- 🧹 Nettoyage des icônes non valides ---
    for champ, meta in data.items():
        if "icon" not in meta or not str(meta["icon"]).startswith("http"):
            meta.pop("icon", None)

    # --- Sauvegarde dans le fichier JSON ---
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # --- Rafraîchissement en mémoire ---
    CHAMPIONS.clear()
    CHAMPIONS.update(data)

    return jsonify({"status": "ok"})


# ================================================================
#  🚀 MAIN (lancement du serveur Flask)
# ================================================================

if __name__ == "__main__":
    app.run(debug=True)
