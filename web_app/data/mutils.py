import pandas as pd
from influxdb import InfluxDBClient

def generate_year_graph(source, target):
    INFLUXDB_HOST = '127.0.0.1'
    INFLUXDB_NAME = 'telegraf_agg'
    try:
        client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', 'telegraf_agg')
        qry = '''select sum(bps_out) as bps from h_interface_statistics where
                source =~ /%s/ and target =~ /%s/
                and time >= now() -52w and time <= now() -1h
                group by time(1h)''' % (source, target)
        result=client.query(qry)
        points=list(result.get_points(measurement='h_interface_statistics'))
        df=pd.DataFrame(points)
        df=df.fillna(0)
        return df
    except Exception as e:
        raise
