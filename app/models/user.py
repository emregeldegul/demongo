from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(70), nullable = False, unique = True)
    password = db.Column(db.String(94), nullable = False)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    created_at = db.Column(db.DateTime, default = db.func.now(), nullable = False)

    def generate_password_hash(self, password):
        """
            This function hashes the password entered by the user with the
            pbkdf2 algorithm.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
            This function compares the password entered during login with the
            hash registered in the system.
        """
        return check_password_hash(self.password, password)
