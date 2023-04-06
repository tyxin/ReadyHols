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

def add_update_maps(type_of_update, vac_id, vacation_name, vacation_upgraded, mysql, app):
    print(type_of_update)
    if type_of_update == "Add":
        if request.method == 'POST' and ('add_map_name' in request.form):
            
            map_category = request.form.get('maps_category')
            map_name = request.form['add_map_name']
            map_attachment_path = ""

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            if not re.match(r'[A-Za-z]+', map_name):
                flash('Map name must contain only characters!', 'error')
            else:
                map_count = cursor.execute('SELECT * from vac_map')
                map_id = generate_id(map_count + 1, cursor, "vac_map", "map_id")
                if 'add_map_attachment' in request.files:
                    uploaded_map = request.files['add_map_attachment']
                    if uploaded_map.filename!='':
                        map_filename = secure_filename(uploaded_map.filename)
                        final_file_path = os.path.join(app.config['UPLOAD_FOLDER_MAP'],map_filename)
                        print("final_file_path")
                        print(final_file_path)
                        uploaded_map.save(final_file_path)
                        map_attachment_path = "/map-attachment/"+map_filename
                cursor.execute('INSERT into vac_map VALUES (%s,%s,%s,%s)',(map_id,map_attachment_path,map_name,map_category,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully added a new map to the drive!','success')
                cursor.close()
                return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))
    else:
        print("error, should not occur")
        return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

