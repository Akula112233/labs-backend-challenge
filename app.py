import http
from sqlalchemy import func
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import webscrape

# DB_FILE = "clubreview.db"
DB_FILE = "db.sqlite3"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from bootstrap import *


@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return make_response(jsonify({"message": "Welcome to the Penn Club Review API!."}), 200,)


@app.route('/api/clubs', methods=["GET", "POST", "PUT"])
def clubs_action():
    if request.method == "GET":
        return make_response(jsonify(get_all_clubs()), http.HTTPStatus.OK, )
    elif request.method == "POST":
        print("got here")
        clubs = request.get_json()
        print("got here")
        print("Is clubs a list? --> " + str(isinstance(clubs, list)))
        if not isinstance(clubs, list):
            clubs = [clubs]
        for i in clubs:
            add_club(code=i["code"], name=i["name"], description=i["description"], tag_names=i["tags"])
        return make_response('Added ' + str(len(clubs)), http.HTTPStatus.OK, )
    elif request.method == "PUT":
        club_modification_request = request.get_json()
        print("Is clubs_modification a list? --> " + str(isinstance(club_modification_request, list)))
        if isinstance(club_modification_request, list):
            return make_response('Multiple Club Modification Not Allowed', http.HTTPStatus.METHOD_NOT_ALLOWED, )
        code = club_modification_request["code"]
        if (code is not None):
            club = Club.query.filter_by(code=code).first()
            if (club is not None):
                name = club_modification_request["name"]
                description = club_modification_request["description"]
                tag_names = club_modification_request["tags"]
                modified_club = modify_club(club=club,name=name, description=description, tag_names=tag_names)
                return make_response(jsonify(modified_club.as_json), http.HTTPStatus.OK, )
            else:
                return make_response('Club not found', http.HTTPStatus.NOT_FOUND, )
        else:
            return make_response('Code not provided', http.HTTPStatus.NOT_FOUND, )

@app.route('/api/clubs/search/<club_substring>', methods=["GET"])
def clubs_substring_action(club_substring):
    clubs = Club.query.filter(func.lower(Club.name).contains(club_substring.lower()))
    return make_response(
        jsonify(
            [i.as_json for i in clubs]
        ),
        http.HTTPStatus.OK
    )

@app.route('/api/clubs/tags', methods=["GET"])
def clubs_tags_action():
    return make_response(jsonify(get_all_tags()), http.HTTPStatus.OK, )


@app.route('/api/users', methods=["GET", "POST"])
def users_action():
    if (request.method == "GET"):
        return make_response(jsonify(get_all_users()), http.HTTPStatus.OK, )
    elif (request.method == "POST"):
        clubs = request.get_json()
        all_clubs = []
        for i in clubs:
            all_clubs.append(add_club(code=i["code"], name=i["name"], description=i["description"], tag_names=i["tags"]))
        return make_response('', http.HTTPStatus.NO_CONTENT, )

@app.route('/api/users/<username>', methods=["GET"])
def users_username_action(username):
    return make_response(jsonify(get_user_by_username(username=username)), http.HTTPStatus.OK, )

@app.route('/api/users/<username>/favorites', methods=["GET", "PUT"])
def favorites_action(username):
    if (request.method == "GET"):
        return make_response(
            jsonify(
                get_user_by_username(username=username)["favorite_clubs"]
            ), http.HTTPStatus.OK,
        )
    elif (request.method == "PUT"):
        club_code = request.get_json()["club_code"]
        print("Club Code Is: " + str(club_code))
        returnVal = add_favorite(username=username, club_code=club_code)
        if returnVal is not None:
            return make_response('', http.HTTPStatus.NO_CONTENT, )
        else:
            return make_response('User not found', http.HTTPStatus.NOT_FOUND, )

@app.route('/api/clubs/webscrape', methods=["GET"])
def webscrape_action():
    webscraped_clubs = webscrape.scrape_clubs("https://ocwp.pennlabs.org/")
    for club in webscraped_clubs:
        add_club(code=club["code"], name=club["name"], description=club["description"], tag_names=club["tags"])
    return make_response(
        jsonify(
            webscraped_clubs
        ), http.HTTPStatus.OK,
    )


if __name__ == '__main__':
    app.run()
