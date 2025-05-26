from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import psycopg2
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "alumne"  # Necesaria para usar flash y sesiones

DB_CONFIG = {
    'dbname': 'mydb',
    'user': 'user',
    'password': 'password',
    'host': 'postgres',  # o localhost, según tu configuración
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/registrar")
def registrar():
    return render_template("registrar.html")

@app.route("/guardar-compra", methods=["POST"])
def guardar_compra():
    importe = request.form.get("importe")
    compra = request.form.get("compra")
    persona = request.form.get("persona")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO compras (importe, compra, fecha, persona)
            VALUES (%s, %s, NOW(), %s)
        """, (importe, compra, persona))
        conn.commit()
        cur.close()
        conn.close()
        flash("Compra registrada correctamente.")
    except Exception as e:
        print("Error al guardar la compra:", e)
        flash("Error al registrar la compra.")

    return redirect(url_for("home"))

@app.route("/ver")
def ver_compras():
    conn = get_db_connection()
    cur = conn.cursor()
    # Obtener todos los registros sin id
    cur.execute("SELECT importe, compra, fecha, persona FROM compras ORDER BY fecha DESC")
    registros = cur.fetchall()

    # Calcular totales por persona
    cur.execute("SELECT persona, SUM(importe) FROM compras GROUP BY persona")
    totales = dict(cur.fetchall())

    cur.close()
    conn.close()

    total_javi = totales.get('JAVI', 0)
    total_paola = totales.get('PAOLA', 0)
    resta = total_javi - total_paola

    return render_template("ver.html", registros=registros, total_javi=total_javi, total_paola=total_paola, resta=resta)

@app.route("/saldar", methods=["POST"])
def saldar_compras():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insertar todos los registros actuales en compras_historico con fecha_saldo = ahora
        cur.execute("""
            INSERT INTO compras_historico (importe, compra, fecha, persona, fecha_saldo)
            SELECT importe, compra, fecha, persona, NOW() FROM compras
        """)

        # Borrar todos los registros de compras (porque ya se "saldaron")
        cur.execute("DELETE FROM compras")

        conn.commit()
        cur.close()
        conn.close()
        flash("Compras saldadas correctamente.")
    except Exception as e:
        print("Error al saldar compras:", e)
        flash("Error al saldar las compras.")

    return redirect(url_for("ver_compras"))

@app.route("/ver-historicos")
def ver_historicos():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Fechas disponibles
        cur.execute("SELECT DISTINCT fecha_saldo::date FROM compras_historico ORDER BY fecha_saldo::date DESC")
        fechas = [row[0] for row in cur.fetchall()]

        fecha_seleccionada = request.args.get("fecha")
        registros = []
        total_javi = 0
        total_paola = 0
        resta = 0

        if fecha_seleccionada:
            cur.execute("""
                SELECT importe, compra, fecha, persona FROM compras_historico
                WHERE fecha_saldo::date = %s
            """, (fecha_seleccionada,))
            registros = cur.fetchall()

            total_javi = sum(r[0] for r in registros if r[3].upper() == "JAVI")
            total_paola = sum(r[0] for r in registros if r[3].upper() == "PAOLA")
            resta = total_paola - total_javi

        cur.close()
        conn.close()

        return render_template(
            "ver_historicos.html",
            fechas=fechas,
            registros=registros,
            fecha_seleccionada=fecha_seleccionada,
            total_javi=total_javi,
            total_paola=total_paola,
            resta=resta
        )
    except Exception as e:
        print("Error en ver históricos:", e)
        flash("Error al obtener los históricos.")
        return redirect(url_for("home"))


CORS(app)

estado_mundo = []

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.json
    bloques = data.get('bloques', [])
    guardar_estado_juego(bloques)
    return jsonify({"mensaje": "Mundo guardado"}), 200

@app.route('/cargar', methods=['GET'])
def cargar():
    bloques = cargar_estado_juego()
    return jsonify({"bloques": bloques}), 200


@app.route('/juego_prueba.html')
def juego():
    return render_template('juego_prueba.html')

def guardar_estado_juego(bloques):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Primero borramos todo lo anterior
        cur.execute("DELETE FROM estado_juego")

        # Insertamos todos los bloques nuevos
        for bloque in bloques:
            cur.execute(
                "INSERT INTO estado_juego (x, y) VALUES (%s, %s)",
                (bloque['x'], bloque['y'])
            )

        conn.commit()
    except Exception as e:
        print("Error guardando estado del juego:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def cargar_estado_juego():
    conn = get_db_connection()
    cur = conn.cursor()
    bloques = []
    try:
        cur.execute("SELECT x, y FROM estado_juego")
        filas = cur.fetchall()
        bloques = [{'x': fila[0], 'y': fila[1]} for fila in filas]
    except Exception as e:
        print("Error cargando estado del juego:", e)
    finally:
        cur.close()
        conn.close()
    return bloques


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
