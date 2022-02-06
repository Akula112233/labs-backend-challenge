from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy

# DB_FILE = "clubreview.db"
DB_FILE = "db.sqlite3"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *
from bootstrap import *


@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route('/api/clubs', methods=["GET", "POST"])
def clubs_action():
    if (request.method == "GET"):
        return jsonify(get_all_clubs())
    elif (request.method == "POST"):
        clubs = request.get_json()
        for i in clubs:
            add_club(code=i["code"], name=i["name"], description=i["description"], tag_names=i["tags"])


if __name__ == '__main__':
    app.run()
