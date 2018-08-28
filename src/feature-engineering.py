import pandas as pd
from datetime import datetime as dt

def get_percent_of_rows_missing(series):
    num = series.isnull().sum()
    total = series.count()
    return 100*(num/total)

def get_cols_missing_data(df):
    cols_with_missing_data = []
    df_temp = pd.DataFrame(round(df.isnull().sum()/len(df) * 100,2))
    df_temp = df_temp.rename(columns={0: 'pct_missing'})

    for col in df_temp[df_temp['pct_missing'] > 0].index:
        cols_with_missing_data.append(col)
    return cols_with_missing_data

def create_missing_data_boolean_columns(df):
    cols_missing_data = get_cols_missing_data(df)
    for col in cols_missing_data:
        df[col+"_missing"] = df[col].isnull().astype('uint8')
    return df

def fill_nas(df, value=-99):
    for col in df.columns:
        df[col] = df[col].fillna(value)
    return df

def add_issue_date_and_month(df):
    df['year'] = df.issue_d.dt.year
    df['month'] = df.issue_d.dt.month.astype('uint8')
    return df

def add_supplemental_interest_rate_data(loans_df):
    date_convert = lambda x: dt.strptime(str(x), '%Y-%m-%d')

    df_inflation = pd.read_csv('data/inflation_expectations.csv')
    df_inflation.rename(columns={'DATE':'date', 'MICH':'expected_inflation'}, inplace=True)
    df_inflation = pd.read_csv('data/inflation_expectations.csv')
    df_inflation.rename(columns={'DATE':'date', 'MICH':'expected_inflation'}, inplace=True)
    df_mortgage = pd.read_csv('data/MORTGAGE30US.csv')
    df_mortgage.rename(columns={'DATE':'date', 'MORTGAGE30US':'us_mortgage_rate'}, inplace=True)
    df_prime = pd.read_csv('data/MPRIME.csv')
    df_prime.rename(columns={'DATE':'date', 'MPRIME':'prime_rate'}, inplace=True)

    supplemental_dfs = (df_inflation, df_mortgage, df_prime)

    for df in supplemental_dfs:
        df['date'] = df['date'].apply(date_convert)
        df['year'] = df.date.dt.year
        df['month'] = df.date.dt.month
        df.drop(columns='date', inplace=True)
        loans_df = pd.merge(loans_df, df, on=('year', 'month'))

    return loans_df

def create_roi_column(principal_col, int_col, loan_amount_col, n_months_col):
    return (((int_col + principal_col)/loan_amount_col)**(12 / n_months_col) - 1) * 100

def get_state_dummies(col):
    '''
    Return a dataframe of dummy columns, one for each state.
    '''
    # States includes DC
    STATES = ("AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL",
              "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
              "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
              "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
              "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI",
              "WY")
    return pd.DataFrame([{'state_' + state: int(val==state) for state in STATES} for val in col])

def get_verification_dummies(col):
    '''
    Return a dataframe of dummy columns, one for each state.
    '''
    VERIFICATIONS = ('Not Verified', 'Source Verified', 'Verified')
    return pd.DataFrame([{'is_' + status: int(val==status) for status in VERIFICATIONS} for val in col])

def get_grade_dummies(col):
    '''
    Return a dataframe of dummy columns, one for each state.
    '''
    GRADES = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    return pd.DataFrame([{'grade_' + grade: int(val==grade) for grade in GRADES} for val in col])

def get_home_ownership_dummies(col):
    '''
    Return a dataframe of dummy columns, one for each state.
    '''
    STATUS = ('RENT', 'MORTGAGE', 'OWN')
    return pd.DataFrame([{'home_' + status: int(val==status) for status in STATUS} for val in col])

def get_loan_purpose_dummies(col):
    '''
    Return a dataframe of dummy columns, one for each loan purpose.
    '''
    PURPOSES = ('debt_consolidation', 'credit_card', 'other', 'home_improvement', 'major_purchase', 'small_business', 'medical', 'car', 'vacation',
                'moving', 'wedding', 'house', 'renewable_energy')
    return pd.DataFrame([{'purpose_' + purpose: int(val==purpose) for purpose in PURPOSES} for val in col])
