from flask import Flask, request, jsonify 
from dotenv import load_dotenv
import os
import sqlite3
import jwt

load_dotenv()                            # Cargo el .env 
app = Flask(__name__)                    # Creo la app de Flask
JWT_SECRET = os.getenv('JWT_SECRET')     # Leo las variables del entorno 
PRODUCTOS_DB = os.getenv('PRODUCTOS_DB')

def database():
    conexion = sqlite3.connect(PRODUCTOS_DB)
    cursor = conexion.cursor()
    return conexion, cursor
def init_database():
    conexion, cursor = database()
    cursor.execute('CREATE TABLE IF NOT EXISTS productos(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, precio INTEGER NOT NULL, stock INTEGER NOT NULL, descripcion TEXT NOT NULL)')
    conexion.commit()
    conexion.close()

def verificar_token():
    authorization = request.headers.get('Authorization', '')
    partes = authorization.split(' ')
    if len(partes) != 2 or partes[0] != 'Bearer':
        return None
    token = partes[1]
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return decode_token['user_id']
    except:
        return None
@app.route('/productos', methods=['GET'])
def productos():
    conexion, cursor = database()
    cursor.execute('SELECT * FROM productos')
    resultados = cursor.fetchall()
    conexion.close()
    lista_productos = []
    for producto in resultados:
        producto_dict ={
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[2],
            'stock': producto[3],
            'descripcion': producto[4],
        }
        lista_productos.append(producto_dict)
    return jsonify(lista_productos)
@app.route('/productos/<int:id>', methods=['GET'])
def obtener_productos(id):
    conexion, cursor = database()
    cursor.execute('SELECT * FROM productos WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    if resultado == None:
        conexion.close()
        return jsonify('Producto no encontrado'), 404
    producto_dict = {
        'id': resultado[0],
        'nombre': resultado[1],
        'precio': resultado[2],
        'stock': resultado[3],
        'descripcion': resultado[4]
    }
    conexion.close()
    return jsonify(producto_dict), 200
@app.route('/productos', methods=['POST'])
