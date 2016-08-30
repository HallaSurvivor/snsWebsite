"""
Creates all of the web forms that we import and turn into html

The actual rendering of these forms, as well as the processing
of their information is handled in views.py
"""

from flask_wtf import Form

from wtforms import (StringField, BooleanField, PasswordField, SubmitField, 
RadioField, SelectMultipleField, widgets, SelectField, DateField, FileField, TextAreaField)

from wtforms.validators import DataRequired, Email, EqualTo
from .models import User 
import datetime

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
        """
        This is what we in the biz call a shitty shitty hack
        """
        return True

class ChooseWebmasterForm(Form):
    """
    See a list of checkboxes to determine who is a webmaster
    """
    masters = MultiCheckboxField('masters')
    submit = SubmitField('make webmaster')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        """
        This is what we in the biz call a shitty shitty hack
        """
        return True

class CreateAuditionTimesForm(Form):
    """
    The form for admins to create a new audition time

    The admin chooses a start time, a duration of 
    time to block out (which determines the end time), and
    a length of time for one audition to last.

    This is used to automatically create a list of possible 
    audition times for the auditioners to see.

    WTForms doesn't play nice with datetime objects, so we need to first
    encode them as strings, then decode them later on... This gets gross
    """

    title = StringField("Title of show", validators=[DataRequired("Please enter a title")])

    date = DateField("Date", format='%Y-%m-%d')

    # A list of every 30 minutes between 00:00 and 23:30 (inclusive)
    start_times = [datetime.time(h, 30*m) for h in xrange(24) for m in xrange(2)]

    # We format the times as HH:MM to pass around WTForms, 
    # rather than passing datetime.time objects
    start_time_strings = [x.strftime("%H:%M") for x in start_times]
    start_time = SelectField("Start Time", choices=[(x,x) for x in start_time_strings])

    # The length of one audition
    # These vary from 5 minutes to 30 minutes in 5 minute intervals
    lengths = [datetime.timedelta(minutes=5*(x+1)) for x in xrange(6)]

    # We format the lengths as strings too. In the back end, we pass around
    # a string representing the number of seconds the audition lasts,
    # because it's easy to turn this back into a timedelta.
    # As for what the user sees, we take the middle digits 
    # (since it's formatted as HH:MM:SS) and strip away just the minutes 
    # we care about before appending " minutes" so the user knows what's happening
    audition_length_choices = [(str(x.total_seconds()), str(x)[2:4] + " minutes") for x in lengths]

    audition_length = SelectField("Individual audition length", choices=audition_length_choices)

    # The length of the total allotted time for auditions
    # These vary from 1 hour to 8 hours
    durations = [datetime.timedelta(hours=x+1) for x in xrange(8)]

    # We do the same process as with the audition lengths,
    # but we strip away the hours instead of the minutes
    duration_choices = [(str(x.total_seconds()), str(x)[0] + " hours") for x in durations]

    duration = SelectField("Length of audition block", choices=duration_choices)

    submit = SubmitField("Make audition")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class ShowSelectForm(Form):
    """
    If there's multiple shows ongoing, pick the show you want to audition for

    Dynamically updated in views.py
    """
    shows = SelectField("Available Shows")
    submit = SubmitField("Select")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class AuditionSignupForm(Form):
    """
    What people planning to audition see when they sign up for a timeslot

    The available times are populated dynamically in views.py
    """

    available_times = RadioField("Available Times")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class SettingsForm(Form):
    """
    Allow the user to modify their settings
    """

    name = StringField('name', validators=[DataRequired("Please enter your name.")])
    email = StringField('email', validators=[DataRequired("Please enter your email.")])
    submit = SubmitField("Save changes")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class AnnouncementsForm(Form):
    """
    Modify the announcements pane on the homepage
    """

    announcements = TextAreaField('announcements')
    submit = SubmitField("Post announcments")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
