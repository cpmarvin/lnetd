import pandas as pd
import sqlite3

def generate_peer_map():
  conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
  sql_bgp_peer = 'SELECT router,neighbour,neighbour_ip from bgp_peers'
  sql_routers = 'SELECT name,ip from Routers'
  # get bgp peers from sql
  df_bgp_peer = pd.read_sql(sql_bgp_peer, conn)
  #df = df.drop(['index'], axis=1)
  # get routers from sql
  df_routers = pd.read_sql(sql_routers, conn)
  # all peers have source icon as router
  df_bgp_peer['src_icon'] = 'router'

  bgp_peer = df_bgp_peer.to_dict(orient='records')

  nested = df_routers.groupby('ip')['name', 'ip'].apply(
      lambda x: x.to_dict(orient='records')).to_dict()

  routers_with_peer_tag = [ router['router'] for router in bgp_peer ]
  routers_list = df_routers['name'].values.tolist()

  bgp_map = []
  for entry in bgp_peer:
    # is it a iBGP peer
    if entry['neighbour_ip'] in nested.keys():
      target = nested[entry['neighbour_ip']][0]['name']
      icon = 'router'
    else:
      target = entry['neighbour']
      icon = 'cloud'
    entry['target'] = target
    entry['tar_icon'] = icon
    bgp_map.append(entry)
    # create reverse only if the target not in routers_with_peer_tag
    if entry['target'] not in routers_with_peer_tag:
        reverse = {'router': entry['target'],
               'target': entry['router'],
               'neighbour_ip': entry['neighbour_ip'],
               'src_icon': 'cloud',
               'tar_icon': 'router'}
        bgp_map.append(reverse)

  df_map = pd.DataFrame(bgp_map)
  # add l_ip/r_ip and the l_ip_r_ip list
  df_map['l_ip'] = df_map['neighbour_ip']
  df_map['r_ip'] = df_map['neighbour_ip']
  df_map.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(
      zip(df_map.l_ip.values.tolist(), df_map.r_ip.values.tolist()))])
  # drop not needed
  df_map = df_map.drop(['neighbour_ip', 'neighbour'], axis=1)
  # change router to
  df_map = df_map.rename(columns={'router': 'source'})
  ibgp_map = df_map[ (df_map['target'].isin(routers_list) ) & ( df_map['source'].isin(routers_list) )]
  return df_map,ibgp_map

