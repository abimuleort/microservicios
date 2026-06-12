import os                      # Para interactuar con el sistema operativo
import datetime                # Paara trabajar con fechas y hora
import sqlite3                 # Base de datos
import bcrypt                  # Para hashear/proteger contraseñas
from dotenv import load_dotenv # Para leer variables del .env
import jwt                     # Crear y verificar tokens
from flask import Flask, request, jsonify  # Servidor HTTP y endpoints

load_dotenv()                  # Accede a datos del .env
app = Flask(__name__)
JWT_SECRET = os.getenv('JWT_SECRET') # Obtencion de datos del .env (Token y database)
DATABASE = os.getenv('USUARIOS_DB')
def database():
    conexion = sqlite3.connect(DATABASE)  # Abro conexion con la base de datos correspondiente
    cursor = conexion.cursor()            # Creo el cursor a partir de la conexion
    return conexion, cursor
def init_database():
    conexion, cursor = database()
    # Creo la tabla usuarios con sus respectivas columnas (id, nombre, email, password_hash y created_at)
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
    conexion.commit() # Guardo los cambios
    conexion.close()  # Cierro conexion

@app.route('/register', methods=['POST']) # (Decorador de Flask) Indico a Flask que se ejecute la funcion cuando se intente hacer un registro
def register():
    data = request.get_json(force=True)                                                    # Extraigo los datos del body
    if data == None:                                                             # Si el body esta vacio devuelve error
        return jsonify('campos de registro vacios'), 400
    if 'nombre' not in data or 'email' not in data or 'password' not in data:    # Si uno de los datos para el registro no fue proporcionado devuelve error
        return jsonify('Datos de registro inclompletos'), 400
    conexion, cursor = database()
    cursor.execute('SELECT email FROM usuarios WHERE email = ?', (data['email'],)) # Compruebo que no sea un email de un usuario existente
    resultado = cursor.fetchone()
    if resultado is not None:
        conexion.close()
        return jsonify('Email existente ingresado'), 409
    password_bytes = data['password'].encode('utf-8')                # Paso la contraseña de string a bytes
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())  # Hasheo la contraseña con bcrypt
    # Guardo los datos del usuario en la db (datetime.now para created_at)
    cursor.execute('INSERT INTO usuarios (nombre, email, password_hash, created_at) VALUES (?, ?, ?, ?)', (data['nombre'], data['email'], password_hash, str(datetime.datetime.now())))
    user_id = cursor.lastrowid                                       # lastrowid devuelve un id que va incrementando para cada usuario
    conexion.commit()
    conexion.close()
    return jsonify({'message': 'Datos de registro guardados correctamente', 'user_id': user_id}), 201 

@app.route('/login', methods=['POST'])                   # Decorador de Flask para la funcion de login
def login():
    data = request.get_json(force=True)                            # Obtencion de datos
    if data == None:
        return jsonify('Body vacio'), 400
    if 'email' not in data or 'password' not in data:    # Si no se ingresaron email o password devuelve error
        return jsonify('Datos inexistentes'), 400  
    conexion, cursor = database()
    cursor.execute('SELECT * FROM usuarios where email = ?', (data['email'],)) # Si se ingresa un email no registrado devuelve error
    resultado = cursor.fetchone()
    if resultado == None:
        conexion.close()
        return jsonify('usuario inexistente'), 404
    password_bytes = data['password'].encode('utf-8')              # Vuelvo a pasar la contraseña a bytes
    comparacion_pw = bcrypt.checkpw(password_bytes, resultado[3])  # Comparo la contraseña del usuario y la hasheada para verificar que coincidan con bcrypt
    if comparacion_pw == False:                                    # si no coincide con el hash la funcion devuelve False, por lo tanto da error
        conexion.close()
        return jsonify('Contraseña invalida'), 401
    token = jwt.encode({'user_id': resultado[0], 'exp': datetime.datetime.now() + datetime.timedelta(hours=24)}, JWT_SECRET, algorithm='HS256') # Creacion del token codificado con contraseña e id
    conexion.close()
    return jsonify({'token': token}), 200

@app.route('/validate', methods=['GET'])                     # Decorador de Flask para la funcion de validacion de token
def validate():
    authorization = request.headers.get('Authorization', '') # Obtengo las partes del header
    partes = authorization.split(' ')                        # Divido las partes de Authorization para trabajar con la validacion
    if len(partes) != 2 or partes[0] != 'Bearer':            # Si no contiene las partes necesarias o no contiene el token se invalida y devuelvo error
        return None, ('Token invalido', 401)
    token = partes[1]
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256']) # Decodifico el token y verifico con JWT_SECRET
        return jsonify({'user_id': decode_token['user_id']}), 200          # Devuelvo el user_id correspondiente
    except:
        return jsonify('Token invalido'), 401  # Si no es valido devuelvo error 


if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=8001)