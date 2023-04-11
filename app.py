import flask
from flask import Flask, redirect, url_for, render_template, request, session, flash, Blueprint, send_from_directory
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


# import from other python files 
import user.user_administration as user_administration
import user.logged_in as logged_in
import vacation.vacation as vacation
import vacation.vacation_destination as vacation_destination
import vacation.vacation_booking as vacation_booking
import vacation.vacation_budget as vacation_budget
import vacation.vacation_itinerary as vacation_itinerary
import vacation.vacation_map as vacation_map
import vacation.vacation_map_itin as vacation_map_itin

from common.generate_id import generate_id

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
    return user_administration.login(mysql)

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    return user_administration.sign_up(mysql)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# logged in

@app.route('/logged/home/')
def logged_home():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/', methods=['GET', 'POST'])
def logged_vacations():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return logged_in.logged_vacations(mysql)

@app.route('/logged/user/', methods=['GET', 'POST'])
def logged_user():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return logged_in.logged_user(mysql)

@app.route('/logged/settings/',methods=['GET','POST'])
def logged_settings():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return logged_in.logged_settings(mysql)

@app.route('/logged/settings/create',methods=['GET','POST'])
def create_vac_grp():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return logged_in.create_vac_grp(mysql)

@app.route('/logged/tutorial/')
def logged_tutorial():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template('/login/tutorial/tutorial.html')

@app.route('/logged/vacations/home/<string:page>/<string:vac_id>/')
def logged_vacations_template(vac_id, page):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT description, upg_user_id from vacation where vac_id=%s', (vac_id,))
    vacation_details = cursor.fetchone()
    vacation_name = vacation_details['description']
    print(vacation_details['upg_user_id'])
    vacation_upgraded = True
    if (vacation_details['upg_user_id'] is None):
        print("none")
        vacation_upgraded = False

    if page == 'summary':
        return redirect(url_for('logged_vacations_summary', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    elif page == 'itinerary':
        return redirect(
            url_for('logged_vacations_itinerary', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    elif page == 'planning':
        return redirect(url_for('logged_vacations_planning', vac_id=vac_id, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded,curr_tab="budget"))
    elif page == 'sharing':
        return redirect(url_for('logged_vacations_sharing', vac_id=vac_id, vacation_name=vacation_name, vacation_upgraded=vacation_upgraded))
    else:
        return redirect(url_for('logged_vacations'))


@app.route('/logged/vacations/summary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/')
def logged_vacations_summary(vac_id, vacation_name,vacation_upgraded):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * from vacation_summary where vac_id=%s order by vac_id', (vac_id,))
    vacation_summary = cursor.fetchone()
    cursor.execute(
        'SELECT vac_id, destination.dest_id, no_days, dstart_date, country, state  from (has_destination join destination on has_destination.dest_id = destination.dest_id)'
        'where vac_id =%s order by destination.dest_id', (vac_id,))
    vacation_destinations = cursor.fetchall()
    cursor.close()
    return render_template('/login/vacations/summary/summary.html', vacation_summary=vacation_summary, vac_id=vac_id,
                           vacation_destinations=vacation_destinations, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded)


@app.route('/logged/vacations/itinerary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/')
def logged_vacations_itinerary(vac_id, vacation_name,vacation_upgraded):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT vac_id, itin_date, date_format(itin_time,%s) as itin_time, itin_type, description, location, country, state, day_no from vacation_itinerary where vac_id=%s order by itin_date, itin_time', ('%T',vac_id,))
    vacation_timeline = cursor.fetchall()
    cursor.execute('SELECT vac_id, date_format(itin_time,%s) as itin_time, day_no, map_id, map_link, name, category, itin_date, itin_type, description, location, country, state from maps_itinerary_tbl where vac_id=%s order by day_no, itin_time', ('%T',vac_id,))
    vacation_maps_itinerary = cursor.fetchall()
    cursor.execute('SELECT * from vac_map order by map_id')
    public_maps = cursor.fetchall()
    cursor.close()
    return render_template('/login/vacations/itinerary/itinerary.html', vacation_timeline=vacation_timeline,
                           vac_id=vac_id, vacation_maps_itinerary=vacation_maps_itinerary, vacation_name=vacation_name,vacation_upgraded=vacation_upgraded, 
                           public_maps=public_maps)


@app.route('/logged/vacations/<string:curr_tab>/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/', methods=['GET', 'POST'])
def logged_vacations_planning(vac_id, vacation_name,vacation_upgraded, curr_tab):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT vac_id, budget_limit, total_spend, remaining_budget from vacation_summary where vac_id=%s',
                   (vac_id,))
    vacation_summary = cursor.fetchone()
    cursor.execute('SELECT * from budget where vac_id=%s order by budget_id', (vac_id,))
    vacation_budget = cursor.fetchall()
    cursor.execute('SELECT * from booking where vac_id=%s order by ref_no', (vac_id,))
    vacation_booking = cursor.fetchall()
    cursor.execute("SELECT vac_id, day_no, date_format(itin_time,%s) as itin_time, itin_type, description, location from itinerary where vac_id=%s order by day_no, itin_time", ('%T',vac_id,))
    vacation_itinerary = cursor.fetchall()
    cursor.execute('SELECT * from vac_map order by map_id')
    public_maps = cursor.fetchall()
    cursor.execute('SELECT vac_id, date_format(itin_time,%s) as itin_time, day_no, map_id, map_link, description, name, category'
                   ' from maps_itinerary_tbl where vac_id=%s order by day_no, itin_time', ('%T',vac_id,))
    maps_itin_fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][1:]
    vacation_itin_map = cursor.fetchall()

    if request.method == 'POST':
        if request.form['maps_itin_search'] != None:
            curr_tab = "maps_itin"
            category = request.form.get('maps_itin_category')
            if category in maps_itin_fields:
                search = '%' + request.form['maps_itin_search'] + '%'
                query = 'SELECT vac_id, date_format(itin_time,%s) as itin_time, day_no, map_link, description, name, category from maps_itinerary_tbl where ' + \
                        category.replace(" ", "_") + \
                        ' like %s and vac_id =%s order by day_no, itin_time'
                print(query)
                cursor.execute(query, ('%T',search, vac_id,))
                vacation_itin_map = cursor.fetchall()  # fetch all records
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
    if 'user_id' not in session:
        return redirect(url_for('home'))
    if vacation_upgraded=="False":
        return render_template('/login/vacations/sharing/not-upgraded-component.html')
    else:
        curr_tab = "memories"
        if request.method=="POST":
            if 'image_file' not in request.files:
                flash('No File Selected!','error')
                return redirect(request.url)
            uploaded_photo = request.files['image_file']
            album_category = request.form.get('album_category')
            print("album_category")
            print(album_category)
            if uploaded_photo.filename!='':
                if album_category=="NONE":
                    photo_album = None
                else:
                    photo_album = album_category
                photo_filename = secure_filename(uploaded_photo.filename)
                final_file_path = os.path.join(app.config['UPLOAD_FOLDER_PHOTO'],photo_filename)
                uploaded_photo.save(final_file_path)
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                photo_count = cursor.execute('SELECT * from photo')
                photo_id = generate_id(photo_count + 1, cursor, "photo", "photo_id")
                cursor.execute('INSERT into photo VALUES (%s,%s,%s)',(photo_id,photo_filename,photo_album,))
                mysql.connection.commit()
                flash('Photo Uploaded Successfully!','success')
                curr_tab = "photo_drive"
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from album where vac_id=%s order by alb_id', (vac_id,))
        vacation_albums = cursor.fetchall()
        cursor.execute('SELECT * from photo order by photo_id')
        vacation_photo_drive = cursor.fetchall()
        # to process blob into strings first before parsing 
        cursor.close()       
        return render_template('/login/vacations/sharing/sharing.html', vacation_photo_drive=vacation_photo_drive,
                            vacation_albums=vacation_albums, vac_id=vac_id, vacation_name=vacation_name, vacation_upgraded=vacation_upgraded,curr_tab=curr_tab)


@app.route('/logged/vacations/sharing/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:album_id>/')
def logged_vacations_album(vac_id, vacation_name, vacation_upgraded, album_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    print("enter")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT alb_name,alb_date from album where alb_id=%s',(album_id,))
    album_details = cursor.fetchone()
    cursor.execute('SELECT distinct alb_id, photo.photo_id, photolink from (user_photos join photo on photo.photo_id = user_photos.photo_id) where vac_id=%s and alb_id=%s order by alb_id,photo.photo_id',(vac_id,album_id,))
    vacation_photo_in_album = cursor.fetchall()
    print(vacation_photo_in_album)
    cursor.close()
    return render_template('/login/vacations/sharing/album-component.html', vac_id=vac_id, vacation_name=vacation_name,
                           vacation_photo_in_album=vacation_photo_in_album,album_details=album_details)


@app.route('/logged/vacations/<string:type_of_update>/<string:vac_id>/', methods=['GET', 'POST'])
def add_update_vacation(type_of_update, vac_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation.add_update_vacation(type_of_update,vac_id,mysql)

@app.route('/logged/vacations/summary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:dest_id>/<string:dstart_date>/<string:no_days>/', methods=['GET', 'POST'])
def add_update_destination(type_of_update, vac_id, vacation_name, vacation_upgraded, dest_id, dstart_date, no_days):
    if 'user_id' not in session:
        return redirect(url_for('home'))    
    return vacation_destination.add_update_destination(type_of_update, vac_id, vacation_name, vacation_upgraded, dest_id, dstart_date, no_days, mysql)

@app.route('/logged/vacations/planning/booking/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:ref_no>/', methods=['GET', 'POST'])
def add_update_booking(type_of_update, vac_id, vacation_name, vacation_upgraded, ref_no):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation_booking.add_update_booking(type_of_update, vac_id, vacation_name, vacation_upgraded, ref_no, mysql, app)
    
@app.route('/logged/vacations/planning/budget/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:budget_id>/', methods=['GET', 'POST'])
def add_update_budget(type_of_update, vac_id, vacation_name, vacation_upgraded, budget_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation_budget.add_update_budget(type_of_update, vac_id, vacation_name, vacation_upgraded, budget_id, mysql)
    
@app.route('/logged/vacations/planning/itinerary/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:day_no>/<string:itin_time>/', methods=['GET', 'POST'])
def add_update_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation_itinerary.add_update_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time, mysql)

@app.route("/logged/vacations/planning/itinerary-map/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/<string:itin_time>/<string:day_no>/<string:map_id>/", methods=['GET','POST'])
def add_delete_map_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time, map_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation_map_itin.add_delete_map_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time, map_id, mysql)


@app.route('/logged/vacations/planning/map/<string:vac_id>/<string:vacation_name>/<string:vacation_upgraded>/<string:type_of_update>/', methods=['GET', 'POST'])
def add_update_map(type_of_update, vac_id, vacation_name, vacation_upgraded):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return vacation_map.add_update_maps(type_of_update, vac_id, vacation_name, vacation_upgraded, mysql, app)


@app.route('/download/<string:attachment_type>/<string:file_path>/')
def download_file(attachment_type,file_path):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    print("filenmae")
    print(file_path)
    if attachment_type=="MAP":
        return send_from_directory(app.config['UPLOAD_FOLDER_MAP'],file_path)
    elif attachment_type=="BOOKING":
        return send_from_directory(app.config['UPLOAD_FOLDER_BOOKING'],file_path)
    else:
        print("something went wrong")
        return send_from_directory(app.config['UPLOAD_FOLDER_PHOTO'],file_path)

if __name__ == '__main__':
    app.run()
