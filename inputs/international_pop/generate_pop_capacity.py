from __future__ import division
import sqlite3

import pandas as pd
import random

import pandas as pd
from sqlalchemy import or_, and_
from mutils import get_max_util, get_util_router, get_capacity_router
from influxdb import InfluxDBClient

from sqlalchemy import create_engine, text
from functools import reduce

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)

disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')


def main():
  conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
  df_input = pd.read_sql("SELECT * FROM International_PoP_temp", conn)
  df_input = df_input.drop(['index'], axis=1)
  df_input['util_out'] = df_input.apply(
      lambda row: get_util_router(row['routers'])[0], axis=1)
  df_input['util_in'] = df_input.apply(
      lambda row: get_util_router(row['routers'])[1], axis=1)
  df_input['capacity'] = df_input.apply(
      lambda row: get_capacity_router(row['routers']), axis=1)
  df_input['text'] = df_input.apply(lambda row: row['name'] + ' <br> Capacity ' + str(row['capacity']) + ' Gbps'
                                    + ' <br> Util IN ' +
                                      str(row['util_in']) + ' Gbps'
                                    + ' <br> Util OUT ' +
                                      str(row['util_out']) + ' Gbps'
                                    + ' <br> Free ' + str(row['capacity'] - max(row['util_out'], row['util_in'])) + ' Gbps', axis=1)
  print('write to db')
  disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
  df_input.to_sql('International_PoP', disk_engine, if_exists='replace')


if __name__ == '__main__':
  main()
