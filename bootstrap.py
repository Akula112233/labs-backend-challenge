import os
from models import *
from app import db, DB_FILE
import json

def create_user():
    josh = User(name='Josh', username='josh', email='josh@upenn.edu')
    db.session.add(josh)
    db.session.commit()


'''
Loading data from json file as a json obj, then unpacking with python standard functionality
Uses helper function add_club() made in case more clubs added later outside of load_data
'''
def load_data():
    f = open("clubs.json")
    data = json.load(f)
    for i in data:
        #print(i["code"])
        add_club(code=i["code"], name=i["name"], description=i["description"], tag_names=i["tags"])

'''
General functions for getting tag ids and adding clubs
Runs with helper function get_tag_id
Basic Process: If club code exists, then pass, otherwise, add club, check uniqueness of tags,
    then add clubs-tags relationship
'''
def add_club(code, name, description, tag_names):
    club = Club.query.filter_by(code=code).first()
    if (club is None):
        tags = list(map(get_tag_id, tag_names))
        club = Club(code=code, name=name, description=description, tags=tags)
        db.session.add(club)
        db.session.commit()
    else:
        pass
'''
Given a tag name, if the tag exists in the tags table, return it, otherwise add and return it
'''
def get_tag_id(tag_name):
    tag = Tag.query.filter_by(tag_name=tag_name).first()
    if (tag is None):
        tag = Tag(tag_name=tag_name)
        db.session.add(tag)
        db.session.flush()
        #print(tag.id)
        db.session.commit()
        #print(tag.id)
        return tag
    else:
        return tag

def get_all_clubs():
    clubs = Club.query.all()
    return list(map(lambda club: {"code": club.code,
            "name": club.name,
            "description": club.description,
            "tags": get_tags_by_club(club)
            }, clubs))
def get_tags_by_club(x):
    return list(map(lambda y: y.tag_name, x.tags))

# No need to modify the below code.
if __name__ == '__main__':
    # Delete any existing database before bootstrapping a new one.
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    db.create_all()
    create_user()
    load_data()
