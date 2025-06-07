import sqlite3

# Conectar (o crear) la base de datos
conn = sqlite3.connect('credit_solid.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT
)
''')

# Crear la tabla de solicitudes si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    income REAL,
    monthly_payment REAL,
    term INTEGER,
    mount REAL,
    garantee TEXT,
    employment_date date,
    debt REAL,
    status TEXT,
    FOREIGN KEY (client_id) REFERENCES clients (id)
)
''')


# Guardar cambios y cerrar
conn.commit()
conn.close()
        
        