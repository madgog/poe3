from flask import (redirect, url_for, render_template, request, flash, Blueprint)
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .model import User
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth',__name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        error = None

        if user:
            if check_password_hash(user.password, password):
                flash(f'Welcome, {username}!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('post.home'))
            else:
                error = 'Wrong creds'
        else:
            error = 'Wrong creds'
 
        flash(error)   
    return render_template('login.html', user=current_user)


@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None
        
        if not username:
            error = 'Please eneter username'
        elif not email:
            error = "Please enter valid email"
        elif not password:
            error = "Please enter password"
        elif User.query.filter_by(username=username).first():
            error = "Username already exists!"
        elif User.query.filter_by(email=email).first():
            error = "Email already exists"

        if error is None:
            user = User(username=username,email=email,password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            # login_user(user, remember=True)
            flash('Account has been created successfully!',category='success')
            return redirect(url_for('post.home'))
        
        flash(error, category='error')

    return render_template('register.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logout')
    return redirect(url_for('auth.login'))
