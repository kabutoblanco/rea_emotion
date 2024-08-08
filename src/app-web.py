from flask import Flask, Response, json, request, render_template
from flask_cors import CORS
from urllib.parse import urlencode

from db import ConexionSQLite

import time
import os
import subprocess
import webbrowser

net = os.getenv('NET', 'wlo1')

address = subprocess.run(['ip', 'addr', 'show', net], capture_output=True, text=True)
stdout = address.stdout

lines = stdout.split('\n')
ip = None
for line in lines:
    if 'inet ' in line and 'global' in line:
        ip = line.strip().split(' ')[1].split('/')[0]
        break

if ip is None:
    raise Exception('Net interface not found')

app = Flask(__name__)
cors = CORS(app)

conexion = ConexionSQLite()

@app.route('/api/student')
def student():
    school_year = request.args.get('school_year')
    students = conexion.get('SELECT * FROM student WHERE school_year = ? ORDER BY name', (school_year, ))
    return Response(status=200, response=json.dumps(students))

@app.route('/api/rea')
def rea():
    school_year = request.args.get('school_year')
    students = conexion.get('SELECT * FROM rea WHERE school_year = ?', (school_year, ))
    return Response(status=200, response=json.dumps(students))

@app.route('/api/sesion', methods=['GET', 'POST'])
def sesion():
    if request.method == 'GET':
        sesion_obj = conexion.get('SELECT id, rea_id, student_id FROM sesion WHERE in_live = 1 LIMIT 1')
        if len(sesion_obj) > 0:
            rea_id = sesion_obj[0][1]
            rea_obj = conexion.get('SELECT school_year FROM rea WHERE id = ? LIMIT 1', (rea_id,))
            res_obj = {
                'id': sesion_obj[0][0],
                'rea_id': rea_id,
                'student_id': sesion_obj[0][2],
                'rea_school_year': rea_obj[0][0]
            }
        else:
            res_obj = { 'id': '-', 'rea_id': -1, 'student_id': -1, 'rea_school_year': '-' }
        return Response(status=200, response=json.dumps(res_obj))
    if request.method == 'POST':
        data = request.json
        rea_id = data['rea_id']
        rea_obj = conexion.get('SELECT school_year, path, duration FROM rea WHERE id = ? LIMIT 1', (rea_id,))
        id = conexion.insert('INSERT INTO sesion(student_id, rea_id, in_live, date_record) VALUES (?,?,?,?)', (data['student_id'], data['rea_id'], 1, int(time.time())))
        params = {
            'time': rea_obj[0][2]
        }
        params_encoded = urlencode(params)
        url = rf'{rea_obj[0][1]}?{params_encoded}'
        webbrowser.open(url)
        res_obj = {
            'id': id, 
            'rea_school_year': rea_obj[0][0]
        }
        return Response(status=210, response=json.dumps(res_obj))

@app.route('/')
def index():
    return render_template('index.html', ip=ip)

if __name__ == '__main__':
    app.run(debug=True)