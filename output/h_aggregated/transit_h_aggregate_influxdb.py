import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
import snmp_get

from influxdb import DataFrameClient

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def write_influx(df, host='localhost', port=8086):
    dbname = 'telegraf_agg'
    user, password = 'dummy', 'dummy'
    client = DataFrameClient(host, port, user, password, dbname)
    tag_columns = ['source', 'target', 'interface','pop','country','type']
    client.write_points(df, 'h_transit_statistics', tag_columns=tag_columns)


def main():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    sql = '''SELECT interface,source,target,node,cir,type from External_topology '''
    df = pd.read_sql(sql, conn)
    print(df)
    df = df[df['source'] == df['node']]
    df = df.drop(['node'], axis=1)
    df.loc[:, 'country'] = df['source'].str[0:2]
    df.loc[:, 'pop'] = df['source'].str[-3:]
    df[['bps_out', 'bps_in', 'time']] = df.apply(
        lambda row: pd.Series(snmp_get.get_util_ifName(
            row['source'], row['interface'])),
        axis=1)
    df['capacity'] = df.apply(
        lambda row: snmp_get.get_capacity_ifName(row['source'], row['interface']), axis=1)
    df = df.dropna()
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    df['bps_out'] = df['bps_out'].astype(int)
    df['bps_in'] = df['bps_in'].astype(int)
    df['capacity'] = df['capacity'].astype(int)
    df['cir'] = df['cir'].astype(int)
    #print(df)
    write_influx(df)

if __name__ == '__main__':
    main()

