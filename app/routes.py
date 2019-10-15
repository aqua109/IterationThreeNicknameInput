import os
import re
import pandas as pd
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User, Contact
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
from app import db


def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def prepare_spreadsheet(file):
    # Read in file and set headers as 1st row
    df = pd.read_excel(file, header=1, dtype=str)

    # Remove: 'Caregiver 1 email', 'Caregiver 2 email', Emergency Contact info, and Other Contact info
    df.drop(df.columns[8], axis=1, inplace=True)
    df.drop(df.columns[11:20], axis=1, inplace=True)

    return df


def db_parse(rows):
    contacts = []
    for row in rows:
        # Removes the surname code at the end of surnames e.g.: Wiggins WIG-DA
        family_name = re.sub('[A-Z]{2,3}[\-]?[A-Z]{2,3}', "", row[2]).strip()
        child = row[1].strip()
        mobile = None
        caregiver = None
        # For number in list of 6 possible phone numbers
        for num in row[5:]:
            # If number is a mobile number
            if num is not None and num[:3] in ['020', '021', '022', '027', '028']:
                mobile = num.replace(" ", "")
                # If mobile number is also a caregiver number
                if mobile in row[7:]:
                    # Set caregiver as either row[3] or row [4], i.e. Caregiver1 or Caregiver2
                    caregiver = row[row[7:].index(mobile) % 2 + 3]
                break
        # If mobile number doesn't match any caregiver, set caregiver as Caregiver1
        if caregiver is None:
            caregiver = row[3]
        json = {
            "Family Name": family_name,
            "Child": child,
            "Mobile": mobile,
            "Caregiver": caregiver
        }
        contacts.append(json)
    return contacts


@app.route('/')
@app.route('/index')
@login_required
def index():
    data = []
    columns = [{"field":"Caregiver","title":"Caregiver","sortable":True,},{"field":"Family Name","title":"Family Name","sortable":True,},{"field":"Child","title":"Child","sortable":True,},{"field":"Mobile","title":"Mobile","sortable":True,}]
    try:
        # latest_file = newest(app.config['UPLOAD_FOLDER']).split("\\")[-1]
        latest_file = newest(app.config['UPLOAD_FOLDER'])
        df = prepare_spreadsheet(latest_file)
        df_list = []
        for index, row in df.iterrows():
            ()

        print(df)


    except ValueError:
        latest_file = "No file selected"
    return render_template("index.html", data=data, columns=columns, latest_file=latest_file)


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


@app.route('/upload')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file found')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f'{now}_{file.filename}'
            filename = secure_filename(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/')
        else:
            flash("File must be of type '.xlsx'")
            return redirect(request.url)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)
