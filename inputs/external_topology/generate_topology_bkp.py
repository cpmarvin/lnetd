import sqlite3
import pandas as pd
import re
from sqlalchemy import create_engine, text
from mutils import *
import datetime


def main():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    df = pd.read_sql("SELECT * FROM External_topology_temp", conn)
    df = df.drop(['index'], axis=1)
    df.loc[:, 'l_ip_r_ip'] = pd.Series(
        [tuple(sorted(each)) for each in list(zip(df.interface.values.tolist(), df.interface.values.tolist()))])
    df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
    df['util'] = df.apply(lambda row: get_util_interface(
        row['node'], row['interface'], row['direction']), axis=1)
    df['capacity'] = df.apply(lambda row: get_capacity_ifname(
        row['node'], row['interface'], 0), axis=1)
    # write to sql db
    print(df)
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df.to_sql('External_topology', disk_engine, if_exists='replace')


if __name__ == '__main__':
    main()
