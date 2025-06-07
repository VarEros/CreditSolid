from datetime import datetime

class Client:
    def __init__(self, name, email, phone):
        self.id: int = None  # ID del cliente, se asignará al guardar en la base de datos
        self.name = name
        self.email = email
        self.phone = phone
        self.debt = 0
        self.record = 'Bueno'

class Request:
    def __init__(self, client_id, income, monthly_payment, term, mount, garantee, employment=None, debt=0):
        self.id: int = None  # ID de la solicitud, se asignará al guardar en la base de datos
        self.client_id: int = client_id
        self.income: float = income
        self.monthly_payment: float = monthly_payment
        self.term: int = term
        self.mount: float = mount
        self.garantee: str = garantee
        self.employment = employment
        self.debt: float = debt
        self.status: str = "Pendiente"

    # contructor para crear una solicitud desde un tuple
    @classmethod
    def from_tuple(cls, data):
        return cls(
            client_id=data[1],
            income=data[2],
            monthly_payment=data[3],
            term=data[4],
            mount=data[5],
            garantee=data[6],
            employment=data[7],
            debt=data[8]
        )

    def calcular_antiguedad_meses(self):
        fecha = datetime.strptime(self.employment, '%Y-%m-%d')
        hoy = datetime.today()
        diferencia = hoy - fecha
        return diferencia.days // 30
    
    def discretizar_request(self):
        return {
            'Income': 1 if self.income >= 800 else 0,
            'MonthlyPayment': 1 if self.monthly_payment >= 300 else 0,
            'Guarantee': 1 if self.garantee else 0,
            'EmploymentLength': 1 if self.calcular_antiguedad_meses() >= 12 else 0,
            'Debt': 1 if self.debt >= self.income * 0.5 else 0,
        }
