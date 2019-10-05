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
  logger = get_module_logger(__name__, 'DEBUG')

  devices = {'juniper.lab': '10.3.3.3'}

  logger.info('Device to connect : %s' % (devices))
  for name in devices:
    try:
      logger.info('Connecting to : %s' % devices[name])
      dev = junos.Device(host=devices[name], user='lab',
                         password='lab123', port='830', gather_facts=False)
      dev.open()
      dev.timeout = 600
      logger.info('Requesting data from device: %s' % devices[name])
      isis_table = isisTable(dev).get()
      logger.info('Data %s received from device: %s' % (isis_table, devices))
      dev.close()
    except Exception as e:
      logging.exception('Got exception while trying to connect')

  if len(isis_table) >= 1:

    isis_db = []
    i = 0
    logger.info('Iterate over data %s received from device: %s' %
                (isis_table, devices))
    for isis in isis_table:
      for level in isis.levelTable:
        for tlv in level.tlvTable:
          a = (level.lsp_id[:-6], tlv.address)
          isis_db.insert(i, (a))

    logger.info('Create panda')
    labels = ['name', 'ip']
    df = pd.DataFrame.from_records(isis_db, columns=labels)

    # create country entry from first 2 letters of hostname
    df.loc[:, 'country'] = df['name'].str[0:2]
    df2 = df.fillna(0)

    try:
      logger.info('Write to database')
      # write to sql db
      disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
      df2.to_sql('rpc_prefixes', disk_engine, if_exists='replace')
      logger.debug('all done - this is the final panda : \n %s' % df2)
    except Exception:
      logging.exception('Got error writing to sqlite3 db')
  else:
    logger.error("No data received from device")


if __name__ == "__main__":
  main()
