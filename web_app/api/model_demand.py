import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from .deploy_demand import deploy_demand
import logging

def model_demand_get(df_links,demand):
    demand = eval(demand)
    #print df_links
    #print demand
    df_all_demands = pd.DataFrame()
    for entry in demand:
        df_entry = deploy_demand(df_links,entry['source'],entry['target'],entry['demand'])
        df_all_demands = pd.concat([df_all_demands, df_entry], axis=0)

    df_final = df_all_demands.groupby(['index','l_ip','r_ip','metric'] , as_index=False)['util'].sum()
    df_links = df_links.drop(['util'], axis=1)
    df_final1 = pd.merge(df_links,df_final,  how='left',on=['index','l_ip','r_ip','metric'])
    df_final1 = df_final1.fillna(0)
    return df_final1

