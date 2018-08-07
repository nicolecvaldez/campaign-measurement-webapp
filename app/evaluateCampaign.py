

import pandas as pd


# parameters:
# - df: input_dataframe
# - sub_id: column containing unique id for each participating unit
# - resp: the column indicating availment of campaign offer indicator (0, 1)
# - metrics: list of metrics columns
# - period_col: column indicating the period in which the data point falls (i.e. pre or post campaign)
# - group_col: column indicating the group assignment of the obs (i.e. treatment, control)
# - ctrl_label: label value for the control group (default = control)
# - treat_label: label value for the control group (default = treatment)

def aggDF(df, sub_id, group_col, resp, period_col, metrics_cols):
   
    """X"""
    if isinstance(metrics_cols, str):
        cols = [sub_id, resp, period_col, group_col, metrics_cols]
        print(cols)
        df = df.loc[:, cols].drop_duplicates(keep = 'first')
        df.loc[:, metrics_cols] = df.loc[:, metrics_cols].fillna(0)
        col_agg = {metrics_cols: 'sum'}

    elif isinstance(metrics_cols, list):
        cols = [sub_id, resp, period_col, group_col]
        cols.extend(metrics_cols)
        print(cols)
        df = df.loc[:, cols].drop_duplicates(keep='first')
        df.loc[:, metrics_cols] = df.loc[:, metrics_cols].fillna(0)
        col_agg = {col: 'sum' for col in metrics_cols}

    df_metrics = df.groupby([group_col, resp, period_col]).agg(col_agg).reset_index()

    df_subsCnt = df.groupby([group_col, resp]).agg({sub_id: 'nunique'}).reset_index()

    df_agg = pd.merge(df_metrics, df_subsCnt, on = [group_col, resp])
    return df_agg

def uptakeRate(n_takers, n_sample):
    return n_takers*100/n_sample   


# 1. s = n_sample
# 2. r = n_takers
# 3. r/s = %Take-up
# 4. Ys_pre - Total Size
# 5. Ys_post - Total Size
# 6. Yr_pre - Responders
# 7. Yr_post - Responders
#    Ys_pre/s - Total Base per sub
#    Ys_post/s - Total Base per sub
# 8. pct_deltaY (i.e %Increase Spend) = (Ys_post/s)/(Ys_pre/s) - 1
# 
# 9. Yr_pre :Pre Spend Taker per sub
# 10. s * pct_deltaY * (r/s) * Yr_pre :Spend Lift Incremental (target or treatment)

def groupSummary(df_agg, sub_id, period_col, resp, metric, group_col, group_label):
    
    """X"""
    
    r = max(df_agg.loc[(df_agg[resp] == 1) & (df_agg[group_col] == group_label), sub_id]) 
    nr = max(df_agg.loc[(df_agg[resp] == 0) & (df_agg[group_col] == group_label), sub_id])
    s = r + nr
    takeRate = 100*(r/s)
    Ys_pre = sum(df_agg.loc[(df_agg[period_col] == 'pre') & (df_agg[group_col] == group_label), metric]) 
    Ys_post = sum(df_agg.loc[(df_agg[period_col] == 'post') & (df_agg[group_col] == group_label), metric]) 
    Yr_pre = sum(df_agg.loc[(df_agg[resp] == 1) & (df_agg[period_col] == 'pre') & (df_agg[group_col] == group_label), metric])
    Yr_post = sum(df_agg.loc[(df_agg[resp] == 1) & (df_agg[period_col] == 'post') & (df_agg[group_col] == group_label), metric])
    pct_deltaY = 100*((Yr_post/s)/(Yr_pre/s) - 1)
    
    grpSum = {
              'InviteSize': s,
              'Response': r,
              'PctTakeUp': takeRate,
              'PreAll': Ys_pre,
              'PostAll': Ys_post,
              'PreTakers': Yr_pre,
              'PostTakers': Yr_post,
              'PctIncrease': pct_deltaY
    }
    return grpSum

def computeLift(Treat, Ctrl):
    
    """X"""
    
    liftTreat = (Treat['PctTakeUp']*Treat['PctIncrease']*0.0001)*(Treat['InviteSize']*Treat['PreTakers']/Treat['Response'])
    liftCtrl = (Ctrl['PctTakeUp']*Ctrl['PctIncrease']*0.0001)*(Treat['InviteSize']*Treat['PreTakers']/Treat['Response'])
    liftIncrement = liftTreat - liftCtrl
    
    lift = {
            'liftTreat' : liftTreat,
            'liftCtrl' : liftCtrl,
            'liftIncrement': liftIncrement
    }
    return lift

def evaluateCampaign(df, sub_id, group_col, resp, period_col, metrics_cols, ctrl_val = 1):
    
    """X"""
    
    df_agg = aggDF(df, sub_id, group_col, resp, period_col, metrics_cols)
    result = {}

    if isinstance(metrics_cols, str):
        metrics_cols = [metrics_cols]

    elif isinstance(metrics_cols, list):
        metrics_cols = metrics_cols

    for metric in metrics_cols:
        groups = df_agg[group_col].unique()
        for g in groups:
            if (g == ctrl_val):
                Ctrl = groupSummary(df_agg, sub_id, period_col, resp, metric, group_col, g)
            else:
                Treat = groupSummary(df_agg, sub_id, period_col, resp, metric, group_col, g)
            
        result.update({metric + '_Lift' : computeLift(Treat, Ctrl)})
    
    return result

