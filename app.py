import streamlit as st
import pandas as pd
import sqlite3

from streamlit_option_menu import option_menu
from openai import OpenAI

from models import Client, Request
from expert_system import ExpertSystem


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
    cursor.execute("INSERT INTO requests (client_id, income, monthly_payment, term, mount, garantee, status, employmentDate, debt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (request.client_id, request.income, request.monthly_payment, request.term, request.mount, request.garantee, request.status, request.employment, request.debt))
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

def format_request_name(req):
    return f"Solicitud {req[0]} - Cliente {req[1]} - Monto: ${req[5]} - Estado: {req[7]}"

# client = OpenAI()
expert_system = ExpertSystem()

# Interfaz en Streamlit
with st.sidebar:
    selected = option_menu("Main Menu", ["Listar Clientes", "Agregar Cliente", 'Agregar Solicitud', 'Listar Solicitudes', 'Evaluar Solicitud'], 
        icons=['people', 'people', 'people', 'people', 'people'], menu_icon="cast", default_index=1)

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
        df = pd.DataFrame(clients, columns=["ID", "Nombre", "Correo", "Teléfono"])
        st.dataframe(df)
    else:
        st.write("No hay clientes registrados.")

elif selected == "Agregar Solicitud":
    clients = get_clients()
    with st.form(key='form_solicitud'):
        client_id = st.selectbox("Seleccionar Cliente", [client[0] for client in clients], format_func=lambda x: next((c[1] for c in clients if c[0] == x), ""))
        income = st.number_input("Ingreso Mensual (Dolares)", min_value=0.0, step=1000.0)
        monthly_payment = st.number_input("Gastos mensuales (Dolares)", min_value=0.0, step=100.0)
        term = st.number_input("Plazo (meses)", min_value=1, step=1)
        mount = st.number_input("Monto Solicitado", min_value=0.0, step=1000.0)
        #create a date input with a validate for employment date
        st.write("Fecha de empleo debe ser menor o igual a la fecha actual")
        
        employment = st.date_input("fecha de empleo", value=pd.to_datetime('today'))
        debt = st.number_input("Deuda", min_value=0.0, step=100.0)

        garantee = st.text_input("Garantía")
        submit_button = st.form_submit_button(label='Registrar Solicitud')

      
           
    if submit_button:
        if client_id and income and monthly_payment and term and mount and garantee:
            request = Request(client_id, income, monthly_payment, term, mount, garantee,employment, debt)
        if  employment <= pd.to_datetime('today').date():
            request = Request(client_id, income, monthly_payment, term, mount, garantee, employment, debt)

            save_request(request)
            st.success("¡Solicitud registrada exitosamente!")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected == "Listar Solicitudes":
    requests = get_requests()
    if requests:
        df = pd.DataFrame(requests, columns=["ID", "Cliente ID", "Ingreso Mensual", "Pago Mensual", "Plazo (meses)", "Monto Solicitado", "Garantía", "Estado", "Fecha de Empleo", "Deuda"])
        st.dataframe(df)
    else:
        st.write("No hay solicitudes registradas.")

elif selected == "Evaluar Solicitud":
    with st.form(key='form_evaluar'):
        requests = get_requests()
        clients = get_clients()
        # for each request, add the client name to the request
        requests = [(req[0], req[1], req[2], req[3], req[4], req[5], req[6], req[7], req[8], req[9], next((c[1] for c in clients if c[0] == req[1]), "")) for req in requests]
        selected_request_id = st.selectbox("Seleccionar Solicitud", [req[0] for req in requests], format_func=lambda x: next((f"Solicitud {req[0]} -  {req[10]} ${req[5]}" for req in requests if req[0] == x), ""))
        submit_button = st.form_submit_button(label='Evaluar Solicitud')
        
        if submit_button:
            request = next((req for req in requests if req[0] == selected_request_id), None)
            if request:
                st.write(f"Solicitud ID: {request[0]}")
                st.write(f"Cliente ID: {request[1]}")
                st.write(f"Ingreso Mensual: {request[2]}")
                st.write(f"Pago Mensual: {request[3]}")
                st.write(f"Plazo (meses): {request[4]}")
                st.write(f"Monto Solicitado: {request[5]}")
                st.write(f"Garantía: {request[6]}")
                st.write(f"Estado: {request[7]}")
                st.write(f"Fecha de Empleo: {request[8]}")
                st.write(f"Deuda: {request[9]}")

                # Aquí se llamaría al sistema experto para evaluar la solicitud
                resultado, probabilidad = expert_system.evaluar(Request.from_tuple(request))
                st.write(f"Resultado de la evaluación: {resultado} (Probabilidad: {probabilidad:.2f})")