from dateutil.relativedelta import relativedelta

class Loan:
    def __init__(self, loan_id, borrowed_amount, investment_amount):
            self.id = int(loan_id)
            self.size = borrowed_amount
            self.initial_investment = min(investment_amount, borrowed_amount)
            self.fractional_investment = self.initial_investment / self.size
            self.principal_balance = min(investment_amount, borrowed_amount)
            self.status = 'Current'
            self.months_since_last_payment = 0
    
    def default(self):
        self.status = 'Default'
        self.principal_balance = 0

    def update_investment_principal_balance(self, overall_principal):
        self.principal_balance = overall_principal * self.fractional_investment
        
    def add_one_month_since_payment(self):
        self.months_since_last_payment += 1

class Portfolio:
    def __init__(self, starting_balance, investment_per_loan, start_date, loans_df, payments_df, min_roi=5.0):
        self.active_loans = []
        self.defaulted_loans = []
        self.cash_balance = starting_balance
        self.total_balance = starting_balance
        self.invested_principal_balance = 0
        self.investment_per_loan = investment_per_loan
        self.date = start_date
        self.min_roi = min_roi
        self.all_loans_available = loans_df
        self.all_payments_data = payments_df

    def update_invested_principal_balance(self):
        self.invested_principal_balance = sum([loan.principal_balance for loan in self.active_loans])

    def increment_date_by_one_month(self):
        self.date += relativedelta(months=1)

    def purchase_loans(self, loans):
        for loan in loans:
            self.active_loans.append(loan)
            self.cash_balance -= loan.initial_investment

    def convert_df_rows_to_loans(self, df):
        loans = []
        rows = df.to_dict(orient='records')
        for row in rows:
            loans.append(Loan(row['id'], row['loan_amnt'], self.investment_per_loan))
        return loans

    def get_loans_available_for_current_date(self):
        '''
        TODO: The date parameter used to need to be of type datetime.date but now I have to cast it to string.
              Figure out why.
        '''
        available_loans = self.all_loans_available.loc[str(self.date)]
        # Setting the dataframe index to loan id makes it easier to search and retrieve loans later.
        #available_loans.set_index('id', inplace=True)
        return available_loans
    
    def get_loans_over_required_roi_threshold(self, loans):
        return loans.loc[loans['predicted_roi'] >= self.min_roi, :]

    def get_top_loans_to_buy(self, loans):
        # We want to take as many loans as we can from the top predicted roi.
        num_loans = int(self.cash_balance // self.investment_per_loan)
        sorted_loans = loans.sort_values(by='predicted_roi', ascending=False)
        return sorted_loans.iloc[0:num_loans, :]
    
    def buy_loans_for_current_month(self):
        loans = self.get_loans_available_for_current_date()
        loans = self.get_loans_over_required_roi_threshold(loans)
        loans_to_buy = self.get_top_loans_to_buy(loans)
        loan_objects = self.convert_df_rows_to_loans(loans_to_buy)
        self.purchase_loans(loan_objects)
        
    def get_payments_for_current_month(self):
        payments_this_month = self.all_payments_data.loc[str(self.date)]
        return payments_this_month
    
    def get_payments_from_active_loans(self, payments_this_month):
        active_loan_ids = (loan.id for loan in self.active_loans)
        latest_payments = payments_this_month.loc[payments_this_month.index.get_level_values(1).isin(active_loan_ids), :]
        # Let's get rid of the date from the index and just make it loan ID for easier lookup.
        if len(latest_payments) > 0:
            latest_payments = latest_payments.reset_index(1).set_index('LOAN_ID')
        return latest_payments
    
    def apply_payments(self, payments_for_month):
        for loan in self.active_loans:
            if loan.id in payments_for_month.index:
                total_payments = 0
                end_principal_total = 0
                # TODO: Just check the length of the loan's payments instead of using try/except.
                try:
                    # In case we have more than 1 payment per month.
                    total_payments = payments_for_month.loc[loan.id, 'RECEIVED_AMT_INVESTORS'].sum()
                    end_principal_total = min(payments_for_month.loc[loan.id].PBAL_END_PERIOD_INVESTORS)
                except:
                    total_payments = payments_for_month.loc[loan.id].RECEIVED_AMT_INVESTORS
                    end_principal_total = payments_for_month.loc[loan.id].PBAL_END_PERIOD_INVESTORS
                    
                self.update_portfolio_cash_balance(loan.fractional_investment * total_payments)
                loan.update_investment_principal_balance(end_principal_total)
                loan.months_since_last_payment = 0
                
    def get_and_apply_payments_for_current_month(self):
        payments_this_month = self.get_payments_for_current_month()
        payments_from_active_loans = self.get_payments_from_active_loans(payments_this_month)
        self.apply_payments(payments_from_active_loans)
                
    def update_portfolio_cash_balance(self, payment):
        self.cash_balance += payment
        
    def add_one_month_since_loan_payment(self):
        for loan in self.active_loans:
            loan.add_one_month_since_payment()
            
    def clear_defaulted_loans(self):
        for loan in self.active_loans:
            if loan.months_since_last_payment > 4:
                self.defaulted_loans.append(loan)
                loan.default()
        self.active_loans = [loan for loan in self.active_loans if loan.status != 'Default']
    
    def update_portfolio_total_balance(self):
        self.total_balance = self.invested_principal_balance + self.cash_balance
        
    def simulate_month(self):
        self.buy_loans_for_current_month()
        self.get_and_apply_payments_for_current_month()
        self.add_one_month_since_loan_payment()
        self.clear_defaulted_loans()
        self.update_invested_principal_balance()
        self.update_portfolio_total_balance()
        self.increment_date_by_one_month()