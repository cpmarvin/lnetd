import sqlite3
import configparser
import pandas as pd
import re
from sqlalchemy import create_engine, text
import random
import sys
sys.path.append('../inputs/utils/')

import snmp_get

config = configparser.ConfigParser()
config.read("config.ini")

from lnetd_log import get_module_logger

logger = get_module_logger(__name__, 'DEBUG')

input = config.get('input', 'routers')
statistics = config.get('input', 'statistics')


def main():
    # connect to sqllite lnetd
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    # create pandas frame
    sql = 'SELECT * from %s' % input
    df = pd.read_sql(sql, conn)
    print (df)
    # drop index from old table
    df = df.drop(['index'], axis=1)
    logger.info('Fill vendor , model and version')
    if statistics == 'influxdb':
        df['vendor'] = df.apply(
            lambda row: snmp_get.get_sysdesc(row['name']), axis=1)
        df['model'] = 'NA'
        df['version'] = 'NA'  # for now
    else:
        df['vendor'] = 'NA'
        df['model'] = 'NA'
        df['version'] = 'NA'
    # set default tacacs_id
    df['tacacs_id'] = 0
    # i need to keep existing tacacs info if any
    df_lnetd = pd.read_sql('SELECT * from Routers', conn)
    df_lnetd = df_lnetd.drop(['index'], axis=1)
    # merge current network info with lnetd
    df_merge = pd.merge(df, df_lnetd, on=[
                        'name', 'ip', 'country', 'vendor'], how='left', suffixes=('_drop', ''))
    # drop the ones in lnetd but not in network
    df_merge = df_merge.loc[:, ~
                            df_merge.columns.str.contains('_drop', case=False)]
    df_merge['tacacs_id'] = df_merge['tacacs_id'].fillna(1).astype(int)
    df_merge.fillna(value='NA', inplace=True)
    df = df_merge
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df.to_sql('Routers', disk_engine, if_exists='replace')
    # print df.to_dict(orient='records')
    logger.info('all done')
    logger.debug('final pandas %s' % df)


if __name__ == '__main__':
    main()
