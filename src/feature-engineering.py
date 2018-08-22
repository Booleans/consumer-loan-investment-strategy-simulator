import pandas as pd

def create_target_column(principal_col, int_col):
    return ((int_col + principal_col)/principal_col - 1)*100