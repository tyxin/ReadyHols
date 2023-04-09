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

def logged_vacations(mysql):    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT vacation.vac_id,vacation.vac_grp_id, description,start_date,end_date,budget_limit, upg_user_id from vac_user_has,vacation'
        ' where vacation.vac_id = vac_user_has.vac_id and vac_user_has.user_id =%s '
        'order by start_date,end_date', (session['user_id'],))
    fields = [(str(i[0]).replace("_", " ")) for i in cursor.description][2:]
    true_all_vacations_user = cursor.fetchall()
    vacations_user = true_all_vacations_user

    cursor.execute('SELECT plan_type from user where user_id=%s',(session['user_id'],))
    plan = cursor.fetchone()['plan_type']

    if request.method == 'POST':
        category = request.form.get('category')
        if category in fields:
            search = '%' + request.form['search'] + '%'
            query = 'SELECT vacation.vac_id,description,start_date,end_date,budget_limit from vac_user_has,vacation where ' + \
                    category.replace(" ", "_") + \
                    ' like %s and vacation.vac_id = vac_user_has.vac_id and vac_user_has.user_id =%s order by start_date,end_date'
            print(query)
            cursor.execute(query, (search, session['user_id'],))
            vacations_user = cursor.fetchall() 
            cursor.close()
            print("plannnn")
            print(plan)
            return render_template('/login/vacations/vacations.html', vacations_user=vacations_user,
                           recent_vacations_user=vacations_user[:4], fields=fields,plan=plan) 

    cursor.close()
    return render_template('/login/vacations/vacations.html', vacations_user=vacations_user,
                           recent_vacations_user=vacations_user[:4], fields=fields,plan=plan)


def logged_user(mysql):
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
            session['sub_mail'] = subEmail
            cursor.execute('UPDATE user set email=%s, password=%s, sub_mail=%s WHERE user_id = %s ',
                           (user_email, generate_password_hash(user_password), subEmail, session['user_id'],))
            mysql.connection.commit()  # note that you need to commit the changes for INSERT,UPDATE and DELETE statements
            flash('You have updated your email and password successfully', 'success')
    return render_template('/login/user/user.html')

def logged_settings(mysql):
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
            cursor.execute('SELECT grp_count,plan_type from user where user_id=%s',(session['user_id'],))
            user_details = cursor.fetchone()
            grp_count = user_details['grp_count']
            if user_details['plan_type']=="Basic" and grp_count>=5:
                flash('You have reached the maximum limit on vacation grps! To add more, upgrade your plan','error')
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
                   , (session['user_id'],))
    same_vacgrp_users = cursor.fetchall()

    return render_template('/login/settings/settings.html', user_vacgrp_details=user_vacgrp_details,
                           same_vacgrp_users=same_vacgrp_users)

def create_vac_grp(mysql):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST' and ('vacation_grp_name' in request.form) and ('vacation_id_pin' in request.form):
        
        vacation_group = request.form['vacation_grp_name']
        vacation_group_pin = request.form['vacation_id_pin']

        print("create")
        print(vacation_group)
        print(vacation_group_pin)

        if not re.match(r'[A-Za-z0-9]+', vacation_group):
            flash('Vacation Group Name can only contain numbers and letters!','error')
        elif not len(vacation_group) <= 50:
            flash('Vacation Group Name cannot contain more than 50 characters!')
        else:
            vacation_grp_count = cursor.execute('SELECT * from vacation_grp')
            vacation_grp_id = generate_id(vacation_grp_count + 1, cursor, "vacation_grp", "vac_grp_id")
            cursor.execute('INSERT INTO vacation_grp VALUES(%s,%s,%s)',
                (vacation_grp_id,vacation_group, generate_password_hash(vacation_group_pin),))
            mysql.connection.commit()
            cursor.execute('INSERT INTO vac_user_in VALUES(%s,%s)',(vacation_grp_id,session['user_id'],))
            mysql.connection.commit()
            flash('You have been created the vacation group successfully!', 'success')

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
                   , (session['user_id'],))
    same_vacgrp_users = cursor.fetchall()

    return redirect(url_for('logged_settings'))

