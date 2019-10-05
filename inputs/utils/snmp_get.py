import datetime
import pandas as pd
from influxdb import InfluxDBClient
from lnetd_log import get_module_logger
import re

logger = get_module_logger(__name__, 'INFO')

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)


def get_ifIndex_IP(hostname, interface):
    logger.debug('Get ifIndex from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == 0:
        return -1
    timestamp = datetime.datetime.utcnow().isoformat()
    queryurl = "SELECT Ifindex as ifIndex from interface_address where hostname =~ /%s/ and  index = '%s' ORDER BY DESC limit 1" % (
        hostname, interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_address'))
    if not points:
        logger.warning('No ifIndex data for %s %s => replace with -1' %
                       (hostname, interface))
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['ifIndex']))
    return result


def get_uti_ifIndex(hostname, interface, start):
    logger.debug('Get util from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == -1:
        return -1
    int(start)
    timestamp = datetime.datetime.utcnow().isoformat()
    queryurl = '''SELECT non_negative_derivative(last(ifHCOutOctets), 1s) *8 as bps from interface_statistics
                  where hostname =~ /%s/ and  ifIndex = '%s' AND time >= now()- %sh10m and time <=now()- %sh
                  GROUP BY time(5m)''' % (hostname, interface, start, start)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        logger.warning('No util data for %s %s =>replace with -1' %
                       (hostname, interface))
        print(queryurl)
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['bps']))
    return result


def get_capacity_ifIndex(hostname, interface):
    logger.debug('Get capacity from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == 0 or interface == -1:
        return -1
    client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)
    queryurl = "SELECT last(ifHighSpeed) as capacity from interface_statistics where hostname =~ /%s/ and  ifIndex = '%s'" % (hostname, interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        logger.warning('No capacity data for %s %s => replace with -1' %
                       (hostname, interface))
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['capacity']))
    return result


def get_errors_ifIndex(hostname, interface, start):
    logger.debug('Get Errors from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == 0:
        return -1
    int(start)
    timestamp = datetime.datetime.utcnow().isoformat()
    queryurl = '''SELECT non_negative_derivative(last(ifInErrors), 1s) as errors from interface_statistics
                  where hostname =~ /%s/ and  ifIndex = '%s' AND time >= now()- %sh10m and time <=now()- %sh
                  GROUP BY time(5m)''' % (hostname, interface, start, start)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        logger.warning(
            'No errors data for %s with %s => replace with -1' % (hostname, interface))
        return -1
    df = pd.DataFrame(points)
    df = df.to_dict(orient='records')
    result = int(round(df[0]['errors']))
    return result


def get_sysdesc(hostname):
    #logger.debug('Get sysDesc from influxdb based on %s with %s'%(hostname))
    timestamp = datetime.datetime.utcnow().isoformat()
    queryurl = '''SELECT last(sysDesc) from snmp where hostname =~ /%s/''' % (hostname)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='snmp'))
    if not points:
        #logger.warning('No sysDesc data for %s => replace with -1'%(hostname,interface))
        return 'NA'
    if re.match("^Cisco IOS XR Software", points[0]['last']):
        vendor = 'cisco-xr'
    elif re.match("^Cisco IOS Software", points[0]['last']):
        vendor = 'cisco-ios'
    elif re.search(r".Huawei", points[0]['last']):
        vendor = 'huawei'
    elif re.match("^Juniper Networks", points[0]['last']):
        vendor = 'juniper'
    else:
        vendor = 'NA'
    return vendor


def get_util_ifName(hostname, interface, start):
    logger.debug('Get util from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == -1:
        return -1
    int(start)
    timestamp = datetime.datetime.utcnow().isoformat()
    queryurl = '''SELECT non_negative_derivative(last(ifHCOutOctets), 1s) *8 from interface_statistics
                  where hostname =~ /%s/ and  ifName = '%s' AND time >= now()- %sh10m and time <=now()- %sh
                  GROUP BY time(5m)''' % (hostname, interface, start, start)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        logger.warning('No util data for %s %s =>replace with -1' %
                       (hostname, interface))
        return -1
    df = pd.DataFrame(points)
    df.columns = ['bps', 'time']
    df = df.to_dict(orient='records')
    result = int(round(df[0]['bps']))
    return result


def get_capacity_ifName(hostname, interface):
    logger.debug('Get capacity from influxdb based on %s with %s' %
                 (hostname, interface))
    if interface == 0 or interface == -1:
        return -1
    client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)
    queryurl = "SELECT last(ifHighSpeed) from interface_statistics where hostname =~ /%s/ and  ifName = '%s'" % (
        hostname, interface)
    result = client.query(queryurl)
    points = list(result.get_points(measurement='interface_statistics'))
    if not points:
        logger.warning('No capacity data for %s %s => replace with -1' %
                       (hostname, interface))
        return -1
    df = pd.DataFrame(points)
    df.columns = ['capacity', 'time']
    df = df.to_dict(orient='records')
    result = int(round(df[0]['capacity']))
    return result
