import pandas as pd
import numpy as np
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

def add_supplemental_rate_data(loans_df):
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
        df['issue_d'] = df['date'].apply(date_convert)
        df.drop(columns='date', inplace=True)
        loans_df = pd.merge(loans_df, df, on=('issue_d'))

    return loans_df

def create_rate_difference_cols(df):
    df['int_minus_inflation'] = df['int_rate'] - df['expected_inflation']
    df['int_minus_mortgage'] = df['int_rate'] - df['us_mortgage_rate']
    df['int_minus_prime'] = df['int_rate'] - df['prime_rate']
    return df

def create_months_since_earliest_cl_col(df):
    df['mths_since_earliest_cr'] = round((df.issue_d - df.earliest_cr_line)/ np.timedelta64(1, 'M'), 0).astype(int)
    return df

def create_loan_life_months_col(df):
    df['loan_life_months'] = round((df.last_pymnt_d - df.issue_d )/ np.timedelta64(1, 'M'), 0).astype(int)
    return df

def create_roi_col(principal_col, int_col, loan_amount_col, n_months_col):
    return (((int_col + principal_col)/loan_amount_col)**(12 / n_months_col) - 1) * 100

def change_data_types(df):
    float64_cols = list(df.select_dtypes(include=['float64']).columns)
    for col in float64_cols:
        df[col] = df[col].astype('float32')
    
    categorical_cols = ['term', 'grade', 'home_ownership', 'purpose', 'addr_state', 'verification_status']
    for col in categorical_cols:
        df[col] = df[col].astype('category')
    
    uint8_cols = ('delinq_2yrs', 'inq_last_6mths', 'open_acc', 'pub_rec', 'total_acc', 'collections_12_mths_ex_med',
                  'acc_now_delinq', 'chargeoff_within_12_mths','pub_rec_bankruptcies', 'tax_liens')

    for col in uint8_cols:
        df[col] = df[col].astype('uint8')
    return df

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

def create_dummy_cols(df):
    dummies = get_state_dummies(df['addr_state'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_verification_dummies(df['verification_status'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_grade_dummies(df['grade'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_home_ownership_dummies(df['home_ownership'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_loan_purpose_dummies(df['purpose'])
    df = pd.concat([df, dummies], axis=1)

    drop_cols = ['grade', 'home_ownership', 'verification_status', 'purpose', 'addr_state']

    for col in drop_cols:
        df.drop(col, axis=1, inplace=True)

    return df

def get_one_loan_payment_data(payments, loan_id):
    return payments[payments['LOAN_ID'] == loan_id]

def calculative_npv_payments(payments_row, month_row, r_guess):
    return sum(payments_row/(1+r_guess)**(month_row/12))

def adjust_estimated_roi(roi_guess, roi_min, roi_max, npv):
    if npv > 0:
        new_guess = (roi_guess + roi_min)/2
        new_min = roi_min
        new_max = roi_guess
    elif npv < 0:
        new_guess = (roi_guess + roi_max)/2
        new_min = roi_guess
        new_max = roi_max
    else:
        return roi_guess
    
    return (new_guess, new_min, new_max)
    