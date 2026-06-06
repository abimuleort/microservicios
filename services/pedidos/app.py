import os
import datetime
import sqlite3
from dotenv import load_dotenv
import jwt
from flask import Flask, request, jsonify
import requests

load_dotenv()
app = Flask(__name__)
JWT_SECRET = os.getenv('JWT_SECRET')
DATABASE = os.getenv('PEDIDOS_DB')
PRODUCTOS_INTERNAL_URL = os.getenv('PRODUCTOS_INTERNAL_URL')

def database():
    conexion = sqlite3.connect(DATABASE)
    cursor = conexion.cursor()
    return conexion, cursor
def init_database():
    conexion, cursor = database()
    cursor.execute('CREATE TABLE IF NOT EXISTS pedidos(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, producto_id INTEGER NOT NULL, cantidad INTEGER, total INTEGER, estado TEXT NOT NULL, created_at TEXT NOT NULL)')
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
@app.route('/pedidos', methods=['POST'])
def crear_pedido():
    verificacion = verificar_token()
    if verificacion == None:
        return jsonify('No autorizado'), 401
    data = request.get_json()
    if data == None:
        return jsonify("Body vacio"), 400
    if 'producto_id' not in data or 'cantidad' not in data:
        return jsonify('Datos incompletos'), 400
    try:
            respuesta = requests.get(f"{PRODUCTOS_INTERNAL_URL}/{data['producto_id']}")
            if respuesta.status_code != 200:
                return jsonify('Producto no encontrado'), 404
            producto = respuesta.json()
    except:
        return jsonify('Servicio de productos no disponible'), 503
    if producto['stock'] < data['cantidad']:
        return jsonify('No hay stock disponible'), 400
    total = producto['precio'] * data['cantidad']
    conexion, cursor = database()
    cursor.execute("INSERT INTO pedidos (user_id, producto_id, cantidad, total, estado, created_at) VALUES (?,?,?,?,?,?)", (verificacion, data['producto_id'], data['cantidad'], total, 'pendiente', str(datetime.datetime.now())))
    pedido_id = cursor.lastrowid  
    conexion.commit()
    conexion.close()
    return jsonify({'message':'Datos del pedido agregados correctamente', 'pedido_id': pedido_id}), 201
@app.route('/pedidos/mis-pedidos', methods=['GET'])
def pedidos_por_usuario():
    verificacion = verificar_token()
    conexion, cursor = database()
    if verificacion == None:
        conexion.close()
        return jsonify('No autorizado'), 401
    cursor.execute('SELECT * FROM pedidos WHERE user_id = ?', (verificacion,))
    resultados = cursor.fetchall()
    if resultados == None:
        conexion.close()
        return jsonify('No hay pedidos registrados bajo el id'), 404
    lista_pedidos = []
    for pedido in resultados:
        pedido_dict = {
            'id': pedido[0],
            'user_id': pedido[1],
            'producto_id': pedido[2],
            'cantidad': pedido[3],
            'total': pedido[4],
            'estado': pedido[5],
            'created_at': pedido[6]
        }
        lista_pedidos.append(pedido_dict)
    return jsonify(lista_pedidos)
@app.route('/pedidos/<int:id>', methods=['GET'])
def detalles_pedido(id):
    verificacion = verificar_token()
    if verificacion == None:
        return jsonify('No autorizado'), 401
    conexion, cursor = database()
    cursor.execute('SELECT * FROM pedidos WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    if resultado == None:
        conexion.close()
        return jsonify('El pedido no existe o no esta registrado'), 404
    pedido_dict = {
        'id': resultado[0],
        'user_id': resultado[1],
        'producto_id': resultado[2],
        'cantidad': resultado[3],
        'total': resultado[4],
        'estado': resultado[5],
        'created_at': resultado[6]
    }
    conexion.close()
    return jsonify(pedido_dict), 200

if __name__ == '__main__':
    init_database()
    app.run(port=8003)