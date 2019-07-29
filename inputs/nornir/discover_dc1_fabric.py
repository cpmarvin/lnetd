from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, napalm_get
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import commands

import json 
import logging
from tqdm import tqdm
import sys
import pandas as pd
from sqlalchemy import create_engine,text

sys.path.append('../utils/')

import snmp_get 

lnetd_dc= []
def cumulus_lldp(data_str,source):
    data = json.loads(data_str)
    if 'interface' in data['lldp'][0].keys():
        for d in data['lldp'][0]['interface']:
            entry = dict()
            entry['source'] = source
            entry['l_ip'] = d['name']
            entry['target'] = d['chassis'][0]['name'][0]['value']
            entry['r_ip'] = d['port'][0]['id'][0]['value']
            entry['metric'] = 1
            lnetd_dc.insert(0,entry)
    return True

def process_tasks(task):
    if task.failed:
        print_result(task)
        print("Exiting script before we break anything else!")
        sys.exit(1)
    else:
        print_title('Processing results')
        for host in dc1.inventory.hosts:
            host_lldp = cumulus_lldp(dc1.inventory.hosts[host]['lldp'],host)
        print(f"Task {task.name} completed successfully!")

def check_lldp_neigh(task,progress_bar):
    r = task.run(name=f'Discover lldp neigh on host: {task.host.hostname}',
		 task=netmiko_send_command,
		 command_string="net show lldp json",
		 severity_level=logging.DEBUG)
    progress_bar.update()
    tqdm.write(f"{task.host}: LLDP discovery complete")
    task.host['lldp'] = r.result


print_title('init Nornir')

nr = InitNornir(config_file="config.yaml",
		logging={"level": "info","to_console":"False"})

dc1 = nr.filter(site='dc1')

print_title('Run LLDP Discovery for DC1 fabric')

with tqdm(total=len(dc1.inventory.hosts), desc="LLDP discovery",) as progress_bar:
    r_lldp = dc1.run(task=check_lldp_neigh,progress_bar=progress_bar)

process_tasks(r_lldp)
print_title('Generate panda dataframe from LLDP neighbours')
df_lnetd = pd.DataFrame(lnetd_dc)
print_title('Resulting dataframe ')
print(df_lnetd)

print_title('Dataframe enrich with snmp data')
df_lnetd['l_int'] = df_lnetd['l_ip']
df_lnetd['util'] = df_lnetd.apply(lambda row: snmp_get.get_util_ifName(row['source'],row['l_int'],0),axis=1)
df_lnetd['capacity'] = df_lnetd.apply(lambda row: snmp_get.get_capacity_ifName(row['source'],row['l_int']),axis=1)
df_lnetd.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(zip(df_lnetd.l_ip.values.tolist(), df_lnetd.r_ip.values.tolist()))])
#df_lnetd['errors'] = df_lnetd.apply(lambda row: snmp_get.get_errors_ifIndex(row['source'],row['l_int'],0),axis=1)
df_lnetd['errors'] = '0'
df_lnetd['l_ip_r_ip'] = df_lnetd['l_ip_r_ip'].astype(str)
print(df_lnetd)
print_title('Update LnetD')
try:
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df_lnetd.to_sql('Fabric_links', disk_engine, if_exists='replace')
    print_title('All done , check web app at http://x.x.x.x:8801/dc/fabric')
except Exception as e:
    print(f'Something went wrong when inserting data into sqlite:\n {e}')
