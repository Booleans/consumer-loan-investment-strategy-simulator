# Code to start training and testing a model once the data has been cleaned.
import pandas as pd

def split_data_into_labels_and_target(df):
    '''
    Split the data into features (X) and a label (y). Our label in this case is ROI of a loan.

    Args:
        df (dataframe): Our loan dataframe that has been cleaned and prepared for modeling.

    Returns:
        Dataframes: Returns 2 dataframes, one for the model features and one for the model label.
    '''
    X = df.drop(['roi', 'issue_d'], axis=1)
    y = df['roi']
    return X, y

def split_training_and_testing_data(df, split_date):
    '''
    Loans before the cutoff date will be used for training the model, the others will be used for
    simulating and evaluating the model's performance.

    Args:
        df (dataframe): Our loan dataframe that has been cleaned and prepared for modeling. At this point we should
            have no loans in the dataframe that were issued before January 2010.
        split_date (string): The final month to be included in your training data. For example, April 2016 would be '2016-04-01'.

    Returns:
        Dataframes: Returns 2 dataframes, one for training the model and another for testing.

    TODO: Apply masks and use .loc to select relevant loans.
    '''
    training_loans = df[df['issue_d'].isin(pd.date_range('2010-01-01', split_date)) == True]
    testing_loans = df[df['issue_d'].isin(pd.date_range('2010-01-01', split_date)) == False]
    return training_loans, testing_loans

def train_model(model, X_train, y_train):
    '''
    We will be iterating through multiple models for our portfolio simulation used in the testing phase so this function
    allows a model to be passed in and trained.

    Args:
        model (varies): A model to be trained on the training data. For example, a model of type xgboost.sklearn.XGBRegressor
            may be used for training.
        X_train (dataframe): Dataframe of training features.
        y_train (dataframe): Dataframe containing the ROI of the training loans.

    Returns:
        Model: Returns the original model type after it has been trained on the training data.
    '''
    fit_model = model.fit(X_train, y_train)
    return fit_model

def get_predictions(fit_model, X_test):
    '''
    Take in a trained model and get predictions of loan ROI for loans in the testing dataset. 

    Args:
        fit_model (varies): A model that has been trained to predict loan ROI.
        X_Test (dataframe): Dataframe of features in our testing dataset. 

    Returns:
        ???: Returns ROI predictions for the loans in the testing data.
    
    TODO: Figure out the correct datatype that is returned.
    '''
    return fit_model.predict(X_test)

def create_dataframe_for_simulation(loan_df, predictions):
    simulation_df = loan_df.copy(deep=True)
    simulation_df['predicted_roi'] = predictions
    return simulation_df[['issue_d', 'loan_amnt', 'predicted_roi']].reset_index(level=0).set_index('issue_d')