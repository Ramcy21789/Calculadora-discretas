from flask import Flask, request, jsonify, render_template
import mysql.connector
import json
from core.logic_parser import LogicParser
from core.set_parser import SetParser

# Iniciamos flask
app = Flask(__name__)

# Conectamos la base de datos
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # [PASSWORD] Se deja vacía por defecto para XAMPP
        database="calculadora_discretas"
    )

# Ruta 1: Funcionamiento del servidor (GET)
@app.route('/estado', methods=['GET'])
def estado():
    return jsonify({"mensaje": "Servidor corriendo"})

# Ruta 2: Creación de usuario (POST)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    try:
        # datos para el JSON
        datos = request.json
        nombres = datos['nombres']
        apellidos = datos['apellidos']
        email = datos['email']
        contrasena = datos['contrasena']
        
        # Conexión y cursor
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Insertamos los datos en el sql
        sql = "INSERT INTO usuarios (nombres, apellidos, email, contrasena) VALUES (%s, %s, %s, %s)"
        valores = (nombres, apellidos, email, contrasena)

        # Guardamos los cambios
        cursor.execute(sql, valores)
        conexion.commit()

        # Cerramos la conexion
        cursor.close()
        conexion.close()

        # Mostramos el mensaje de exito
        return jsonify({"mensaje": "Usuario creado exitosamente"})

    except Exception as a:
        # Si hay error
        return jsonify({"error": str(a)}), 400

#Ruta 3. Interfaz
@app.route('/',methods=['GET'])
def inicio():
    #render_template
    return render_template('index.html')

#Ruta 4: Recibir y analizar la expresión matemática
@app.route('/resolver', methods=['POST'])
def resolver_expresion():
    try:
        datos = request.json
        expresion = datos.get('expresion', '')

        if not expresion:
            return jsonify({"error": "No se recibió ninguna expresión"}), 400

        expresion_limpia = expresion.replace(" ", "")
        
        logic_parser = LogicParser()
        set_parser = SetParser()
        
        pasos = []
        tipo_problema = "General"
        
        if set_parser.is_set_expression(expresion_limpia):
            tipo_problema = "Conjuntos"
            pasos = set_parser.solve(expresion_limpia)
        elif logic_parser.is_logic_expression(expresion_limpia):
            tipo_problema = "Lógica"
            pasos = logic_parser.solve(expresion_limpia)
        else:
            pasos = [
                f"Paso 1: Expresión recibida: {expresion}", 
                "Paso 2: No se reconoció ningún operador de conjuntos ni de lógica proposicional."
            ]
            
        respuesta = {
            "mensaje": f"Procesado como problema de {tipo_problema}",
            "expresion_original": expresion,
            "pasos_solucion": pasos
        }

        # Guardar en base de datos
        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            
            # Asegurar que el tipo de problema existe
            cursor.execute("INSERT IGNORE INTO tipos_problemas (tipo_problema, descripcion) VALUES (%s, %s)", 
                           (tipo_problema, "Generado automáticamente por el motor"))
            
            sql = "INSERT INTO historial_escaneos (tipo_problema, expresion_original, resultado_json) VALUES (%s, %s, %s)"
            valores = (tipo_problema, expresion, json.dumps(respuesta))
            cursor.execute(sql, valores)
            conexion.commit()
            
            cursor.close()
            conexion.close()
        except Exception as db_err:
            print("No se pudo guardar en BD:", db_err)
            # No interrumpimos la respuesta al usuario si la BD falla
            pass

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar la expresión: {str(e)}"}), 500

import threading
import webbrowser

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

# Arranque del servidor
if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
