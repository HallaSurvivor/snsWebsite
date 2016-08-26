"""
Runs the website
"""
from app import app
import sys

# Cheaty, cheaty hack to assume utf8 instead of ascii
reload(sys)
sys.setdefaultencoding('utf8')

# Run the actual site
app.run(debug=True)
