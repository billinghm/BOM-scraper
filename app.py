from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import dbcon
import time
from datetime import date
import calendar
from logging.config import dictConfig
from flask import has_request_context, request
import time

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

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
    date = [date[0:8], date[19:]]
    try:
        user_id = current_user.id
        user_location = user_location_title(user_id)
    except:
        user_location = 1
    location = title_location()
    hot_warning = hottest_location()
    return render_template("home.html", location=location, date=date, user_location=user_location,
                           hot_warning=hot_warning)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        try:
            user = users.query.filter_by(username=request.form['username']).first()
        except:
            time.sleep(10)
            flash('An error occurred. Please check username and password and try again')
            return redirect(url_for('login'))
        if user is not None:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                app.logger.info('%s logged in successfully', user.username)
                return redirect(url_for('home'))
            else:
                app.logger.info('%s failed to log in', user.username)
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
        loc = request.form['location']
        if loc == "Preferred Location":
            flash('Please choose a valid location')
            return redirect(url_for('register'))
        else:
            new_user_details = (
                request.form['email'],
                request.form['username'],
                request.form['first'],
                request.form['last'],
                generate_password_hash(request.form['password']),
                request.form['location'])
            email = request.form['email']
            data = sql_new_user(new_user_details, email)
        if data == "Success":
            try:
                user = users.query.filter_by(username=request.form['username']).first()
            except:
                user = 0
            if user is not None:
                if check_password_hash(user.password, request.form['password']):
                    login_user(user)
                    app.logger.info('%s logged in successfully', user.username)
                    return redirect(url_for('home'))
                else:
                    app.logger.info('%s failed to log in', user.username)
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


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update_user_details():
    if request.method == 'POST':
        user_id = current_user.id
        user_details = (request.form['firstname'],
                        request.form['surname'],
                        request.form['username'],
                        request.form['email'],
                        request.form['location'],
                        user_id)
        sql_update_user_details(user_details)
        return redirect(url_for('home'))
    else:
        user_id = current_user.id
        user_details = sql_retrieve_user_details(user_id)
        return render_template("update_details.html", user_details=user_details)


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


@app.route('/weather_location')
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


@app.route('/map/<type>/<lat>/<long>/<zoom>')
def maps(type, lat, long, zoom):
    return render_template('rain_map.html', type=type, lat=lat, long=long, zoom=zoom)


# -----------------------------------SQL Queries------------------------------------------------ #
def title_location():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT * FROM locations WHERE name = 'Brisbane' OR name = 'Townsville' 
        OR name='Toowoomba' OR name='Mount Isa' OR name = 'Cairns' OR name = 'Longreach' ORDER BY name""")
    locations = c.fetchall()
    return (locations)


def user_location_title(id):
    con = dbcon.connect()
    c = con.cursor()
    query = """SELECT locations.lat, locations.long FROM locations 
        INNER JOIN users ON users.location = locations.name 
        WHERE users.id = ? LIMIT 1"""
    c.execute(query, (id,))
    new_data = c.fetchall()
    return new_data


def hottest_location():
    con = dbcon.connect()
    c = con.cursor()
    sql_code = """SELECT name, temp FROM locations ORDER BY temp DESC LIMIT 1"""
    c.execute(sql_code)
    data = c.fetchall()
    return data


def sql_retrieve_weather_name():
    connie = dbcon.connect()
    c = connie.cursor()
    sql_code = "SELECT name FROM locations ORDER BY name"
    c.execute(sql_code)
    weather_data = c.fetchall()
    return weather_data


def all_location():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT id, name AS 'Location', date AS 'Last Checked', 
    CASE WHEN temp  IS NULL THEN 'N/A' ELSE temp END AS 'Air Temperature', 
        wind_speed AS 'Wind Speed', wind_dir AS 'Wind Direction', humidity AS 'Relative Humidity', rain AS 'Rain',
         cloud AS 'Cloud', lat AS 'Latitude', long AS 'Longitude'
         FROM locations WHERE UPPER(name) NOT LIKE 'PORTABLE%' ORDER BY name""")
    locations = c.fetchall()
    return locations


def sql_retrieve_location_name(name):
    con = dbcon.connect()
    c = con.cursor()
    sql_code = """SELECT name AS 'Location', date AS 'Last Checked', 
    CASE WHEN temp  IS NULL THEN 'N/A' ELSE temp END AS 'Air Temperature', 
        wind_speed AS 'Wind Speed', wind_dir AS 'Wind Direction', humidity AS 'Relative Humidity', rain AS 'Rain',
         cloud AS 'Cloud', lat AS 'Latitude', long AS 'Longitude'
         FROM locations WHERE UPPER(name) = UPPER(?) AND UPPER(name) NOT LIKE 'PORTABLE%'"""
    c.execute(sql_code, (name,))
    locations = c.fetchall()

    headers = [i[0] for i in c.description]

    return (locations, headers)


def sql_retreieve_locations():
    con = dbcon.connect()
    c = con.cursor()
    c.execute(
        """SELECT name AS 'Location', date AS 'Last Checked', CASE WHEN temp  IS NULL THEN 'N/A' ELSE temp 
        END AS 'Air Temperature', wind_speed AS 'Wind Speed', wind_dir AS 'Wind Direction',
        humidity AS 'Relative Humidity', rain AS 'Rain', cloud AS 'Cloud' 
        FROM locations WHERE UPPER(name) NOT LIKE 'PORTABLE%' ORDER BY name""")
    locations = c.fetchall()

    headers = [i[0] for i in c.description]

    return (locations, headers)


def sql_new_user(new_user_details, email):
    connie = dbcon.connect()
    c = connie.cursor()
    # Check if user already exists
    c.execute("""SELECT * FROM users WHERE email = ?""", (email,))
    emails = c.fetchall()
    if emails == []:
        # If new user is unique then insert new user into the database
        c.execute(
            """INSERT INTO users(email, username, Firstname, Surname, password, location) VALUES(?, ?, ?, ?, ?, ?)""",
            new_user_details)
        connie.commit()
        return ("Success")
    else:
        return ("Fail")


def sql_retrieve_user_details(user_id):
    con = dbcon.connect()
    c = con.cursor()
    sql_query = """SELECT Firstname, Surname, username, email, location FROM users WHERE id = ?"""
    c.execute(sql_query, (user_id,))
    details = c.fetchall()
    return details


def sql_update_user_details(user_details):
    con = dbcon.connect()
    c = con.cursor()
    sql_query = """UPDATE users SET Firstname = ?, Surname = ?, username = ?, email = ?, location = ? WHERE id = ? """
    c.execute(sql_query, user_details)
    con.commit()
    return "Success"


if __name__ == "__main__":
    app.run()
