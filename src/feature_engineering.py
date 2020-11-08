import pandas as pd
import numpy as np
from datetime import datetime as dt

def get_percent_of_rows_missing(series):
    '''
    Given a pandas Series, return the percent of the series that is null.

    Args:
        series (pandas series): One column of a dataframe.

    Returns:
        float: Returns 100 times the percentage of rows in a series that are null.
               1357 missing rows out of 10,000 is returned as 13.57.
    '''
    num = series.isnull().sum()
    total = series.count()
    return 100*(num/total)

def get_cols_missing_data(df):
    '''
    Given a dataframe, return the names of the columns with missing data. 

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        list: List of names of the columns that contain any null data.
    '''
    cols_with_missing_data = []
    df_temp = pd.DataFrame(round(df.isnull().sum()/len(df) * 100,2))
    df_temp = df_temp.rename(columns={0: 'pct_missing'})

    for col in df_temp[df_temp['pct_missing'] > 0].index:
        cols_with_missing_data.append(col)
    return cols_with_missing_data

def create_missing_data_boolean_columns(df):
    '''
    Given a dataframe, create boolean columns to signify missing data. For example, if a column called 'purpose' had
    missing data, this function would add a column called 'purpose_missing' with a value of 1 for rows where the 'purpose'
    column is missing data.

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with columns added for all rows that contained missing data.
    '''
    cols_missing_data = get_cols_missing_data(df)
    for col in cols_missing_data:
        df[col+"_missing"] = df[col].isnull().astype('uint8')
    return df

def fill_nas(df, value=-99):
    '''
    Fill in missing data with the value pass into this function.

    Args:
        df (dataframe): The dataframe containing information on the loans.
        value (int or float): The numeric value to replace NaN values.

    Returns:
        Dataframe: Returns the input dataframe with missing values replaced.
    '''
    for col in df.columns:
        # The ROI column is the label for our models. We don't want to fill in missing values.
        if col != 'roi':
            df[col] = df[col].fillna(value)
    return df

def add_issue_date_and_month(df):
    '''
    Take in the loan dataframe and based off the issue date column, create 2 new columns to indicate issue year and month.
    The original purpose of these extra columns were to make grouping and plotting easier but I'm not sure if it's
    necessary at this point in time.

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with 2 new columns to indicate the year and month each loan was issued.
    '''
    df['year'] = df.issue_d.dt.year
    df['month'] = df.issue_d.dt.month.astype('uint8')
    return df

def add_supplemental_rate_data(loans_df):
    '''
    Function that adds additional columns based on supplemental interest rate data taken from the Federal Reserve Economic Database.
    The point of this is to reflect the fact that interest rates do not exist in a vacuum. For example, in today's current
    economy a mortgage rate of 10% would be a high burden to bear. A mortgage rate of 10% in 1980 would essentially be free money
    when you consider inflation was over 13% that year. 

    This function currently reads in 3 interest rate files stored in the data folder of the repository.

    data/inflation_expectations.csv: The expected annual inflation rate. 
    data/MORTGAGE30US.csv:           Average interest rate for a 30 year fixed mortgage. 
    data/MPRIME.csv:                 The prime interest rate.

    The files can be found at the following URLs and should be downloaded with the frequency set to monthly.

    MPRIME.csv: https://fred.stlouisfed.org/series/MPRIME
    MORTGAGE30US.csv: https://fred.stlouisfed.org/series/MORTGAGE30US
    inflation_expectations.csv: https://fred.stlouisfed.org/series/MICH

    Args:
        loans_df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with 3 new columns for the expected inflation rate, mortgage rate, and
        prime rate. 

    TODO:
        I'd rather perform a vectorized operation instead of doing .apply(date_convert).
        I need to just pull this data from the FRED API instead of manually downloading new files every month.
    '''
    date_convert = lambda x: dt.strptime(str(x), '%Y-%m-%d')

    df_inflation = pd.read_csv('data/inflation_expectations.csv')
    df_inflation.rename(columns={'DATE':'date', 'MICH':'expected_inflation'}, inplace=True)
    df_mortgage = pd.read_csv('data/MORTGAGE30US.csv')
    df_mortgage.rename(columns={'DATE':'date', 'MORTGAGE30US':'us_mortgage_rate'}, inplace=True)
    df_prime = pd.read_csv('data/MPRIME.csv')
    df_prime.rename(columns={'DATE':'date', 'MPRIME':'prime_rate'}, inplace=True)

    supplemental_dfs = (df_inflation, df_mortgage, df_prime)

    for df in supplemental_dfs:
        df['issue_d'] = df['date'].apply(date_convert)
        df.drop(columns='date', inplace=True)
        loans_df = pd.merge(loans_df, df, on=('issue_d'))

    return loans_df

def create_rate_difference_cols(df):
    '''
    Take in the loan dataframe and create 3 new columns where we take the difference between the loan's interest rate
    and the supplemental data added in from the Federal Reserve Economic Database in the add_supplemental_rate_data
    function.

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with 3 new columns where we've calculated the difference between the loan's
        interest rate and the expected inflation rate, US 30 year fixed mortgage rate, and prime bank rate. 
    '''
    df['int_minus_inflation'] = df['int_rate'] - df['expected_inflation']
    df['int_minus_mortgage'] = df['int_rate'] - df['us_mortgage_rate']
    df['int_minus_prime'] = df['int_rate'] - df['prime_rate']
    return df

def create_months_since_earliest_cl_col(df):
    '''
    Engineer a new feature where we calculate how many months it's been since the borrower first had a credit line.
    The hope is that this feature may provide useful information.

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with a new column added for how many months it's been since the borrower opened
        their first line of credit.
    '''
    df['mths_since_earliest_cr'] = round((df.issue_d - df.earliest_cr_line)/ np.timedelta64(1, 'M'), 0).astype(int)
    return df

def create_loan_life_months_col(df):
    '''
    Engineer a new feature where we calculate how many months went by between a loan's last payment date and the date the loan
    was issued. The purpose of this function was to look at defaulted loans to see how long they lasted before defaulting.

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the input dataframe with a new column added for how many months passed between a loan's issue date
        and the last date a payment was made on that loan.
    '''
    df['loan_life_months'] = round((df.last_pymnt_d - df.issue_d )/ np.timedelta64(1, 'M'), 0).astype(int)
    return df

def change_data_types(df):
    '''
    This feature was written to reduce the memory size of the dataframe by changing some columns to the correct data types.
    float64 columns can be float32, many columns are categorical, and some columns can be uint8. This should be done before
    pickling the raw dataframe to save online. 

    Args:
        df (dataframe): The dataframe containing information on the loans.

    Returns:
        Dataframe: Returns the dataframe with certain columns having their dtype changed.
    '''
    float64_cols = list(df.select_dtypes(include=['float64']).columns)
    for col in float64_cols:
        df[col] = df[col].astype('float32')
    
    categorical_cols = ('term', 'grade', 'home_ownership', 'purpose', 'addr_state', 'verification_status')
    for col in categorical_cols:
        df[col] = df[col].astype('category')
    
    uint8_cols = ('delinq_2yrs', 'inq_last_6mths', 'open_acc', 'pub_rec', 'total_acc', 'collections_12_mths_ex_med',
                  'acc_now_delinq', 'chargeoff_within_12_mths','pub_rec_bankruptcies', 'tax_liens')

    for col in uint8_cols:
        df[col] = df[col].astype('uint8')
    return df

def get_state_dummies(state_col):
    '''
    Create dummy columns for each US state.

    Args:
        state_col (dataframe column): The column from our loan dataframe that contains the state the borrower lives in.

    Returns:
        DataFrame: Returns a dataframe containing 51 columns that represent dummy boolean variables for the state a borrower
            lives in. For example, a row containing a loan issued in Michigan, "MI", will be returned in this dataframe as a row
            that has a value of 1 in the column 'state_MI' and a 0 in all other state columns.
    '''
    # Washington DC is included in STATES.
    STATES = ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
              'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME',
              'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH',
              'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI',
              'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI',
              'WY')
    return pd.DataFrame([{'state_' + state: int(val == state) for state in STATES} for val in state_col], index=state_col.index)

def get_verification_dummies(verification_col):
    '''
    Create dummy columns for each type of loan verification status.

    Args:
        verification_col (dataframe column): The column from our loan dataframe that contains the loan's verification status.

    Returns:
        DataFrame: Returns a dataframe containing 3 columns that represent dummy boolean variables for the loan's
            verification status.
    '''
    VERIFICATIONS = ('Not Verified', 'Source Verified', 'Verified')
    return pd.DataFrame([{'is_' + status: int(val == status) for status in VERIFICATIONS} for val in verification_col],
     index=verification_col.index)

def get_grade_dummies(grade_col):
    '''
    Create dummy columns for the types of loan grades assigned by Lending Club. Lending Club assigns a grade to each loan,
    with 'A' being the least risky and 'G' being the most risky.

    Args:
        grade_col (dataframe column): The column from our loan dataframe that contains the grade of all loans.

    Returns:
        DataFrame: Returns a dataframe containing 7 columns that represent dummy boolean variables for the grade that
            Lending Club has assigned to the loan.
    '''
    GRADES = ('A', 'B', 'C', 'D', 'E', 'F', 'G')
    return pd.DataFrame([{'grade_' + grade: int(val == grade) for grade in GRADES} for val in grade_col], index=grade_col.index)

def get_home_ownership_dummies(home_col):
    '''
    Create dummy columns for the possible home ownership status of the borrower.

    Args:
        home_col (dataframe column): The column from our loan dataframe that contains the borrower's home ownership status.

    Returns:
        DataFrame: Returns a dataframe containing 3 columns that represent dummy boolean variables for the home ownership
            status of the borrower.
    '''
    STATUS = ('RENT', 'MORTGAGE', 'OWN')
    return pd.DataFrame([{'home_' + status: int(val==status) for status in STATUS} for val in home_col], index=home_col.index)

def get_loan_purpose_dummies(purpose_col):
    '''
    Create dummy columns for the stated purpose of each loan. It should be notied that loan purpose is supplied by
    the borrower and not necessarily verified.

    Args:
        purpose_col (dataframe column): The column from our loan dataframe that contains the loan's stated purpose.

    Returns:
        DataFrame: Returns a dataframe containing 13 columns that represent dummy boolean variables for the stated purpose
            of the loan.
    '''
    PURPOSES = ('debt_consolidation', 'credit_card', 'other', 'home_improvement', 'major_purchase', 'small_business',
                'medical', 'car', 'vacation', 'moving', 'wedding', 'house', 'renewable_energy')
    return pd.DataFrame([{'purpose_' + purpose: int(val==purpose) for purpose in PURPOSES} for val in purpose_col],
     index=purpose_col.index)

def create_dummy_cols(df):
    '''
    Function that chains together all of the previous functions related to create dummy variable columns. This
    function applies all those changes sequentially to generate an updated dataframe containing the dummy columns.

    Args:
        df (dataframe): Our loan data dataframe. 

    Returns:
        DataFrame: Returns a dataframe with dummy columns added in, and the original columns dropped. For example,
        the column 'addr_state' is dropped after the state dummy columns have been added. 
    '''
    dummies = get_state_dummies(df['addr_state'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_verification_dummies(df['verification_status'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_grade_dummies(df['grade'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_home_ownership_dummies(df['home_ownership'])
    df = pd.concat([df, dummies], axis=1)
    dummies = get_loan_purpose_dummies(df['purpose'])
    df = pd.concat([df, dummies], axis=1)

    drop_cols = ['grade', 'home_ownership', 'verification_status', 'purpose', 'addr_state']

    for col in drop_cols:
        df.drop(col, axis=1, inplace=True)

    return df
    