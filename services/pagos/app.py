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
DATABASE = os.getenv('PAGOS_DB')
PEDIDOS_INTERNAL_URL = os.getenv('PEDIDOS_INTERNAL_URL')

def database():
    conexion = sqlite3.connect(DATABASE)
    cursor = conexion.cursor()
    return conexion, cursor
def init_database():
    conexion, cursor = database()
    cursor.execute('CREATE TABLE IF NOT EXISTS pagos(id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER NOT NULL, monto INTEGER NOT NULL, metodo TEXT NOT NULL, estado TEXT NOT NULL, created_at TEXT NOT NULL)')
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
@app.route('/pagos', methods=['POST'])
def pagos():
    verificacion = verificar_token()
    if verificacion == None:
        return jsonify('No autorizado'), 401
    data = request.get_json(force=True)
    if data == None:
        return jsonify("Body vacio"), 400
    if 'pedido_id' not in data or 'metodo_pago' not in data:
        return jsonify('Datos incompletos'), 400
    try:
            token = request.headers.get('Authorization')
            respuesta = requests.get(f"{PEDIDOS_INTERNAL_URL}/{data['pedido_id']}", headers={'Authorization': token})
            if respuesta.status_code != 200:
                return jsonify('Pedido no encontrado'), 404
            pedido = respuesta.json()
    except:
        return jsonify('Servicio de pedidos no disponible'), 503
    conexion, cursor = database()
    cursor.execute('INSERT INTO pagos (pedido_id, monto, metodo, estado, created_at) VALUES (?,?,?,?,?)', (data['pedido_id'], pedido['total'], data['metodo_pago'], 'completado', str(datetime.datetime.now())))
    pago_id = cursor.lastrowid
    requests.put(f"{PEDIDOS_INTERNAL_URL}/{data['pedido_id']}", json={'estado': 'pagado'})
    conexion.commit()
    conexion.close()
    return jsonify({'message':'Pago actualizado con exito', 'pago_id':pago_id}), 201
@app.route('/pagos/<int:pedido_id>', methods=['GET'])
def detalles_pago(pedido_id):
    verificacion = verificar_token()
    if verificacion == None:
        return jsonify('No autorizado'), 401
    conexion, cursor = database()
    cursor.execute('SELECT * FROM pagos WHERE pedido_id=?', (pedido_id,))
    resultado = cursor.fetchone()
    if resultado == None:
        conexion.close()
        return jsonify('El pago no fue registrado'), 404
    pago_dict = {
        'id': resultado[0],
        'pedido_id': resultado[1],
        'monto': resultado[2],
        'metodo': resultado[3],
        'estado': resultado[4],
        'created_at': resultado[5]
    }
    conexion.close()
    return jsonify(pago_dict), 200
if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=8004)