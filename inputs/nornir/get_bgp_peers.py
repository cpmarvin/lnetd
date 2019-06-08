from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, napalm_get
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import commands

import pandas as pd
from sqlalchemy import create_engine, text
import ipaddress
from mutils import *
import datetime

print('init Nornir')
nr = InitNornir(config_file="config.yaml")
#all_devices = nr
all_devices = nr.filter(role='peering')

#get all peering points
def get_lnetd_bgp_peering_points():
    # get links into panda filter by core only devices
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    df_links = pd.read_sql("SELECT * FROM Bgp_peering_points", conn)
    df_links = df_links.drop(['index'], axis=1)
    return df_links.to_dict(orient='records')

#get all customers ASN
def get_lnetd_bgp_customers():
    # get links into panda filter by core only devices
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    df_links = pd.read_sql("SELECT * FROM Bgp_customers", conn)
    df_cst = df_links['ASN'].map(lambda x: x.split()[0])
    return df_cst.unique().tolist()

def get_lnetd_our_ans():
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    df_config = pd.read_sql("SELECT * FROM App_config", conn)
    return int(df_config['asn'].values[0])

ix_lans = get_lnetd_bgp_peering_points()
ipt_cst = get_lnetd_bgp_customers()
our_asn = get_lnetd_our_ans()
print('our_asn is :',our_asn)

def check_bgp_table(task):
    r = task.run(task=napalm_get, getters=["bgp_neighbors"])
    # print_result(r)


r = all_devices.run(task=check_bgp_table)
print('failed bgp hosts:\n{}\n'.format(r.failed_hosts.keys()))
for i in r.failed_hosts.keys():
    print('HOSTNAME:{}|ERROR:{}'.format(i, r[i][1].result))

bgp_neighbours = []

for i in r:
    if i in r.failed_hosts.keys():
        continue
    for n in r[i][1].result['bgp_neighbors']['global']['peers']:
        work_level = r[i][1].result['bgp_neighbors']['global']['peers'][n]
        #print (r[i][1].result['bgp_neighbors']['global']['peers'][n])
        rtr = i
        neighbour = work_level['description']
        neighbour_ip = n
        neighbour_version = ipaddress.ip_address(neighbour_ip).version
        if ipaddress.ip_address(neighbour_ip).version == 4:
            version = 'ipv4'
        else:
            version = 'ipv6'
        accepted_prefixes = work_level['address_family'][version]['accepted_prefixes']
        remote_as = work_level['remote_as']
        is_up = work_level['is_up']
        uptime = datetime.timedelta(seconds=work_level['uptime'])
        if remote_as == our_asn:
            type = 'internal'
            ix_name = 'n/a'
        else:
            type = type = get_type(str(remote_as),ipt_cst)
            entry = get_ix_name(neighbour_ip, neighbour_version,ix_lans)
            ix_name = entry['name']
        bgp_neighbours.append((rtr, neighbour, neighbour_ip, remote_as,
				is_up, type, accepted_prefixes,
				ix_name,uptime))

labels = ['router', 'neighbour', 'neighbour_ip',
          'remote_as', 'is_up', 'type',
          'accepted_prefixes', 'ix_name', 'uptime']

df = pd.DataFrame.from_records(bgp_neighbours, columns=labels)
df['uptime'] = df['uptime'].values.astype("timedelta64[m]")
df['uptime'] = df['uptime'].astype(str)
df['uptime'] = df['uptime'].map(lambda x: x[:-10])
print(df.head(10))

disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
df.to_sql('Bgp_peers', disk_engine, if_exists='replace')
