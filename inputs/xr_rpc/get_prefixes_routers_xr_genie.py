#!/usr/bin/env python
from netmiko import ConnectHandler
import pandas as pd
import logging
from sqlalchemy import create_engine

import sys
sys.path.append('../utils/')

from lnetd_log import get_module_logger

import pprint

isis_instance = '64'
isis_level = 2

isis_db_routers = []
isis_db_prefixes = []

logger = get_module_logger(__name__, 'DEBUG')

def get_isis_database():
    conn = ConnectHandler(
        host="10.13.13.13",
        device_type="cisco_xr",
        username="cpetrescu",
        password='lab123',
    )
    logger.info('Connect to device and get show isis database detail')
    output = conn.send_command("show isis database detail", use_genie=True)
    return output

def main():
    output = get_isis_database()
    work_level = output['instance'][isis_instance]['level'][isis_level]['lspid']
    for rtr in work_level:
      name = work_level[rtr].get('hostname')
      ip = work_level[rtr].get('router_id')
      entry = (name,ip)
      isis_db_routers.insert(0,(entry))
      if not name:
        name = rtr.split('-')[0][:-3]
      if work_level[rtr].get('extended_ipv4_reachability'):
          for prefix in work_level[rtr]['extended_ipv4_reachability']:
            ip_prefix = work_level[rtr]['extended_ipv4_reachability'][prefix]['ip_prefix']
            ip_prefix_mask = work_level[rtr]['extended_ipv4_reachability'][prefix]['prefix_length']
            entry_prefix = (name,ip_prefix+'/'+ip_prefix_mask)
            isis_db_prefixes.insert(0,(entry_prefix))
      if work_level[rtr].get('ipv6_reachability'):
          for prefix in work_level[rtr]['ipv6_reachability']:
            ip_prefix = work_level[rtr]['ipv6_reachability'][prefix]['ip_prefix']
       	    ip_prefix_mask = work_level[rtr]['ipv6_reachability'][prefix]['prefix_length']
       	    entry_prefix = (name,ip_prefix+'/'+ip_prefix_mask)
            isis_db_prefixes.insert(0,(entry_prefix))

    labels = ['name', 'ip']

    df_routers = pd.DataFrame.from_records(isis_db_routers, columns=labels)
    df_routers.loc[:, 'country'] = df_routers['name'].str.split('-').str[0]
    df_routers = df_routers.fillna(0)
    indexNames = df_routers[ df_routers['name'] == 0 ].index
    df_routers.drop(indexNames , inplace=True)
    #print(df_routers)

    df_prefixes = pd.DataFrame.from_records(isis_db_prefixes, columns=labels)
    #df_prefixes.loc[:, 'country'] = df_prefixes['name'].str[0:2]
    df_prefixes.loc[:, 'country'] = df_prefixes['name'].str.split('-').str[0]
    df_prefixes = df_prefixes.fillna(0)
    try:
        logger.info('Write to database')
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df_prefixes.to_sql('rpc_prefixes', disk_engine, if_exists='replace')
        logger.debug('all done - this is the final panda for prefixes: \n %s' %df_prefixes)
        df_routers.to_sql('rpc_routers', disk_engine, if_exists='replace')
        logger.debug('all done - this is the final panda for routers: \n %s' %df_routers)
    except:
        logging.exception('Got error writing to sqlite3 db')
if __name__ == "__main__":
    main()
