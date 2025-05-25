import psycopg2
from werkzeug.security import generate_password_hash

DB_CONFIG = {
    'dbname': 'mydb',
    'user': 'user',
    'password': 'password',
    'host': '192.168.110.38',  # Solo IP, sin :5432
    'port': 5432,              # Puerto en otro campo
}

def get_db_connection():
    print("Intentando conectar a la base de datos...")
    return psycopg2.connect(**DB_CONFIG)

def crear_usuario(username, password, role='user'):
    hash_pw = generate_password_hash(password)
    print(f"Creando usuario {username} con rol {role}")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)",
            (username, hash_pw, role)
        )
        conn.commit()
        cur.close()
        conn.close()
        print(f"Usuario '{username}' creado con rol '{role}'.")
    except Exception as e:
        print("Error al crear usuario:", e)

if __name__ == "__main__":
    crear_usuario("administrador", "maletin", "admin")

