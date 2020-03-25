import sqlite3
import pandas as pd
import re
from sqlalchemy import create_engine, text
from mutils import *
import sys

from slack_notification import send_slack_notification
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

import os
import slack
client = slack.WebClient(token='xoxb-3738957452-1000578228822-xouk7yjHeKz2OEm16XjYRudb')

conn = sqlite3.connect("/opt/lnetd/web_app/database.db")

alarms = True

df_external = pd.read_sql("SELECT * FROM Noc_Topology_Edit where graph_status = 1", conn)
#df_external = df_external.drop(['index'], axis=1)
df_external.loc[:, 'l_ip_r_ip'] = pd.Series(
        [tuple(sorted(each)) for each in list(zip(df_external.node.values.tolist() , df_external.interface.values.tolist()))])
#print(df_external)
#df_external = df_external.drop(['alert_status', 'graph_status'], axis = 1)
df_external['src_icon'] = 'router'
df_external['tar_icon'] = 'router'
df_external['direction'] = 'out'
df_external['l_ip_r_ip'] = df_external['l_ip_r_ip'].astype(str)
df_external['util'] = df_external.apply(lambda row: get_util_interface(
        row['node'], row['interface'], row['direction']), axis=1)

print(df_external)

try:
    if alarms:
        for entry in df_external.to_dict(orient='records'):
            if entry['util'] <= 0 and entry['alert_status'] == "1":
               send_slack_notification(entry['source'],entry['interface'],'down')
except Exception as e:
    pass


df_external = df_external.drop(['alert_status', 'graph_status'], axis = 1)

disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df_external.to_sql('Noc_Topology', disk_engine, if_exists='replace')
