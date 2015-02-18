""" User Session Management: Flask-Login """

from flask.ext.login import LoginManager

from . import app
from models import User
from database import session

# Initialize Login Manager for user management
login_manager = LoginManager()
login_manager.init_app(app)

# Set login redirect view/messaging
login_manager.login_view = "login_get"
login_manager.login_message = "Sorry about that, but you'll need to login to access this page."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(userid):
    """ Re/load user from session

    Returns:
        User exists: User object
        User no exists: None
    """
    return session.query(User).get(int(userid))