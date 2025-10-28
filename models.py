from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------- MODELE REFUGE ----------
class Refuge(db.Model):
    __tablename__ = "refuges"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    responsable = db.Column(db.String(100))
    telephone = db.Column(db.String(50))
    adresse = db.Column(db.String(200))

    chiens = db.relationship("Chien", backref="refuge", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "responsable": self.responsable,
            "telephone": self.telephone,
            "adresse": self.adresse,
        }


# ---------- MODELE CHIEN ----------
class Chien(db.Model):
    __tablename__ = "chiens"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    race = db.Column(db.String(100))
    refuge_id = db.Column(db.Integer, db.ForeignKey("refuges.id"), nullable=True)

    transferts = db.relationship("Transfert", backref="chien", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "age": self.age,
            "race": self.race,
            "refuge_id": self.refuge_id,
        }


# ---------- MODELE TRANSFERT ----------
class Transfert(db.Model):
    __tablename__ = "transferts"
    id = db.Column(db.Integer, primary_key=True)
    chien_id = db.Column(db.Integer, db.ForeignKey("chiens.id"), nullable=False)
    refuge_depart_id = db.Column(db.Integer, db.ForeignKey("refuges.id"), nullable=False)
    refuge_arrivee_id = db.Column(db.Integer, db.ForeignKey("refuges.id"), nullable=False)
    date_transfert = db.Column(db.Date)
    statut = db.Column(db.String(50), default="En attente")

    def to_dict(self):
        return {
            "id": self.id,
            "chien_id": self.chien_id,
            "refuge_depart_id": self.refuge_depart_id,
            "refuge_arrivee_id": self.refuge_arrivee_id,
            "date_transfert": self.date_transfert.isoformat() if self.date_transfert else None,
            "statut": self.statut,
        }
