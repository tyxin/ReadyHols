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

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT plan_type,upg_count from user where user_id=%s',(session['user_id'],))
            user_details = cursor.fetchone()

            year_start_date = vacation_start_date.split("-")[0]
            year_end_date = vacation_end_date.split("-")[0]


            if 'vacationUpgrade' in request.form:
                upgradeVacation = True
                if (user_details['plan_type']=="Premium" and user_details['upg_count']>=5):
                    flash('You have reached your upgrade limit. To upgrade more vacations, upgrade your plan','error')
                else:
                    upg_user_id = session['user_id']

            if upgradeVacation and (upg_user_id is None):
                print("cannot upgrade :(") 
            elif len(year_start_date)!=4 and len(year_end_date)!=4:
                flash('Date in incorrect format!','error')
            elif not (date.fromisoformat(vacation_start_date) <= date.fromisoformat(vacation_end_date)):
                flash('End date cannot be before start date!','error')
            elif int(vacation_budget_limit)<0:
                flash('You cannot have a negative budget limit!','error')
            else:
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
                        elif not len(vacation_description) <=50:
                            flash('Description cannot be more than 50 characters','error')
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

            year_start_date = vacation_start_date.split("-")[0]
            year_end_date = vacation_end_date.split("-")[0]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT plan_type,upg_count from user where user_id=%s',(session['user_id'],))
            user_details = cursor.fetchone()

            if 'vacationUpgrade' in request.form:
                upgradeVacation = True
                if (user_details['plan_type']=="Plus" and user_details['upg_count']>=5):
                    flash('You have reached your upgrade limit. To upgrade more vacations, upgrade your plan','error')
                else:
                    upg_user_id = session['user_id']

            if upgradeVacation and (upg_user_id is None):
                print("cannot upgrade :(")
            elif len(year_start_date)!=4 and len(year_end_date)!=4:
                flash('Date in incorrect format!','error')
            elif not (date.fromisoformat(vacation_start_date) < date.fromisoformat(vacation_end_date)):
                flash('End date cannot be before start date!','error')
            elif int(vacation_budget_limit)<0:
                flash('You cannot have a negative budget limit!','error')
            else:
                if not re.match(r'[A-Za-z0-9]+', vacation_description):
                    flash('Description must contain only characters and numbers!', 'error')
                elif not len(vacation_description) <=50:
                    flash('Description cannot be more than 50 characters','error')
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
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE from vacation where vac_id=%s', (vac_id,))
        mysql.connection.commit()
        flash('You have deleted your vacation successfully!','success')
        return redirect(url_for('logged_vacations'))
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations'))
