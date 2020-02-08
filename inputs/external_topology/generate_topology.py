import sqlite3
import pandas as pd
import re
from sqlalchemy import create_engine, text
from mutils import *
import sys

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

conn = sqlite3.connect("/opt/lnetd/web_app/database.db")

df_external = pd.read_sql("SELECT * FROM External_topology_temp", conn)
df_external = df_external.drop(['index'], axis=1)
df_external.loc[:, 'l_ip_r_ip'] = pd.Series(
        [tuple(sorted(each)) for each in list(zip(df_external.interface.values.tolist(), df_external.interface.values.tolist()))])
#print(df_external)

df_links = pd.read_sql("SELECT * FROM Links", conn)
df_links = df_links.drop(['index'], axis=1)
df_links = df_links.drop(['metric','l_ip','r_ip','capacity', 'errors','util'], axis = 1)
df_links['node'] = df_links['source']
df_links['src_icon'] = 'router'
df_links['tar_icon'] = 'router'
df_links['direction'] = 'out'
df_links['interface'] = df_links.apply(lambda row: get_interface_ifName(
        row['node'], row['l_int']), axis=1)
df_links = df_links.drop(['l_int'], axis = 1)
df_links['type'] = 'backbone'
df_links['cir'] = 0
#print(df_links)

df_final = [df_links , df_external]
df = pd.concat(df_final)
df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
df['util'] = df.apply(lambda row: get_util_interface(
        row['node'], row['interface'], row['direction']), axis=1)
df['capacity'] = df.apply(lambda row: get_capacity_ifname(
        row['node'], row['interface'], 0), axis=1)
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df.to_sql('External_topology', disk_engine, if_exists='replace')
print(df)
