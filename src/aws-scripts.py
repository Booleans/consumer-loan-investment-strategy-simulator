from io import BytesIO
import pandas as pd
import boto3
import multiprocessing as mp
import pickle

def load_data_from_s3(filename, format='csv'):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='loan-analysis-data', Key=filename)
    data = obj['Body'].read()
    f = BytesIO(data)
    if format=='csv':
        df = pd.read_csv(f, low_memory=False)
    if format=='pkl.bz2':
        df = pd.read_pickle(f, compression='bz2')
    return df
    
def load_raw_data_froms3(filename, format='csv'):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket='loan-analysis-data', Key=filename)
    data = obj['Body'].read()
    f = BytesIO(data)
    if format=='csv':
        df = pd.read_csv(f, low_memory=False)