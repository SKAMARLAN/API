from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)



DB_CONFIG = {
    'dbname': 'mydb',
    'user': 'user',
    'password': 'password',
    'host': 'postgres',  # nombre del servicio en docker-compose
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

app.secret_key = 'alumne'
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT password, role FROM usuarios WHERE username = %s", (user,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                hashed_password, role = result
                if check_password_hash(hashed_password, password):
                    session['username'] = user
                    session['role'] = role
                    if role == 'admin':
                        return redirect(url_for('admin_panel'))
                    else:
                        return redirect(url_for('home'))
                else:
                    error = "Credenciales incorrectas"
            else:
                error = "Credenciales incorrectas"
        except Exception as e:
            error = f"Error al conectar con la base de datos: {e}"

        return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route("/admin")
def admin_panel():
    print("SESSION:", session)
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route('/admin/nueva_persona', methods=['GET'])
def form_nueva_persona():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    return render_template('nueva_persona.html')

@app.route('/admin/nueva_persona', methods=['POST'])
def guardar_persona():
    if session.get("role") != "admin":
        return redirect(url_for("login"))

    nombre = request.form.get('nombre')
    apellido1 = request.form.get('apellido1')
    apellido2 = request.form.get('apellido2')
    fecha_nacimiento = request.form.get('fecha_nacimiento')

    if not all([nombre, apellido1, apellido2, fecha_nacimiento]):
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('form_nueva_persona'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO persona (nombre, apellido1, apellido2, fecha_nacimiento)
            VALUES (%s, %s, %s, %s)
            """,
            (nombre, apellido1, apellido2, fecha_nacimiento)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Error al guardar la persona: {e}")
        return redirect(url_for('form_nueva_persona'))

    return redirect(url_for('admin_panel'))
@app.route('/buscar', methods=['GET'])
def buscar():
    nombre = request.args.get('nombre', '').strip()
    apellido1 = request.args.get('apellido1', '').strip()
    apellido2 = request.args.get('apellido2', '').strip()
    fecha_nacimiento = request.args.get('fecha_nacimiento', '').strip()

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = "SELECT * FROM persona WHERE TRUE"
        params = []

        if nombre:
            query += " AND nombre ILIKE %s"
            params.append(f"%{nombre}%")
        if apellido1:
            query += " AND apellido1 ILIKE %s"
            params.append(f"%{apellido1}%")
        if apellido2:
            query += " AND apellido2 ILIKE %s"
            params.append(f"%{apellido2}%")
        if fecha_nacimiento:
            query += " AND fecha_nacimiento = %s"
            params.append(fecha_nacimiento)

        cur.execute(query, params)
        resultados = cur.fetchall()
        cur.close()
        conn.close()

    except Exception as e:
        flash(f"Error al buscar personas: {e}")
        resultados = []

    return render_template('resultados.html', resultados=resultados)
