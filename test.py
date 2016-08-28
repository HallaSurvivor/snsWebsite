#!flask/bin/python
from app import db, models
import datetime

### Create a test database ###
db.create_all()

### Put users into the database ###

# User.create(NAME, EMAIL, PASSWORD)
webmaster = models.User.create("Webmaster", "webmaster@gmail.com", "webmaster")
webmaster.update(user_level = 2)

admin = models.User.create("admin", "admin@gmail.com", "admin")
admin.update(user_level = 1)

for i in xrange(100):
    models.User.create("user {0}".format(i), "test{0}@gmail.com".format(i), "test")

### Put shows with times into the database ###

today = datetime.datetime.today()
for j in xrange(5):
    title = "Show #{0}".format(j)
    audition_day = today + datetime.timedelta(days=j)
    start_time = datetime.datetime.utcnow()
    end_time = start_time + datetime.timedelta(hours=j)
    audition_length = datetime.timedelta(minutes=15)

    models.PossibleAuditionTimes.create(title, audition_day, start_time, end_time, audition_length)
    models.PossibleAuditionTimes.create(title, today, start_time, end_time, audition_length)
