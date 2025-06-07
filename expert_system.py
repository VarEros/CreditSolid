from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from datetime import datetime
from models import Request


class ExpertSystem:
    def __init__(self):
        # CPDs (distribuciones de probabilidad condicional)
        cpd_income = TabularCPD(variable='Income', variable_card=2, values=[[0.6], [0.4]])  # 0: Bajo, 1: Alto
        cpd_debt = TabularCPD(variable='Debt', variable_card=2, values=[[0.5], [0.5]])  # 0: Baja, 1: Alta
        cpd_payment = TabularCPD(variable='MonthlyPayment', variable_card=2, values=[[0.5], [0.5]])  # 0: Bajo, 1: Alto
        cpd_employment = TabularCPD(variable='EmploymentLength', variable_card=2, values=[[0.4], [0.6]])  # 0: <12 meses, 1: >=12 meses
        cpd_guarantee = TabularCPD(variable='Guarantee', variable_card=2, values=[[0.7], [0.3]])  # 0: No, 1: Sí

        cpd_risk = TabularCPD(
            variable='Risk',
            variable_card=2,
            values=[
                # Bajo riesgo
                [0.9, 0.8, 0.85, 0.7, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2, 0.1],
                # Alto riesgo
                [0.1, 0.2, 0.15, 0.3, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.9],
            ],
            evidence=['Income', 'Debt', 'MonthlyPayment', 'EmploymentLength'],
            evidence_card=[2, 2, 2, 2]
        )

        # Nodo objetivo: Aprobación
        cpd_approved = TabularCPD(
            variable='Approved',
            variable_card=2,
            values=[
                # Rechazado
                [0.9, 0.6, 0.5, 0.2],
                # Aprobado
                [0.1, 0.4, 0.5, 0.8],
            ],
            evidence=['Risk', 'Guarantee'],
            evidence_card=[2, 2]
        )

        # Crear el modelo de red bayesiana discreta
        model = DiscreteBayesianNetwork([
            ('Income', 'Risk'),
            ('Debt', 'Risk'),
            ('MonthlyPayment', 'Risk'),
            ('EmploymentLength', 'Risk'),
            ('Risk', 'Approved'),
            ('Guarantee', 'Approved'),
        ])

        model.add_cpds(cpd_income, cpd_payment, cpd_guarantee, cpd_employment, cpd_debt, cpd_risk, cpd_approved)
        assert model.check_model()
        self.inference = VariableElimination(model)

    def evaluar(self, request: Request):
        evidencias = request.discretizar_request()
        resultado = self.inference.query(variables=['Approved'], evidence=evidencias)
        prob_aprobado = resultado.values[1]
        return "Aprobado" if prob_aprobado >= 0.5 else "Rechazado", prob_aprobado