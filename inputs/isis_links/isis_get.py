import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
from isis import isisTable
import pandas as pd
from snmp_get import * 

devices = {'juniper.lab': '10.9.9.9'}
for name in devices:

  print '---------------------------------------------------------------------------'
  print devices[name]
  print '---------------------------------------------------------------------------'

  try:
    dev = junos.Device(host=devices[name], user='lab', password='lab123',port='830', gather_facts=False)
    dev.open()
    dev.timeout = 600
    isis_table = isisTable(dev).get()
    dev.close()
  except ConnectAuthError:
    print 'ConnectAuthError'
    continue
  except ConnectRefusedError:
    print 'ConnectRefusedError'
    continue
  except ConnectTimeoutError:
    print 'ConnectTimeoutError'
    continue
  isis_db =[]
  i = 0
  print isis_table
  for isis in isis_table:
       for entry in isis.levelTable:
        for entry1 in entry.remoteTable:
         for entry2 in entry1.reachability:
          a = (entry.lsp_id[:-6],entry2.remoteRTR[:-3],entry2.metric,entry2.local_ip,entry2.local_interface,entry2.remote_ip,entry2.remote_interface)
          isis_db.insert(i,(a))
print "-------"

#create panda dataframe
print "create panda dataframe"
labels = ['source', 'target', 'metric', 'l_ip','l_int','r_ip','r_int']
df = pd.DataFrame.from_records(isis_db, columns=labels)
#create ip pair and sort
df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
df2 = df.fillna(0)
df4 = df2 

'''
uncomment this if influxdb and telegraf info available
df4['l_int'] = df4.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
df4['util'] = df4.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
df4['capacity'] = df4.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
'''

#comment below once influxdb and telegraf is up and running 
df4['l_int'] = 34
df4['util'] = 50
df4['capacity'] = 100

df4 = df4.fillna(0)
#write to sql db
from sqlalchemy import create_engine
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df4.to_sql('Links', disk_engine, if_exists='replace')
print "------Done----"
print df4
