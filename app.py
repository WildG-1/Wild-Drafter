# ================================================================
#  app.py — Application principale Flask pour LoL Wild's Picks
#  Version persistante (PostgreSQL - Railway)
# ================================================================

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json, os

# ================================================================
#  ⚙️ CONFIGURATION DE L’APPLICATION
# ================================================================

app = Flask(__name__)

# Railway fournit la variable d'environnement DATABASE_URL automatiquement
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///champions.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


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
#  🗄️ BASE DE DONNÉES PERSISTANTE
# ================================================================

class Champion(db.Model):
    name = db.Column(db.String(80), primary_key=True)
    data = db.Column(db.JSON, nullable=False)


with app.app_context():
    db.create_all()
    # Si la base est vide, on initialise avec champions.json
    if not Champion.query.first() and os.path.exists("champions.json"):
        with open("champions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for name, meta in data.items():
                db.session.add(Champion(name=name, data=meta))
            db.session.commit()


# ================================================================
#  🧮 SYSTÈME DE SCORING DES CHAMPIONS
# ================================================================

def score_with_answers(meta: dict, answers: dict):
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
#  🌐 ROUTES UTILISATEUR
# ================================================================

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", q_count=len(QUESTIONS))


@app.route("/questions", methods=["GET"])
def get_questions():
    return jsonify([{"text": q[0], "key": q[1], "weight": q[2]} for q in QUESTIONS])


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True) or {}
    answers = data.get("answers", {})
    max_results = int(data.get("max_results", 6))

    scored = []
    for champ in Champion.query.all():
        meta = champ.data
        s, reasons = score_with_answers(meta, answers)
        if s > 0:
            icon = meta.get("icon")
            if not icon or not str(icon).startswith("http"):
                icon = None
            scored.append({
                "champion": champ.name,
                "score": s,
                "reasons": reasons[:5],
                "icon": icon,
                "tags": [k for k, v in meta.items() if isinstance(v, bool) and v],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(scored[:max_results])


# ================================================================
#  🔐 ADMINISTRATION
# ================================================================

@app.route("/admin")
def admin():
    champs = {c.name: c.data for c in Champion.query.all()}
    return render_template("admin.html", champions=champs, reason_labels=REASON_LABELS)


@app.route("/api/champions", methods=["GET"])
def api_get_champions():
    champs = {c.name: c.data for c in Champion.query.all()}
    return jsonify(champs)


@app.route("/api/champions", methods=["POST"])
def api_save_champions():
    data = request.get_json(force=True) or {}
    Champion.query.delete()
    for name, meta in data.items():
        db.session.add(Champion(name=name, data=meta))
    db.session.commit()
    return jsonify({"status": "ok"})


# ================================================================
#  🚀 MAIN
# ================================================================

if __name__ == "__main__":
    app.run(debug=True)
