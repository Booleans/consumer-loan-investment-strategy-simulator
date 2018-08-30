import pandas as pd

def convert_payment_date(col_date):
    return pd.to_datetime(col_date, format = '%b%Y')

def load_payment_history_data(filepath, num_rows):
    cols_to_use = ('LOAN_ID', 'RECEIVED_D', 'PBAL_END_PERIOD_INVESTORS', 'RECEIVED_AMT_INVESTORS', 'IssuedDate')# 'PERIOD_END_LSTAT')
    df = pd.read_csv(filepath, usecols=cols_to_use, nrows=num_rows)
    return df

def get_cleaned_payment_history_data(filepath, num_rows=None):
    df = load_payment_history_data(filepath, num_rows)
    df['RECEIVED_D'] = convert_payment_date(df['RECEIVED_D'])
    df['IssuedDate'] = convert_payment_date(df['IssuedDate'])
    df['mths_since_issue'] = 12*(df['RECEIVED_D'].dt.year - df['IssuedDate'].dt.year) + (df['RECEIVED_D'].dt.month - df['IssuedDate'].dt.month)
    df = df.dropna()
    df['mths_since_issue'] = df['mths_since_issue'].astype('uint8')
    df.drop(columns='IssuedDate', inplace=True)
    #df['defaulted'] = [1 if row in ('Default', 'Charged Off') else 0 for row in df['PERIOD_END_LSTAT']]
    #df['defaulted'] = df['defaulted'].astype('uint8')
    #df.drop(columns='PERIOD_END_LSTAT', inplace=True)
    df['RECEIVED_AMT_INVESTORS'] = df['RECEIVED_AMT_INVESTORS'].astype('float32')
    df['PBAL_END_PERIOD_INVESTORS'] = df['PBAL_END_PERIOD_INVESTORS'].astype('float32')
    return df