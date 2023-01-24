from flask import Blueprint
import ldap3
from flask import (request, render_template, flash, redirect, url_for,
                   Blueprint, g
                   )
from flask_login import (current_user, login_user, logout_user, login_required)

from project.api.models import LoginForm, User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('auth.home'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']

        try:
            User.try_login(username, password)
        except:
            print("login failed")
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            return render_template('login.html', form=form)
        print("loggin")
        user = User.query.filter_by(username=username)
        login_user(user)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('auth.home'))
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/signup')
def signup():
    return 'Signup'


@auth.route('/logout')
def logout():
    return 'Logout'
