import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu
from models import Client, Request


# Conexión a la base de datos
def get_connection():
    conn = sqlite3.connect('credit_solid.db')
    return conn

# Guardar cliente
def save_client(client: Client):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)",
                   (client.name, client.email, client.phone))
    conn.commit()
    conn.close()

# Guardar solicitud
def save_request(request: Request):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO requests (client_id, income, monthly_payment, term, mount, garantee, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (request.client_id, request.income, request.monthly_payment, request.term, request.mount, request.garantee, request.status))
    conn.commit()
    conn.close()

# Mostrar solicitudes
def get_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM requests")
    requests = cursor.fetchall()
    conn.close()
    return requests

# Mostrar clientes
def get_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

# Interfaz en Streamlit
with st.sidebar:
    selected = option_menu("Main Menu", ["Listar Clientes", "Agregar Cliente", 'Agregar Solicitud', 'Listar Solicitudes'], 
        icons=['people', 'people', 'people', 'people'], menu_icon="cast", default_index=1)

st.title(selected)

if selected == "Agregar Cliente":
    with st.form(key='form_cliente'):
        name = st.text_input("Nombre")
        email = st.text_input("Correo")
        phone = st.text_input("Teléfono")
        submit_button = st.form_submit_button(label='Registrar')

    if submit_button:
        if name and email and phone:
            client = Client(name, email, phone)
            save_client(client)
            st.success("¡Cliente registrado exitosamente!")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected == "Listar Clientes":
    clients = get_clients()
    if clients:
        st.write("Lista de Clientes:")
        for client in clients:
            st.write(f"ID: {client[0]}, Nombre: {client[1]}, Correo: {client[2]}, Teléfono: {client[3]}")
    else:
        st.write("No hay clientes registrados.")

elif selected == "Agregar Solicitud":
    with st.form(key='form_solicitud'):
        client_id = st.number_input("ID del Cliente", min_value=1, step=1)
        income = st.number_input("Ingreso Mensual", min_value=0.0, step=1000.0)
        monthly_payment = st.number_input("Pago Mensual", min_value=0.0, step=100.0)
        term = st.number_input("Plazo (meses)", min_value=1, step=1)
        mount = st.number_input("Monto Solicitado", min_value=0.0, step=1000.0)
        garantee = st.text_input("Garantía")
        submit_button = st.form_submit_button(label='Registrar Solicitud')

    if submit_button:
        if client_id and income and monthly_payment and term and mount and garantee:
            request = Request(client_id, income, monthly_payment, term, mount, garantee)
            save_request(request)
            st.success("¡Solicitud registrada exitosamente!")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected == "Listar Solicitudes":
    requests = get_requests()
    if requests:
        st.write("Lista de Solicitudes:")
        for request in requests:
            st.write(f"ID: {request[0]}, Cliente ID: {request[1]}, Ingreso: {request[2]}, Pago Mensual: {request[3]}, Plazo: {request[4]}, Monto: {request[5]}, Garantía: {request[6]}, Estado: {request[7]}")
    else:
        st.write("No hay solicitudes registradas.")