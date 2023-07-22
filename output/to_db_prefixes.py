import sqlite3
import configparser
import pandas as pd
import re
from sqlalchemy import create_engine,text
import random
import ipaddress
import sys
sys.path.append('../inputs/utils/')

config = configparser.ConfigParser()
config.read("config.ini")

from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'DEBUG')

input = config.get('input', 'prefixes')

def main():
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        #create pandas frame
        sql = 'SELECT * from %s' %input
        df=pd.read_sql(sql, conn)
        #drop index from old table
        if len(df.index) >0:
            df=df.drop(['index'], axis=1)
            logger.info('Find the ipaddress version')
            df['version'] = df.apply(lambda row: ipaddress.ip_address(row['ip'].split('/')[0]).version,axis=1)
            disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
            df.to_sql('Prefixes', disk_engine, if_exists='replace')
            logger.info('all done')
            logger.debug('final pandas %s' %df)
        else:
            print(f'No routes in input database')
            sys.exit()

if __name__ == '__main__':
        main()
