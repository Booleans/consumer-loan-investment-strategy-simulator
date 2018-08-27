import pandas as pd
from datetime import datetime as dt

def load_data(csv_files, columns, number_of_rows=None):
    loan_data = []
    for file in csv_files:    
        data = pd.read_csv('data/' + file + '.csv', header=1, low_memory=False, na_values='n/a',
                           usecols=columns, nrows=number_of_rows) 
        loan_data.append(data)
    loans = pd.concat(loan_data)
    return loans

def drop_loans_not_complete(df):
    df = df[(df['loan_status'] == 'Charged Off') | (df['loan_status'] == 'Fully Paid')]
    return df

def drop_loan_status(df):
    df = df.drop('loan_status', axis=1)
    return df

def drop_joint_applicant_loans(df):
    df = df[df['application_type'] == "INDIVIDUAL"]
    return df

def fix_rate_cols(df):
    # Columns that end with % were read in as strings instead of floats. We need to remove the % and change data types.
    rate_cols = ['int_rate', 'revol_util']
    for col in rate_cols:
        df[col] = df[col].str.rstrip('%').astype('float32')
    return df

def clean_loan_term_col(df):
    '''
    '''
    df['term'] = [36 if row.strip() == '36 months' else 60 for row in df['term']]
    df['term'] = df['term'].astype('uint8')
    return df 

def only_include_36_month_loans(df):
    df = df[df['term'] == 36]
    return df

def exclude_recent_loans(df, min_age_months):
    '''
    '''
    #df = df[df['issue_d'] < cutoff_date]
    df.drop(labels=['issue_d'], axis=1, inplace=True)
    return df

def clean_employment_length(df):
    '''
    '''
    df['emp_length'] = [0 if row == '< 1 year' else row for row in df['emp_length']]
    df['emp_length'] = df['emp_length'].str.extract('(\d+)', expand=True).astype('float32')
    return df

# issue_d column can be in two formats. This function will handle the conversion of both formats.
def convert_date(col_date):
    if col_date[0].isdigit():
        # Need to pad the date string with a 0 if it's too short. 
        col_date = col_date.rjust(6, '0')
        return pd.to_datetime(col_date, format = '%y-%b')
    else:
        try:
            return pd.to_datetime(col_date, format = '%b-%y')
        except:
            return pd.to_datetime(col_date, format = '%b-%Y')

def fix_date_cols(df):
    df['issue_d'] = df['issue_d'].map(convert_date)
    df['earliest_cr_line'] = df['earliest_cr_line'].map(convert_date)
    df.dropna(subset=['last_pymnt_d'], inplace = True)
    df['last_pymnt_d'] = df['last_pymnt_d'].map(convert_date)
    return df

def fill_nas(df, value=-99):
    for col in df.columns:
        df[col] = df[col].fillna(value)

    return df

def memory_management(df):
    pass
