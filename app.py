from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Refuge, Chien, Chien12Mois, Chat12Mois, Transfert
from datetime import date

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:3000",
    "https://spa-transferts-frontend.onrender.com"
]}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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


@app.route("/api/refuges/<int:id>", methods=["DELETE"])
def delete_refuge(id):
    refuge = Refuge.query.get_or_404(id)
    db.session.delete(refuge)
    db.session.commit()
    return jsonify({"message": "Refuge supprimé"}), 200


# ---------- ROUTES CHIENS ----------
@app.route('/api/chiens', methods=['GET'])
def get_chiens():
    chiens = Chien.query.all()
    return jsonify([c.to_dict() for c in chiens])


@app.route('/api/chiens', methods=['POST'])
def add_chien():
    data = request.json
    c = Chien(
        nom=data['nom'],
        age=data.get('age'),
        race=data.get('race'),
        refuge_id=data.get('refuge_id')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Chien ajouté'}), 201


@app.route("/api/chiens/<int:id>", methods=["PUT"])
def update_chien(id):
    chien = Chien.query.get_or_404(id)
    data = request.get_json()
    chien.nom = data.get("nom", chien.nom)
    chien.age = data.get("age", chien.age)
    chien.race = data.get("race", chien.race)
    chien.refuge_id = data.get("refuge_id", chien.refuge_id)
    db.session.commit()
    return jsonify({"message": "Chien mis à jour"}), 200


@app.route("/api/chiens/<int:id>", methods=["DELETE"])
def delete_chien(id):
    chien = Chien.query.get_or_404(id)
    db.session.delete(chien)
    db.session.commit()
    return jsonify({"message": "Chien supprimé"}), 200


# ---------- ROUTES CHIENS 12 MOIS ----------
@app.route('/api/chiens12', methods=['GET'])
def get_chiens12():
    chiens = Chien12Mois.query.all()
    return jsonify([{
        'id': c.id, 'nom': c.nom, 'age': c.age, 'race': c.race, 'refuge_id': c.refuge_id
    } for c in chiens])

@app.route('/api/chiens12', methods=['POST'])
def add_chien12():
    data = request.get_json()
    c = Chien12Mois(
        nom=data.get('nom'),
        age=data.get('age'),
        race=data.get('race'),
        refuge_id=data.get('refuge_id')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Chien 12 mois ajouté', 'id': c.id}), 201

@app.route('/api/chiens12/<int:cid>', methods=['PUT'])
def update_chien12(cid):
    c = Chien12Mois.query.get_or_404(cid)
    data = request.get_json()
    c.nom = data.get('nom', c.nom)
    c.age = data.get('age', c.age)
    c.race = data.get('race', c.race)
    c.refuge_id = data.get('refuge_id', c.refuge_id)
    db.session.commit()
    return jsonify({'message': 'Chien 12 mois modifié'})

@app.route('/api/chiens12/<int:cid>', methods=['DELETE'])
def delete_chien12(cid):
    c = Chien12Mois.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Chien 12 mois supprimé'})


# ---------- ROUTES CHATS 12 MOIS ----------
@app.route('/api/chats12', methods=['GET'])
def get_chats12():
    chats = Chat12Mois.query.all()
    return jsonify([c.to_dict() for c in chats])


@app.route('/api/chats12', methods=['POST'])
def add_chat12():
    data = request.get_json()
    c = Chat12Mois(
        nom=data.get('nom'),
        age=data.get('age'),
        race=data.get('race'),
        refuge_id=data.get('refuge_id')
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'message': 'Chat 12 mois ajouté', 'id': c.id}), 201


@app.route('/api/chats12/<int:id>', methods=['PUT'])
def update_chat12(id):
    c = Chat12Mois.query.get_or_404(id)
    data = request.get_json()
    c.nom = data.get('nom', c.nom)
    c.age = data.get('age', c.age)
    c.race = data.get('race', c.race)
    c.refuge_id = data.get('refuge_id', c.refuge_id)
    db.session.commit()
    return jsonify({'message': 'Chat 12 mois mis à jour'})


@app.route('/api/chats12/<int:id>', methods=['DELETE'])
def delete_chat12(id):
    c = Chat12Mois.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Chat 12 mois supprimé'})


# ---------- ROUTES TRANSFERTS ----------
@app.route('/api/transferts', methods=['GET'])
def get_transferts():
    transferts = Transfert.query.all()
    return jsonify([t.to_dict() for t in transferts])


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
    return jsonify({'message': 'Transfert ajouté'}), 201


@app.route("/api/transferts/<int:id>", methods=["PUT"])
def update_transfert(id):
    transfert = Transfert.query.get_or_404(id)
    data = request.get_json()
    transfert.chien_id = data.get("chien_id", transfert.chien_id)
    transfert.refuge_depart_id = data.get("refuge_depart_id", transfert.refuge_depart_id)
    transfert.refuge_arrivee_id = data.get("refuge_arrivee_id", transfert.refuge_arrivee_id)
    transfert.statut = data.get("statut", transfert.statut)
    db.session.commit()
    return jsonify({"message": "Transfert mis à jour"}), 200


@app.route("/api/transferts/<int:id>", methods=["DELETE"])
def delete_transfert(id):
    transfert = Transfert.query.get_or_404(id)
    db.session.delete(transfert)
    db.session.commit()
    return jsonify({"message": "Transfert supprimé"}), 200


# ---------- LANCEMENT SERVEUR ----------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render fournit PORT
    # pas de reloader en prod (debug False)
    app.run(host="0.0.0.0", port=port, debug=False)
