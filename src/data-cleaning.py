import pandas as pd
# issue_d column can be in two formats. This function will handle the conversion of both formats.
def convert_date(col_date):
    if col_date[0].isdigit():
        # Need to pad the date string with a 0 if it's too short. 
        col_date = col_date.rjust(6, '0')
        return pd.to_datetime(col_date, format = '%y-%b')
    else:
        try:
            return pd.to_datetime(col_date, format = '%b-%y')
        except:
            return pd.to_datetime(col_date, format = '%b-%Y')

def clean_data(df):
    df['issue_d'] = df['issue_d'].map(convert_date)
    # Term should be either 36 or 60.
    df['term'] = [30 if row.strip() == '36 months' else 60 for row in df['term']]

    df['emp_length'] = [0 if row == '< 1 year' else row for row in df['emp_length']]
    df['emp_length'] = df['emp_length'].str.extract('(\d+)', expand=True).astype(float)

def memory_management(df):
    pass

def get_percent_of_column_missing(series):
    num = series.isnull().sum()
    total = series.count()
    return 100*(num/total)

def get_cols_missing_data(df):
    cols = []
    df_temp = pd.DataFrame(round(df.isnull().sum()/len(df) * 100,2))
    df_temp = df_temp.rename(columns={0: 'pct_missing'})

    for col in df_temp[df_temp['pct_missing'] > 0].index:
        cols.append(col)

    return cols

def create_missing_data_boolean_columns(df):
    cols_missing_data = get_cols_missing_data(df)
    for col in cols_missing_data:
        df[col+"_missing"] = df[col].isnull().astype('uint8')

    return df

def fill_nas(df, value=-99):
    for col in df.columns:
        df[col].fillna(value, inplace=True)
        
    return df