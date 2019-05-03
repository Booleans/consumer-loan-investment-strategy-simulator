'''
This file contains all functions related to working with loan payments data.
Payments data is used to calculate the actual return on investment (ROI) of completed loans. 
'''

import pandas as pd
import boto3
from io import BytesIO

def load_raw_payments_data_from_s3(filename, bucket='loan-analysis-data', get_all_columns=False):
    '''
    Function to load in the raw payments data CSV file from an S3 bucket. 

    Args:
        filename (string): The dataframe containing payments data for loans. As of April 2019 the file is 'PMTHIST_INVESTOR_201904.csv'. 
        bucket (string): The name of the S3 bucket containing the payments data. 
        get_all_columns (boolean): True/False depending on whether you want to load all available columns in the CSV file.
            If False then we can load only the columns relevant for our purpose of calculating ROI/running a portfolio simulation.
    Returns:
        DataFrame: Returns a dataframe containing the data on all payments made by all loans issued.

    TODO: In the future can we skip over completed loans where we've already calculated their ROI and no longer need payment information? 
    '''
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=filename)
    data = obj['Body'].read()
    f = BytesIO(data)
    
    columns_to_use = ('LOAN_ID', 'RECEIVED_D', 'PBAL_END_PERIOD_INVESTORS', 'RECEIVED_AMT_INVESTORS', 'IssuedDate')
    
    if get_all_columns == True:
        columns_to_use = None

    df = pd.read_csv(f, low_memory=False, usecols=columns_to_use)
    return df

def convert_payment_date(col_date):
    '''
    Function to convert the date column in the payments dataframe to a datetime data type. The date initially comes in as a string,
    such as 'SEP2009'. 

    Args:
        col_date (dataframe column): The columns that contains the date to be converted. 

    Returns:
        DataFrame: Returns a dataframe column converted to a datetime data type.
    '''
    # Format %b%Y is used because the date comes as the first 3 letters of the month followed by a 4 digit year. 
    return pd.to_datetime(col_date, format = '%b%Y')

def extract_relevant_cols(raw_payments_df):
    '''
    Function that takes in all the raw payments data and extracts only the columns that are relevant. This function is likely no longer
    needed since the load_raw_payments_data_from_s3 function now automatically extracts the desired columns.

    Args:
        raw_payments_df (dataframe): The dataframe containing payments data for loans. 

    Returns:
        DataFrame: Takes the raw payments dataframe and returns a dataframe with only the relevant columns, which are listed below in the
        cols_to_use variable.
    '''
    cols_to_use = ('LOAN_ID', 'RECEIVED_D', 'PBAL_END_PERIOD_INVESTORS', 'RECEIVED_AMT_INVESTORS', 'IssuedDate')
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
    '''
    Function to clean the raw dataframe containing loan payments. Converts columns that are dates, integers, or floats to their
    proper data type. Creates new column to calculate how many months into the loan each payment was made. A payment made in April 2019
    for a loan issued in January 2019 would have a 'mths_since_issue' value of 3.

    At the end set the index to be a multi-level index of date, loan id and sort the index.

    Args:
        raw_payments_df (dataframe): The dataframe containing the raw payments data for loans.

    Returns:
        DataFrame: Returns the payments dataframe with a multi-level index of payment date and loan ID. 

    TODO:
        Figure out where in here to use .loc[] to avoid warnings in my Jupyter notebook.
    '''
    df = raw_payments_df
    df['RECEIVED_D'] = convert_payment_date(df['RECEIVED_D'])
    df['IssuedDate'] = convert_payment_date(df['IssuedDate'])
    df['mths_since_issue'] = 12*(df['RECEIVED_D'].dt.year - df['IssuedDate'].dt.year) + (df['RECEIVED_D'].dt.month - df['IssuedDate'].dt.month)
    df = df.dropna()
    df['mths_since_issue'] = df['mths_since_issue'].astype('uint8')
    df.drop(columns='IssuedDate', inplace=True)
    df['RECEIVED_AMT_INVESTORS'] = df['RECEIVED_AMT_INVESTORS'].astype('float32')
    df['PBAL_END_PERIOD_INVESTORS'] = df['PBAL_END_PERIOD_INVESTORS'].astype('float32')
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
    cols = ('RECEIVED_AMT_INVESTORS', 'mths_since_issue')
    return all_payments.loc[pd.IndexSlice[:, loan_ids_from_training_set], :][cols]

def get_training_payments(df_payments_clean, training_loan_ids):
    '''
   Function to take in all of the historical payments data and extract only the information for loans in our training set.
   Only the loans in our training set need payments data in this format to have their ROI calculated.

    Args:
        df_payments_clean (dataframe): The dataframe output by the get_cleaned_payment_history function.
        training_loan_ids (list or tuple of ints): The loan IDs contained within our training set.

    Returns:
        DataFrame: Returns a dataframe containing payment history for loans in our training data. The dataframe index
        has been set to the loan ID. 
    '''
    # We can grab training loans easier if we set the index to loan ID.
    df_index_set = df_payments_clean.set_index('LOAN_ID')
    # Only 2 columns are relevant for calculating the ROI of training loans.
    cols = ('RECEIVED_AMT_INVESTORS', 'mths_since_issue')
    training_loan_payments = df_index_set.loc[training_loan_ids, cols]
    return training_loan_payments

def get_one_loan_payment_data(payments_training_loans, loan_id):
    '''
    Function to extract payments made by a single loan ID. 

    Args:
        payments_training_loans (dataframe): The dataframe containing all loan payments data for our training loans.
            Only training loans are relevant since ROI needs to be calculated as our label to use in model training.
        loan_id (int): The loan ID that we want to get payments for.

    Returns:
        DataFrame: Returns a dataframe containing payment history for a single loan.

    Todo: Add in description of the format the payments_training_loans dataframe should be in.
    '''
    try:
        # Loan ID must be passed in as a list to ensure we get a dataframe back and not a series.
        # Otherwise a series is returned when we have a loan where only 1 payment has been made.
        return payments_training_loans.loc[[loan_id]]
    except:
        # Need to return an empty dataframe if no payments were found for the given loan_id.
        return pd.DataFrame()

def calculative_npv_payments(loan_payments, r_guess):
    '''
    Function that takes in payments made for a loan and returns the net present value of the payments, given an
    estimated rate for return on investment and how many months into the loan the payment was made.

    Args:
        loan_payments (dataframe): Dataframe containing the payments made for the given loan. This dataframe
            comes with 2 columns, the dollar amount received by investors and the months since the loan was issued
            at the time of that payment.
        r_guess (float): Current guess of loan's ROI. For example, 13.5% would have r_guess=.135. 

    Returns:
        float: Returns the dollar value of the NPV given the current guess at the loan's ROI. 
    '''
    payments = loan_payments.RECEIVED_AMT_INVESTORS
    months = loan_payments.mths_since_issue
    return sum(payments/(1+r_guess)**(months/12))

def adjust_estimated_roi(roi_guess, roi_min, roi_max, npv):
    '''
    We calculate a loan's ROI by taking guesses at the ROI's value and calculating the net present value of the loan's payments
    based off our guess. The target NPV is 0, and we adjust our guess at ROI based off whether the NPV is too high or too lower.
    The way we update our guess is by taking a range of potential ROI values. For example, in the beginning we know that our
    minimum ROI can be -100% and our maximum will not be greater than 50%. If our initial ROI guess produces a negative NPV,
    we know about ROI guess is too lower and adjust it upwards. We adjust it to be halfway between our current guess and our
    maximum ROI possible. Then, we adjust our minimum to be our old guess, while our maximum stays the same.

    Args:
        roi_guess (float): A guess at the loan's annualized ROI. 10% should be passed in as .10. 
        roi_min (float): The potential minimum ROI value based off the information we have so far.
        roi_max (float): The potential maximum ROI value based off the information we have so far.
        npv (float): The net present value of the loan based off roi_guess. The the NPV is positive, we need to adjust
            our ROI guess to be lower. If the NPV is negative, we need to increase our ROI guess. 

    Returns:
        tuple of floats: Return updated guess for the loan's ROI, along with the updated minimum and maximum ROI values.
    '''
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

def get_roi_for_loan_id(loan_id, loan_amount, loan_payments):
    '''
    This function will calculate the annualized return on investment of a completed loan based off the initial loan balance
    and payments made to investors over the life of the loan. We start the calculation with a guess at the ROI, along with
    a minimum and maximum ROI possible. We use this guess to calculate the NPV of the loan's payments using the original
    loan balance. Based off the results, we adjust our maximum and minimum ROI range and make a new guess halfway between the
    new range. This adjustment calculation is performed by the adjust_estimated_roi function.

    Args:
        loan_id (int): The ID of the loan we are calculating ROI for.
        loan_amount (float or int): The initial balance of the loan. This, along with payments information, is 
            required for ROI calculations.
        loan_payments (dataframe): A dataframe containing the payments made towards this one loan. The dataframe contains 
            2 columns, "RECEIVED_AMT_INVESTORS" and "mths_since_issue".

    Returns:
        float: Return the annualized return on investment of the given loan. Values returned are in the format of
        "13.57" and not ".1357".
    '''
    # If there are no payments then we've lost all money, a return of -100%.
    if loan_payments.empty:
        return -100
    
    r_guess = .10
    r_min = -.999
    r_max = .50
    
    for _ in range(15):
        npv_payments = calculative_npv_payments(loan_payments, r_guess)
        npv = loan_amount - npv_payments
        r_guess, r_min, r_max = adjust_estimated_roi(r_guess, r_min, r_max, npv)
    return r_guess*100

def get_rois_for_loans(loan_amount_dict, all_loan_payments):
    '''
    fdsadgfasd

    Args:
        loan_amount_dict (dict): A dictionary where the key is the integer value representing the loan ID, and the value
            is the initial balance of the loan.
        all_loan_payments (dataframe): The dataframe for all loan payments data for our training dataset. This dataframe
            is the one created by the function get_training_payments. 

    Returns:
        dict: Dictionary where the key is loan ID and the value is the annualized return on investment calculated for that loan.

    TODO:
        Incorporate multiprocessing or it'll take unnecessarily long to calculate over 2 million ROI values.
    '''
    loan_rois = {}
    for loan_id, amount in loan_amount_dict.items():
        payments = get_one_loan_payment_data(all_loan_payments, loan_id)
        loan_rois[loan_id] = get_roi_for_loan_id(loan_id, amount, payments)
    return loan_rois