import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
from jnpr.junos.op.teddb import TedTable
import pandas as pd
import random
from snmp_get import * 
from get_hostname import get_hostname
from sqlalchemy import create_engine

devices = {'juniper.lab': '10.5.5.5'}
for name in devices:

  print 'connecting to : %s ' %devices[name]

  try:
    dev = junos.Device(host=devices[name], user='lab', password='lab123',port='830', gather_facts=False)
    dev.open()
    dev.timeout = 600
    ospf_table = TedTable(dev).get()
    #print ospf_table
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
  #print isis_table
  for entry in ospf_table:
      print entry
      source = str(entry).split(':')[1]
      for n in entry.link:
          print n
          print "router: %s" %n.remoteRTR
          print "l_ip: %s" %n.remoteADD
          print "r_ip: %s" %n.localADD
          print "metric: %s" %n.metric
          a = (source,n.remoteRTR,n.metric,n.localADD,0,n.remoteADD,0)
          isis_db.insert(i,(a))

print "-------"
print isis_db
#create panda dataframe
print "create panda dataframe"
labels = ['source', 'target', 'metric', 'l_ip','l_int','r_ip','r_int']
df = pd.DataFrame.from_records(isis_db, columns=labels)
#create ip pair and sort
df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
df['source']=df['source'].astype(str)
df2 = df.fillna(0)
df4 = df2
df4['source'] = df4.apply(lambda row: get_hostname(row['source']),axis=1)
df4['target'] = df4.apply(lambda row: get_hostname(row['target']),axis=1)
print df4
"""
#uncomment this if influxdb and telegraf info available
df4['l_int'] = df4.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
df4['util'] = df4.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
df4['capacity'] = df4.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
df4['errors'] = df4.apply(lambda row: get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)
"""

#comment below once influxdb and telegraf is up and running 
df4['l_int'] = 34
df4['util'] = random.randint(0,2000)
df4['capacity'] = 1000
df4['errors'] = random.randint(0,2000)

df4 = df4.fillna(0)
#write to sql db , replace if exists 
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df4.to_sql('Links', disk_engine, if_exists='replace')

print "resulting pandas : \n%s" %df4
