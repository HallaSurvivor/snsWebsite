"""
Creates all of the web forms that we import and turn into html

The actual rendering of these forms, as well as the processing
of their information is handled in views.py
"""

from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, SubmitField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Email, EqualTo
from .models import User

class MultiCheckboxField(SelectMultipleField):
    """
    Allow people to tick multiple checkboxes
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LoginForm(Form):
    """
    Handle logging in to the website.
    """
    email = StringField('email', validators=[DataRequired("Please enter your email.")])
    password = PasswordField('password', validators=[DataRequired("Please enter your password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        """
        Check the user exists and the password matches
        """

        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()

        if not user:
            self.email.errors.append("Invalid email")
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
    name = StringField('name', validators=[DataRequired("Please enter your name.")])
    email = StringField('email', validators=[DataRequired("Please enter a valid email."), Email("Please enter a valid email.")])
    password = PasswordField('password', validators=[DataRequired("Please enter a password.")])
    password_confirmation = PasswordField('password confirmation', validators=[DataRequired("Please confirm your password."), EqualTo('password', "Please make sure your passwords match.")])
    submit = SubmitField('Sign up!')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        """
        Ensure the email is not taken
        """
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken.")
            return False
        else:
            return True

class ChooseAdminsForm(Form):
    """
    See a list of checkboxes to determine who is an admin
    """
    admins = MultiCheckboxField('admins')
    submit = SubmitField('adminify!')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class ChooseWebmasterForm(Form):
    """
    See a list of checkboxes to determine who is an admin
    """
    masters = MultiCheckboxField('masters')
    submit = SubmitField('make webmaster')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True
