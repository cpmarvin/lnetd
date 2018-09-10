import sqlite3
import pandas as pd
import re
from latency_fct import get_ping_results
from sqlalchemy import create_engine,text

import numpy as np
from multiprocessing import Pool

#connect to sqllite lnetd
conn = sqlite3.connect("/opt/lnetd/web_app/database.db")

#create pandas frame
df_links=pd.read_sql("SELECT * FROM Links", conn)

#drop index from old table
df_links=df_links.drop(['index'], axis=1)

#drop if r_ip =0
df_links = df_links[df_links['r_ip'] != '0']

df4 = df_links

def wrapper(df):
    df['latency'] = df.apply(lambda row: get_ping_results(row['source'],row['r_ip']),axis=1)
    print df
    return df

n_processes = 10
pool = Pool(processes=n_processes)

df_split = np.array_split(df4, n_processes)
pool_results = pool.map(wrapper, df_split)
new_df2 = pd.concat(pool_results)

df6 = new_df2 
print df6

print "write to DB"
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')

df6.to_sql('Links_latency', disk_engine, if_exists='replace')

