from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm, NicknameForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, db
from werkzeug.urls import url_parse
import requests
import json


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = NicknameForm()
    if form.validate_on_submit():
        flash('Your nickname will now be available within Unity')
        new_user = {
            "id": current_user.id,
            "nickname": form.nickname.data,
            "colour": form.colour.data
        }

        url = "https://api.myjson.com/bins/g8p8m"
        resp = requests.get(url).json()
        id_exists = False
        for i in range(len(resp)):
            if resp[i]['id'] == new_user['id']:
                resp[i] = new_user
                id_exists = True

        if not id_exists:
            json_data = resp + [new_user]
        else:
            json_data = resp
        put_req = requests.put(url, json=json_data)
        print(put_req)
    return render_template("index.html", username=current_user.username, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f"User {form.username.data} has been successfully registered")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
