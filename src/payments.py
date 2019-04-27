'''
This file contains all functions related to working with loan payments data.
Payments data is used to calculate the actual return on investment (ROI) of completed loans. 
'''

import pandas as pd

def convert_payment_date(col_date):
    return pd.to_datetime(col_date, format = '%b%Y')

def extract_relevant_cols(raw_payments_df):
    cols_to_use = ['LOAN_ID', 'RECEIVED_D', 'PBAL_END_PERIOD_INVESTORS', 'RECEIVED_AMT_INVESTORS', 'IssuedDate']
    return raw_payments_df[cols_to_use]

def set_and_sort_indices(payments_df):
    '''
    Function to set the index of the payments dataframe to be the payment date and loan ID.
    This way we can easily extract payments in a certain month and/or for a certain loan.
    Sort the index after it's set.

    Args:
        payments_df (dataframe): The dataframe containing payments data for loans.

    Returns:
        DataFrame: Returns the payments dataframe with a multi-level index of payment date and loan ID. 
    '''
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
    '''
    The file that contains all payments made to investors is a massive file. For the purposes of calculating the ROI
    of loans in our training set, we should extract only the training loans from the complete payments file.
    These are the only payments that are relevant. 

    Args:
        all_payments (dataframe): The dataframe containing payments data for all loans ever issued.
        loan_ids_from_training_set (list or tuple of ints): The loan IDs contained within our training set.

    Returns:
        DataFrame: Returns a dataframe containing payment history for loans in our training data.
    '''
    cols = ['RECEIVED_AMT_INVESTORS', 'mths_since_issue']
    return all_payments.loc[pd.IndexSlice[:, loan_ids_from_training_set], :][cols]

def get_one_loan_payment_data(payments, loan_id):
    '''
    Function to extract payments made by a single loan ID. 

    Args:
        payments (dataframe): The dataframe containing all loan payments data.
        loan_id (int): The loan ID that we want to get payments for.

    Returns:
        DataFrame: Returns a dataframe containing payment history for a single loan.

    Todo:
        Shouldn't we be accessing the payments data frame with .loc[loan_id]? 
    '''
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