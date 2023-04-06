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

from app import generate_id

def add_update_vacation(type_of_update, vac_id, mysql):
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
