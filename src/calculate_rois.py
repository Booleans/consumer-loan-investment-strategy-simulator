import multiprocessing as mp
import numpy as np
from numpy_financial import irr
import pickle
import boto3
import pandas as pd
from io import BytesIO

def read_pickle_from_s3(filename, bucket='loan-analysis-data'):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=filename)
    data = obj['Body'].read()
    f = BytesIO(data)
    file = pickle.load(f)
    return file

def read_dataframe_from_s3(filename, bucket='loan-analysis-data'):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=filename)
    data = obj['Body'].read()
    f = BytesIO(data)
    df = pd.read_pickle(f, compression='bz2') 
    return df

def get_one_loan_payment_data(df_payments, loan_id):
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
        return df_payments.loc[pd.IndexSlice[:, loan_id], ['RECEIVED_AMT_INVESTORS', 'mths_since_issue']]
    except:
        # Need to return an empty dataframe if no payments were found for the given loan_id.
        return pd.DataFrame()

def convert_monthly_return_to_annual(irr):
    return (1 + irr)**12 - 1    

def get_roi_for_loan_id(loan_id):
    starting_loan_balance = loan_amounts[loan_id]
    loan_payments = get_one_loan_payment_data(df_payments, loan_id)
    if len(loan_payments) == 0:
        return -100
    max_months = loan_payments['mths_since_issue'].max()
    payments = np.zeros(max_months+1)
    payments[0] = -starting_loan_balance
    for payment, month in zip(loan_payments['RECEIVED_AMT_INVESTORS'], loan_payments['mths_since_issue']):
        payments[month] += payment
    irr_monthly = irr(payments)
    irr_annual = convert_monthly_return_to_annual(irr_monthly)
    return 100 * irr_annual

def stop_EC2_instance(instance_id, region='us-west-2'):
    ec2 = boto3.resource('ec2', region_name=region)
    ec2.instances.filter(InstanceIds=[instance_id]).stop()
    

if __name__ == '__main__':
    loan_amounts = read_pickle_from_s3('loan_amounts.pickle')
    training_loan_ids = read_pickle_from_s3('training_loan_ids.pickle')
    df_payments = read_dataframe_from_s3('df_payments_training_loans.pkl.bz2')
    loan_rois = read_pickle_from_s3('loan_rois.pickle')
    # We can skip loans that have already been processed.
    unprocessed_ids = {loan_id for loan_id in training_loan_ids if loan_id not in loan_rois}
    num_cpus = mp.cpu_count()
    print(f'Number of CPUs: {num_cpus}')
    pool = mp.Pool(processes=num_cpus)
    rois = pool.map(get_roi_for_loan_id, unprocessed_ids)
    new_rois = dict(zip(unprocessed_ids, rois))
    loan_rois.update(new_rois)
    bucket = 'loan-analysis-data'
    key = 'loan_rois.pickle'
    pickle_byte_obj = pickle.dumps(loan_rois) 
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, key).put(Body=pickle_byte_obj)
    stop_EC2_instance('i-05c63d902d7d04e7b')