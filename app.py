import http
from sqlalchemy import func
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import webscrape

DB_FILE = "clubreview.db"
# DB_FILE = "db.sqlite3"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from bootstrap import *

'''
Main route, left untouched
'''
@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

'''
Route untouched (just wrapped in make_response)
'''
@app.route('/api')
def api():
    return make_response(jsonify({"message": "Welcome to the Penn Club Review API!."}), 200,)

'''
Route accepts GET for seeing all clubs
Route accepts POST for adding single club or list of clubs
Route accepts PUT for modifying a single club (everything but club_code is optional)
'''
@app.route('/api/clubs', methods=["GET", "POST", "PUT"])
def clubs_action():
    #Request to get all clubs
    if request.method == "GET":
        return make_response(jsonify(get_all_clubs()), http.HTTPStatus.OK, )


    #Request to add club(s), only adds if club with same code doesn't exist already
    elif request.method == "POST":
        clubs = request.get_json()
        if not isinstance(clubs, list): #If a single club is requested, make it a single-item list to reuse code below
            clubs = [clubs]
        all_added_clubs = []
        for i in clubs:
            all_added_clubs.append(
                add_club(code=i.get("code"), name=i.get("name"), description=i.get("description"),
                         tag_names=i.get("tags")).as_json
            )
        return make_response(
            jsonify({"a_message": "Processed #Clubs: " + str(len(all_added_clubs)), "clubs": all_added_clubs}),
            http.HTTPStatus.OK,
        )


    #Request to modify a club, only modifies storage if code is provided and club is found
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

'''
This route takes a URL identifier string and finds clubs that contain that string
Case insensitive!
'''
@app.route('/api/clubs/search/<club_substring>', methods=["GET"])
def clubs_substring_action(club_substring):
    clubs = Club.query.filter(func.lower(Club.name).contains(club_substring.lower()))
    return make_response(
        jsonify(
            [i.as_json for i in clubs]
        ),
        http.HTTPStatus.OK
    )

'''
This route returns all tags and their respective amount of associated clubs
'''
@app.route('/api/clubs/tags', methods=["GET"])
def clubs_tags_action():
    return make_response(jsonify(get_all_tags()), http.HTTPStatus.OK, )

'''
This route accepts GET to view all data for all users
This route accepts POST to add new users to storage ****Custom Route #1*****
'''
@app.route('/api/users', methods=["GET", "POST"])
def users_action():
    #Route for getting all data for all users
    if request.method == "GET":
        return make_response(jsonify(get_all_users()), http.HTTPStatus.OK, )


    #Route for adding a single user, only works if all data is provided and username is unique
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


'''
This route takes a username URL identifier to search for a specific user
It only returns data that should be publicly accessible (ex: by other clubs)
'''
@app.route('/api/users/<username>', methods=["GET"])
def users_username_action(username):
    return make_response(jsonify(get_user_by_username(username=username)), http.HTTPStatus.OK, )

'''
This route takes a username URL identifier to perform actions on a specific user
On a GET request, this route returns the favorite clubs of a user
On a POST request, this route adds a club to a user's favorites.
    If a club is already favorited and this route is called, the club will be removed 
    from that user's favorite clubs (like a toggle function)
'''
@app.route('/api/users/<username>/favorites', methods=["GET", "PUT"])
def favorites_action(username):
    #GET request returns user's favorite clubs
    if (request.method == "GET"):
        return make_response(
            jsonify(
                get_user_by_username(username=username).get("favorite_clubs")
            ), http.HTTPStatus.OK,
        )


    #PUT request modifies a user's favorite clubs (add or remove) only if user is found
    elif (request.method == "PUT"):
        club_code = request.get_json().get("club_code")
        returnVal = add_favorite(username=username, club_code=club_code)
        if returnVal is not None:
            return make_response('', http.HTTPStatus.NO_CONTENT, )
        else:
            return make_response('User not found', http.HTTPStatus.NOT_FOUND, )

'''
This route simply performs the webscraping and club adding funcitonality defined in webscrape.py
No input is necessary in the body of this request
'''
@app.route('/api/clubs/webscrape', methods=["POST"])
def webscrape_action():
    scraped_clubs = webscrape.scrape_clubs("https://ocwp.pennlabs.org/")
    for club in scraped_clubs:
        add_club(code=club.get("code"), name=club.get("name"), description=club.get("description"), tag_names=club.get("tags"))
    return make_response(
        jsonify({"a_message": "Added #Clubs: " + str(len(scraped_clubs)), "clubs": scraped_clubs}),
        http.HTTPStatus.OK,
    )


'''
This route handles all comment actions with POST, PUT, and DELETE requests
A POST request will allow a new comment to be added regardless of if a user already 
    commented on this particular club (multiple comments are allowed!)
A PUT request will modify a specific comment using the provided comment id and new text
A DELETE request will delete a specific comment using the provided comment id
Only works on single comment actions, lists of comments not allowed.
'''
@app.route('/api/users/comment', methods=["POST", "PUT", "DELETE"])
def clubs_comment_action():
    #Ensures the comment input isn't a list of comments
    comment_request = request.get_json()
    if isinstance(comment_request, list):
        return make_response('Acting on multiple comments not allowed', http.HTTPStatus.METHOD_NOT_ALLOWED, )
    returnVal = None

    #POST Request to add new comment, only works if all information is provided in club/user is found
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


    #PUT Request to modify existing comment, only works if all data is provided and comment with given id exists
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


    #DELETE Request to delete a comment, only works if a comment id is provided and it exists
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


    #General return statement assuming success
    return make_response(jsonify(returnVal.as_json), http.HTTPStatus.OK, )
if __name__ == '__main__':
    app.run()
