import flask
from flask import Flask, redirect, url_for, render_template, request, session, flash, Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import check_password_hash, generate_password_hash
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
import os
from werkzeug.utils import secure_filename
import datetime
from datetime import *

app = flask.Flask(__name__)

UPLOAD_FOLDER_PHOTO = os.getcwd().replace("\\","/")+'/static/server-storage/pictures/'
UPLOAD_FOLDER_BOOKING = os.getcwd().replace("\\","/")+'/static/server-storage/booking-attachment/'
UPLOAD_FOLDER_MAP = os.getcwd().replace("\\","/")+'/static/server-storage/map-attachment/'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'readyhols'
app.config['UPLOAD_FOLDER_PHOTO'] = UPLOAD_FOLDER_PHOTO
app.config['UPLOAD_FOLDER_BOOKING'] = UPLOAD_FOLDER_BOOKING
app.config['UPLOAD_FOLDER_MAP'] = UPLOAD_FOLDER_MAP

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
        elif not ((len(password) >= 8) and (len(password) <= 20) and (re.match(r'[A-Za-z0-9]+', password))):
            flash('Password must be 8-20 characters long, contain letters and numbers,'
                  ' and must not contain spaces, special characters, or emoji.')
        else:
            user_count = cursor.execute('SELECT * from user')
            user_id = generate_id(user_count + 1, cursor, "user", "user_id")
            cursor.execute('INSERT into user VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (user_id, username, generate_password_hash(password), email, planType,
                            int(subEmail), int(False), 0, 0))
            mysql.connection.commit()
            flash('Congratulations, you have successfully registered. Try logging in now!', 'success')
            return redirect(url_for('login'))
        cursor.close()

    return render_template('/n-login/sign-up.html')


def generate_id(type_count, cursor, table_name, id_name):
    valid_id = "{:09d}".format(type_count)
    exist_entry = None
    while exist_entry == None:
        cursor.execute('SELECT * from ' + table_name + ' where ' + ' ' + id_name + '=%s', (valid_id,))
        exist_entry = cursor.fetchone()
        if exist_entry == None:
            break
        type_count += 1
        valid_id = "{:09d}".format(type_count)
    return valid_id


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
    cursor.execute(
        'SELECT vacation.vac_id,vacation.vac_grp_id, description,start_date,end_date,budget_limit, upg_user_id from vac_user_has,vacation'
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


@app.route('/logged/user/', methods=['GET', 'POST'])
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
        elif not ((len(user_password) >= 8) and (len(user_password) <= 20) and (
                re.match(r'[A-Za-z0-9]+', user_password))):
            flash('Password must be 8-20 characters long, contain letters and numbers,'
                  ' and must not contain spaces, special characters, or emoji.', 'error')
        else:
            cursor.execute('UPDATE user set email=%s, password=%s, sub_mail=%s WHERE user_id = %s ',
                           (user_email, generate_password_hash(user_password), subEmail, session['user_id'],))
            mysql.connection.commit()  # note that you need to commit the changes for INSERT,UPDATE and DELETE statements
            flash('You have updated your email and password successfully', 'success')
    return render_template('/login/user/user.html')


@app.route('/logged/settings/',methods=['GET','POST'])
def logged_settings():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST' and ('vacation_grp_id' in request.form) and ('vacation_id_pin' in request.form):
        vacation_group = request.form['vacation_grp_id']
        vacation_group_pin = request.form['vacation_id_pin']

        print(vacation_group)
        print(vacation_group_pin)

        cursor.execute('SELECT vac_grp_id, vac_grp_pin from vacation_grp where vac_grp_id=%s',(vacation_group,))
        vacation_grp_details = cursor.fetchone()

        if vacation_grp_details is None:
            flash('There is no such vacation group!','error')
        elif not check_password_hash(vacation_grp_details['vac_grp_pin'],vacation_group_pin):
            flash('Incorrect Vacation Group Pin!','error')
        else:
            cursor.execute('INSERT INTO vac_user_in VALUES (%s,%s)', (vacation_group, session['user_id'],))
            mysql.connection.commit()  # note that you need to commit the changes for INSERT,UPDATE and DELETE statements
            flash('You have been added to the vacation group successfully!', 'success')

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
                   'and user.user_id<>%s', (session['user_id'], session['user_id'],))
    same_vacgrp_users = cursor.fetchall()

    return render_template('/login/settings/settings.html', user_vacgrp_details=user_vacgrp_details,
                           same_vacgrp_users=same_vacgrp_users)


@app.route('/logged/vacations/home/<string:page>/<string:vac_id>/')
def logged_vacations_template(vac_id, page):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT description, upg_user_id from vacation where vac_id=%s', (vac_id,))
    vacation_details = cursor.fetchone()
    vacation_name = vacation_details['description']
    print(vacation_details['upg_user_id'])
    vacation_upgraded = True
    if (vacation_details['upg_user_id'] is None):
        print("none")
        vacation_upgraded = False

    # render_template('/login/vacations/vacation-collapse-bar.html', vac_id=vac_id, page=page,vacation_name=vacation_name['description'])

    if page == 'summary':
        return redirect(url_for('logged_vacations_summary', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    elif page == 'itinerary':
        return redirect(
            url_for('logged_vacations_itinerary', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    elif page == 'planning':
        return redirect(url_for('logged_vacations_planning', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    elif page == 'sharing':
        return redirect(url_for('logged_vacations_sharing', vac_id=vac_id, vacation_name=vacation_name, vacation_upgraded=vacation_upgraded))
    else:
        return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/summary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>')
def logged_vacations_summary(vac_id, vacation_name,vacation_upgraded):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from vacation_summary where vac_id=%s', (vac_id,))
    vacation_summary = cursor.fetchone()
    cursor.execute(
        'SELECT vac_id, destination.dest_id, no_days, dstart_date, country, state  from (has_destination join destination on has_destination.dest_id = destination.dest_id)'
        'where vac_id =%s', (vac_id,))
    vacation_destinations = cursor.fetchall()
    cursor.close()
    return render_template('/login/vacations/summary/summary.html', vacation_summary=vacation_summary, vac_id=vac_id,
                           vacation_destinations=vacation_destinations, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded)


@app.route('/logged/vacations/itinerary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>')
def logged_vacations_itinerary(vac_id, vacation_name,vacation_upgraded):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from vacation_itinerary where vac_id=%s order by itin_date, itin_time', (vac_id,))
    vacation_timeline = cursor.fetchall()
    cursor.execute('SELECT * from maps_itinerary_tbl where vac_id=%s order by day_no, itin_time', (vac_id,))
    vacation_maps_itinerary = cursor.fetchall()

    cursor.close()
    return render_template('/login/vacations/itinerary/itinerary.html', vacation_timeline=vacation_timeline,
                           vac_id=vac_id, vacation_maps_itinerary=vacation_maps_itinerary, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded)


@app.route('/logged/vacations/planning/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/', methods=['GET', 'POST'])
def logged_vacations_planning(vac_id, vacation_name,vacation_upgraded):
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
    curr_tab = "budget"

    if request.method == 'POST':
        if request.form['maps_itin_search'] != None:
            curr_tab = "maps_itin"
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
                                       vac_id=vac_id, vacation_summary=vacation_summary,
                                       maps_itin_fields=maps_itin_fields,
                                       curr_tab=curr_tab, vacation_name=vacation_name,
                                       vacation_itinerary=vacation_itinerary,
                                       public_maps=public_maps,vacation_upgraded=vacation_upgraded)

    cursor.close()
    return render_template('/login/vacations/planning/planning.html', vacation_budget=vacation_budget,
                           vacation_booking=vacation_booking, vacation_itin_map=vacation_itin_map, vac_id=vac_id,
                           vacation_summary=vacation_summary, maps_itin_fields=maps_itin_fields, curr_tab=curr_tab,
                           vacation_name=vacation_name, vacation_itinerary=vacation_itinerary, public_maps=public_maps,vacation_upgraded=vacation_upgraded)


@app.route('/logged/vacations/sharing/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/', methods=['GET','POST'])
def logged_vacations_sharing(vac_id, vacation_name,vacation_upgraded):
    if vacation_upgraded=="False":
        return render_template('/login/vacations/sharing/not-upgraded-component.html')
    else:
        curr_tab = "memories"
        if request.method=="POST":
            if 'image_file' not in request.files:
                flash('No File Selected!','error')
                return redirect(request.url)
            uploaded_photo = request.files['image_file']
            if uploaded_photo.filename!='':
                photo_filename = secure_filename(uploaded_photo.filename)
                final_file_path = os.path.join(app.config['UPLOAD_FOLDER_PHOTO'],photo_filename)
                print("final")
                print(final_file_path)
                uploaded_photo.save(final_file_path)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                photo_count = cursor.execute('SELECT * from photo')
                photo_id = generate_id(photo_count + 1, cursor, "photo", "photo_id")
                cursor.execute('INSERT into photo VALUES (%s,%s,%s)',(photo_id,"/pictures/"+photo_filename,None,))
                mysql.connection.commit()
                flash('Photo Uploaded Successfully!','success')
                curr_tab = "photo_drive"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from album where vac_id=%s', (vac_id,))
        vacation_albums = cursor.fetchall()
        cursor.execute('SELECT * from photo')
        vacation_photo_drive = cursor.fetchall()
        # to process blob into strings first before parsing 
        cursor.close()       
        return render_template('/login/vacations/sharing/sharing.html', vacation_photo_drive=vacation_photo_drive,
                            vacation_albums=vacation_albums, vac_id=vac_id, vacation_name=vacation_name, vacation_upgraded=vacation_upgraded,curr_tab=curr_tab)


@app.route('/logged/vacations/sharing/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:album_id>/')
def logged_vacations_album(vac_id, vacation_name, vacation_upgraded, album_id):
    print("enter")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT alb_name,alb_date from album where alb_id=%s',(album_id,))
    album_details = cursor.fetchone()
    cursor.execute('SELECT distinct alb_id, photo.photo_id, photolink from (user_photos join photo on photo.photo_id = user_photos.photo_id) where vac_id=%s and alb_id=%s',(vac_id,album_id,))
    vacation_photo_in_album = cursor.fetchall()
    print(vacation_photo_in_album)
    cursor.close()
    return render_template('/login/vacations/sharing/album-component.html', vac_id=vac_id, vacation_name=vacation_name,
                           vacation_photo_in_album=vacation_photo_in_album,album_details=album_details)


@app.route('/logged/vacations/<string:type_of_update>/<string:vac_id>/', methods=['GET', 'POST'])
def add_update_vacation(type_of_update, vac_id):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_vacation_description' in request.form) and (
                'add_vacation_grp' in request.form) \
                and ('add_vacation_grp_pin' in request.form) and ('add_vacation_start_date' in request.form) and \
                ('add_vacation_end_date' in request.form) and ('add_vacation_budget_limit' in request.form):
            vacation_description = request.form['add_vacation_description']
            vacation_grp = request.form['add_vacation_grp']
            vacation_grp_pin = request.form['add_vacation_grp_pin']
            vacation_start_date = request.form['add_vacation_start_date']
            vacation_end_date = request.form['add_vacation_end_date']
            vacation_budget_limit = request.form['add_vacation_budget_limit']
            upgradeVacation = False
            upg_user_id = None

            print(vacation_grp)

            print(vacation_description)
            if 'vacationUpgrade' in request.form:
                upgradeVacation = True
                upg_user_id = session['user_id']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT vacation_grp.vac_grp_id,vac_grp_pin from vacation_grp,vac_user_in'
                           ' where (vac_user_in.vac_grp_id = vacation_grp.vac_grp_id) and vacation_grp.vac_grp_id=%s and user_id=%s',
                           (vacation_grp, session['user_id'],))
            vacation_grp_details = cursor.fetchone()
            print(vacation_grp_details)
            if vacation_grp_details == None:
                flash('You can only create vacations for groups you are in!', 'error')
            else:
                if check_password_hash(vacation_grp_details['vac_grp_pin'], vacation_grp_pin):
                    vacation_count = cursor.execute('SELECT * from vacation')

                    if not re.match(r'[A-Za-z0-9]+', vacation_description):
                        flash('Description must contain only characters and numbers!', 'error')
                    else:
                        vacation_id = generate_id(vacation_count + 1, cursor, "vacation", "vac_id")
                        cursor.execute('INSERT INTO vacation VALUES(%s,%s,%s,%s,%s,%s,%s)',
                                       (vacation_id, vacation_description, vacation_grp, upg_user_id,
                                        vacation_start_date,
                                        vacation_end_date, vacation_budget_limit,))
                        mysql.connection.commit()
                        flash('Congratulations, you have successfully added a new vacation!', 'success')
                        cursor.close()
                        return redirect(url_for('logged_vacations'))
                    cursor.close()

                else:
                    flash('Incorrect Vacation Group PIN!', 'error')
    elif type_of_update == "Update":
        if request.method == 'POST' and ('add_vacation_description' in request.form) \
                and ('add_vacation_start_date' in request.form) and \
                ('add_vacation_end_date' in request.form) and ('add_vacation_budget_limit' in request.form):
            vacation_description = request.form['add_vacation_description']
            vacation_start_date = request.form['add_vacation_start_date']
            vacation_end_date = request.form['add_vacation_end_date']
            vacation_budget_limit = request.form['add_vacation_budget_limit']
            upgradeVacation = False
            upg_user_id = None

            if 'vacationUpgrade' in request.form:
                upgradeVacation = True
                upg_user_id = session['user_id']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z0-9]+', vacation_description):
                flash('Description must contain only characters and numbers!', 'error')
            else:
                cursor.execute(
                    'UPDATE vacation set description=%s,upg_user_id=%s,start_date=%s,end_date=%s,budget_limit=%s where vac_id=%s',
                    (vacation_description, upg_user_id, vacation_start_date, vacation_end_date, vacation_budget_limit,
                     vac_id,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully updated your vacation!', 'success')
                cursor.close()
                return redirect(url_for('logged_vacations'))

    elif type_of_update == "Delete":
        print("helloooooo deleting?")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from vacation where vac_id=%s', (vac_id,))
        mysql.connection.commit()
        return redirect(url_for('logged_vacations'))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/summary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:dest_id>/<string:dstart_date>/<string:no_days>/', methods=['GET', 'POST'])
def add_update_destination(type_of_update, vac_id, vacation_name, vacation_upgraded, dest_id, dstart_date, no_days):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_destination_country' in request.form) and (
                'add_destination_state' in request.form) \
                and ('add_destination_start_date' in request.form) and ('add_destination_duration' in request.form):
            destination_country = request.form['add_destination_country']
            destination_state = request.form['add_destination_state']
            destination_start_date = request.form['add_destination_start_date']
            destination_duration = request.form['add_destination_duration']

            destination_start_date_datetype = date.fromisoformat(destination_start_date)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT start_date,end_date from vacation where vac_id=%s',(vac_id,))
            vacation_duration = cursor.fetchone()
            betweenDate,errorMessage = check_between_date(destination_start_date_datetype,vacation_duration['start_date'],vacation_duration['end_date'],destination_duration)
            
            print("betweenDate")
            print(betweenDate)
            if not re.match(r'[A-Za-z]+', destination_country):
                flash('Country must contain only characters!', 'error')
            if not re.match(r'[A-Za-z]+', destination_state):
                flash('State must contain only characters!', 'error')
            elif not betweenDate:
                flash(errorMessage,'error')
            else:
                cursor.execute('SELECT * from destination where country=%s and state=%s',
                            (destination_country, destination_state,))
                has_such_destination = cursor.fetchone()
                print(has_such_destination)
                if has_such_destination == None:
                    destination_count = cursor.execute('SELECT * from destination')
                    destination_id = generate_id(destination_count + 1, cursor, "destination", "dest_id")
                    cursor.execute('INSERT into destination VALUES(%s,%s,%s)',(destination_id,destination_country,destination_state,))
                    mysql.connection.commit()
                    to_ref_dest_id = destination_id
                else:    
                    to_ref_dest_id = has_such_destination['dest_id']
                print(to_ref_dest_id)
                cursor.execute('INSERT into has_destination VALUES (%s,%s,%s,%s)',(vac_id,to_ref_dest_id,destination_duration,destination_start_date,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully added your new destination!','success')
                cursor.close()
                return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Update":
        if request.method == 'POST' and ('add_destination_country' in request.form) \
                and ('add_destination_state' in request.form) and \
                ('add_destination_start_date' in request.form) and ('add_destination_duration' in request.form):
            destination_country = request.form['add_destination_country']
            destination_state = request.form['add_destination_state']
            destination_start_date = request.form['add_destination_start_date']
            destination_duration = request.form['add_destination_duration']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            destination_start_date_datetype = date.fromisoformat(destination_start_date)

            cursor.execute('SELECT start_date,end_date from vacation where vac_id=%s',(vac_id,))
            vacation_duration = cursor.fetchone()
            betweenDate,errorMessage = check_between_date(destination_start_date_datetype,vacation_duration['start_date'],vacation_duration['end_date'],destination_duration)
            
            if not re.match(r'[A-Za-z]+', destination_country):
                flash('Country must contain only characters!', 'error')
            if not re.match(r'[A-Za-z]+', destination_state):
                flash('State must contain only characters!', 'error')
            elif not betweenDate:
                flash(errorMessage,'error')
            else:
                cursor.execute('SELECT * from destination where country=%s and state=%s',
                            (destination_country, destination_state,))
                has_such_destination = cursor.fetchone()
                print(has_such_destination)
                if has_such_destination == None:
                    destination_count = cursor.execute('SELECT * from destination')
                    destination_id = generate_id(destination_count + 1, cursor, "destination", "dest_id")
                    cursor.execute('INSERT into destination VALUES(%s,%s,%s)',(destination_id,destination_country,destination_state,))
                    mysql.connection.commit()
                    to_ref_dest_id = destination_id
                else:
                    to_ref_dest_id = has_such_destination['dest_id']
                
                # delete and add as primary key cannot be modified 
                cursor.execute('DELETE from has_destination where vac_id=%s and dest_id=%s and dstart_date=%s and no_days=%s',
                               (vac_id,dest_id,dstart_date,no_days))
                mysql.connection.commit()
                cursor.execute('INSERT into has_destination VALUES(%s,%s,%s,%s)',(vac_id,to_ref_dest_id,destination_duration,destination_start_date_datetype,))
                mysql.connection.commit()
                flash('Destination updated successfully!', 'success')
                cursor.close()
                return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Delete":
        print("helloooooo deleting?")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from has_destination where vac_id=%s and dest_id=%s and dstart_date=%s and no_days=%s', (vac_id,dest_id,destination_start_date_datetype,no_days))
        mysql.connection.commit()
        flash('Destination deleted successfully!')
        return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))


@app.route('/logged/vacations/planning/booking/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:ref_no>/', methods=['GET', 'POST'])
def add_update_booking(type_of_update, vac_id, vacation_name, vacation_upgraded, ref_no):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_booking_ref_no' in request.form) \
                and ('add_booking_description' in request.form) :
            
            print("checkpoitsf1")
            booking_category = request.form.get('booking_category')
            booking_ref_no = request.form['add_booking_ref_no']
            booking_description = request.form['add_booking_description']
            booking_attachment_path = ""

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', booking_description):
                flash('Remarks must contain only characters!', 'error')
            else:
                print("checionasdj12")
                cursor.execute('SELECT * from booking where vac_id=%s',(vac_id,))
                vacation_bookings = cursor.fetchall()
                booking_ref_no_taken = False
                for i in vacation_bookings:
                    if i['ref_no']==booking_ref_no:
                        booking_ref_no_taken = True
                        break
                if (booking_ref_no_taken):
                    flash('This reference no is being taken and cannot be repeated!','error')
                else:
                    if 'add_booking_attachment' in request.files:
                        uploaded_booking = request.files['add_booking_attachment']
                        if uploaded_booking.filename!='':
                            booking_filename = secure_filename(uploaded_booking.filename)
                            final_file_path = os.path.join(app.config['UPLOAD_FOLDER_BOOKING'],booking_filename)
                            uploaded_booking.save(final_file_path)
                            booking_attachment_path = "/booking-attachment/"+booking_filename
                    cursor.execute('INSERT into booking VALUES (%s,%s,%s,%s,%s)',(vac_id,booking_ref_no,booking_category,booking_description,booking_attachment_path,))
                    mysql.connection.commit()
                    flash('Congratulations, you have successfully added your new booking!','success')
                    cursor.close()
                    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    if type_of_update == "Update":
        if request.method == 'POST' \
                and ('add_booking_description' in request.form) :
            
            print("kjf;aklfjd2241412")
            
            booking_category = request.form.get('booking_category')
            booking_description = request.form['add_booking_description']
            booking_attachment_path = ""

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            print("43143134")

            if not re.match(r'[A-Za-z]+', booking_description):
                flash('Country must contain only characters!', 'error')
            else:
                print("134515509")
                
                if 'add_booking_attachment' in request.files:
                    uploaded_booking = request.files['add_booking_attachment']
                    if uploaded_booking.filename!='':
                        booking_filename = secure_filename(uploaded_booking.filename)
                        final_file_path = os.path.join(app.config['UPLOAD_FOLDER_BOOKING'],booking_filename)
                        uploaded_booking.save(final_file_path)
                        booking_attachment_path = "/booking-attachment/"+booking_filename
                print("sql updating")
                cursor.execute('UPDATE booking set description=%s,booking_type=%s,attachment=%s where vac_id=%s and ref_no=%s',
                            (booking_description,booking_category,booking_attachment_path,vac_id,ref_no,))
                mysql.connection.commit()
                flash('Booking updated component updated successfully!', 'success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Delete":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from booking where vac_id=%s and ref_no=%s', (vac_id,ref_no,))
        mysql.connection.commit()
        flash('Booking deleted successfully!','success')
        return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

@app.route('/logged/vacations/planning/budget/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:budget_id>/', methods=['GET', 'POST'])
def add_update_budget(type_of_update, vac_id, vacation_name, vacation_upgraded, budget_id):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and (
                'add_budget_expenditure' in request.form) \
                and ('add_budget_remarks' in request.form) :
            
            budget_category = request.form.get('budget_category')
            budget_expenditure = request.form['add_budget_expenditure']
            budget_remarks = request.form['add_budget_remarks']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', budget_remarks):
                flash('Remarks must contain only characters!', 'error')
            else:
                budget_count = cursor.execute('SELECT * from budget')
                budget_id = generate_id(budget_count + 1, cursor, "budget", "budget_id")
                cursor.execute('INSERT into budget VALUES (%s,%s,%s,%s,%s)',(vac_id,budget_id,budget_category,budget_expenditure,budget_remarks,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully added your new budget component!','success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Update":
        print("updating")
        print(vac_id)
        print(budget_id)
        if request.method == 'POST' and (
                'add_budget_expenditure' in request.form) \
                and ('add_budget_remarks' in request.form) :
            budget_category = request.form.get('budget_category')
            budget_expenditure = request.form['add_budget_expenditure']
            budget_remarks = request.form['add_budget_remarks']

            print("budget_category")
            print(budget_category)

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', budget_remarks):
                flash('Country must contain only characters!', 'error')
            else:
                cursor.execute('UPDATE budget set category=%s,expenditure=%s,remarks=%s where vac_id=%s and budget_id=%s',
                               (budget_category,int(budget_expenditure),budget_remarks,vac_id,budget_id,))
                mysql.connection.commit()
                flash('Budget component updated successfully!', 'success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Delete":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from budget where vac_id=%s and budget_id=%s', (vac_id,budget_id,))
        mysql.connection.commit()
        flash('Budget component deleted successfully!','success')
        return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))


def check_between_date(dstart_date, start_date, end_date, no_days):
    error_message = ""
    end_date_destination = dstart_date + timedelta(days=int(no_days))
    if dstart_date < start_date:
        error_message = "Start Date of Destination cannot be before Start Date of Trip!"
        return False, error_message
    elif end_date_destination > end_date:
        error_message = "Destination cannot last beyond the End Date of the Trip!"
        return False, error_message
    return True, error_message

if __name__ == '__main__':
    app.run()
