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

def add_delete_map_itinerary(type_of_update, vac_id, vacation_name, vacation_upgraded, day_no, itin_time, map_id, mysql):
    if type_of_update == "Add":
        print("addingggdslafj;sflkjsd")
        if request.method == 'POST':

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT * from ref_map_itin where vac_id=%s and day_no=%s and itin_time=%s and map_id=%s',(vac_id,day_no,itin_time,map_id,))
            existsMapItin = cursor.fetchone()

            if existsMapItin is not None:
                flash('Duplicate entry! You cannot have the same map referenced to the same itinerary multiple times!','error')
            else:
                cursor.execute('INSERT INTO ref_map_itin VALUES (%s,%s,%s,%s)',(vac_id,itin_time,day_no,map_id,))
                mysql.connection.commit()
                flash('Congratulations, you have successfully added the map to your itinerary!','success')
                cursor.close()
                return redirect(url_for('logged_vacations_itinerary',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded))

    elif type_of_update == "Delete":
        print("deleting!")
        if request.method == 'POST':
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('DELETE from ref_map_itin where vac_id=%s and day_no=%s and itin_time=%s and map_id=%s',(vac_id,day_no,itin_time,map_id,))
            mysql.connection.commit()
            flash('Congratulations, you have successfully added the map to your itinerary!','success')
            cursor.close()
            return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded,curr_tab='maps_itin'))          
    else:
        print("error, should not occur")

    return redirect(url_for('logged_vacations_planning',vac_id=vac_id,vacation_name=vacation_name,vacation_upgraded=vacation_upgraded,curr_tab='maps_itin'))