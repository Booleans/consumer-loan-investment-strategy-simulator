class Loan:
    def __init__(self, df_row):
            self.id = loan_id
            self.initial_balance = amount
            self.investment_amount = 0
            self.principal_balance = 0
            self.status = 'Current'
    
    def default(self):
        self.principal_balance = 0
        
class Portfolio:
    def __init__(self, starting_balance, investment_per_loan):
        self.loans = []
        self.balance = starting_balance
        self.investment_per_loan = investment_per_loan

    def update_balance(self):
        self.balance = sum([loan.principal_balance for loan in self.loans])