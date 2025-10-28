from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Refuge, Chien, Transfert
from datetime import date

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Création de la base si elle n’existe pas encore
with app.app_context():
    db.create_all()
    print("✅ Base de données initialisée")

# ---------- ROUTES REFUGES ----------
@app.route("/api/refuges", methods=["GET", "POST"])
def handle_refuges():
    if request.method == "GET":
        refuges = Refuge.query.all()
        return jsonify([r.to_dict() for r in refuges])

    if request.method == "POST":
        data = request.get_json()
        nouveau_refuge = Refuge(
            nom=data.get("nom"),
            responsable=data.get("responsable"),
            telephone=data.get("telephone"),
            adresse=data.get("adresse")
        )
        db.session.add(nouveau_refuge)
        db.session.commit()
        return jsonify(nouveau_refuge.to_dict()), 201

# ---------- MISE À JOUR D’UN REFUGE ----------
@app.route("/api/refuges/<int:id>", methods=["PUT"])
def update_refuge(id):
    refuge = Refuge.query.get_or_404(id)
    data = request.get_json()

    refuge.nom = data.get("nom", refuge.nom)
    refuge.responsable = data.get("responsable", refuge.responsable)
    refuge.telephone = data.get("telephone", refuge.telephone)
    refuge.adresse = data.get("adresse", refuge.adresse)

    db.session.commit()
    return jsonify(refuge.to_dict()), 200


# ---------- SUPPRESSION D’UN REFUGE ----------
@app.route("/api/refuges/<int:id>", methods=["DELETE"])
def delete_refuge(id):
    refuge = Refuge.query.get_or_404(id)
    db.session.delete(refuge)
    db.session.commit()
    return jsonify({"message": "Refuge supprimé avec succès"}), 200


# ---------- ROUTES CHIENS ----------
@app.route('/api/chiens', methods=['GET'])
def get_chiens():
    chiens = Chien.query.all()
    return jsonify([
        {'id': c.id, 'nom': c.nom, 'age': c.age, 'race': c.race, 'refuge_id': c.refuge_id}
        for c in chiens
    ])

@app.route('/api/chiens', methods=['POST'])
def add_chien():
    data = request.json
    chien = Chien(
        nom=data['nom'],
        age=data.get('age'),
        race=data.get('race'),
        refuge_id=data.get('refuge_id')
    )
    db.session.add(chien)
    db.session.commit()
    return jsonify({'message': 'Chien ajouté avec succès'}), 201

# ---------- MISE À JOUR D’UN CHIEN ----------
@app.route("/api/chiens/<int:id>", methods=["PUT"])
def update_chien(id):
    chien = Chien.query.get_or_404(id)
    data = request.get_json()

    chien.nom = data.get("nom", chien.nom)
    chien.age = data.get("age", chien.age)
    chien.race = data.get("race", chien.race)
    chien.refuge_id = data.get("refuge_id", chien.refuge_id)

    db.session.commit()
    return jsonify({"message": "Chien mis à jour avec succès"}), 200


# ---------- SUPPRESSION D’UN CHIEN ----------
@app.route("/api/chiens/<int:id>", methods=["DELETE"])
def delete_chien(id):
    chien = Chien.query.get_or_404(id)
    db.session.delete(chien)
    db.session.commit()
    return jsonify({"message": "Chien supprimé avec succès"}), 200


# ---------- ROUTES TRANSFERTS ----------
@app.route('/api/transferts', methods=['GET'])
def get_transferts():
    transferts = Transfert.query.all()
    return jsonify([
        {
            'id': t.id,
            'chien_id': t.chien_id,
            'refuge_depart_id': t.refuge_depart_id,
            'refuge_arrivee_id': t.refuge_arrivee_id,
            'date_transfert': t.date_transfert.isoformat() if t.date_transfert else None,
            'statut': t.statut
        }
        for t in transferts
    ])

@app.route('/api/transferts', methods=['POST'])
def add_transfert():
    data = request.json
    transfert = Transfert(
        chien_id=data['chien_id'],
        refuge_depart_id=data['refuge_depart_id'],
        refuge_arrivee_id=data['refuge_arrivee_id'],
        date_transfert=date.today(),
        statut=data.get('statut', 'En attente')
    )
    db.session.add(transfert)
    db.session.commit()
    return jsonify({'message': 'Transfert ajouté avec succès'}), 201

# ---------- MISE À JOUR D’UN TRANSFERT ----------
@app.route("/api/transferts/<int:id>", methods=["PUT"])
def update_transfert(id):
    transfert = Transfert.query.get_or_404(id)
    data = request.get_json()

    transfert.chien_id = data.get("chien_id", transfert.chien_id)
    transfert.refuge_depart_id = data.get("refuge_depart_id", transfert.refuge_depart_id)
    transfert.refuge_arrivee_id = data.get("refuge_arrivee_id", transfert.refuge_arrivee_id)
    transfert.statut = data.get("statut", transfert.statut)
    db.session.commit()

    return jsonify({"message": "Transfert mis à jour avec succès"}), 200


# ---------- SUPPRESSION D’UN TRANSFERT ----------
@app.route("/api/transferts/<int:id>", methods=["DELETE"])
def delete_transfert(id):
    transfert = Transfert.query.get_or_404(id)
    db.session.delete(transfert)
    db.session.commit()
    return jsonify({"message": "Transfert supprimé avec succès"}), 200


# ---------- LANCEMENT SERVEUR ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

