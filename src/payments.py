import pandas as pd

def convert_payment_date(col_date):
    return pd.to_datetime(col_date, format = '%b%Y')

def extract_relevant_cols(raw_payments_df):
    cols_to_use = ['LOAN_ID', 'RECEIVED_D', 'PBAL_END_PERIOD_INVESTORS', 'RECEIVED_AMT_INVESTORS', 'IssuedDate']
    return raw_payments_df[cols_to_use]

def set_and_sort_indices(payments_df):
    df = payments_df.set_index(['RECEIVED_D', 'LOAN_ID'])
    df = df.sort_index()
    return df

def get_cleaned_payment_history_data(raw_payments_df):
    df = extract_relevant_cols(raw_payments_df)
    df['RECEIVED_D'] = convert_payment_date(df['RECEIVED_D'])
    df['IssuedDate'] = convert_payment_date(df['IssuedDate'])
    df['mths_since_issue'] = 12*(df['RECEIVED_D'].dt.year - df['IssuedDate'].dt.year) + (df['RECEIVED_D'].dt.month - df['IssuedDate'].dt.month)
    df = df.dropna()
    df['mths_since_issue'] = df['mths_since_issue'].astype('uint8')
    df.drop(columns='IssuedDate', inplace=True)
    df['RECEIVED_AMT_INVESTORS'] = df['RECEIVED_AMT_INVESTORS'].astype('float32')
    df['PBAL_END_PERIOD_INVESTORS'] = df['PBAL_END_PERIOD_INVESTORS'].astype('float32')
    df = set_and_sort_indices(df)
    return df

def get_relevant_payments(all_payments, loan_ids_from_training_set):
    cols = ['RECEIVED_AMT_INVESTORS', 'mths_since_issue']
    return all_payments.loc[pd.IndexSlice[:, loan_ids_from_training_set], :][cols]