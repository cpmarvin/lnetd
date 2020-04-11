import pandas as pd
from sqlalchemy import create_engine,text
import sqlite3
import pandas as pd
from sqlalchemy import create_engine,text

from influxdb import InfluxDBClient
from datetime import date, timedelta

INFLUXDB_HOST = '127.0.0.1'
INFLUXDB_NAME = 'telegraf_agg'
client = InfluxDBClient(INFLUXDB_HOST, '8086', '', '', INFLUXDB_NAME)


disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')

def get_hosname(ip):
    sql_qry = "select name from Routers where ip = '%s'" %(ip)
    router_name = disk_engine.execute(text(sql_qry).execution_options(autocommit=True))
    router = router_name.fetchall()
    if not router:
        return ip
    else:
        return str(router[0][0])

def get_demand_newtflow(router='none',interface='none'):
    try:
        #connect to sqllite lnetd
        conn = sqlite3.connect("/opt/lnetd/web_app/pmacct.db")
        #create pandas frame
        sql='''SELECT peer_ip_src,peer_ip_dst,bytes,peer_as_dst FROM
            acct_bgp where peer_ip_src = '%s' and iface_in=%s and bytes >= 187000000 ''' %(router,interface)
        df_netflow=pd.read_sql(sql, conn)
        return df_netflow
    except Exception as e:
        print(e)
        return {}

def return_cc(name):
    if '-' in name:
        return name[:2]
    else:
        return 'NO-NHS'

def check_type(source):
    if 'TRANS' in source:
        return 'TRANS'
    elif 'CDN' in source:
        return 'CDN'
    elif 'PEER' in source:
        return 'PEER'
    else:
        return 'none'

def get_lnetd_external():
    '''
    Fetch current LnetD target data from External Topology
    and return a panda
    '''
    #connect to sqllite lnetd
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    #create pandas frame
    sql='''SELECT source,target,node,cir,type from External_topology where type !='backbone' '''
    df = pd.read_sql(sql, conn)
    return df

def generat_unique_info():
    df = get_lnetd_external()
    #drop row that have both source and node the same
    df = df[df['source'] == df['node']]

    df.loc[:, 'country'] = df['source'].str[0:2]
    df['pop'] = df['source'].apply(lambda x: x.split('-')[2])
    # no need for now 
    #df['type'] = df.apply(lambda row: check_type(row['target']), axis=1)

    # per type of traffic
    df_type = df[['type']].drop_duplicates()
    df_type['name'] = 'All ' + df_type['type'].str.upper() + ' traffic'
    df_type.reset_index(drop=True, inplace=True)
    #per country
    df_country = df[['country']].drop_duplicates()
    df_country['name'] = 'All traffic in country: ' + df_country['country']
    df_country.reset_index(drop=True, inplace=True)
    #per country and type
    df_country_type = df[['country', 'type']].drop_duplicates()
    df_country_type['name'] = 'All ' + df_country_type['type'].str.upper() + \
        ' traffic in country: ' + df_country_type['country']
    df_country_type.reset_index(drop=True, inplace=True)
    #per pop
    df_pop = df[['pop']].drop_duplicates()
    df_pop['name'] = 'All traffic in PoP: ' + df_pop['pop']
    df_pop.reset_index(drop=True, inplace=True)
    #per pop and type
    df_pop_type = df[['pop', 'type']].drop_duplicates()
    df_pop_type['name'] = 'All ' + df_pop_type['type'].str.upper() + \
        ' traffic in PoP: ' + df_pop_type['pop']
    df_pop_type.reset_index(drop=True, inplace=True)
    #per target
    df_target = df[['target']].drop_duplicates()
    df_target['name'] = 'All traffic to : ' + df_target['target']
    df_target.reset_index(drop=True, inplace=True)
    #per country , pop and target
    df_country_pop_target = df[['country', 'pop', 'target']].drop_duplicates()
    df_country_pop_target['name'] = 'All traffic to : ' + \
        df_country_pop_target['target'] + ' in PoP ' + df_country_pop_target['pop']
    df_country_pop_target.reset_index(drop=True, inplace=True)
    #concatenate all in a final panda
    df_final = pd.concat([df_type,
                          df_country, df_country_type, df_pop, df_pop_type, df_target, df_country_pop_target])
    df_final = df_final.reset_index(drop=True)
    df_final = df_final.fillna('').reset_index()
    #print(df_final)
    final = df_final.to_dict(orient='records')
    return final

def generate_traffic_util(df):
  '''Parse panda and create dict with traffic util'''
  traffic_values = {}
  # get inbound traffic
  df_inbound_total = df.loc[df['direction'] == 'in']
  df_inbound_transit = df_inbound_total.loc[df['type'].str.contains(
      r'(TRANS)', case=False)]
  df_inbound_cdn = df_inbound_total.loc[df['type'].str.contains(
      r'(CDN)', case=False)]
  df_inbound_peering = df_inbound_total.loc[df['type'].str.contains(
      r'(PEER)', case=False)]
  # get outbound traffic
  df_outbound_total = df.loc[df['direction'] == 'out']
  df_outbound_transit = df_outbound_total.loc[df['type'].str.contains(
      r'(TRANS)', case=False)]
  df_outbound_cdn = df_outbound_total.loc[df['type'].str.contains(
      r'(CDN)', case=False)]
  df_outbound_peering = df_outbound_total.loc[df['type'].str.contains(
      r'(PEER)', case=False)]
  # add to dict inbound
  traffic_values['total_in'] = df_inbound_total['util'].sum()
  traffic_values['transit_in'] = df_inbound_transit['util'].sum()
  traffic_values['cdn_in'] = df_inbound_cdn['util'].sum()
  traffic_values['peer_in'] = df_inbound_peering['util'].sum()
  # add to dict outbound
  traffic_values['total_out'] = df_outbound_total['util'].sum()
  traffic_values['transit_out'] = df_outbound_transit['util'].sum()
  traffic_values['cdn_out'] = df_outbound_cdn['util'].sum()
  traffic_values['peer_out'] = df_outbound_peering['util'].sum()

  return traffic_values


def get_month_util(provider,pop):
  today = date.today().replace(day=1)
  prev = today - timedelta(days=1)
  end_interval = today.strftime("%Y-%m")+"-01T00:00:00Z"
  start_interval = prev.strftime("%Y-%m")+"-01T00:00:00Z"
  if pop == 'all':
      query = f'''SELECT PERCENTILE(bps_out,95) as bps_out ,PERCENTILE(bps_in,95) as bps_in from h_transit_statistics
      where target =~/{provider}/
      and pop =~//
      and type =~ /transit/
      AND time >= '{start_interval}'  and time < '{end_interval}' ;
      '''
  else:
      query = f'''select PERCENTILE(bps_out,95) as bps_out ,PERCENTILE(bps_in,95) as bps_in from h_transit_statistics
      where target =~/{provider}/
      and pop =~/{pop}/
      and type =~ /transit/
      AND time >= '{start_interval}'  and time < '{end_interval}' ;
      '''
  try:
      result = client.query(query)
      #print(query)
      t = list(result.get_points(measurement='h_transit_statistics'))
      df = pd.DataFrame(t)
      df = df.fillna(0)
      df["bps"] = df[["bps_in", "bps_out"]].max(axis=1)
      df["bps"] = df["bps"] / 1000000
      #print(df)
      return round(float(df["bps"].values[0]),2)
  except Exception as e:
      return -1
