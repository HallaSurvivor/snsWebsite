"""
Handles the databases and their properties
"""

from app import db
from werkzeug import generate_password_hash, check_password_hash

class User(db.Model):
    """
    A table of Users of the website
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    audition_times = db.relationship('AuditionTimes', backref='auditioner', lazy='dynamic')
    password_hash = db.Column(db.String(120))

    def __init__(self, username, email, password):
        """
        Create a new user
        """
        self.username = username.lower()
        self.email = email.lower()

        self.set_password(password)

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
        return '<User: {username}>'.format(username=self.username)

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
