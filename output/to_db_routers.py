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

input = config.get('input', 'routers')
statistics = config.get('input', 'statistics')

def main():
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        #create pandas frame
        sql = 'SELECT * from %s' %input
        df=pd.read_sql(sql, conn)
        print (df)
        #drop index from old table
        df=df.drop(['index'], axis=1)
        logger.info('Fill vendor , model and version')
        if statistics == 'influxdb':
            df['vendor'] = df.apply(lambda row: snmp_get.get_sysdesc(row['name']),axis=1)
            df['model'] = 'NA'
            df['version'] = 'NA' #for now
        else:
            df['vendor'] = 'NA'
            df['model'] = 'NA'
            df['version'] = 'NA'
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df.to_sql('Routers', disk_engine, if_exists='replace')
        #print df.to_dict(orient='records')
        logger.info('all done')
        logger.debug('final pandas %s' %df)

if __name__ == '__main__':
        main()
