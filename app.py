"""Wild Drafter — application Flask principale.

Cette réécriture consolide toutes les attentes fonctionnelles :
- base de données de champions accessible côté serveur uniquement ;
- recommandations calculées sur les réponses et un éventuel payload local ;
- proposition de modifications via export explicite depuis le navigateur ;
- icône placeholder commune pour sécuriser l'affichage.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Tuple

from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

###############################################################################
# Configuration de l'application
###############################################################################

app = Flask(__name__, instance_relative_config=True)
app.config.setdefault("SQLALCHEMY_DATABASE_URI", os.getenv("DATABASE_URL", "sqlite:///champions.db"))
app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
app.config.setdefault("JSON_AS_ASCII", False)

db = SQLAlchemy(app)

###############################################################################
# Modèle de données
###############################################################################


class Champion(db.Model):
    __tablename__ = "champions"

    name = db.Column(db.String(80), primary_key=True)
    data = db.Column(db.JSON, nullable=False)


###############################################################################
# Questions / attributs manipulés sur l'interface
###############################################################################

Question = Tuple[str, str, int]

QUESTIONS: List[Question] = [
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

REASON_LABELS: Dict[str, str] = {
    "heavy_ad": "Bon vs AD",
    "heavy_ap": "Bon vs AP",
    "need_engage": "Engage",
    "need_cc": "Contrôle",
    "frontline": "Frontline",
    "peeling": "Peeling",
    "invade": "Solo invade",
    "scaling": "Scaling",
    "early_game": "Early game",
    "ally_melee": "Synergie melee",
    "hp_tanks": "Fort vs HP",
    "aa_heavy": "Fort vs AA",
    "enchanter_adc": "Enchant ADC",
    "lock_target": "Target lock",
    "range_heavy": "Fort vs ranges",
}

REASON_WEIGHTS: Dict[str, int] = {key: weight for _, key, weight in QUESTIONS}

###############################################################################
# Utilitaires
###############################################################################


def ensure_database_seeded() -> None:
    """Insère le dump JSON de champions dans la base si vide."""

    with app.app_context():
        db.create_all()
        if Champion.query.first() is not None:
            return

        dump_path = Path("champions.json")
        if not dump_path.exists():
            return

        with dump_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        for name, meta in data.items():
            db.session.add(Champion(name=name, data=meta))
        db.session.commit()


def iter_champions_from_payload(payload: Dict[str, Dict]) -> Iterator[Tuple[str, Dict]]:
    for name, meta in payload.items():
        if isinstance(name, str) and isinstance(meta, dict):
            yield name, meta


def iter_champions_from_db() -> Iterator[Tuple[str, Dict]]:
    for champion in Champion.query.order_by(Champion.name.asc()).all():
        yield champion.name, champion.data or {}


def resolve_icon(meta: Dict, default_icon: str) -> str:
    icon_value = meta.get("icon") if isinstance(meta, dict) else None
    if isinstance(icon_value, str) and icon_value.strip():
        if icon_value.startswith(("http://", "https://", "/")):
            return icon_value
    return default_icon


def compute_score(meta: Dict, answers: Dict[str, bool]) -> Tuple[int, List[Dict[str, object]]]:
    score = 0
    reasons: List[Dict[str, object]] = []
    for _, key, weight in QUESTIONS:
        if answers.get(key) and meta.get(key):
            score += weight
            reasons.append({
                "key": key,
                "label": REASON_LABELS.get(key, key),
                "weight": weight,
            })
    return score, reasons


def build_recommendations(source: Iterable[Tuple[str, Dict]], answers: Dict[str, bool], default_icon: str) -> List[Dict]:
    recommendations: List[Dict] = []
    for name, meta in source:
        score, reasons = compute_score(meta, answers)
        if score <= 0:
            continue
        active_tags = [key for key, value in meta.items() if isinstance(value, bool) and value]
        recommendations.append(
            {
                "champion": name,
                "score": score,
                "reasons": sorted(reasons, key=lambda item: item["weight"], reverse=True)[:5],
                "icon": resolve_icon(meta, default_icon),
                "tags": active_tags,
            }
        )

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    return recommendations


def clamp_max_results(value: int) -> int:
    return max(1, min(30, value))


def record_proposal(payload: Dict) -> str:
    proposals_dir = Path(app.instance_path) / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    filename = proposals_dir / f"champions_{timestamp}.json"
    with filename.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return filename.name


###############################################################################
# Hooks de contexte
###############################################################################


@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.utcnow().year,
    }


###############################################################################
# Routes HTTP
###############################################################################


@app.route("/")
def index():
    return render_template("index.html", q_count=len(QUESTIONS))


@app.route("/changelog")
def changelog():
    return render_template("changelog.html")


@app.route("/questions")
def get_questions():
    payload = [
        {"text": text, "key": key, "weight": weight}
        for text, key, weight in QUESTIONS
    ]
    return jsonify(payload)


@app.route("/recommend", methods=["POST"])
def recommend():
    request_data = request.get_json(force=True, silent=True) or {}
    answers = request_data.get("answers") or {}
    if not isinstance(answers, dict):
        return jsonify([])

    max_results = clamp_max_results(int(request_data.get("max_results", 6)))

    payload = request_data.get("payload")
    if isinstance(payload, dict):
        source = iter_champions_from_payload(payload)
    else:
        source = iter_champions_from_db()

    default_icon = url_for("static", filename="icons/default.png")
    recommendations = build_recommendations(source, answers, default_icon)
    return jsonify(recommendations[:max_results])


@app.route("/admin")
def admin_panel():
    champions = {name: data for name, data in iter_champions_from_db()}
    return render_template(
        "admin.html",
        champions=champions,
        reason_labels=REASON_LABELS,
        reason_weights=REASON_WEIGHTS,
        default_icon=url_for("static", filename="icons/default.png"),
    )


@app.route("/api/champions")
def api_get_champions():
    return jsonify({name: data for name, data in iter_champions_from_db()})


@app.route("/api/champions", methods=["POST"])
def api_propose_champions():
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, dict):
        return jsonify({"status": "invalid", "message": "Payload invalide"}), 400

    proposal_name = record_proposal(payload)
    return jsonify(
        {
            "status": "received",
            "proposal": proposal_name,
            "message": "La proposition a été sauvegardée pour revue.",
        }
    )


###############################################################################
# Initialisation
###############################################################################


ensure_database_seeded()

if __name__ == "__main__":
    app.run(debug=True)
