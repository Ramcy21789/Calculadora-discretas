from flask import Flask, request, jsonify, render_template
import json
import threading
import webbrowser
from core.logic_parser import LogicParser
from core.set_parser import SetParser, random_sets

# Iniciamos flask
app = Flask(__name__)

# ─────────────────────────────────────────────
# Conexión a BD SQLite
def obtener_conexion():
    import sqlite3
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    return sqlite3.connect(db_path)

def guardar_en_bd(tipo_problema, expresion, respuesta):
    """Intenta guardar el historial en la BD. Silencia errores si no hay conexión."""
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO tipos_problemas (tipo_problema, descripcion) VALUES (?, ?)",
            (tipo_problema, "Generado automáticamente por el motor")
        )
        cursor.execute(
            "INSERT INTO historial_escaneos (tipo_problema, expresion_original, resultado_json) VALUES (?, ?, ?)",
            (tipo_problema, expresion, json.dumps(respuesta))
        )
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as db_err:
        print("No se pudo guardar en BD:", db_err)

# ─────────────────────────────────────────────
# Ruta 1: Estado del servidor
# ─────────────────────────────────────────────
@app.route('/estado', methods=['GET'])
def estado():
    return jsonify({"mensaje": "Servidor corriendo"})

# ─────────────────────────────────────────────
# Ruta 2: Interfaz principal
# ─────────────────────────────────────────────
@app.route('/', methods=['GET'])
def inicio():
    return render_template('index.html')

# ─────────────────────────────────────────────
# Endpoint: conjuntos aleatorios
# ─────────────────────────────────────────────
@app.route('/conjuntos-aleatorios', methods=['GET'])
def get_conjuntos_aleatorios():
    return jsonify(random_sets())

# ─────────────────────────────────────────────
# Ruta 3: Resolver expresión matemática
# ─────────────────────────────────────────────
@app.route('/resolver', methods=['POST'])
def resolver_expresion():
    try:
        datos = request.json
        expresion = datos.get('expresion', '').strip()
        custom_sets = datos.get('conjuntos', None)   # Dict opcional del frontend

        if not expresion:
            return jsonify({"error": "No se recibió ninguna expresión"}), 400

        expresion_limpia = expresion.replace(" ", "")

        logic_parser = LogicParser()
        set_parser = SetParser(custom_sets=custom_sets)

        pasos = []
        venn_data = None
        tipo_problema = "General"

        if set_parser.is_set_expression(expresion_limpia):
            tipo_problema = "Conjuntos"
            pasos, venn_data = set_parser.solve(expresion_limpia)
        elif logic_parser.is_logic_expression(expresion_limpia):
            tipo_problema = "Lógica"
            pasos = logic_parser.solve(expresion_limpia)
        else:
            pasos = [
                f"Expresión recibida: {expresion}",
                "Error: No se reconoció ningún operador de conjuntos ni de lógica proposicional.",
                "Sugerencia: Usa símbolos del teclado virtual como ∪, ∩, ∧, ∨, →, ¬"
            ]

        respuesta = {
            "mensaje": f"Procesado como problema de {tipo_problema}",
            "expresion_original": expresion,
            "pasos_solucion": pasos,
            "venn_data": venn_data,
            "tipo_problema": tipo_problema
        }

        guardar_en_bd(tipo_problema, expresion, respuesta)

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar la expresión: {str(e)}"}), 500

# ─────────────────────────────────────────────
# Ruta 4: Creación de usuario
# ─────────────────────────────────────────────
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    try:
        datos = request.json
        nombres = datos['nombres']
        apellidos = datos['apellidos']
        email = datos['email']
        contrasena = datos['contrasena']

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        sql = "INSERT INTO usuarios (nombres, apellidos, email, contrasena) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (nombres, apellidos, email, contrasena))
        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Usuario creado exitosamente"})

    except Exception as a:
        return jsonify({"error": str(a)}), 400

# ─────────────────────────────────────────────
# Arranque del servidor
# ─────────────────────────────────────────────
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.25, open_browser).start()
    app.run(debug=True)
