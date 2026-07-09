import random

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cards.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    front = db.Column(db.Text, nullable=False)

    definition = db.Column(db.Text, default="")

    notes = db.Column(db.Text, default="")

    remembered = db.Column(db.Boolean, default=False, nullable=False)



with app.app_context():
    db.create_all()


@app.route("/")
def index():
    cards = Card.query.order_by(Card.id.desc()).all()
    return render_template("index.html", cards=cards)

@app.route("/list_tts")
def list_tts():
    cards = Card.query.order_by(Card.id.desc()).all()
    return render_template("list_tts.html", cards=cards)

@app.route("/new", methods=["GET", "POST"])
def new_card():

    if request.method == "POST":
        card = Card(
            front=request.form["front"],
            definition=request.form["definition"],
            notes=request.form["notes"],
        )
        db.session.add(card)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit.html", card=None)


@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_card(card_id):

    card = Card.query.get_or_404(card_id)

    if request.method == "POST":
        card.front = request.form["front"]
        card.definition = request.form["definition"]
        card.notes = request.form["notes"]

        db.session.commit()
        return redirect(url_for("index"))

    return render_template("edit.html", card=card)


@app.route("/delete/<int:card_id>")
def delete_card(card_id):

    card = Card.query.get_or_404(card_id)

    db.session.delete(card)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/review")
def review():

    cards = Card.query.all()

    if not cards:
        return render_template("review.html", card=None)

    card = random.choice(cards)

    return redirect(url_for("show_front", card_id=card.id))


@app.route("/review/<int:card_id>/front")
def show_front(card_id):

    card = Card.query.get_or_404(card_id)

    return render_template(
        "review.html",
        card=card,
        side="front",
    )


@app.route("/review/<int:card_id>/back")
def show_back(card_id):

    card = Card.query.get_or_404(card_id)

    return render_template(
        "review.html",
        card=card,
        side="back",
    )


@app.route("/next")
def next_card():

    cards = Card.query.all()

    if not cards:
        return redirect(url_for("review"))

    card = random.choice(cards)

    return redirect(url_for("show_front", card_id=card.id))


@app.route("/remembered/<int:card_id>", methods=["POST"])
def toggle_remembered(card_id):
    card = Card.query.get_or_404(card_id)
    data = request.get_json(silent=True) or {}
    remembered = data.get("remembered", request.form.get("remembered"))

    if remembered is None:
        return jsonify({"success": False, "error": "Missing remembered flag"}), 400

    if isinstance(remembered, bool):
        card.remembered = remembered
    else:
        card.remembered = str(remembered) in ("1", "true", "True", "yes", "on")

    db.session.commit()

    return jsonify({"success": True, "remembered": card.remembered})


if __name__ == "__main__":
    app.run(debug=True)
