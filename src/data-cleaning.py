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



rate_cols = ['int_rate', 'revol_util']

for col in rate_cols:
    loans[col] = loans[col].str.rstrip('%').astype('float64')
all_col_names = list(loans.columns)