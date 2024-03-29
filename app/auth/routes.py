from flask import render_template, flash, redirect, url_for, request, Blueprint
from app.extensions import db
from .forms import RegistrationForm, LoginForm, ChangePasswordForm
from app.models import User
from flask_login import current_user, login_required, login_user,logout_user
auth = Blueprint('auth', __name__, template_folder='templates', url_prefix = "/auth")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Replace 'index' with the name of your homepage route

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.index'))

        login_user(user)
        return redirect('/')  # Redirect to the homepage after login
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the username or email already exists
        existing_user_by_username = User.query.filter_by(username=form.username.data).first()
        existing_user_by_email = User.query.filter_by(email=form.email.data).first()

        if existing_user_by_username:
            flash('This username is already taken. Please choose a different one.', 'error')
            return render_template('auth/register.html', title='Register', form=form)

        if existing_user_by_email:
            flash('This email is already in use. Please choose a different one or log in.', 'error')
            return render_template('auth/register.html', title='Register', form=form)

        # Create new user
        user = User(username=form.username.data, email=form.email.data, is_tutor=form.is_tutor.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))  # Redirect to login page after registration

    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/reset_password')
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid old password.')
    return render_template('auth/reset_password.html', title='Change Password', form=form)
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))