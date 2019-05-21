import sqlite3
import pandas as pd
from sqlalchemy import create_engine,text
import snmp_get

from influxdb import DataFrameClient

def write_influx(df,tags,host='localhost', port=8086):
    dbname = 'telegraf_agg'
    user,password = 'dummy','dummy'
    client = DataFrameClient(host, port, user, password, dbname)
    #print(tags.items())
    tag_columns= ['source','target','l_int']
    client.write_points(df, 'h_interface_statistics', tag_columns=tag_columns)
def main():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    sql = '''SELECT * from rpc_links '''
    df = pd.read_sql(sql, conn)
    #print(df)
    df = df.drop(['index','l_ip_r_ip','r_ip','metric'], axis=1)
    #df = df[df['capacity'] != -1]
    #print(df)
    df['l_int'] = df.apply(lambda row: snmp_get.get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
    df['capacity'] = df.apply(lambda row: snmp_get.get_capacity_ifIndex(row['source'],row['l_int']),axis=1)
    df = df[df['capacity'] != -1]
    df[['bps_out','time']] = df.apply(
                lambda row: pd.Series(snmp_get.get_util_ifIndex(row['source'],row['l_int'],0)), 
                axis=1)
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')
    df['bps_out'] = df['bps_out'].astype(int)
    tags = { 'source': df[['source']], 'target': df[['target']], 'l_int':df[['l_int']]  }
    #print(df)
    write_influx(df,tags)

if __name__ == '__main__':
    main()
