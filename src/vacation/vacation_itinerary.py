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

def add_update_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time, mysql):
    
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_itin_day_no' in request.form) \
                and ('add_itin_time' in request.form) and ('add_itin_description' in request.form) \
                and ('add_itin_location' in request.form):
            
            itinerary_type = request.form.get('itin_category')
            itinerary_day_no = request.form['add_itin_day_no']
            itinerary_time = request.form['add_itin_time']
            itinerary_description = request.form['add_itin_description']
            itinerary_location = request.form['add_itin_location']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', itinerary_description):
                flash('Remarks must contain only characters!', 'error')
            elif not re.match(r'[A-Za-z]+', itinerary_location):
                flash('Location must only contain characters!','error')
            else:
                cursor.execute('SELECT * from itinerary where vac_id=%s',(vac_id,))
                used_ids = cursor.fetchall()
                is_id_take = False
                for i in used_ids:
                    if i['day_no']==day_no and i['itin_time']==itin_time:
                        is_id_take = True
                if is_id_take:
                    flash('There cannot be an itinerary with the same day no. and itin time!','error')
                else:
                    cursor.execute('INSERT into itinerary VALUES (%s,%s,%s,%s,%s,%s)',(vac_id,itinerary_day_no,itinerary_time,itinerary_type,itinerary_description,itinerary_location,))
                    mysql.connection.commit()
                    flash('Congratulations, you have successfully added your new itinerary!','success')
                    cursor.close()
                    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Update":
        print("updating")

        if request.method == 'POST' and ('add_itin_description' in request.form) \
                and ('add_itin_location' in request.form):
            
            itinerary_type = request.form.get('itin_category')
            itinerary_description = request.form['add_itin_description']
            itinerary_location = request.form['add_itin_location']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', itinerary_description):
                flash('Country must contain only characters!', 'error')
            elif not re.match(r'[A-Za-z]+', itinerary_location):
                flash('Location must only contain characters!','error')
            else:
                cursor.execute('UPDATE itinerary set itin_type=%s,description=%s,location=%s where vac_id=%s and day_no=%s and itin_time=%s',
                               (itinerary_type,itinerary_description,itinerary_location,vac_id,day_no,itin_time,))
                mysql.connection.commit()
                flash('Itinerary updated successfully!', 'success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Delete":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from itinerary where vac_id=%s and day_no=%s and itin_time=%s', (vac_id,day_no,itin_time,))
        mysql.connection.commit()
        flash('Itinerary deleted successfully!','success')
        return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))