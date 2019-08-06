import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
from jnpr.junos.op.teddb import TedTable
import pandas as pd
import random
from snmp_get import *
from get_hostname import get_hostname
from sqlalchemy import create_engine

import sys
sys.path.append('../utils/')

from lnetd_log import get_module_logger
#import logging

def main():
  logger = get_module_logger(__name__, 'DEBUG')
  devices = {'juniper.lab': '10.3.3.3'}
  logger.info('Device to connect : %s' % (devices))

  for name in devices:
    try:
      logger.info('Connecting to : %s' % devices[name])
      dev = junos.Device(host=devices[name], user='lab', password='lab123', port='830', gather_facts=False)
      dev.open()
      dev.timeout = 600
      logger.info('Requesting data from device: %s' % devices[name])
      ospf_table = TedTable(dev).get()
      logger.info('Data %s received from device: %s' % (ospf_table, devices))
      dev.close()
    except Exception as e:
      logger.exception('Got exception while trying to connect')
  if len(ospf_table) >= 1:
    ospf_db =[]
    i = 0
    logger.info('Iterate over data %s received from device: %s' % (ospf_table, devices))
    for entry in ospf_table:
        source = str(entry).split(':')[1]
        for n in entry.link:
            a = (source,n.remoteRTR,n.metric,n.localADD,n.remoteADD)
            ospf_db.insert(i,(a))

    logger.info('Create panda')
    labels = ['source', 'target', 'metric', 'l_ip', 'r_ip']
    df = pd.DataFrame.from_records(ospf_db, columns=labels)
    logger.info('Generate l_ip r_ip pair')
    df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
    logger.info('Set l_ip r_ip pair as string')
    df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
    logger.info('Get source and target names')
    df['source'] = df.apply(lambda row: get_hostname(row['source']),axis=1)
    df['target'] = df.apply(lambda row: get_hostname(row['target']),axis=1)
    logger.info('Fill NA values with 0')
    try:
      logger.info('Write to database')
      disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
      df.to_sql('rpc_links', disk_engine, if_exists='replace')
      logger.info('All done')
      logger.debug('here is the resulting info :\n %s' % (df))
    except Exception:
      logger.exception('Got error writing to sqlite3 db')
  else:
    logger.error("No data received from device")


if __name__ == "__main__":
  main()
