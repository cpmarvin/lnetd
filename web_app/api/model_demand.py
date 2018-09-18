import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from deploy_demand import deploy_demand


def model_demand_get(df_links,demand):
    demand = eval(demand)
    #demand = [{"source":"gb-p10-lon","target":"fr-p7-mrs","demand":"10"}]
    #print "-2-2-2-2-2: %s" %demand
    #df_all_demands = pd.DataFrame([],columns=['id','l_ip','metric','r_ip','util'])
    df_all_demands = pd.DataFrame()
    for entry in demand:
        #print "-3-3-3-3: %s" %entry
        df_entry = deploy_demand(df_links,entry['source'],entry['target'],entry['demand'])
        #print "df_entry:\n%s" %df_entry
        #print "df_all_demands\n%s" %df_all_demands
        #df_all_demands = df_all_demands + df_entry
        #df_all_demands = pd.merge(df_all_demands,df_entry)
        df_all_demands = pd.concat([df_all_demands, df_entry], axis=0)
        #print "df_all_demands after add :\n%s" %df_all_demands
        #print "------end for entry---"
        #df_all_demands = pd.merge(df_entry, df_entry, on=['id']).set_index(['id']).sum(axis=1)

    #print "----all done with entry in demand and merge of result----"
    #print df_all_demands

    #print "---now sum"
    #df_final = df_all_demands.groupby('util',as_index=False).sum()
    df_final = df_all_demands.groupby(['index','l_ip','r_ip','metric'] , as_index=False)['util'].sum()
    #print "--before merge with initial"
    #print df_final
    #print "---now merge with initial df_links "
    # drop util from initial df_links , needed for proper merge
    df_links = df_links.drop(['util'], axis=1)
    df_final1 = pd.merge(df_links,df_final,  how='left',on=['index','l_ip','r_ip','metric'])
    df_final1 = df_final1.fillna(-1)
    #print "--vs initial"
    #print df_final1
    return df_final1

