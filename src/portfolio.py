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

    def update_principal_balance(self, overall_principal):
        self.principal_balance = (self.investment_amount / self.size) * overall_principal

class Portfolio:
    def __init__(self, starting_balance, investment_per_loan, start_month, start_year):
        self.active_loans = []
        self.defaulted_loans = []
        self.cash_balance = starting_balance
        self.invested_principal_balance = 0
        self.investment_per_loan = investment_per_loan
        self.current_month = start_month
        self.current_year = start_year

    def update_invested_principal_balance(self):
        self.invested_principal_balance = sum([loan.principal_balance for loan in self.active_loans])

    def buy_loan(self, loan):
        self.active_loans.append(loan)