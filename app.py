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
                session['plan_type'] = account['plan_type']
                session['email'] = account['email']
                session['sub_mail'] = account['sub_mail']
                session['share_drive'] = account['share_drive']
                session['grp_count'] = account['grp_count']
                session['upg_count'] = account['upg_count']
                session['password'] = account['password']
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
        elif not ((len(password) >= 8) and (len(password) <= 20) and (re.match(r'[A-Za-z0-9]+',password))):
            flash('Password must be 8-20 characters long, contain letters and numbers,'
                  ' and must not contain spaces, special characters, or emoji.')
        else:
            user_count = cursor.execute('SELECT * from user')
            user_id = generate_user_id(user_count + 1, cursor)
            cursor.execute('INSERT into user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (user_id, username, generate_password_hash(password), email, planType,
                            int(subEmail), int(False), 0, 0))
            mysql.connection.commit()
            flash('Congratulations, you have successfully registered. Try logging in now!', 'success')
            return redirect(url_for('login'))
        cursor.close()

    return render_template('/n-login/sign-up.html')


def generate_user_id(user_count, cursor):
    valid_user_id = "{:09d}".format(user_count)
    account = None
    while account == None:
        cursor.execute('SELECT * from user where user_id=%s', (valid_user_id,))
        account = cursor.fetchone()
        if account == None:
            break
        user_count += 1
        cursor.close()
    return valid_user_id


def logout():
    session.clear()
    return redirect(url_for('home'))


# logged in


@app.route('/logged/home/')
def logged_home():
    return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/', methods=['GET', 'POST'])
def logged_vacations():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT vacation.vac_id,description,start_date,end_date,budget_limit from vac_user_has,vacation'
                   ' where vacation.vac_id = vac_user_has.vac_id and vac_user_has.user_id =%s '
                   'order by start_date,end_date', (session['user_id'],))
    fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][1:]
    true_all_vacations_user = cursor.fetchall()
    vacations_user = true_all_vacations_user

    if request.method == 'POST':
        category = request.form.get('category')
        if category in fields:
            search = '%' + request.form['search'] + '%'
            query = 'SELECT vacation.vac_id,description,start_date,end_date,budget_limit from vac_user_has,vacation where ' + \
                    category.replace(" ", "_") + \
                    ' like %s and vacation.vac_id = vac_user_has.vac_id and vac_user_has.user_id =%s order by start_date,end_date'
            print(query)
            cursor.execute(query, (search, session['user_id'],))
            vacations_user = cursor.fetchall()  # fetch all records
            cursor.close()
            return render_template('/login/vacations/vacations.html', vacations_user=vacations_user,
                                   recent_vacations_user=true_all_vacations_user[:4],
                                   fields=fields)  # pass books data to search.html

    cursor.close()
    return render_template('/login/vacations/vacations.html', vacations_user=vacations_user,
                           recent_vacations_user=vacations_user[:4], fields=fields)


@app.route('/logged/user/',methods=['GET','POST'])
def logged_user():
    if request.method == 'POST' and ('user_email' in request.form) and ('user_password' in request.form):
        user_email = request.form['user_email']
        user_password = request.form['user_password']
        subEmail = False
        if 'checkEmail' in request.form:
            subEmail = True
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if not re.match(r'[^@]+@[^@]+\.[^@]+', user_email):
            flash('Invalid email address! Updates not done.', 'error')
        elif not ((len(user_password) >= 8) and (len(user_password) <= 20) and (re.match(r'[A-Za-z0-9]+',user_password))):
            flash('Password must be 8-20 characters long, contain letters and numbers,'
                  ' and must not contain spaces, special characters, or emoji.','error')
        else:
            cursor.execute('UPDATE user set email=%s, password=%s, sub_mail=%s WHERE user_id = %s ',
                           (user_email, generate_password_hash(user_password), subEmail, session['user_id'],))
            mysql.connection.commit()  # note that you need to commit the changes for INSERT,UPDATE and DELETE statements
            flash('You have updated your email and password successfully', 'success')
    return render_template('/login/user/user.html')


@app.route('/logged/settings/')
def logged_settings():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT vac_grp_tbl.vac_grp_id, grp_name, vac_grp_pin from '
                   '(SELECT vu2.vac_grp_id from vac_user_in vu2 where user_id=%s) as vac_user_tbl join'
                   ' (SELECT * from vacation_grp) as vac_grp_tbl'
                   ' on vac_grp_tbl.vac_grp_id = vac_user_tbl.vac_grp_id'
                   ' order by vac_grp_tbl.vac_grp_id',
                   (session['user_id'],))
    user_vacgrp_details = cursor.fetchall()
    print(user_vacgrp_details)
    cursor.execute('SELECT vac_grp_id, user.user_id, username from vac_user_in, user '
                   'where user.user_id = vac_user_in.user_id and '
                   '(vac_grp_id in (select vu2.vac_grp_id from vac_user_in vu2 where user_id=%s))'
                   'and user.user_id<>%s',(session['user_id'],session['user_id'],))
    same_vacgrp_users = cursor.fetchall()
    return render_template('/login/settings/settings.html',user_vacgrp_details=user_vacgrp_details,
                           same_vacgrp_users=same_vacgrp_users)


@app.route('/logged/vacations/home/<string:page>/<string:vac_id>/')
def logged_vacations_template(vac_id, page):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT description from vacation where vac_id=%s',(vac_id,))
    vacation_name = cursor.fetchone()
    # render_template('/login/vacations/vacation-collapse-bar.html', vac_id=vac_id, page=page,vacation_name=vacation_name['description'])

    if page == 'summary':
        return redirect(url_for('logged_vacations_summary', vac_id=vac_id,vacation_name=vacation_name['description']))
    elif page == 'itinerary':
        return redirect(url_for('logged_vacations_itinerary', vac_id=vac_id,vacation_name=vacation_name['description']))
    elif page == 'planning':
        return redirect(url_for('logged_vacations_planning', vac_id=vac_id,vacation_name=vacation_name['description']))
    elif page == 'sharing':
        return redirect(url_for('logged_vacations_sharing', vac_id=vac_id,vacation_name=vacation_name['description']))
    else:
        return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/summary/<string:vac_id>/<string:vacation_name>/')
def logged_vacations_summary(vac_id,vacation_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from vacation_summary where vac_id=%s', (vac_id,))
    vacation_summary = cursor.fetchone()
    cursor.execute(
        'SELECT vac_id, destination.dest_id, no_days, dstart_date, country, state  from (has_destination join destination on has_destination.dest_id = destination.dest_id)'
        'where vac_id =%s', (vac_id,))
    vacation_destinations = cursor.fetchall()
    cursor.close()
    return render_template('/login/vacations/summary/summary.html', vacation_summary=vacation_summary, vac_id=vac_id,
                           vacation_destinations=vacation_destinations,vacation_name=vacation_name)


@app.route('/logged/vacations/itinerary/<string:vac_id>/<string:vacation_name>/')
def logged_vacations_itinerary(vac_id,vacation_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from vacation_itinerary where vac_id=%s order by itin_date, itin_time', (vac_id,))
    vacation_timeline = cursor.fetchall()
    cursor.execute('SELECT * from maps_itinerary_tbl where vac_id=%s order by day_no, itin_time', (vac_id,))
    vacation_maps_itinerary = cursor.fetchall()

    cursor.close()
    return render_template('/login/vacations/itinerary/itinerary.html', vacation_timeline=vacation_timeline,
                           vac_id=vac_id, vacation_maps_itinerary=vacation_maps_itinerary,vacation_name=vacation_name)


@app.route('/logged/vacations/planning/<string:vac_id>/<string:vacation_name>/',methods=['GET','POST'])
def logged_vacations_planning(vac_id,vacation_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT vac_id, budget_limit, total_spend, remaining_budget from vacation_summary where vac_id=%s',
                   (vac_id,))
    vacation_summary = cursor.fetchone()
    cursor.execute('SELECT * from budget where vac_id=%s', (vac_id,))
    # budget_fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][1:]
    # print(budget_fields)
    vacation_budget = cursor.fetchall()
    cursor.execute('SELECT * from booking where vac_id=%s', (vac_id,))
    # booking_fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][1:]
    # print(booking_fields)
    vacation_booking = cursor.fetchall()
    # maps related to each itinerary
    cursor.execute('SELECT * from itinerary where vac_id=%s', (vac_id,))
    vacation_itinerary = cursor.fetchall()
    cursor.execute('SELECT * from vac_map')
    public_maps = cursor.fetchall()
    cursor.execute('SELECT vac_id, itin_time, day_no, map_link, description, name, category'
                   ' from maps_itinerary_tbl where vac_id=%s order by day_no, itin_time', (vac_id,))
    maps_itin_fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][1:]
    print(maps_itin_fields)
    vacation_itin_map = cursor.fetchall()
    curr_tab="budget"

    if request.method == 'POST':
        if request.form['maps_itin_search']!= None:
            curr_tab="maps_itin"
            category = request.form.get('maps_itin_category')
            if category in maps_itin_fields:
                search = '%' + request.form['maps_itin_search'] + '%'
                query = 'SELECT vac_id, itin_time, day_no, map_link, description, name, category from maps_itinerary_tbl where ' + \
                        category.replace(" ", "_") + \
                        ' like %s and vac_id =%s order by day_no, itin_time'
                print(query)
                cursor.execute(query, (search, vac_id,))
                vacation_itin_map = cursor.fetchall()  # fetch all records
                print(curr_tab)
                return render_template('/login/vacations/planning/planning.html', vacation_budget=vacation_budget,
                                       vacation_booking=vacation_booking, vacation_itin_map=vacation_itin_map,
                                       vac_id=vac_id,vacation_summary=vacation_summary, maps_itin_fields=maps_itin_fields,
                                       curr_tab=curr_tab,vacation_name=vacation_name,vacation_itinerary=vacation_itinerary,
                                       public_maps=public_maps)

    cursor.close()
    return render_template('/login/vacations/planning/planning.html', vacation_budget=vacation_budget,
                           vacation_booking=vacation_booking, vacation_itin_map=vacation_itin_map, vac_id=vac_id,
                           vacation_summary=vacation_summary,maps_itin_fields=maps_itin_fields,curr_tab=curr_tab,
                           vacation_name=vacation_name,vacation_itinerary=vacation_itinerary,public_maps=public_maps)


@app.route('/logged/vacations/sharing/<string:vac_id>/<string:vacation_name>/')
def logged_vacations_sharing(vac_id,vacation_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from album where vac_id=%s',(vac_id,))
    vacation_albums = cursor.fetchall()
    vacation_photo_drive = None
    vacation_photo_in_album = None
    cursor.close()
    return render_template('/login/vacations/sharing/sharing.html', vacation_photo_drive=vacation_photo_drive,
                           vacation_albums=vacation_albums, vac_id=vac_id,vacation_name=vacation_name,
                           vacation_photo_in_album=vacation_photo_in_album)


if __name__ == '__main__':
    app.run()
