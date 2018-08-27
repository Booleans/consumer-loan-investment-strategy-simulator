class Loan:
    def __init__(self, loan_id, loan_size, dollars_invested):
            self.id = loan_id
            self.size = loan_size
            self.investment_amount = dollars_invested
            self.principal_balance = dollars_invested
            self.status = 'Current'
    
    def default(self):
        self.status = 'Default'
        self.principal_balance = 0

    def update_balance(self, payment_to_investors):
        pass

class Portfolio:
    def __init__(self, starting_balance, investment_per_loan, start_month, start_year):
        self.loans = []
        self.cash_balance = starting_balance
        self.invested_principal_balance = 0
        self.investment_per_loan = investment_per_loan
        self.current_month = start_month
        self.current_year = start_year

    def update_invested_principal_balance(self):
        self.invested_principal_balance = sum([loan.principal_balance for loan in self.loans])    