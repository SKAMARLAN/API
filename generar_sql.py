import random
from datetime import datetime, timedelta

nombres = ['María', 'José', 'Ana', 'Luis', 'Carmen', 'Juan', 'Laura', 'Carlos', 'Isabel', 'Miguel',
           'Elena', 'Francisco', 'Patricia', 'Jorge', 'Sofía', 'Andrés', 'Lucía', 'Diego', 'Marta', 'Raúl']
apellidos = ['García', 'Martínez', 'Rodríguez', 'Gómez', 'Díaz', 'Pérez', 'Sánchez', 'Torres',
             'Ramírez', 'Flores', 'López', 'Jiménez', 'Ruiz', 'Alonso', 'Gutiérrez', 'Castro', 'Morales',
             'Navarro', 'Molina', 'Vázquez']

def random_date(start_year=1950, end_year=2010):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

with open("personas.sql", "w", encoding="utf-8") as f:
    f.write("INSERT INTO persona (nombre, apellido1, apellido2, fecha_nacimiento) VALUES\n")
    for i in range(500):
        nombre = random.choice(nombres)
        apellido1 = random.choice(apellidos)
        apellido2 = random.choice(apellidos)
        fecha = random_date()
        coma = "," if i < 499 else ";"
        f.write(f"('{nombre}', '{apellido1}', '{apellido2}', '{fecha}'){coma}\n")
