from flask import Blueprint
from project import db
from flask import (request, render_template, flash, redirect, url_for,
                   Blueprint, g
                   )
from flask_login import (current_user, login_user, logout_user, login_required)

from project.api.models import LoginForm, User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
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
            flash(
                'Invalid username or password. Please try again.',
                'danger')
            return render_template('login.html', form=form)
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
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
