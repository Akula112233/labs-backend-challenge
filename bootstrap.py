import os
from models import *
from app import db, DB_FILE
import json


'''
This function takes inputs of name, username, email, gender, and current schooling year
If a user exists with the username, simply returns them, otherwise adds the user then returns 
the newly added user with their storage id

The default user values create the requested user "Josh" with username "josh"
'''
def create_user(name='Josh', username='josh', email='josh@upenn.edu', gender=0, year="freshman"):
    new_user = User.query.filter_by(username=username).first()
    if(new_user is None):
        new_user = User(name=name, username=username, email=email, gender=gender, year=year)
        db.session.add(new_user)
        db.session.commit()
    return new_user

'''
This function loads in data from json file as a json obj, then unpacking with python standard functionality
uses helper function add_club() to iterate through the json obj and add each club to storage
'''
def load_data():
    f = open("clubs.json")
    data = json.load(f)
    for i in data:
        add_club(code=i.get("code"), name=i.get("name"), description=i.get("description"), tag_names=i.get("tags"))

'''
This function adds a club to the system if there isn't already an existing one with the same club_code.
Basic Process: If club code exists, then pass and return club, otherwise, add club, check uniqueness of tags,
then add clubs-tags relationship. 
Makes use of the get_tag_from_name funciton to check tag uniqueness and get id
'''
def add_club(code, name, description, tag_names):
    club = Club.query.filter_by(code=code).first()
    if (club is None):
        tags = list(map(get_tag_from_name, tag_names))
        club = Club(code=code, name=name, description=description, tags=tags)
        db.session.add(club)
        db.session.commit()
    return club

'''
Given a tag name, if the tag exists in the tags table, return it, otherwise add it then return it
This gives users also information about the specific id the tag is stored under in the DB
'''
def get_tag_from_name(tag_name):
    tag = Tag.query.filter_by(tag_name=tag_name).first()
    if (tag is None):
        tag = Tag(tag_name=tag_name)
        db.session.add(tag)
        db.session.flush()
        db.session.commit()
        return tag
    else:
        return tag

'''
Function gets all clubs by querying all rows of the Club table (no filtering), converting to 
json through defined as_json property in the Club db model
'''
def get_all_clubs():
    clubs = Club.query.all()
    return [i.as_json for i in clubs]

'''
Function gets a user querying with username property, converting to json through defined as_json property
in the User db model
'''
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user.as_public_json

'''
Function gets all users by querying all rows of the User table (no filtering), converting to 
json through defined as_json property in the User db model
'''
def get_all_users():
    users =  User.query.all()
    return [i.as_json for i in users]

'''
This function takes a username and a club_code to add a club to a certain user's favorites list
If a favorite already exists within a user's list, it will remove it, acting as a toggle function
If a user doesn't exist, None is returned and handled in app.py as an unknown user
'''
def add_favorite(username, club_code):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        club = Club.query.filter_by(code=club_code).first()
        new_list = user.favorite_clubs.copy()
        if(club in new_list):
            new_list.remove(club)
        else:
            new_list.append(club)
        setattr(user, "favorite_clubs", new_list)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        return user
    else:
        return None

'''
This function queries a club given it's club code then counts the number of users it is related 
to in the association table of users_favorite_clubs (which relates Club to Users as Many-to-Many)
'''
def get_num_favorited(club_code):
    club = Club.query.filter_by(code=club_code).first()
    return len(club.users)

'''
This function takes a club object and optionally name, description, and tag_names to modify the original
club object only if a parameter is provided (otherwise, None type is ignored).
'''
def modify_club(club, name=None, description=None, tag_names=None):
    setattr(club, "name", name if (name is not None) else club.name)
    setattr(club, "description", description if (description is not None) else club.description)
    setattr(club, "tags",
            [get_tag_from_name(i) for i in tag_names] if (tags is not None) else club.tags
    )
    db.session.add(club)
    db.session.flush()
    db.session.commit()
    return club

'''
This function takes club id, user id, and comment text to create a comment instance and
add it to the system storage. 
It returns the comment added along with storage id information to the user
'''
def add_comment(club_id, user_id, comment_text):
    comment = Comment(club_id=club_id, user_id=user_id, text=comment_text)
    db.session.add(comment)
    db.session.flush()
    db.session.commit()
    return comment

'''
This function takes a comment id and comment text to modify an existing comment
It returns the modified comment along with storage id information to the user
'''
def modify_comment(comment_id, comment_text):
    comment = Comment.query.filter_by(id=comment_id).first()
    setattr(comment, "text", comment_text if (comment_text is not None) else comment.text)
    db.session.add(comment)
    db.session.flush()
    db.session.commit()
    return comment

'''
This function takes a comment id and comment text to delete an existing comment
It returns the deleted comment to the user
'''
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return comment

'''
This function will query all the tags in the Tag table and maps them to a list of 
each tag's string value and the number of clubs which are connected to that tag
'''
def get_all_tags():
    all_tags = Tag.query.all()
    all_tags = list(map(lambda x: {"tag": x.as_string, "num_clubs": len(x.clubs)}, all_tags))
    return all_tags

# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
