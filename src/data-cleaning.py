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

def exclude_recent_loans(df, cutoff_date=datetime.date(2015,9,1)):
    '''

    '''

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

def memory_management(df):
    pass

def get_percent_of_column_missing(series):
    num = series.isnull().sum()
    total = series.count()
    return 100*(num/total)

def get_cols_missing_data(df):
    cols = []
    df_temp = pd.DataFrame(round(df.isnull().sum()/len(df) * 100,2))
    df_temp = df_temp.rename(columns={0: 'pct_missing'})

    for col in df_temp[df_temp['pct_missing'] > 0].index:
        cols.append(col)

    return cols

def create_missing_data_boolean_columns(df):
    cols_missing_data = get_cols_missing_data(df)
    for col in cols_missing_data:
        df[col+"_missing"] = df[col].isnull().astype('uint8')

    return df

def fill_nas(df, value=-99):
    for col in df.columns:
        df[col].fillna(value, inplace=True)
        
    return df