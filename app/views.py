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
from .forms import LoginForm, SignUpForm
from .models import User
from app import app, db
from functools import wraps
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
  return render_template('index.html', announcements=get_txt("announcements.txt"))

@app.route('/about')
def about():
  return render_template('about.html', title="About Us")

@app.route('/tickets')
def tickets():
  return render_template('tickets.html', title="Buy Tickets")

@app.route('/subtroupes')
def subtroupes():
  # Dynamically update subtroupes.html with: tisbert.txt, npp.txt, workshopping.txt
  return render_template('subtroupes.html', title="SNS Subtroupes", 
      tisbert_text=get_txt("tisbert.txt"), npp_text=get_txt("npp.txt"), 
      workshopping_text=get_txt("workshopping.txt"))

@app.route('/join')
def join():
  return render_template('join.html', title="Join Us!")

@app.route('/alumni')
def alumni():
  return render_template('alumni.html', title="Alumni")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('signup.html', title="Sign up!", form=form)
        else:
            # Create the new user
            newUser = User(form.name.data, form.email.data, form.password.data)
            db.session.add(newUser)
            db.session.commit()

            # Sign in the new user
            session['email'] = newUser.email

            # Redirect to profile
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('signup.html', title="Sign up!", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('login.html', title="Log in!", form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('login.html', title="Log in!", form=form)

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
    return render_template('profile.html')

# @app.route('/audition-time', methods=['GET', 'POST'])
# def audition_time():
#     if 'email' not in session:
#         return redirect(url_for('login'))

#     user = User.query.filter_by(email=session['email']).first()

#     if user is None:
#         return redirect(url_for('login'))
#     else:
#         return render_template('audition-time.html', form=form)
