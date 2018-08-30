from dateutil.relativedelta import relativedelta

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
    def __init__(self, starting_balance, investment_per_loan, start_date):
        self.active_loans = []
        self.defaulted_loans = []
        self.cash_balance = starting_balance
        self.invested_principal_balance = 0
        self.investment_per_loan = investment_per_loan
        self.date = start_date

    def update_invested_principal_balance(self):
        self.invested_principal_balance = sum([loan.principal_balance for loan in self.active_loans])

    def buy_loan(self, loan):
        self.active_loans.append(loan)

    def get_payments_for_current_month(self):
        pass

    def increment_date_by_one_month(self):
        self.date += relativedelta(months=1)

def get_payments_for_date(payments_df, date):
    '''
    date parameter needs to be of type datetime.date
    '''
    return payments_df[(payments_df['RECEIVED_D'].dt.year == date.year) & (payments_df['RECEIVED_D'].dt.month == date.month)]