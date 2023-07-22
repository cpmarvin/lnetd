import pandas as pd
from influxdb import InfluxDBClient
import sys
#from fbprophet import *

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf_agg'

client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)

def SQL_INSERT_UPDATE_FROM_DATAFRAME(SOURCE, TARGET):
  '''Create insert or REPLACE SQL
  from dataframe'''
  sql_texts = []
  for index, row in SOURCE.iterrows():
    sql_texts.append('INSERT OR REPLACE INTO ' + TARGET + ' (' +
                     str(', '.join(SOURCE.columns)) + ') VALUES ' + str(tuple(row.values)))
  return sql_texts

def get_influxdb_data(source,target):
    try:
        qry = '''select sum(bps_out) as bps from h_interface_statistics where
                source =~ /%s/ and target =~ /%s/
                and time >= now() -3w and time <= now()
                group by time(1h)''' % (source, target)
        result = client.query(qry)
        points = list(result.get_points(measurement='h_interface_statistics'))
        df = pd.DataFrame(points)
        df['time'] = pd.to_datetime(df['time'])
        df['ds'] = df['time'].dt.tz_convert(None)
        df['y'] = df['bps']
        df = df.drop(['time','bps'],axis=1)
        df = df.dropna()
        return df
    except Exception as e:
        raise


def generate_forecast(source,target):
    print('what is the source and target',source,target)
    try:
        df = get_influxdb_data(source,target)
        #print(df.head(10))
        #no ideea yet what mcmc_samples=300 is 
        #model = Prophet(mcmc_samples=300)
        model = Prophet(daily_seasonality=True,weekly_seasonality=True,yearly_seasonality=True)
        model.fit(df)
        #predict next 30 days 
        future = model.make_future_dataframe(periods=5*24,freq='H')
        forecast = model.predict(future)
        #print('before_rename',forecast.columns)
        forecast = forecast[['ds', 'trend', 'yhat', 'yhat_lower', 'yhat_upper']]
        forecast['bps'] = (forecast.yhat).round()
        forecast['bps_lower'] = (forecast.yhat_lower).round()
        forecast['bps_upper'] = (forecast.yhat_upper).round()
        #forecast['bps_trend'] = (forecast.trend).round()
        forecast = forecast[['ds','bps','bps_lower','bps_upper']]
        #print('initial\n',df.head(10))
        #forecast_bps = forecast[['ds','bps_upper']]
        forecast['ds']= forecast['ds'].astype(str)
        #print(forecast.to_dict(orient='records'))
        #fig = model.plot(forecast)
        return forecast.to_dict(orient='records')
    except Exception as e:
        raise

