from dateutil.relativedelta import relativedelta

class Loan:
    def __init__(self, loan_id, borrowed_amount, investment_amount):
            self.id = loan_id
            self.size = borrowed_amount
            self.initial_investment = min(investment_amount, borrowed_amount)
            self.principal_balance = min(investment_amount, borrowed_amount)
            self.status = 'Current'
            self.months_since_last_payment = 0
    
    def default(self):
        self.status = 'Default'
        self.principal_balance = 0

    def update_investment_principal_balance(self, overall_principal):
        self.principal_balance = (self.initial_investment / self.size) * overall_principal

class Portfolio:
    def __init__(self, starting_balance, investment_per_loan, start_date, min_roi=5.0):
        self.active_loans = []
        self.defaulted_loans = []
        self.cash_balance = starting_balance
        self.invested_principal_balance = 0
        self.investment_per_loan = investment_per_loan
        self.date = start_date
        self.min_roi = min_roi

    def update_invested_principal_balance(self):
        self.invested_principal_balance = sum([loan.principal_balance for loan in self.active_loans])

    def increment_date_by_one_month(self):
        self.date += relativedelta(months=1)

    def purchase_loans(self, loans):
        for loan in loans:
            self.active_loans.append(loan)

    def convert_df_rows_to_loans(self, df):
        loans = []
        rows = df.to_dict(orient='records')
        for row in rows:
            loans.append(Loan(row['id'], row['loan_amnt'], self.investment_per_loan))
        return loans

    def get_loans_available_for_given_date(self, loans_df):
        '''
        date parameter needs to be of type datetime.date
        '''
        return loans_df[(loans_df['issue_d'].dt.year == self.date.year) & (loans_df['issue_d'].dt.month == self.date.month)]

    def get_top_n_loans_to_buy(self, loans, n):
        loans.sort_values(by='predicted_roi', ascending=False, inplace=True)
        return loans.head(n)

    def get_loans_over_required_roi_threshold(self, df, min_roi):
        return df[df['predicted_roi'] >= min_roi]

    def get_payments_for_date(self, payments_df, date):
        '''
        date parameter needs to be of type datetime.date
        '''
        return payments_df[(payments_df['RECEIVED_D'].dt.year == date.year) & (payments_df['RECEIVED_D'].dt.month == date.month)]

    def get_top_n_loans_to_buy(loans, n):
        loans.sort_values(by='predicted_roi', ascending=False, inplace=True)
        return loans.head(n)

    def add():
        pass
