import sqlite3
import ConfigParser
import pandas as pd
import re
from sqlalchemy import create_engine,text
import random
import sys
sys.path.append('../inputs/utils/')

import snmp_get 
config = ConfigParser.ConfigParser()
config.read("config.ini")

from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'DEBUG')

input = config.get('input', 'links')
statistics = config.get('input', 'statistics')

def main():
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        #create pandas frame
        sql = 'SELECT * from %s' %input
        df=pd.read_sql(sql, conn)
        #drop index from old table
        df=df.drop(['index'], axis=1)
        logger.info('Fill l_int util capacity and error with static values')
        if statistics == 'influxdb':
            df['l_int'] = df.apply(lambda row: snmp_get.get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
            df['util'] = df.apply(lambda row: snmp_get.get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
            df['capacity'] = df.apply(lambda row: snmp_get.get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
            df['errors'] = df.apply(lambda row: snmp_get.get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)
        else:
            df['l_int'] = 3
            df['util'] = 200
            df['capacity'] = 1000
            df['errors'] = random.randint(0,2000)
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df.to_sql('Links', disk_engine, if_exists='replace')
        logger.info('all done')
        logger.debug('final pandas %s' %df)
        add_to_table = disk_engine.execute(text("insert into Links_time select null,*,DATETIME('now') from Links").execution_options(autocommit=True))

if __name__ == '__main__':
        main()
