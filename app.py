from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import dbcon
import time
from datetime import date
import calendar

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# ---------------------------------LOGIN SETUP------------------------------------------

db = SQLAlchemy(app)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# set the type and location of the DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
# make sure this key stays secret
app.config['SECRET_KEY'] = 'super_secret'


# class name has to match the table name
# class variables must match the column names of the table
# one column must be called 'id'
class users(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    Firstname = db.Column(db.String)
    Surname = db.Column(db.String)
    password = db.Column(db.String)


# should be set to refer to the class name as above
@login_manager.user_loader
def load_user(id):
    return users.query.get(id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


# -----------------------------------GLOBAL VARIBLES------------------------------------------------ #
@app.context_processor
def weather_search_names():
    glob_weather_data = sql_retrieve_weather_name()
    return dict(glob_weather_data=glob_weather_data)


# -----------------------------------ROUTES------------------------------------------------ #
@app.route('/')
@app.route('/home')
def home():
    date = time.asctime()
    date1 = date[0:8]
    date2 = date[19:]
    location = title_location()
    return render_template("home.html", location=location, date=date1, date2=date2)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        try:
            my_user = users.query.filter_by(username=request.form['username']).first()
        except:
            flash('An error occurred. Please check username and password and try again')
            return redirect(url_for('login'))
        if my_user is not None:
            if check_password_hash(my_user.password, request.form['password']):
                login_user(my_user)
                return redirect(url_for('home'))
            else:
                flash('An error occurred. Please check username and password and try ')
                return redirect(url_for('login'))
        else:
            flash('An error occurred. Please check username and password and try again')
            return redirect(url_for('login'))
    else:
        flash('An error occurred. Please check username and password and try again')
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        new_user_details = (
            request.form['email'],
            request.form['username'],
            request.form['first'],
            request.form['last'],
            generate_password_hash(request.form['password']))
        email = request.form['email']
        data = sql_new_user(new_user_details, email)
        if data == "Success":
            try:
                my_user = users.query.filter_by(username=request.form['username']).first()
            except:
                my_user = 0
            if my_user is not None:
                if check_password_hash(my_user.password, request.form['password']):
                    login_user(my_user)
                    return redirect(url_for('home'))
                else:
                    flash('An error occured. Please try again')
                    return redirect(url_for('register'))
            else:
                flash('An error occured. Please try again')
                return redirect(url_for('register'))
        else:
            flash('This email has an account linked to it. Please try another one')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    try:
        logout_user()
    except:
        pass
    return redirect(url_for('home'))


@app.route('/locations')
def locations():
    locations, headers = sql_retreieve_locations()
    month = time.asctime()[4:7]
    return render_template("locations.html", locations=locations, headers=headers, month=month)


@app.route('/weather/', methods=['GET', 'POST'])
def weather_location():
    if request.method == 'POST':
        id = request.form['weatherID']
        return redirect(url_for('weather', type=id))
    else:
        return render_template('base.html')


@app.route('/weather')
def weather():
    date = time.asctime()
    date1 = date[0:8]
    date2 = date[19:]
    location = all_location()
    return render_template('weather.html', location=location, date=date1, date2=date2)


@app.route('/weather/<id>')
def weatherloc(id):
    data, headers = sql_retrieve_location_name(id)
    month = time.asctime()[4:7]
    curr_date = date.today()
    day = calendar.day_name[curr_date.weekday()]
    return render_template("locweather.html", data=data, headers=headers, month=month, day=day)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/map/<type>')
def maps(type):
    return render_template('rain_map.html', type=type)


# ----------------------SQL Queries---------------------- #
def title_location():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT * FROM locations WHERE name = 'Brisbane' OR name = 'Townsville' 
        OR name='Toowoomba' OR name='Mount Isa' OR name = 'Cairns' OR name = 'Longreach' ORDER BY name""")
    locations = c.fetchall()
    return (locations)


def all_location():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT * FROM locations WHERE UPPER(name) NOT LIKE 'PORTABLE%' ORDER BY name""")
    locations = c.fetchall()
    return (locations)


def sql_retrieve_location_name(name):
    con = dbcon.connect()
    c = con.cursor()
    sql_code = """SELECT name AS 'Location', date AS 'Last Checked', temp AS 'Air Temperature', 
        wind_speed AS 'Wind Speed', wind_dir AS 'Wind Direction', humidity AS 'Relative Humidity', rain AS 'Rain', cloud AS 'Cloud'
         FROM locations WHERE UPPER(name) = UPPER(?) AND UPPER(name) NOT LIKE 'PORTABLE%'"""
    c.execute(sql_code, (name,))
    locations = c.fetchall()

    headers = [i[0] for i in c.description]

    return (locations, headers)


def sql_retreieve_locations():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT name AS 'Location', date AS 'Last Checked', temp AS 'Air Temperature', 
        wind_speed AS 'Wind Speed', wind_dir AS 'Wind Direction', humidity AS 'Relative Humidity', rain AS 'Rain', cloud AS 'Cloud' 
         FROM locations WHERE UPPER(name) NOT LIKE 'PORTABLE%' ORDER BY name""")
    locations = c.fetchall()

    headers = [i[0] for i in c.description]

    return (locations, headers)


# -----------------------------------SQL Queries------------------------------------------------ #
def sql_new_user(new_user_details, email):
    connie = dbcon.connect()
    c = connie.cursor()
    # Check if user already exists
    c.execute("""SELECT * FROM users WHERE email = ?""", (email,))
    emails = c.fetchall()
    if emails == []:
        # If new user is unique then insert new user into the database
        c.execute("""INSERT INTO users(email, username, Firstname, Surname, password) VALUES(?, ?, ?, ?, ?)""",
                  new_user_details)
        connie.commit()
        return ("Success")
    else:
        return ("Fail")


def sql_retrieve_weather_name():
    connie = dbcon.connect()
    c = connie.cursor()
    sql_code = "SELECT name FROM locations ORDER BY name"
    c.execute(sql_code)
    weather_data = c.fetchall()
    return weather_data


if __name__ == "__main__":
    app.run()
