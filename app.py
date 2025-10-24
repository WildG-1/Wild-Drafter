# ================================================================
#  app.py — Application principale Flask pour Wild Drafter
#  Version persistante (PostgreSQL - Railway)
# ================================================================

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json, os

# ================================================================
#  ⚙️ CONFIGURATION DE L’APPLICATION
# ================================================================

app = Flask(__name__)

# Si tu es hébergé sur Railway, la variable DATABASE_URL est fournie automatiquement.
# Sinon, le code crée une base locale "champions.db".
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///champions.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connexion à la base de données
db = SQLAlchemy(app)


# ================================================================
#  ❓ LISTE DES QUESTIONS UTILISÉES DANS L'INTERFACE
# ================================================================
# Chaque question correspond à un "besoin" (clé) et un poids (importance).
# Ces questions servent à évaluer quels champions sont les plus adaptés.

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
#  🏷️ LIBELLÉS AFFICHÉS À L'ÉCRAN (pour les tooltips)
# ================================================================
# Ces noms sont utilisés pour rendre les raisons de recommandation lisibles.

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

# Poids associés à chaque raison (utile pour les couleurs ou tri)
REASON_WEIGHTS = {key: weight for _, key, weight in QUESTIONS}


# ================================================================
#  🗄️ BASE DE DONNÉES : CHAMPIONS
# ================================================================
# Chaque champion a :
# - un nom (clé primaire)
# - un dictionnaire "data" contenant tous ses attributs (JSON)

class Champion(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    data = db.Column(db.JSON, nullable=False)


# Création automatique de la base au lancement de l'app
with app.app_context():
    db.create_all()

    # Si la base est vide, on la remplit avec les données du fichier champions.json
    if not Champion.query.first() and os.path.exists("champions.json"):
        with open("champions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for name, meta in data.items():
                db.session.add(Champion(name=name, data=meta))
            db.session.commit()


# ================================================================
#  🧮 CALCUL DU SCORE DES CHAMPIONS
# ================================================================
# Compare les réponses de l’utilisateur avec les attributs d’un champion.
# Retourne :
# - un score total
# - une liste de "raisons" expliquant le choix

def score_with_answers(meta: dict, answers: dict):
    score = 0
    reasons = []

    for text, key, weight in QUESTIONS:
        user_answer = bool(answers.get(key, False))
        champ_has_trait = meta.get(key, False)

        # Si le joueur a répondu "oui" et que le champion a ce trait
        if user_answer and champ_has_trait:
            score += weight
            label = REASON_LABELS.get(key, text)
            reasons.append({"key": key, "label": label, "weight": weight})

    return score, reasons


# ================================================================
#  🌐 ROUTES UTILISATEUR (pages publiques)
# ================================================================

# --- Page principale (interface du questionnaire)
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", q_count=len(QUESTIONS))


# --- API : obtenir la liste des questions
@app.route("/questions", methods=["GET"])
def get_questions():
    return jsonify([{"text": q[0], "key": q[1], "weight": q[2]} for q in QUESTIONS])


# --- API : recommander les meilleurs champions selon les réponses
@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True) or {}
    answers = data.get("answers", {})
    max_results = int(data.get("max_results", 6))

    scored = []

    # On parcourt tous les champions de la base
    for champ in Champion.query.all():
        meta = champ.data
        s, reasons = score_with_answers(meta, answers)

        if s > 0:
            # Vérifie que l'icône est bien un lien complet (http)
            icon = meta.get("icon")
            if not icon or not str(icon).startswith("http"):
                icon = None

            scored.append({
                "champion": champ.name,
                "score": s,
                "reasons": reasons[:5],  # limite à 5 raisons affichées
                "icon": icon,
                "tags": [k for k, v in meta.items() if isinstance(v, bool) and v],
            })

    # Trie par score décroissant et renvoie les meilleurs résultats
    scored.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(scored[:max_results])


# ================================================================
#  🔐 ROUTES ADMIN (interface de gestion des champions)
# ================================================================

# --- Page admin (interface web)
@app.route("/admin")
def admin():
    champs = {c.name: c.data for c in Champion.query.all()}
    return render_template(
        "admin.html",
        champions=champs,
        reason_labels=REASON_LABELS,
        reason_weights=REASON_WEIGHTS
    )

# --- API : récupérer tous les champions (JSON)
@app.route("/api/champions", methods=["GET"])
def api_get_champions():
    champs = {c.name: c.data for c in Champion.query.all()}
    return jsonify(champs)

# --- API : sauvegarder les changements faits dans l'admin
@app.route("/api/champions", methods=["POST"])
def api_save_champions():
    data = request.get_json(force=True) or {}

    # On supprime tout et on réécrit (simple et efficace)
    Champion.query.delete()
    for name, meta in data.items():
        db.session.add(Champion(name=name, data=meta))
    db.session.commit()

    return jsonify({"status": "ok"})


# ================================================================
#  🚀 LANCEMENT LOCAL DE L’APPLICATION
# ================================================================
# (Sur Railway, Flask est lancé automatiquement via le Procfile)

if __name__ == "__main__":
    app.run(debug=True)
