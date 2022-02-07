import bootstrap
from app import db
from enum import Enum

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

tags = db.Table('tags',
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

users_favorite_clubs = db.Table('users_favorite_clubs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String)
    name = db.Column(db.String)
    description = db.Column(db.String)

    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('clubs', lazy=True))

    @property
    def as_json(self):
        return {"code": self.code, "name": self.name,
                "description": self.description,
                "num_favorited": bootstrap.get_num_favorited(self.code),
                "tags": [i.as_string for i in self.tags]}

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String)

    @property
    def as_string(self):
        return self.tag_name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    email = db.Column(db.String)
    gender = db.Column(db.Integer)
    year = db.Column(db.Integer)

    favorite_clubs = db.relationship('Club', secondary=users_favorite_clubs, lazy='subquery',
        backref=db.backref('users',lazy=True))

    @property
    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'year': self.year,
            'favorite_clubs': [{"code": i.code, "name": i.name} for i in self.favorite_clubs]
        }

    @property
    def as_public_json(self):
        return {
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'year': self.year,
            'favorite_clubs': [{"id": i.id, "name": i.name} for i in self.favorite_clubs]
        }

class Genders(Enum):
    MALE = "male"
    FEMALE = "female"


class Years(Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"