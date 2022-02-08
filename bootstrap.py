import os
from models import *
from app import db, DB_FILE
import json



def create_user(name='Josh', username='josh', email='josh@upenn.edu', gender=0, year="freshman"):
    new_user = User.query.filter_by(username=username).first()
    if(new_user is None):
        new_user = User(name=name, username=username, email=email, gender=gender, year=year)
        db.session.add(new_user)
        db.session.commit()
    return new_user

'''
Loading data from json file as a json obj, then unpacking with python standard functionality
Uses helper function add_club() made in case more clubs added later outside of load_data
'''
def load_data():
    f = open("clubs.json")
    data = json.load(f)
    for i in data:
        add_club(code=i.get("code"), name=i.get("name"), description=i.get("description"), tag_names=i.get("tags"))

'''
General functions for getting tag ids and adding clubs
Runs with helper function get_tag_from_name
Basic Process: If club code exists, then pass and return club, otherwise, add club, check uniqueness of tags,
    then add clubs-tags relationship
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
Function gets all clubs by querying all, converting to json through defined as_json() property in Club Model
'''
def get_all_clubs():
    clubs = Club.query.all()
    return [i.as_json for i in clubs]

def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()
    return user.as_public_json

def get_all_users():
    users =  User.query.all()
    return [i.as_json for i in users]

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

def get_num_favorited(club_code):
    club = Club.query.filter_by(code=club_code).first()
    return len(club.users)
'''
The assumption in the modify club function is that the front end will pull all data, allow the user
to modify what is necessary, then send all fields back. Empty fields should be addresed in the front end, but just
in case, if None is given back, this system keeps the old values
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

def add_comment(club_id, user_id, comment_text):
    comment = Comment(club_id=club_id, user_id=user_id, text=comment_text)
    db.session.add(comment)
    db.session.flush()
    db.session.commit()
    return comment

def modify_comment(comment_id, comment_text):
    comment = Comment.query.filter_by(id=comment_id).first()
    setattr(comment, "text", comment_text if (comment_text is not None) else comment.text)
    db.session.add(comment)
    db.session.flush()
    db.session.commit()
    return comment

def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return comment

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
