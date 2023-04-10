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

from common.generate_id import generate_id

def add_update_destination(type_of_update, vac_id, vacation_name, vacation_upgraded, dest_id, dstart_date, no_days, mysql):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_destination_country' in request.form) and (
                'add_destination_state' in request.form) \
                and ('add_destination_start_date' in request.form) and ('add_destination_duration' in request.form):
            destination_country = request.form['add_destination_country']
            destination_state = request.form['add_destination_state']
            destination_start_date = request.form['add_destination_start_date']
            destination_duration = request.form['add_destination_duration']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT start_date,end_date from vacation where vac_id=%s',(vac_id,))
            vacation_duration = cursor.fetchone()
            betweenDate,errorMessage = check_between_date(destination_start_date,vacation_duration['start_date'],vacation_duration['end_date'],destination_duration)
            
            print("betweenDate")
            print(betweenDate)
            if not re.match(r'[A-Za-z]+', destination_country):
                flash('Country must contain only characters!', 'error')
            elif not len(destination_country) <=50:
                flash('Country cannot contain more than 50 characters!','error')
            if not re.match(r'[A-Za-z]+', destination_state):
                flash('State must contain only characters!', 'error')
            elif not len(destination_state) <=50:
                flash('State cannot contain more than 50 characters','error')
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
                cursor.execute('SELECT * from has_destination where vac_id=%s and dest_id=%s and no_days=%s and dstart_date=%s',(vac_id,to_ref_dest_id,destination_duration,destination_start_date,))
                has_destination_entry = cursor.fetchone()
                if has_destination_entry is not None:
                    flash('Duplicate destination entry cannot be inserted!','error')
                else:
                    cursor.execute('INSERT into has_destination VALUES (%s,%s,%s,%s)',(vac_id,to_ref_dest_id,destination_duration,destination_start_date,))
                    mysql.connection.commit()
                    flash('Congratulations, you have successfully added your new destination!','success')
                    cursor.close()
                return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
            cursor.close()
    elif type_of_update == "Update":
        if request.method == 'POST' and ('add_destination_country' in request.form) \
                and ('add_destination_state' in request.form) and \
                ('add_destination_start_date' in request.form) and ('add_destination_duration' in request.form):
            destination_country = request.form['add_destination_country']
            destination_state = request.form['add_destination_state']
            destination_start_date = request.form['add_destination_start_date']
            destination_duration = request.form['add_destination_duration']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT start_date,end_date from vacation where vac_id=%s',(vac_id,))
            vacation_duration = cursor.fetchone()
            betweenDate,errorMessage = check_between_date(destination_start_date,vacation_duration['start_date'],vacation_duration['end_date'],destination_duration)
            
            if not re.match(r'[A-Za-z]+', destination_country):
                flash('Country must contain only characters!', 'error')
            elif not len(destination_country) <=50:
                flash('Country cannot contain more than 50 characters!','error')
            if not re.match(r'[A-Za-z]+', destination_state):
                flash('State must contain only characters!', 'error')
            elif not len(destination_state) <=50:
                flash('State cannot contain more than 50 characters!','error')
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
                
                cursor.execute('SELECT * from has_destination where vac_id=%s and dest_id=%s and no_days=%s and dstart_date=%s',
                               (vac_id,to_ref_dest_id,destination_duration,destination_start_date,))
                has_destination_entry = cursor.fetchone()

                if has_destination_entry is not None:
                    flash('Duplicate destination entry cannot be inserted!','error')
                else:
                    # delete and add as primary key cannot be modified 
                    cursor.execute('DELETE from has_destination where vac_id=%s and dest_id=%s and dstart_date=%s and no_days=%s',
                               (vac_id,dest_id,dstart_date,no_days))
                    mysql.connection.commit()
                    cursor.execute('INSERT into has_destination VALUES(%s,%s,%s,%s)',(vac_id,to_ref_dest_id,destination_duration,destination_start_date,))
                    mysql.connection.commit()
                    flash('Destination updated successfully!', 'success')
                    cursor.close()
                return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
            cursor.close()
    elif type_of_update == "Delete":
        print("helloooooo deleting?")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from has_destination where vac_id=%s and dest_id=%s and dstart_date=%s and no_days=%s', (vac_id,dest_id,dstart_date,no_days))
        mysql.connection.commit()
        flash('Destination deleted successfully!')
        cursor.close()
        return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")
    

    return redirect(url_for('logged_vacations_summary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))


def check_between_date(dstart_date, start_date, end_date, no_days):
    error_message = ""
    year_dstart_date = dstart_date.split("-")[0]
    if (len(year_dstart_date)!=4):
        error_message = "Date is in incorrect format!"
        return False, error_message
    elif int(no_days)-1<0:
        error_message = "Number of days cannot be less than 1!"
        return False, error_message
    else:
        dstart_date_obj = date.fromisoformat(dstart_date)
        end_date_destination = dstart_date_obj + timedelta(days=int(no_days)-1)
        if dstart_date_obj < start_date:
            error_message = "Start Date of Destination cannot be before Start Date of Trip!"
            return False, error_message
        elif end_date_destination > end_date:
            error_message = "Destination cannot last beyond the End Date of the Trip!"
            return False, error_message
    return True, error_message