"""
Runs the website
"""
from app import app, db
import sys

# Cheaty, cheaty hack to assume utf8 instead of ascii
reload(sys)
sys.setdefaultencoding('utf8')

# Create the database if it doesn't exist
db.create_all()

# Run the actual site
app.run(debug=True)
