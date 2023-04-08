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

def add_update_budget(type_of_update, vac_id, vacation_name, vacation_upgraded, budget_id, mysql):
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
            elif int(budget_expenditure)<0:
                flash('You cannot have negative expenditure!','error')
            else:
                budget_count = cursor.execute('SELECT * from budget')
                budget_id = generate_id(budget_count + 1, cursor, "budget", "budget_id")
                cursor.execute('INSERT into budget VALUES (%s,%s,%s,%s,%s)',(vac_id,budget_id,budget_category,budget_expenditure,budget_remarks,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully added your new budget component!','success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Update":
        if request.method == 'POST' and (
                'add_budget_expenditure' in request.form) \
                and ('add_budget_remarks' in request.form) :
            budget_category = request.form.get('budget_category')
            budget_expenditure = request.form['add_budget_expenditure']
            budget_remarks = request.form['add_budget_remarks']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', budget_remarks):
                flash('Country must contain only characters!', 'error')
            elif int(budget_expenditure)<0:
                flash('Your expenditure cannot be negative!','error')
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
