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

def add_update_booking(type_of_update, vac_id, vacation_name, vacation_upgraded, ref_no, mysql, app):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_booking_ref_no' in request.form) \
                and ('add_booking_description' in request.form) :
            
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


