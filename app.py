# app.py
import os
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import text, inspect  # <-- inspect pour introspection cross-DB

from models import db, Refuge, Chien, Chien12Mois, Chat12Mois, Transfert

app = Flask(__name__)

# ---------------- CORS ----------------
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "https://spa-transferts-frontend.onrender.com",
    # ajoute ici ton domaine custom si besoin, ex. "https://transferts.la-spa.fr"
]}})

# ------------- Base de données -------------
# Local: SQLite ; Render: PostgreSQL via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # compat psycopg/SQLAlchemy
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# --------- MIGRATION AUTO (Postgres & SQLite) ----------
def ensure_transferts_columns():
    """
    Ajoute les colonnes manquantes (animal_type, animal_id, chien_id) dans la table 'transferts'.
    Compatible PostgreSQL & SQLite (via SQLAlchemy Inspector).
    """
    with app.app_context():
        engine = db.engine
        insp = inspect(engine)
        try:
            existing_cols = {col["name"] for col in insp.get_columns("transferts")}
        except Exception:
            # Table pas encore créée
            return

        # Colonnes à ajouter si absentes
        missing = []
        if "animal_type" not in existing_cols:
            missing.append(("animal_type", "VARCHAR(20)"))
        if "animal_id" not in existing_cols:
            missing.append(("animal_id", "INTEGER"))
        if "chien_id" not in existing_cols:
            missing.append(("chien_id", "INTEGER"))

        if not missing:
            return

        dialect = engine.dialect.name  # 'postgresql' ou 'sqlite'

        with engine.connect() as conn:
            for name, coltype in missing:
                if dialect == "postgresql":
                    # Postgres supporte IF NOT EXISTS
                    conn.execute(text(f'ALTER TABLE transferts ADD COLUMN IF NOT EXISTS {name} {coltype}'))
                else:
                    # SQLite: pas de IF NOT EXISTS, on re-vérifie à chaque passage
                    now_cols = {c["name"] for c in inspect(engine).get_columns("transferts")}
                    if name not in now_cols:
                        conn.execute(text(f'ALTER TABLE transferts ADD COLUMN {name} {coltype}'))


# Création des tables + migration auto
with app.app_context():
    db.create_all()
    ensure_transferts_columns()
    print("✅ Base de données initialisée (migration auto OK)")


# ------------------- REFUGES -------------------
@app.route("/api/refuges", methods=["GET", "POST"])
def handle_refuges():
    if request.method == "GET":
        refuges = Refuge.query.all()
        return jsonify([r.to_dict() for r in refuges])

    data = request.get_json(force=True)
    r = Refuge(
        nom=data.get("nom"),
        responsable=data.get("responsable"),
        telephone=data.get("telephone"),
        adresse=data.get("adresse"),
    )
    db.session.add(r)
    db.session.commit()
    return jsonify(r.to_dict()), 201


@app.route("/api/refuges/<int:id>", methods=["PUT"])
def update_refuge(id):
    refuge = Refuge.query.get_or_404(id)
    data = request.get_json(force=True)
    refuge.nom = data.get("nom", refuge.nom)
    refuge.responsable = data.get("responsable", refuge.responsable)
    refuge.telephone = data.get("telephone", refuge.telephone)
    refuge.adresse = data.get("adresse", refuge.adresse)
    db.session.commit()
    return jsonify(refuge.to_dict()), 200


@app.route("/api/refuges/<int:id>", methods=["DELETE"])
def delete_refuge(id):
    refuge = Refuge.query.get_or_404(id)
    db.session.delete(refuge)
    db.session.commit()
    return jsonify({"message": "Refuge supprimé"}), 200


# ------------------- CHIENS -------------------
@app.route("/api/chiens", methods=["GET"])
def get_chiens():
    return jsonify([c.to_dict() for c in Chien.query.all()])


@app.route("/api/chiens", methods=["POST"])
def add_chien():
    data = request.get_json(force=True)
    c = Chien(
        nom=data["nom"],
        age=data.get("age"),
        race=data.get("race"),
        refuge_id=data.get("refuge_id"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "Chien ajouté"}), 201


@app.route("/api/chiens/<int:id>", methods=["PUT"])
def update_chien(id):
    c = Chien.query.get_or_404(id)
    data = request.get_json(force=True)
    c.nom = data.get("nom", c.nom)
    c.age = data.get("age", c.age)
    c.race = data.get("race", c.race)
    c.refuge_id = data.get("refuge_id", c.refuge_id)
    db.session.commit()
    return jsonify({"message": "Chien mis à jour"}), 200


@app.route("/api/chiens/<int:id>", methods=["DELETE"])
def delete_chien(id):
    c = Chien.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Chien supprimé"}), 200


# --------------- CHIENS 12 MOIS ----------------
@app.route("/api/chiens12", methods=["GET"])
def get_chiens12():
    return jsonify([c.to_dict() for c in Chien12Mois.query.all()])


@app.route("/api/chiens12", methods=["POST"])
def add_chien12():
    data = request.get_json(force=True)
    c = Chien12Mois(
        nom=data.get("nom"),
        age=data.get("age"),
        race=data.get("race"),
        refuge_id=data.get("refuge_id"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "Chien 12 mois ajouté", "id": c.id}), 201


@app.route("/api/chiens12/<int:id>", methods=["PUT"])
def update_chien12(id):
    c = Chien12Mois.query.get_or_404(id)
    data = request.get_json(force=True)
    c.nom = data.get("nom", c.nom)
    c.age = data.get("age", c.age)
    c.race = data.get("race", c.race)
    c.refuge_id = data.get("refuge_id", c.refuge_id)
    db.session.commit()
    return jsonify({"message": "Chien 12 mois modifié"}), 200


@app.route("/api/chiens12/<int:id>", methods=["DELETE"])
def delete_chien12(id):
    c = Chien12Mois.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Chien 12 mois supprimé"}), 200


# ---------------- CHATS 12 MOIS ----------------
@app.route("/api/chats12", methods=["GET"])
def get_chats12():
    return jsonify([c.to_dict() for c in Chat12Mois.query.all()])


@app.route("/api/chats12", methods=["POST"])
def add_chat12():
    data = request.get_json(force=True)
    c = Chat12Mois(
        nom=data.get("nom"),
        age=data.get("age"),
        race=data.get("race"),
        refuge_id=data.get("refuge_id"),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "Chat 12 mois ajouté", "id": c.id}), 201


@app.route("/api/chats12/<int:id>", methods=["PUT"])
def update_chat12(id):
    c = Chat12Mois.query.get_or_404(id)
    data = request.get_json(force=True)
    c.nom = data.get("nom", c.nom)
    c.age = data.get("age", c.age)
    c.race = data.get("race", c.race)
    c.refuge_id = data.get("refuge_id", c.refuge_id)
    db.session.commit()
    return jsonify({"message": "Chat 12 mois modifié"}), 200


@app.route("/api/chats12/<int:id>", methods=["DELETE"])
def delete_chat12(id):
    c = Chat12Mois.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Chat 12 mois supprimé"}), 200


# -------------- LISTE UNIFIÉE ANIMAUX ----------
@app.route("/api/animaux", methods=["GET"])
def get_animaux():
    chiens = [{"id": c.id, "nom": c.nom, "type": "chien"} for c in Chien.query.all()]
    chiens12 = [{"id": c.id, "nom": c.nom, "type": "chien12"} for c in Chien12Mois.query.all()]
    chats12 = [{"id": c.id, "nom": c.nom, "type": "chat12"} for c in Chat12Mois.query.all()]
    return jsonify(chiens + chiens12 + chats12)


# ------------------ TRANSFERTS -----------------
@app.route("/api/transferts", methods=["GET"])
def get_transferts():
    try:
        transferts = Transfert.query.all()
        return jsonify([t.to_dict() for t in transferts])
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "serialization_error", "detail": str(e)}), 500


@app.route("/api/transferts", methods=["POST"])
def add_transfert():
    data = request.get_json(force=True)

    animal_type = data.get("animal_type")     # "chien" | "chien12" | "chat12"
    animal_id   = data.get("animal_id")

    # Compat ancien format
    if not animal_type and data.get("chien_id"):
        animal_type = "chien"
        animal_id = data.get("chien_id")

    # Champs obligatoires
    if not data.get("refuge_depart_id") or not data.get("refuge_arrivee_id"):
        return jsonify({"error": "bad_request", "detail": "refuge_depart_id et refuge_arrivee_id sont requis"}), 400

    t = Transfert(
        animal_type=animal_type,
        animal_id=animal_id,
        chien_id=data.get("chien_id"),  # compat éventuelle
        refuge_depart_id=data["refuge_depart_id"],
        refuge_arrivee_id=data["refuge_arrivee_id"],
        date_transfert=date.today(),
        statut=data.get("statut", "En attente"),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"message": "Transfert ajouté"}), 201


@app.route("/api/transferts/<int:id>", methods=["PUT"])
def update_transfert(id):
    t = Transfert.query.get_or_404(id)
    data = request.get_json(force=True)

    if "animal_type" in data:
        t.animal_type = data["animal_type"]
    if "animal_id" in data:
        t.animal_id = data["animal_id"]

    # Compat ancien format
    if "chien_id" in data:
        t.chien_id = data["chien_id"]
        if data["chien_id"] is not None:
            t.animal_type = "chien"
            t.animal_id = data["chien_id"]

    t.refuge_depart_id = data.get("refuge_depart_id", t.refuge_depart_id)
    t.refuge_arrivee_id = data.get("refuge_arrivee_id", t.refuge_arrivee_id)
    t.statut = data.get("statut", t.statut)

    db.session.commit()
    return jsonify({"message": "Transfert mis à jour"}), 200


@app.route("/api/transferts/<int:id>", methods=["DELETE"])
def delete_transfert(id):
    t = Transfert.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Transfert supprimé"}), 200


# -------------- RUN -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render fournit PORT
    app.run(host="0.0.0.0", port=port, debug=False)
