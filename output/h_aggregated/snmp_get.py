import datetime
import pandas as pd
from influxdb import InfluxDBClient
import re


INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)

def get_ifIndex_IP(hostname,interface):
        if interface == 0:
            return -1
        timestamp = datetime.datetime.utcnow().isoformat()

        queryurl = "SELECT Ifindex as ifIndex from interface_address where hostname =~ /%s/ and  index = '%s' ORDER BY DESC limit 1" %(hostname,interface)
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_address'))
        if not points:
            return -1
        df = pd.DataFrame(points)
        df=df.to_dict(orient='records')
        result = int(round(df[0]['ifIndex']))
        return result

def get_capacity_ifIndex(hostname,interface):
    if interface == 0 or interface == -1:
        return -1
    client = InfluxDBClient(INFLUXDB_HOST,'8086','','',INFLUXDB_NAME)
    queryurl = "SELECT last(ifHighSpeed) as capacity from interface_statistics where hostname =~ /%s/ and  ifIndex = '%s'" %(hostname,interface)
    #print queryurl
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        return -1
    df = pd.DataFrame(points)
    df=df.to_dict(orient='records')
    result = int(round(df[0]['capacity']))
    return result

def get_util_ifIndex(hostname,interface,start):
        if interface == 0:
            return 0
        int(start)
        timestamp = datetime.datetime.utcnow().isoformat()

        queryurl = '''SELECT non_negative_derivative(percentile(ifHCOutOctets,95), 1s) *8 as bps from 
                        interface_statistics where hostname =~ /%s/ and  ifIndex = '%s' 
                        AND time >= now()- 1h and time < now() 
                        GROUP BY time(1h)''' %(hostname,interface)
        #print(queryurl)
        result = client.query(queryurl)
        points = list(result.get_points(measurement='interface_statistics'))
        if not points:
            return 0

        df = pd.DataFrame(points)
        #print(df.head(1).values.tolist())
        df=df.to_dict(orient='records')
        result = int(round(df[0]['bps']))
        time = df[0]['time']
        return [result,time]

def get_util_ifName(hostname, interface):
    if interface == 0:
        return 0
    timestamp = datetime.datetime.utcnow().isoformat()

    queryurl = '''SELECT non_negative_derivative(percentile(ifHCOutOctets,95), 1s) *8 as bps_out,
                   non_negative_derivative(percentile(ifHCInOctets,95), 1s) *8 as bps_in from
                        interface_statistics where hostname =~ /%s/ and  ifName = '%s'
                        AND time >= now()- 1h and time < now()
                        GROUP BY time(1h)''' % (hostname, interface)

    #print(queryurl)
    result = client.query(queryurl)
    #print(result)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        return 0

    df = pd.DataFrame(points)
    #print(df)
    df = df.to_dict(orient='records')
    result_out = int(round(df[0]['bps_out']))
    result_in = int(round(df[0]['bps_in']))
    time = df[0]['time']
    return [result_out, result_in, time]


def get_capacity_ifName(hostname, interface):
    if interface == 0:
        return 0
    timestamp = datetime.datetime.utcnow().isoformat()

    queryurl = '''SELECT last(ifHighSpeed) as capacity from interface_statistics
            where hostname =~ /%s/ and  ifName = '%s' ''' % (hostname, interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['capacity']))
    return result

