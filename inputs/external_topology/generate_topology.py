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

from slack_notification import send_slack_notification

alarms = True

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

#reset index
df.reset_index(drop=True, inplace=True)

disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df.to_sql('External_topology', disk_engine, if_exists='replace')
print(df)

#keep external topology for look back in time
add_to_table = disk_engine.execute(text(
        '''insert into External_topology_time select null,"index",cir,direction,interface,l_ip_r_ip,node,source,src_icon,tar_icon,target,type,util,capacity,DATETIME('now','localtime') 
		from External_topology where type !='backbone' ''').execution_options(autocommit=True))
#delete old entries
delete_old_values = disk_engine.execute(text(
        '''DELETE FROM External_topology_time WHERE timestamp <= datetime('now','-7 days','localtime')''').execution_options(autocommit=True))

#alert if util greater than thresold
def _get_alert_values():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    sql_app_config = pd.read_sql("select * from App_config", conn)
    alert_thresold = sql_app_config["alert_threshold"].values[0]
    alert_backoff =  sql_app_config["alert_backoff"].values[0]
    return alert_thresold

alert_thresold = _get_alert_values()

try:
    if alarms:
        for entry in df.to_dict(orient='records'):
            util = (entry['util']*100)/(entry['capacity']*1000000)
            #print(entry,util)
            if util > int(alert_thresold)  and entry['alert_status'] == "1":
               #print(entry,util)
               send_slack_notification(entry['source'],entry['interface'],'util',alert_thresold,util)
except Exception as e:
    print(e)
