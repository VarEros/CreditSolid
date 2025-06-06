from datetime import datetime

class Client:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone
        self.debt = 0
        self.record = 'Bueno'

class Request:
    def __init__(self, client_id, income, monthly_payment, term, mount, garantee, employment=None, debt=0,  status='Pendiente'):
        
        self.client_id = client_id
        self.income = income
        self.monthly_payment = monthly_payment
        self.term = term
        self.mount = mount
        self.garantee = garantee
        self.status = status
        self.employment = employment
        self.debt = debt

    def calcular_antiguedad_meses(self):
        fecha = datetime.strptime(self.fecha_empleo, '%Y-%m-%d')
        hoy = datetime.today()
        diferencia = hoy - fecha
        return diferencia.days // 30
    
    def discretizar_request(self):
        return {
            'Income': 1 if self.income >= 800 else 0,
            'MonthlyPayment': 1 if self.monthly_payment >= 300 else 0,
            'Guarantee': 1 if self.garantee.lower() == "sí" else 0,
            'EmploymentLength': 1 if self.calcular_antiguedad_meses() >= 12 else 0,
            'Debt': 1 if self.debt >= self.income * 0.5 else 0,
        }
