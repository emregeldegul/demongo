from flask import Blueprint, redirect, url_for, render_template, request
from flask_login import login_user, logout_user, current_user

from app.models.user import User

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/')
@auth.route('/index')
def index():
    return redirect(url_for('auth.login'))

@auth.route('/register')
def register():
    return render_template('auth/register.html', title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', title='Login')

@auth.route('/logout')
def logout():
    return 'ok'
