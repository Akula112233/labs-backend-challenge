import bootstrap
from app import db
from enum import Enum

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

'''
This is an association table between tags and clubs as clubs can have many tags and
tags can be related to many clubs (many to many relationship).
The foreign key for each instance in this table is a compound key consisting of the id
for the club and the id of the tag
'''
tags = db.Table('tags',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

'''
This is an association table between users and clubs as clubs can have many users favorite 
them and users can favorite many clubs (many to many relationship).
The foreign key for each instance in this table is a compound key consisting of the id
for the club and the id of the user
'''
users_favorite_clubs = db.Table('users_favorite_clubs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

'''
A club has properties of id (primary key integer), code (non-nullable string), name (string), and description (string)
It contains tags and comments, related to Tag and Comment tables (a club has tags and comments)
Property as_json is used to give a json serializable representation of a Club instance
'''
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    description = db.Column(db.String)

    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('clubs', lazy=True))

    comments = db.relationship('Comment', backref=db.backref('club', lazy=True))

    @property
    def as_json(self):
        return {
                "id": self.id,
                "code": self.code,
                "name": self.name,
                "description": self.description,
                "num_favorited": bootstrap.get_num_favorited(self.code),
                "tags": [i.as_string for i in self.tags],
                "comments": [i.as_string for i in self.comments]
        }

'''
A Tag has properties of id (primary key integer), and tag_name (string)
Property as_string is used to give a string representation of a Tag instance
'''
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String)

    @property
    def as_string(self):
        return self.tag_name

'''
A User has properties of id (primary key integer), name (string), username (string), email (string),
gender (integer: 0 biological male, 1 biological female), and school year (string)
It contains favorite_clubs and comments, related to users_favorite_clubs table and Comment tables
Property as_json is used to give a json serializable representation of a User instance
Property as_public_json is used to give a publicly data-safe json serializable representation of a User instance
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    email = db.Column(db.String)
    gender = db.Column(db.Integer)
    year = db.Column(db.String)

    favorite_clubs = db.relationship('Club', secondary=users_favorite_clubs, lazy='subquery',
        backref=db.backref('users',lazy=True))

    comments = db.relationship('Comment', backref=db.backref('user', lazy=True))

    @property
    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'year': self.year,
            'favorite_clubs': [{"code": i.code, "name": i.name} for i in self.favorite_clubs],
            'comments': [i.as_user_json for i in self.comments]
        }

    @property
    def as_public_json(self):
        return {
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'year': self.year,
            'favorite_clubs': [{"id": i.id, "code": i.code, "name": i.name} for i in self.favorite_clubs],
        }


'''
A Comment has properties of id (primary key integer), text (string), user_id (integer), and club_id (integer)
Property as_string is sued to give just the text of the comment
Property as_json is used to give a complete json serializable representation of a Comment instance
Property as_user_json is used to give a slightly modified json serializable representation of a Comment instance
that includes data about the club (club name and code) used for display when all users are called
'''
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    @property
    def as_string(self):
        return self.text

    @property
    def as_json(self):
        return {
            "id": self.id,
            "comment": self.text,
            "user_id": self.user_id,
            "club_id": self.club_id,
        }

    @property
    def as_user_json(self):
        club = Club.query.filter_by(id=self.club_id).first()
        return {
            "id": self.id,
            "comment": self.text,
            "club_code": club.code,
            "club_name": club.name,
        }