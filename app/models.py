"""
Handles the databases and their properties
"""

from app import db
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash

class QueryMixin(object):
    """
    Allows us to easily query and modify the database
    """
    @classmethod
    def create(cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        return instance.save()

    def update(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return self.save()

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

class User(db.Model, QueryMixin):
    """
    A table of Users of the website

    * id is the unique id assigned to each user
    * name is the name of the user
    * email is the user's email
    * password_hash is the salted and hashed version of the user's password
    * user_level defines the permissions of the user
        + 0 by default
        + 1 if admin
        + 2 if webmaster
    * date_joined is the date and time that the user signed up
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(120))
    user_level = db.Column(db.Integer, index=True)
    date_joined = db.Column(db.DateTime, index=True)

    def __init__(self, name, email, password):
        """
        Create a new user
        """
        self.name = name.lower()
        self.email = email.lower()
        self.user_level = 0

        self.set_password(password)

        self.date_joined = datetime.utcnow()

    def set_password(self, password):
        """
        Salt and hash the password before we store it.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Compare the offered password with our salted/hashed one
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {name} Level: {level}>'.format(name=self.name, level=self.user_level)

class PossibleAuditionTimes(db.Model, QueryMixin):
    """
    A table of the legal audition times for any given show
    """
    
    id = db.Column(db.Integer, primary_key=True)
    show = db.Column(db.String(64), index=True)
    date = db.Column(db.DateTime, index=True)

    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    audition_length = db.Column(db.Interval)

    def __init__(self, show, date, start, end, audition_length):
        """
        Create a new audition block
        """
        self.show = show
        self.date = date

        self.start_time = start
        self.end_time = end

        audition_length = audition_length

class AuditionTimes(db.Model):
    """
    A table of who is auditioning for what when
    """
    id = db.Column(db.Integer, primary_key=True)
    show = db.Column(db.String(64), index=True)
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Audition for {show} at {time} :: {person}>'.format(show=self.show, time=self.time, person=self.auditioner)
