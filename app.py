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
        clubs = request.get_json()
        if not isinstance(clubs, list):
            clubs = [clubs]
        all_added_clubs = []
        for i in clubs:
            all_added_clubs.append(
                add_club(code=i.get("code"), name=i.get("name"), description=i.get("description"), tag_names=i.get("tags")).as_json
            )
        return make_response(
            jsonify({"a_message": "Processed #Clubs: " + str(len(all_added_clubs)), "clubs": all_added_clubs}),
            http.HTTPStatus.OK,
        )

    elif request.method == "PUT":
        club_modification_request = request.get_json()
        if isinstance(club_modification_request, list):
            return make_response('Multiple Club Modification Not Allowed', http.HTTPStatus.METHOD_NOT_ALLOWED, )
        code = club_modification_request.get("code")
        if (code is not None):
            club = Club.query.filter_by(code=code).first()
            if (club is not None):
                name = club_modification_request.get("name")
                description = club_modification_request.get("description")
                tag_names = club_modification_request.get("tags")
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
    if request.method == "GET":
        return make_response(jsonify(get_all_users()), http.HTTPStatus.OK, )

    elif request.method == "POST":
        user_request = request.get_json()
        if isinstance(user_request, list):
            return make_response('Acting on multiple users not allowed', http.HTTPStatus.METHOD_NOT_ALLOWED, )
        name = user_request.get("name")
        username = user_request.get("username")
        email = user_request.get("email")
        gender = user_request.get("gender")
        year = user_request.get("year")
        if (name is not None) and (username is not None) and (email is not None) \
                and (gender is not None) and (year is not None):
            created_user = create_user(name=name, username=username, email=email, gender=gender, year=year)
            return make_response(jsonify(created_user.as_json), http.HTTPStatus.OK)
        else:
            return make_response('Missing information: need name, username, email, gender, and year',
                                 http.HTTPStatus.NOT_FOUND, )


@app.route('/api/users/<username>', methods=["GET"])
def users_username_action(username):
    return make_response(jsonify(get_user_by_username(username=username)), http.HTTPStatus.OK, )

@app.route('/api/users/<username>/favorites', methods=["GET", "PUT"])
def favorites_action(username):
    if (request.method == "GET"):
        return make_response(
            jsonify(
                get_user_by_username(username=username).get("favorite_clubs")
            ), http.HTTPStatus.OK,
        )
    elif (request.method == "PUT"):
        club_code = request.get_json().get("club_code")
        returnVal = add_favorite(username=username, club_code=club_code)
        if returnVal is not None:
            return make_response('', http.HTTPStatus.NO_CONTENT, )
        else:
            return make_response('User not found', http.HTTPStatus.NOT_FOUND, )

@app.route('/api/clubs/webscrape', methods=["POST"])
def webscrape_action():
    scraped_clubs = webscrape.scrape_clubs("https://ocwp.pennlabs.org/")
    for club in scraped_clubs:
        add_club(code=club.get("code"), name=club.get("name"), description=club.get("description"), tag_names=club.get("tags"))
    return make_response(
        jsonify({"a_message": "Added #Clubs: " + str(len(scraped_clubs)), "clubs": scraped_clubs}),
        http.HTTPStatus.OK,
    )
@app.route('/api/users/comment', methods=["POST", "PUT", "DELETE"])
def clubs_comment_action():
    comment_request = request.get_json()
    if isinstance(comment_request, list):
        return make_response('Acting on multiple comments not allowed', http.HTTPStatus.METHOD_NOT_ALLOWED, )
    returnVal = None

    if request.method == "POST":
        comment_text = comment_request.get("text")
        user_id = comment_request.get("user_id")
        club_id = comment_request.get("club_id")
        if (comment_text is not None) and (user_id is not None) and (club_id is not None):
            club = Club.query.filter_by(id=club_id).first()
            user = User.query.filter_by(id=user_id).first()
            if (club is not None) and (user is not None):
                returnVal = add_comment(club_id=club.id, user_id=user.id, comment_text=comment_text)
            else:
                return make_response('Club/User not found or comment not found',
                                     http.HTTPStatus.NOT_FOUND, )
        else:
            return make_response('Missing information: need comment text, user id, and club id',
                                 http.HTTPStatus.NOT_FOUND, )

    elif request.method == "PUT":
        comment_id = comment_request.get("comment_id")
        comment_text = comment_request.get("text")
        if (comment_text is not None) and (comment_id is not None):
            comment = Comment.query.filter_by(id=comment_id)
            if comment is not None:
                returnVal = modify_comment(comment_id=comment_id, comment_text=comment_text)
            else:
                return make_response('Comment not found',
                                     http.HTTPStatus.NOT_FOUND, )
        else:
            return make_response('Missing information: need comment text and comment id',
                                 http.HTTPStatus.NOT_FOUND, )

    elif request.method == "DELETE":
        comment_id = comment_request.get("comment_id")
        if comment_id is not None:
            comment = Comment.query.filter_by(id=comment_id)
            if comment is not None:
                returnVal = delete_comment(comment_id=comment_id)
            else:
                return make_response('Comment not found',
                                     http.HTTPStatus.NOT_FOUND, )
        else:
            return make_response('Missing information: need comment id',
                                 http.HTTPStatus.NOT_FOUND, )

    return make_response(jsonify(returnVal.as_json), http.HTTPStatus.OK, )
if __name__ == '__main__':
    app.run()
