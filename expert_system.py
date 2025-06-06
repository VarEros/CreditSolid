from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from datetime import datetime
from models import Request

# Define el modelo bayesiano
model = BayesianModel([
    ('Income', 'Approved'),
    ('MonthlyPayment', 'Approved'),
    ('Guarantee', 'Approved'),
    ('EmploymentLength', 'Approved'),
    ('Debt', 'Approved'),
])

# CPDs (distribuciones de probabilidad condicional)
cpd_income = TabularCPD(variable='Income', variable_card=2, values=[[0.6], [0.4]])  # 0 = Bajo, 1 = Alto
cpd_payment = TabularCPD(variable='MonthlyPayment', variable_card=2, values=[[0.5], [0.5]])  # 0 = Bajo, 1 = Alto
cpd_guarantee = TabularCPD(variable='Guarantee', variable_card=2, values=[[0.7], [0.3]])  # 0 = No, 1 = Sí
cpd_employment = TabularCPD(variable='EmploymentLength', variable_card=2, values=[[0.4], [0.6]])  # 0 = < 12 meses, 1 = >= 12 meses
cpd_debt = TabularCPD(variable='Debt', variable_card=2, values=[[0.6], [0.4]])  # 0 = Baja, 1 = Alta

# Nodo objetivo: Aprobación
cpd_approved = TabularCPD(
    variable='Approved',
    variable_card=2,
    values=[
        # Rechazado
        [0.9, 0.8, 0.85, 0.7, 0.9, 0.95, 0.7, 0.6, 0.5, 0.3, 0.7, 0.5, 0.4, 0.2, 0.6, 0.4],
        # Aprobado
        [0.1, 0.2, 0.15, 0.3, 0.1, 0.05, 0.3, 0.4, 0.5, 0.7, 0.3, 0.5, 0.6, 0.8, 0.4, 0.6],
    ],
    evidence=['Income', 'MonthlyPayment', 'Guarantee', 'EmploymentLength', 'Debt'],
    evidence_card=[2, 2, 2, 2, 2]
)

# Añadir CPDs al modelo
model.add_cpds(cpd_income, cpd_payment, cpd_guarantee, cpd_employment, cpd_debt, cpd_approved)

# Validar
assert model.check_model()

# Inference engine
inference = VariableElimination(model)

# === Función de evaluación ===

def evaluar_con_red_bayesiana(req: Request):
    evidencias = req.discretizar_request()
    resultado = inference.query(variables=['Approved'], evidence=evidencias)
    prob_aprobado = resultado.values[1]
    return "Aprobado" if prob_aprobado >= 0.5 else "Rechazado", prob_aprobado
