import json
from jnpr import junos
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError
import pandas as pd
import random
from sqlalchemy import create_engine
from isis import isisTable
import logging

import sys
sys.path.append('../utils/')

from snmp_get import * 
from lnetd_log import get_module_logger

def main():
  logger = get_module_logger(__name__,'DEBUG')

  devices = {'juniper.lab': '10.3.3.3'}

  logger.info('Device to connect : %s' %(devices))
  for name in devices:
    try:
      logger.info('Connecting to : %s' %devices[name])
      dev = junos.Device(host=devices[name], user='lab', password='lab123',port='830', gather_facts=False)
      dev.open()
      dev.timeout = 600
      logger.info('Requesting data from device: %s' %devices[name])
      isis_table = isisTable(dev).get()
      logger.info('Data %s received from device: %s' %(isis_table,devices))
      dev.close()
    except Exception,e:
      logging.exception('Got exception while trying to connect')

  if len(isis_table) >=1:
    isis_db =[]
    i = 0
    logger.info('Iterate over data %s received from device: %s' %(isis_table,devices))
    for isis in isis_table:
         for entry in isis.levelTable:
          for entry1 in entry.remoteTable:
           for entry2 in entry1.reachability:
            a = (entry.lsp_id[:-6],entry2.remoteRTR[:-3],entry2.metric,entry2.local_ip,entry2.local_interface,entry2.remote_ip,entry2.remote_interface)
            isis_db.insert(i,(a))
    logger.info('Create panda')
    labels = ['source', 'target', 'metric', 'l_ip','l_int','r_ip','r_int']
    df = pd.DataFrame.from_records(isis_db, columns=labels)
    logger.info('Generate l_ip r_ip pair')
    df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
    logger.info('Set l_ip r_ip pair as string')
    df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
    logger.info('Fill NA values with 0')
    df = df.fillna(0)
    #"""
    #uncomment this if influxdb and telegraf info available
    logger.info('Fill l_int util capacity and error with influxdb values')
    df['l_int'] = df.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
    df['util'] = df.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
    df['capacity'] = df.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
    df['errors'] = df.apply(lambda row: get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)
    #"""
    """
    #comment below once influxdb and telegraf is up and running 
    logger.info('Fill l_int util capacity and error with static values')
    df['l_int'] = 34
    df['util'] = random.randint(0,2000)
    df['capacity'] = 1000
    df['errors'] = random.randint(0,2000)
    #"""
    try:
      logger.info('Write to database')
      disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
      df.to_sql('Links', disk_engine, if_exists='replace')
      logger.info('All done')
      logger.debug('here is the resulting info :\n %s' %(df))
    except Exception:
      logging.exception('Got error writing to sqlite3 db')

  else:
    logger.error("No data received from device")

if __name__ == "__main__":
    main()