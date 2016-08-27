#!flask/bin/python
from app import db, models

### Create a test database ###

db.create_all()

# User.create(NAME, EMAIL, PASSWORD)
webmaster = models.User.create("Webmaster", "webmaster@gmail.com", "webmaster")
webmaster.update(user_level = 2)

admin = models.User.create("admin", "admin@gmail.com", "admin")
admin.update(user_level = 1)

for i in xrange(100):
    models.User.create("user {0}".format(i), "test{0}@gmail.com".format(i), "test")

