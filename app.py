import flask
from flask import Flask, redirect, url_for, render_template, request, session, flash, Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import check_password_hash, generate_password_hash

app = flask.Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'readyhols'

mysql = MySQL(app)

app.secret_key = 'rEaDyHoLs!'

@app.route('/')
def home():
    return render_template('/n-login/home.html')


@app.route('/about-us')
def about_us():
    return render_template('/n-login/about-us.html')


@app.route('/contact-us')
def contact_us():
    return render_template('/n-login/contact-us.html')


@app.route('/learn-more')
def learn_more():
    return render_template('/n-login/learn-more.html')


@app.route('/tutorial')
def tutorial():
    return render_template('/n-login/tutorial.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ''
    if request.method == 'POST' and ('loginUsername' in request.form) and ('loginPassword' in request.form):
        username = request.form['loginUsername']
        password = request.form['loginPassword']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from user where username=%s', (username,))
        account = cursor.fetchone()
        print(account)

        if account:
            if check_password_hash(account['password'], password):
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['username'] = account['username']
                session['email'] = account['email']
                session['plan_type'] = account['plan_type']
                session['sub_mail'] = account['sub_mail']
                session['share_drive'] = account['share_drive']
                session['grp_count'] = account['grp_count']
                session['upg_count'] = account['upg_count']
                return redirect(url_for('logged_home'))
            else:
                flash('Incorrect password', 'error')
                session['loggedin'] = False

        else:
            flash('Invalid username', 'error')
            session['loggedin'] = False

        cursor.close()
    return render_template('/n-login/login.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST' and ('inputUsername' in request.form) and ('inputPassword' in request.form) and (
            'inputEmail' in request.form) and ('planRadios' in request.form):
        print("what")
        print(request.form)
        username = request.form['inputUsername']
        password = request.form['inputPassword']
        email = request.form['inputEmail']
        planRadios = request.form['planRadios']

        planType = ""

        subEmail = False
        if 'checkEmail' in request.form:
            subEmail = True

        if planRadios == 'basicOption':
            planType = "Basic"
        elif planRadios == 'plusOption':
            planType = "Plus"
        elif planRadios == 'premiumOption':
            planType = "Premium"
        else:
            flash("An error occurred while signing up. Please try again.", "error")

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from user where username =%s', (username,))
        account = cursor.fetchone()
        if account:
            flash('Account already exists!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid Email Address', 'error')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!', 'error')
        else:
            user_count = cursor.execute('SELECT * from user')
            cursor.execute('INSERT into user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           ("000000008", username, generate_password_hash(password), email, planType,
                            int(subEmail), int(False), 0, 0))
            mysql.connection.commit()
            flash('Congratulations, you have successfully registered. Try logging in now!', 'success')
            return redirect(url_for('login'))

    return render_template('/n-login/sign-up.html')


def logout():
    session.clear()
    return redirect(url_for('home'))


# logged in


@app.route('/logged/home')
def logged_home():
    return render_template('/login/vacations/vacations.html')


@app.route('/logged/vacations')
def logged_vacations():
    return render_template('/login/vacations/vacations.html')


@app.route('/logged/user')
def logged_user():
    return render_template('/login/user/user.html')


@app.route('/logged/settings')
def logged_settings():
    return render_template('/login/settings/settings.html')


@app.route('/logged/vacations/summary')
def logged_vacations_summary():
    return render_template('/login/vacations/summary/summary.html')


@app.route('/logged/vacations/itinerary')
def logged_vacations_itinerary():
    return render_template('/login/vacations/itinerary/itinerary.html')


@app.route('/logged/vacations/planning')
def logged_vacations_planning():
    return render_template('/login/vacations/planning/planning.html')


@app.route('/logged/vacations/sharing')
def logged_vacations_sharing():
    return render_template('/login/vacations/sharing/sharing.html')


if __name__ == '__main__':
    app.run()
