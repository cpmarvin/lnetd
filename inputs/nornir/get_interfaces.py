from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks.networking import netmiko_send_command,napalm_get
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
import pandas as pd
import re
from sqlalchemy import create_engine, text

from mutils_interfaces import get_interfaces_xr,get_interfaces_jnp

# disable warnings
import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

# load the config
print('init Nornir')
nr = InitNornir(config_file="config.yaml")

all_interfaces = []

#filter function
def core_device_jnp(host):                                                          
    return bool(re.search('.',host.name) and (host['type'] == 'juniper')) 

def core_device_xr(host):
    return bool(re.search('.',host.name) and (host['type'] == 'cisco-xr'))

def get_juniper():
    print('getting interfaces for JNP')
    all_juniper = nr.filter(filter_func=core_device_jnp)
    show_juniper_optics = all_juniper.run(task=napalm_get,getters=["optics","interfaces"])

    for i in show_juniper_optics.keys():
        if i not in show_juniper_optics.failed_hosts.keys():
            try:
                all_interfaces.append(get_interfaces_jnp(i,show_juniper_optics[i][0].result))
            except Exception as e:
                pass
    print('failed juniper hosts:\n{}\n'.format(show_juniper_optics.failed_hosts.keys()))


def get_cisco_xr():
    print('getting interfaces for CISCO-XR')
    all_xr = nr.filter(filter_func=core_device_xr)
    show_platform_xr = all_xr.run(task=xr_multiple)
    for i in show_platform_xr.keys():
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                df = get_interfaces_xr(i, show_platform_xr[i][0].result)
                all_interfaces.append(df)
            except Exception as e:
                pass
    print('failed XR hosts:\n{}\n'.format(show_platform_xr.failed_hosts.keys()))


def xr_multiple(task):
    g = task.run(task=netmiko_send_command, command_string=f'show controllers GigabitEthernet *')
    te = task.run(task=netmiko_send_command, command_string=f'show controllers tenGigE *')
    hu = task.run(task=netmiko_send_command, command_string=f'show controllers HundredGigE *')
    return(g.result + te.result + hu.result)


get_cisco_xr()
get_juniper()

try:
    dummy =[
        ['GigabitEthernet0/0/1/0', 'Up', '1Gbps','dummy-p10-lon'], 
        ['GigabitEthernet0/0/1/1', 'Down (Reason: Link loss or low light, no loopback)', '1Gbps','dummy-p10-lon'], 
        ['HundredGigE0/1/0/0', 'Down (Reason: Link loss or low light, no loopback)', '100Gbps','dummy-p10-lon'], 
        ['HundredGigE0/1/0/1', 'Up', '100Gbps','dummy-p10-lon'], 
        ['HundredGigE0/1/0/2', 'Down (Reason: Link loss or low light, no loopback)', '100Gbps','dummy-p10-lon'],
        ['xe-0/0/0','Up','10Gbps','dummy-p8-lon'],
        ['ge-0/0/1','Down (Reason: The optics for the port are not present)','1Gbps','dummy-p8-lon'],
        ['xe-0/0/2','Down (Reason: The optics for the port are not present)','10Gbps','dummy-p8-lon'],
        ['et-0/0/0','Up','100Gbps','dummy-p8-lon'],
        ['et-0/0/1','Up','100Gbps','dummy-p8-lon'],
        ['et-0/0/2','Down (Reason: The optics for the port are not present)','100Gbps','dummy-p8-lon'],
        ]
    labels = ['interface_name', 'interface_status','interface_speed','router_name']
    df = pd.DataFrame(dummy, columns=labels)
    all_interfaces.append(df)
    #end dummy
    df = pd.concat(all_interfaces, ignore_index=True)
    #print(df)
    # write to db here
    disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
    df.to_sql('Inventory_interfaces', disk_engine, if_exists='replace')
except Exception as e:
    print(e)
