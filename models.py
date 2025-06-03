class Client:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone
        self.debt = 0
        self.record = 'Bueno'

class Request:
    def __init__(self, client_id, income, monthly_payment, term, mount, garantee, status='Pendiente'):
        self.client_id = client_id
        self.income = income
        self.monthly_payment = monthly_payment
        self.term = term
        self.mount = mount
        self.garantee = garantee