"""
Creates all of the web forms that we import and turn into html

The actual rendering of these forms, as well as the processing
of their information is handled in views.py
"""

from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from .models import User

class LoginForm(Form):
    """
    Handle logging in to the website.
    """
    username = StringField('username', validators=[DataRequired("Please enter a username.")])
    password = PasswordField('password', validators=[DataRequired("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        """
        Check the user exists and the password matches
        """

        if not Form.validate(self):
            return False

        user = User.query.filter_by(username = self.username.data.lower()).first()

        if not user:
            self.username.errors.append("Invalid username")
            return False

        if user.check_password(self.password.data):
            return True
        else:
            self.password.errors.append("Invalid password")
            return False

class SignUpForm(Form):
    """
    Handle signing in to the website.
    """
    username = StringField('username', validators=[DataRequired("Please enter a username.")])
    email = StringField('email', validators=[DataRequired("Please enter a valid email."), Email("Please enter a valid email.")])
    password = PasswordField('password', validators=[DataRequired("Please enter a password.")])
    password_confirmation = PasswordField('password_confirmation', validators=[DataRequired("Please confirm your password."), EqualTo('password', "Please make sure your passwords match.")])
    submit = SubmitField('Sign up!')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        """
        Ensure the username is not taken
        """
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken.")
            return False
        else:
            return True
