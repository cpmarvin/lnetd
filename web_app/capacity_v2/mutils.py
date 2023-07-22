import pandas as pd
import sys
import urllib3
import jinja2
import logging
from influxdb import InfluxDBClient

urllib3.disable_warnings()
def generate_year_graph(source, target):
    INFLUXDB_HOST = '127.0.0.1'
    INFLUXDB_NAME = 'telegraf_agg'
    try:
        client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', 'telegraf_agg')
        qry = '''select sum(bps_out) as bps from h_interface_statistics where
                source =~ /%s/ and target =~ /%s/
                and time >= now() -52w and time <= now() -1h
                group by time(1h)''' % (source, target)
        result = client.query(qry)
        points = list(result.get_points(measurement='h_interface_statistics'))
        df = pd.DataFrame(points)
        df = df.fillna(0)
        return df
    except Exception as e:
        raise

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)


def get_max_util(hostname, interface, start):
    if interface == 0:
        return -1
    int(start)
    queryurl = '''SELECT max(non_negative_derivative) as bps from (SELECT non_negative_derivative(max(ifHCOutOctets), 1s) *8 from
                        interface_statistics where hostname =~ /%s/ and ifIndex ='%s' AND time >= now()- %sh
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
