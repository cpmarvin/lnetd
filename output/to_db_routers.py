import sqlite3
import configparser
import pandas as pd
import re
from sqlalchemy import create_engine, text
import random
import sys

path_app = '/opt/lnetd/web_app'
sys.path.append(path_app)
from database import db
from objects_v2 import models

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
    for rtr_value in df.to_dict(orient='records'):
        print(rtr_value)
        existing_router = models.Routers.query.filter_by(name=rtr_value['name']).first()
        if existing_router:
            existing_router.ip = rtr_value['ip']
            existing_router.country = rtr_value['country']
            existing_router.vendor = rtr_value['vendor']
            existing_router.model = rtr_value['model']
            db.session.add(existing_router)
            db.session.commit()

        else:
            new_rtr = models.Routers(**rtr_value)
            db.session.add(new_rtr)
            db.session.commit()
    logger.info('all done')
    logger.debug('final pandas %s' % df)


if __name__ == '__main__':
    main()
