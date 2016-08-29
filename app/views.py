"""
Deines a relationship between relative urls and html files (i.e. WEBSITE/about links to about.html)

get_txt: 
  a helper function which retrieves the text from a file passed as input.
  We use this function to update information on the website, such as subtroupe descriptions
  and announcements without modifying the source html.

We use the user's email as a token (stored as a cookie in flask `session`) to
check if a proper user is logged in, and change the functionality appropriately.
"""
from flask import render_template, flash, redirect, request, session, url_for
from .forms import LoginForm, SignUpForm, ChooseAdminsForm, ChooseWebmasterForm, CreateAuditionTimesForm, AuditionSignupForm, ShowSelectForm
from .models import User, PossibleAuditionTimes, AuditionTimes
from app import app, db
from functools import wraps
import datetime
import os

#### Helper functions ####

def get_txt(filename):
  """
  Return the text stored in app/static/txts/filename.txt if it exists. 

  filename should be a string with extension, for example, "npp.txt"

  If pages that use this function aren't loading properly, particularly
  if the error message given relates to encoding or ascii, verify that in 
  whatever file you use as an entry for the program 
  (run.py for local, wsgi.py for pythonanywhere, etc.) is properly setting
  its encoding to utf8. Check run.py in this repo for one way of fixing it.
  """
  complete_path = os.path.join(os.getcwd(), "app", "static", "txts", filename)

  try:
    with open(complete_path) as text_file:
      raw_text = text_file.read()
  except IOError:
    raw_text = complete_path
  
  return raw_text

def get_user():
    """
    Return the user if there is one logged in, None otherwise
    """
    if 'email' not in session:
        return None
    else:
        return User.query.filter_by(email=session['email']).first()

def require_login(user_level=0):
    """
    A decorator to verify the user is logged in before going to a webpage

    user_level = 0 requires the user to simply exist
    user_level = 1 requires the user be an admin
    user_level = 2 requires the user be the webmaster
    """
    def login_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # If there isn't a cookie
            if 'email' not in session:
                flash("Please log in to access that page")
                return redirect(url_for('login'))

            user = User.query.filter_by(email=session['email']).first()

            # If there *is* a cookie but it doesn't correspond to a user
            if user is None:  
                flash("Please log in to access that page")
                return redirect(url_for('login'))

            # If there is a user, but they don't have permission
            elif user.user_level < user_level:
                flash("You do not have permission to access this page")
                return redirect(url_for('profile'))

            # We gucci, fam
            else:
                return func(*args, **kwargs)

        return wrapper
    return login_decorator

#### routes ####

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', announcements=get_txt("announcements.txt"), user=get_user())

@app.route('/about')
def about():
    return render_template('about.html', title="About Us", user=get_user())

@app.route('/tickets')
def tickets():
    return render_template('tickets.html', title="Buy Tickets", user=get_user())

@app.route('/subtroupes')
def subtroupes():
    # Dynamically update subtroupes.html with: tisbert.txt, npp.txt, workshopping.txt
    return render_template('subtroupes.html', title="SNS Subtroupes", 
        tisbert_text=get_txt("tisbert.txt"), npp_text=get_txt("npp.txt"), 
        workshopping_text=get_txt("workshopping.txt"), user=get_user())

@app.route('/join')
def join():
    return render_template('join.html', title="Join Us!", user=get_user())

@app.route('/alumni')
def alumni():
    return render_template('alumni.html', title="Alumni", user=get_user())

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('signup.html', title="Sign up!", form=form, user=get_user())
        else:
            # Create the new user
            newUser = User.create(form.name.data, form.email.data, form.password.data)

            # Sign in the new user
            session['email'] = newUser.email

            # Redirect to profile
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', title="Sign up!", form=form, user=get_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', title="Log in!", form=form, user=get_user())
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('login.html', title="Log in!", form=form, user=get_user())

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)

    return redirect(url_for('index'))

@app.route('/profile')
@require_login()
def profile():
    """
    Render the profile of the signed in user.

    The dynamic content based in user 
    is handled in profile.html
    """
    return render_template('profile.html', user=get_user())

@app.route('/adminify', methods=['GET', 'POST'])
@require_login(2)
def adminify():
    """
    Render a checkbox for each user. Checked boxes correspond to admins

    note: only the webmaster can see this page
    """
    form = ChooseAdminsForm()

    # Dynamically populate possible admins with the user list.
    users = User.query.all()
    form.admins.choices = [(user.email, user.name) for user in users if user.user_level != 2]

    if request.method == 'POST':
        if not form.validate():
            # Dynamically update the prechecked boxes with users who are already admins
            admins = User.query.filter_by(user_level=1).all()
            form.admins.data = [user.email for user in admins]

            return render_template('adminify.html', form=form, user=get_user())

        else:
            old_admin_emails = [user.email for user in users if user.user_level == 1]

            for new_admin_email in form.admins.data:
                user = User.query.filter_by(email=new_admin_email).first()
                user.update(user_level=1)  # Make the user an admin

                try:
                    # Remove the admins from old_admin_emails
                    # so that we're left with a list of people
                    # to un-admin-ify
                    old_admin_emails.remove(user.email)
                except ValueError:
                    # Get around trying to remove somebody who wasn't an admin
                    pass

            # Un-admin-ify people who were admins but aren't now
            for old_admin_email in old_admin_emails:
                user = User.query.filter_by(email=old_admin_email).first()
                user.update(user_level=0)

            return redirect(url_for('profile'))

    elif request.method == 'GET':
        # Dynamically update the prechecked boxes with users who are already admins
        admins = User.query.filter_by(user_level=1).all()
        form.admins.data = [user.email for user in admins]

        return render_template('adminify.html', form=form, user=get_user())

@app.route('/webmasterify', methods=['GET', 'POST'])
@require_login(2)
def webmasterify():
    """
    Render a checkbox for each user. Checked boxes correspond to webmasters

    note: only the webmaster can see this page
    """
    form = ChooseWebmasterForm()

    # Dynamically populate possible webmasters with the user list.
    users = User.query.all()
    form.masters.choices = [(user.email, user.name) for user in users if user.email != session['email']]

    if request.method == 'POST':
        if not form.validate():
            # Dynamically update the prechecked boxes with users who are already admins
            masters = User.query.filter_by(user_level=2).all()
            # Make sure you can't un-webmaster yourself, which
            # could leave us in a situation with no webmaster.
            form.masters.data = [user.email for user in masters if user.email != session['email']]

            return render_template('webmasterify.html', form=form, user=get_user())

        else:
            old_master_emails = [user.email for user in users if user.user_level == 2 and user.email != session['email']]

            for new_master_email in form.masters.data:
                user = User.query.filter_by(email=new_master_email).first()
                user.update(user_level=2)  # Make the user a webmaster

                try:
                    old_master_emails.remove(user.email)
                except ValueError:
                    pass

            # Un-webmaster-ify people who were admins but aren't now
            for old_master_email in old_master_emails:
                user = User.query.filter_by(email=old_master_email).first()
                user.update(user_level=0)

            return redirect(url_for('profile'))

    elif request.method == 'GET':
        # Dynamically update the prechecked boxes with users who are already admins
        masters = User.query.filter_by(user_level=2).all()
        form.masters.data = [user.email for user in masters]

        return render_template('webmasterify.html', form=form, user=get_user())

@app.route('/make-audition-times', methods=['GET', 'POST'])
@require_login(1)
def make_audition_times():
    form = CreateAuditionTimesForm()

    if request.method == 'POST':
        if not form.validate():
            print form.data
            return render_template('make-audition-times.html', form=form, user=get_user())
        else:

            # WTForms doesn't like passing around datetime objects,
            # so we first encode them as strings in various ways,
            # now we need to decode them.
            title = form.title.data
            date  = form.date.data

            start_raw = form.start_time.data
            start_hour = int(start_raw[:2])  # Take the HH part of the HH:MM
            start_minute = int(start_raw[-2:]) # Take the MM part of the HH:MM

            start_time = datetime.time(hour=start_hour, minute=start_minute)

            # We need to convert the time into a dateTime, so we 
            # arbitrarily merge it with today's date
            start = datetime.datetime.combine(datetime.date.today(), start_time)
            end = start + datetime.timedelta(seconds=int(float(form.duration.data)))

            # We stored the audition length as a string representing
            # the number of seconds the audition time lasts.
            # Why do we need to go string -> float -> int 
            # rather than str -> int? I have no idea.
            audition_length_in_seconds = int(float(form.audition_length.data))
            audition_length = datetime.timedelta(seconds=audition_length_in_seconds)

            PossibleAuditionTimes.create(title, date, start, end, audition_length)

            flash("Audition time created successfully!")
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('make-audition-times.html', form=form, user=get_user())

@app.route('/audition-signup', methods=['GET', 'POST'])
@require_login()
def audition_signup_selector():
    """
    Select the show to audition for if there is more than one, otherwise redirect immediately
    """
    today = datetime.datetime.today()

    all_auditions = PossibleAuditionTimes.query.all()
    upcoming_auditions = [a for a in all_auditions if a.date > today]
   
    shows = set()
    for a in upcoming_auditions:
        shows.add(a.show)

    if len(shows) == 0:
        flash("No upcoming auditions")
        return redirect(url_for('profile'))

    if len(shows) == 1:
        return redirect(url_for('audition_signup', show=shows[0]))

    if len(shows) > 1:
        form = ShowSelectForm()
        form.shows.choices = [(s,s) for s in shows]
        
        if request.method == 'POST':
            if not form.validate():
                return render_template('select-show.html', form=form, user=get_user())
            else:
                return redirect(url_for('audition_signup', show=form.shows.data))

        elif request.method == 'GET':
            return render_template('select-show.html', form=form, user=get_user())

@app.route('/audition-signup/<string:show>', methods=['GET', 'POST'])
@require_login()
def audition_signup(show):
    form = AuditionSignupForm()

    today = datetime.datetime.today()

    all_audition_blocks = PossibleAuditionTimes.query.all()
    upcoming_audition_blocks = [a for a in all_audition_blocks if a.date > today]
    relevant_audition_blocks = [a for a in upcoming_audition_blocks if a.show == show]

    days = [a.date.strftime("%A %B %d") for a in relevant_audition_blocks]

    # We expand the relevant audition blocks into a list of every possible audition
    # the user can sign up for (for a given show)
    relevant_auditions = []
    for a in relevant_audition_blocks:

        all_auditions_in_block = []
        current_start = a.start_time
        while current_start <= a.end_time:
            all_auditions_in_block.append(current_start.strftime("%H:%M"))
            current_start += a.audition_length

        formatted_auditions = zip([a.date.strftime("%A %B %d")] * len(all_auditions_in_block), all_auditions_in_block)
        relevant_auditions += formatted_auditions


    # We create a complex label here, which codifies all the information
    # that we need to properly sort and display the audition times in the
    # html file. The label the user sees will be just the audition time
    labels = ["{0}::{1}".format(a[0], a[1]) for a in relevant_auditions]

    form.available_times.choices = [(c,c) for c in labels]

    if request.method == 'POST':
        if not form.validate():
            return render_template('audition-signup.html', form=form, show=show, days=days, user=get_user())
        else:
            user = get_user()

            time_raw = form.available_times.data
            datetime_object = datetime.datetime.strptime(time_raw.replace("::", " "), "%A %B %d %H:%M")

            AuditionTimes.create(show, datetime_object, user)

            time_string = time_raw.replace("::", " @ ")
            flash("Successfully registered for {0} audition at {1}".format(show, time_string))
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('audition-signup.html', form=form, show=show, days=days, user=get_user())
