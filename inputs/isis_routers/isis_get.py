import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
from isis import isisTable
import pandas as pd
from sqlalchemy import create_engine

devices = {'juniper.lab': '10.3.3.3'}
for name in devices:

  print 'connecting to : %s ' %devices[name]

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
  for isis in isis_table:
      for level in isis.levelTable:
          for tlv in level.tlvTable:
              a = (level.lsp_id[:-6],tlv.address)
              isis_db.insert(i,(a))

#create panda dataframe
labels = ['name', 'ip']
df = pd.DataFrame.from_records(isis_db, columns=labels)
#drop ip if is 0.0.0.0 
df=df[df['ip'].str.contains("0.0.0.0") == False]
#create country from hostname 
df.loc[:, 'country'] = df['name'].str[0:2]
df2 = df.fillna(0)

#write to sql db
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df2.to_sql('Routers', disk_engine, if_exists='replace')

print "resulting pandas : \n%s" %df2
