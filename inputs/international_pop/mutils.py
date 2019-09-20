from __future__ import division
import sqlite3
import pandas as pd
from influxdb import InfluxDBClient
from functools import reduce

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)


def get_router_links(router):
    router = router + "%"
    not_local = router[:2] + "%"
    # sys.exit(0)
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    qry = '''SELECT * FROM Links where source LIKE '%s' AND target NOT LIKE '%s' ''' % (router, not_local)
    df = pd.read_sql(qry, conn)
    #qry = db.session.query(Links).filter(and_(Links.source.like(router), Links.target.notilike(not_local))).statement
    #df = pd.read_sql(qry, db.session.bind)
    return df.to_dict(orient='records')


def get_util_router(lst):
    lst = lst.split(',')
    capacity = 0
    interval = 24
    df_variable = []
    df_variable_inbound = []
    for router in lst:
        links = get_router_links(router)
        for link in links:
            # print link
            queryurl = '''SELECT non_negative_derivative(mean(ifHCOutOctets), 1s) *8 from interface_statistics where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh group by time(5m)''' % (link['source'], link['l_int'], interval)
            result = client.query(queryurl)
            points = list(result.get_points(measurement='interface_statistics'))
            df_max = pd.DataFrame(points)
            if not df_max.empty:
                df_variable.append(df_max)
            # print link
            queryurl_inbound = '''SELECT non_negative_derivative(mean(ifHCInOctets), 1s) *8 from interface_statistics where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh group by time(5m)''' % (link['source'], link['l_int'], interval)
            result_inbound = client.query(queryurl_inbound)
            points_inbound = list(result_inbound.get_points(measurement='interface_statistics'))
            df_max_inbound = pd.DataFrame(points_inbound)
            if not df_max_inbound.empty:
                df_variable_inbound.append(df_max_inbound)
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['time'], how='outer'), df_variable).fillna(0)
    df_merged['bps'] = df_merged.drop('time', axis=1).sum(axis=1)
    df_merged = df_merged.sort_values(by=['time'])
    max_value = df_merged['bps'].max() /  1000000000  # 1000000000 #demo uses 1000 real is 1000000000
    max_value = round(max_value, 1)
    df_merged_inbound = reduce(lambda left, right: pd.merge(left, right, on=['time'], how='outer'), df_variable_inbound).fillna(0)
    df_merged_inbound['bps'] = df_merged_inbound.drop('time', axis=1).sum(axis=1)
    df_merged_inbound = df_merged_inbound.sort_values(by=['time'])
    max_value_inbound = df_merged_inbound['bps'].max() / 1000000000  # 1000000000 #demo uses 1000 real is 1000000000
    max_value_inbound = round(max_value_inbound, 1)
    return [max_value, max_value_inbound]


def get_capacity_router(lst):
    lst = lst.split(',')
    capacity = 0
    for router in lst:
        links = get_router_links(router)
        for link in links:
            # print(link)
            capacity = capacity + link['capacity']
    return capacity / 1000  # 1000 #demo uses 100 real data is 1000


def get_max_util(hostname, interface, start):
    if interface == 0:
        return -1
    int(start)
    queryurl = '''SELECT max(non_negative_derivative) as bps from
            (SELECT non_negative_derivative(max(ifHCOutOctets), 1s) *8 from interface_statistics
            where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh
            group by time(5m))''' % (hostname, interface, start)
    result = client.query(queryurl)
    # print queryurl
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['bps']))
    return result
