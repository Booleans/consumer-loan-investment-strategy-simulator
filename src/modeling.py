# Code to start training and testing a model once the data has been cleaned.
import pandas as pd

def split_data_into_labels_and_target(df):
    X = df.drop(['roi', 'issue_d', 'id'], axis=1)
    y = df['roi']
    return X, y

def get_training_and_testing_data(df, split_date='2015-09-01'):
    '''
    Loans before the cutoff date will be used for training the model, the others will be used for
    simulating and evaluating the model's performance.
    '''
    training_loans = df[df['issue_d'].isin(pd.date_range('2005-01-01', split_date)) == True]
    testing_loans = df[df['issue_d'].isin(pd.date_range('2005-01-01', split_date)) == False]
    return training_loans, testing_loans

def train_model(model, X_train, y_train):
    fit_model = model.fit(X_train, y_train)
    return fit_model
    