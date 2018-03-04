import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
from isis import isisTable
import pandas as pd

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
      print "for isis in isis_table : %s" %isis
      for level in isis.levelTable:
          print "for level in isis.table: %s" %level
          for tlv in level.tlvTable:
              a = (level.lsp_id[:-6],tlv.address)
              isis_db.insert(i,(a))
#create panda dataframe
labels = ['name', 'ip']
df = pd.DataFrame.from_records(isis_db, columns=labels)
df.loc[:, 'country'] = df['name'].str[0:2]
df2 = df.fillna(0)

#write to sql db
from sqlalchemy import create_engine
disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df2.to_sql('Prefixes', disk_engine, if_exists='replace')

print df2
