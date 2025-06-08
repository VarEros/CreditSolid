import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

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

# Inicialización de OpenAI
client = OpenAI(api_key="")
expert_system = ExpertSystem()
request_obj = None
selected_request = None

# Configuración inicial de estado de sesión
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = {'resultado': "", 'probabilidad': 0.0}

# Interfaz en Streamlit
with st.sidebar:
    selected = option_menu("Main Menu", ["Listar Clientes", "Agregar Cliente", 'Agregar Solicitud', 'Listar Solicitudes', 'Evaluar Solicitud'], 
        icons=['people', 'person-add', 'file-earmark-plus', 'list', 'clipboard-check'], menu_icon="cast", default_index=1)

st.title(selected)

if selected == "Agregar Cliente":
    with st.form(key='form_cliente'):
        name = st.text_input("Nombre")
        email = st.text_input("Correo")
        phone = st.text_input("Teléfono")
        submit_button = st.form_submit_button(label='Registrar')

    if submit_button:
        if name and email and phone:
            new_client = Client(name, email, phone)
            save_client(new_client)
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
        client_id = st.selectbox("Seleccionar Cliente", 
                               [client[0] for client in clients], 
                               format_func=lambda x: next((c[1] for c in clients if c[0] == x), ""))
        income = st.number_input("Ingreso Mensual (Dolares)", min_value=0.0, step=1000.0)
        monthly_payment = st.number_input("Gastos mensuales (Dolares)", min_value=0.0, step=100.0)
        term = st.number_input("Plazo (meses)", min_value=1, step=1)
        mount = st.number_input("Monto Solicitado", min_value=0.0, step=1000.0)
        employment = st.date_input("Fecha de empleo", value=datetime.today())
        debt = st.number_input("Deuda", min_value=0.0, step=100.0)
        garantee = st.text_input("Garantía")
        submit_button = st.form_submit_button(label='Registrar Solicitud')

    if submit_button:
        if client_id and income and monthly_payment and term and mount and garantee:
            if employment <= datetime.today().date():
                request = Request(client_id, income, monthly_payment, term, mount, garantee, employment, debt)
                save_request(request)
                st.success("¡Solicitud registrada exitosamente!")
            else:
                st.error("Error: La fecha de empleo no puede ser futura")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected == "Listar Solicitudes":
    requests = get_requests()
    if requests:
        df = pd.DataFrame(requests, columns=["ID", "Cliente ID", "Ingreso Mensual", "Pago Mensual", 
                                            "Plazo (meses)", "Monto Solicitado", "Garantía", "Estado", 
                                            "Fecha de Empleo", "Deuda"])
        st.dataframe(df)
    else:
        st.write("No hay solicitudes registradas.")

elif selected == "Evaluar Solicitud":
    # Obtener datos necesarios
    requests = get_requests()
    clients = get_clients()
    
    # Crear lista de solicitudes con nombres de clientes
    requests_with_names = []
    for req in requests:
        client_name = next((c[1] for c in clients if c[0] == req[1]), "Cliente desconocido")
        requests_with_names.append({
            'id': req[0],
            'client_id': req[1],
            'client_name': client_name,
            'mount': req[5],
            'data': req
        })
    
    # Selección de solicitud
    selected_request = st.selectbox(
        "Seleccionar Solicitud",
        options=requests_with_names,
        format_func=lambda x: f"Solicitud {x['id']} - {x['client_name']} - ${x['mount']}"
    )
    
    # Botón de evaluación
    if st.button('Evaluar Solicitud', key='eval_btn'):
        if selected_request:
            request_obj = Request.from_tuple(selected_request['data'])
            resultado, probabilidad = expert_system.evaluar(request_obj)
            st.session_state.evaluation = {
                'resultado': resultado,
                'probabilidad': probabilidad,
                'request': request_obj
            }
            st.success(f"Resultado de la evaluación: {resultado} (Probabilidad: {probabilidad:.2f})")
    
    # Botón de explicación (solo si hay evaluación reciente)
    if st.session_state.evaluation['resultado']:
        if st.button('Explicar Resultado', key='explain_btn'):
            # mandar expertSystem.evidences y request 
            response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "Eres un experto en evaluación de solicitudes de crédito. Tu tarea es analizar resultados de modelos de evaluación crediticia y explicar con claridad cómo se llegó a esa conclusión, basándote en datos y evidencias."
        },
        {
            "role": "user",
            "content": f"""Analiza el siguiente resultado de evaluación crediticia y explica de forma clara, técnica y concisa lo siguiente:

            1. ¿Qué significa el resultado obtenido? ({st.session_state.evaluation['resultado']})
            2. ¿Qué indica la probabilidad asociada? ({st.session_state.evaluation['probabilidad']:.2f})
            3. ¿Qué evidencias del sistema experto influyeron más en la decisión? ({expert_system.evidences})
            4. Relaciona esas evidencias con los datos de la solicitud.
            5. Si el resultado es negativo, sugiere recomendaciones para mejorar.

            Datos de la solicitud:
            - Ingreso mensual: {st.session_state.evaluation['request'].income}
            - Cuota mensual solicitada: {st.session_state.evaluation['request'].monthly_payment}
            - Monto del crédito: {st.session_state.evaluation['request'].mount}
            - Plazo del crédito (meses): {st.session_state.evaluation['request'].term}
            - Garantía ofrecida: {st.session_state.evaluation['request'].garantee}
            - Empleo: {st.session_state.evaluation['request'].employment}
            - Deuda existente: {st.session_state.evaluation['request'].debt}
            """
                    }
                ]
            )

            explanation = response.choices[0].message.content
            st.subheader("Explicación del resultado:")
            st.write(explanation)