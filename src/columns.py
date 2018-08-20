# Columns we know we can ignore and not load them into the dataframe.
# Columns are ignored if they provide information not available for new loans.
ignore_cols = ('annual_inc_joint', 'collection_recovery_fee', 'desc', 'funded_amnt', 'funded_amnt_inv', 'id', 'last_credit_pull_d',
 'last_fico_range_high', 'last_fico_range_low', 'last_pymnt_amnt', 'last_payment_d', 'member_id', 'next_pymnt_d', 'out_prncp',
 'out_prncp_inv', 'policy_code', 'pymnt_plan', 'recoveries', 'sub_grade', 'title', 'total_pymnt', 'total_payment_inv', 'total_rec_late_fee',
 'url', 'verified_status_joint', 'revol_bal_joint', 'hardship_flag', 'hardship_type', 'hardship_reason', 'hardship_status', 'deferral_term',
 'hardship_amount', 'hardship_start_date', 'hardship_end_date', 'payment_plan_start_date', 'hardship_length', 'hardship_dpd',
 'hardship_loan_status', 'orig_projected_additional_accrued_interest', 'hardship_payoff_balance_amount', 'hardship_last_payment_amount',
 'debt_settlement_flag', 'debt_settlement_flag_date', 'settlement_status', 'settlement_date', 'settlement_amount', 'settlement_percentage',
 'settlement_term', 'sec_app_fico_range_low', 'sec_app_fico_range_high', 'sec_app_earliest_cr_line', 'sec_app_inq_last_6mths',
 'sec_app_mort_acc', 'sec_app_open_acc', 'sec_app_revol_util', 'sec_app_open_il_6m', 'sec_app_num_rev_accts',
 'sec_app_chargeoff_within_12_mths', 'sec_app_collections_12_mths_ex_med', 'sec_app_mths_since_last_major_derog', 'verification_status_joint')