import streamlit as st
import sqlite3
import pandas as pd
from streamlit_option_menu import option_menu
from awesome_table import AwesomeTable
from awesome_table.column import Column


# Conexión a la base de datos
def get_connection():
    conn = sqlite3.connect('credit_solid.db')
    return conn

# Guardar cliente
def guardar_cliente(nombre, correo, telefono):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, correo, telefono) VALUES (?, ?, ?)", (nombre, correo, telefono))
    conn.commit()
    conn.close()

# Mostrar clientes
def obtener_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# Interfaz en Streamlit
with st.sidebar:
    selected = option_menu("Main Menu", ["Listar Clientes", "Agregar Cliente", 'Agregar Solicitud', 'Listar Solicitudes'], 
        icons=['people', 'people', 'people', 'people'], menu_icon="cast", default_index=1)

st.title(selected)

if selected == "Agregar Cliente":
    with st.form(key='form_cliente'):
        nombre = st.text_input("Nombre")
        correo = st.text_input("Correo")
        telefono = st.text_input("Teléfono")
        submit_button = st.form_submit_button(label='Registrar')

    if submit_button:
        if nombre and correo and telefono:
            guardar_cliente(nombre, correo, telefono)
            st.success("¡Cliente registrado exitosamente!")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected == "Listar Clientes":
    clientes = obtener_clientes()
    AwesomeTable(pd.json_normalize(clientes), columns=[
        Column(name='id', label='ID'),
        Column(name='nombre', label='Name'),
        Column(name='correo', label='Job Title'),
        Column(name='telefono', label='Avatar'),
])
