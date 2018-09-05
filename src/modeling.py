# Code to start training and testing a model once the data has been cleaned.
import pandas as pd

def split_data_into_labels_and_target(df):
    X = df.drop(['roi', 'issue_d'], axis=1)
    y = df['roi']
    return X, y

def get_training_and_testing_data(df, split_date='2015-09-01'):
    '''
    Loans before the cutoff date will be used for training the model, the others will be used for
    simulating and evaluating the model's performance.
    '''
    training_loans = df[df['issue_d'].isin(pd.date_range('2010-01-01', split_date)) == True]
    testing_loans = df[df['issue_d'].isin(pd.date_range('2010-01-01', split_date)) == False]
    return training_loans, testing_loans

def train_model(model, X_train, y_train):
    fit_model = model.fit(X_train, y_train)
    return fit_model

def get_predictions(fit_model, X):
    return fit_model.predict(X)

def create_dataframe_for_simulation(loan_df, predictions):
    simulation_df = loan_df.copy(deep=True)
    simulation_df['predicted_roi'] = predictions
    return simulation_df[['issue_d', 'loan_amnt', 'predicted_roi']].reset_index(level=0).set_index('issue_d')