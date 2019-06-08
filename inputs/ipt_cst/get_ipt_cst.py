import yaml
import pandas as pd
import sys

from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader

from datetime import datetime

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

# Set device information with IP-address, login user and passwort
dev = Device(host="10.3.3.3", user="lab", password="lab123",port='22', gather_facts=False)
 
# Open connection to the device
dev.open()
 
# Instead of loading a YAML-file place it within the code
yml = '''
---
bgpRoutes:
 rpc: get-route-information
 args:
  advertising-protocol-name: "bgp"
  neighbor: "10.2.2.2"
 item: route-table/rt
 key: rt-destination
 view: bgpView
 
bgpView:
 fields:
  as_path: rt-entry/as-path
  rt_destination: rt-destination
'''

yml_v6 = '''
---
bgpRoutes_v6:
 rpc: get-route-information
 args:
  advertising-protocol-name: "bgp"
  neighbor: "<>"
 item: route-table/rt
 key: rt-destination
 view: bgpView_v6

bgpView_v6:
 fields:
  as_path: rt-entry/as-path
  rt_destination: rt-destination
'''
 
# Load Table and View definitions via YAML into namespace
globals().update(FactoryLoader().load(yaml.load(yml)))
#globals().update(FactoryLoader().load(yaml.load(yml_v6)))

bt = bgpRoutes(dev).get()
#bt_v6 = bgpRoutes_v6(dev).get()

route_db =[]
i = 0

for item in bt:
    a=(item.rt_destination,item.as_path)
    route_db.insert(i,(a))
'''
for item in bt_v6:
    a=(item.rt_destination,item.as_path)
    route_db.insert(i,(a))
'''

dev.close()    

#create panda dataframe
labels = ['prefix', 'ASN']
df = pd.DataFrame.from_records(route_db, columns=labels)

df1=df[df['ASN'].str.contains('^I$') == False]

df1['ASN'] = df1['ASN'].map(lambda x:' '.join(unique_list(x.split())))
df1['ASN'] = df1['ASN'].map(lambda x: x.replace('I',''))
df1['ASN'] = df1['ASN'].map(lambda x: x.replace('?',''))


#write to sql db
from sqlalchemy import create_engine,text
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
print(df1)
df1.to_sql('Bgp_customers', disk_engine, if_exists='replace')


