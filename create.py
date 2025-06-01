import sqlite3

# Conectar (o crear) la base de datos
conn = sqlite3.connect('credit_solid.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    correo TEXT,
    telefono TEXT
)
''')

# Guardar cambios y cerrar
conn.commit()
conn.close()
