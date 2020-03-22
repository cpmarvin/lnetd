from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
import pandas as pd
import re

from sqlalchemy import create_engine, text

from mutils import get_cards_jnp, get_cards_xr, get_cards_huawei

# disable warnings
import warnings

warnings.filterwarnings(action="ignore", module=".*paramiko.*")

# fix ntc-templates
import os

os.environ["NET_TEXTFSM"] = "/opt/lnetd/inputs/nornir/ntc-templates/"

# allow dummy
add_dummy = True

# filter function
def core_device_jnp(host):
    return bool(re.search(".", host.name) and (host["type"] == "juniper"))


def core_device_xr(host):
    return bool(re.search(".", host.name) and (host["type"] == "cisco-xr"))


def core_device_huawei(host):
    return bool(re.search(".", host.name) and (host["type"] == "huawei"))


# load the config
print("init Nornir")
nr = InitNornir(config_file="config.yaml")

all_cards = []


def get_juniper():
    print("running show juniper facts")
    all_juniper = nr.filter(filter_func=core_device_jnp)
    show_juniper_facts = all_juniper.run(task=get_cards_jnp)

    for i in show_juniper_facts.keys():
        if i not in show_juniper_facts.failed_hosts.keys():
            try:
                all_cards.append(show_juniper_facts[i][0].result)
            except Exception as e:
                pass
    print("failed juniper hosts:\n{}\n".format(show_juniper_facts.failed_hosts.keys()))


def get_cisco_xr():
    print("runing show platform XR")
    all_xr = nr.filter(filter_func=core_device_xr)
    show_platform_xr = all_xr.run(
        task=netmiko_send_command,
        command_string=f"admin show platform",
        use_textfsm=True,
    )
    # print(show_platform_xr)
    for i in show_platform_xr.keys():
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                # print(show_platform_xr[i][0].result)
                df = get_cards_xr(i, show_platform_xr[i][0].result)
                # print(df)
                all_cards.append(df)
            except Exception as e:
                pass
    print("failed XR hosts:\n{}\n".format(show_platform_xr.failed_hosts.keys()))


def huawei_multiple(task):
    temp = task.run(
        task=netmiko_send_command, command_string="screen-length 0 temporary"
    )
    r = task.run(task=netmiko_send_command, command_string=f"display version")
    p = task.run(task=netmiko_send_command, command_string="display device pic-status")
    # pow = task.run(task=netmiko_send_command, command_string='display power')
    # print(r.result)
    # print(p.result)
    return r.result + p.result


def get_huawei():
    print("runing display version and display device pic-status")
    all_xr = nr.filter(filter_func=core_device_huawei)
    # all_xr = nr.filter(name='acc1.pru.lon')
    show_platform_xr = all_xr.run(task=huawei_multiple)
    print_result(show_platform_xr)
    for i in show_platform_xr.keys():
        print("i in show plat", i)
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                print(show_platform_xr[i][0].result)
                # df = get_cards_huawei(i,show_platform_xr[i][0].result)
                df = get_cards_huawei(show_platform_xr[i][0].result)
                df["router_name"] = i
                print(df)
                all_cards.append(df)
                # print('this is the all_jnp_cards inside xr',all_jnp_cards)
            except Exception as e:
                print(e)
                pass
    print("failed huawei hosts:\n{}\n".format(show_platform_xr.failed_hosts.keys()))


get_cisco_xr()
get_juniper()
get_huawei()

try:
    # dummy data
    dummy = [
        ["0/RP0/CPU0", "A99-RSP-SE(Active)", "IOS", "dummy-p10-lon"],
        ["0/RP1/CPU0", "A99-RSP-SE(Standby)", "IOS", "dummy-p10-lon"],
        ["0/0/CPU0", "A9K-2x100GE-TR", "IOS", "dummy-p10-lon"],
        ["0/2/CPU0", "A9K-36x10GE-TR", "IOS", "dummy-p10-lon"],
        ["0/3/CPU0", "A9K-2x100GE-TR", "IOS", "dummy-p10-lon"],
        ["0/4/CPU0", "A9K-8X100GE-L-SE", "IOS", "dummy-p10-lon"],
        ["0/6/CPU0", "A9K-8X100GE-L-SE", "IOS", "dummy-p10-lon"],
        ["0/10/CPU0", "A9K-8X100GE-L-SE", "IOS", "dummy-p10-lon"],
        ["0/11/CPU0", "A9K-8X100GE-L-SE", "IOS", "dummy-p10-lon"],
        ["1/0", "LPU 1", "online", "dummy-p9-lon"],
        ["1/0", "ETH_2x100GC_T_CARD", "online", "dummy-p9-lon"],
        ["2/0", "LPU 2", "online", "dummy-p9-lon"],
        ["2/0", "LAN_WAN_5x10GF_B_CARD", "online", "dummy-p9-lon"],
        ["6/0", "LPU 6", "online", "dummy-p9-lon"],
        ["6/0", "ETH_1x100GC_B_CARD", "online", "dummy-p9-lon"],
        ["9/0", "MPU(Master) 9", "online", "dummy-p9-lon"],
        ["10/0", "MPU(Master) 10", "online", "dummy-p9-lon"],
        ["FPC 0", "MPC7E 3D 40XGE", "online", "dummy-p8-lon"],
        ["PIC 0", "20x10GE SFPP", "online", "dummy-p8-lon"],
        ["PIC 1", "MIC-3D-8OC3OC12-4OC48", "online", "dummy-p8-lon"],
        ["FPC 7", "MPC7E 3D 40XGE", "online", "dummy-p8-lon"],
        ["PIC 0", "20x10GE SFPP", "online", "dummy-p8-lon"],
        ["PIC 1", "MIC-3D-8OC3OC12-4OC48", "online", "dummy-p8-lon"],
        ["Routing Engine 0", "RE-MX2008-X8-64G", "online", "dummy-p8-lon"],
        ["Routing Engine 1", "RE-MX2008-X8-64G", "online", "dummy-p8-lon"],
    ]
    labels = ["card_slot", "card_name", "card_status", "router_name"]
    df = pd.DataFrame(dummy, columns=labels)
    if add_dummy:
        all_cards.append(df)
    ##end dummy
    df = pd.concat(all_cards, ignore_index=True)
    print(df)
    # write to db here
    disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
    df.to_sql("Inventory_cards", disk_engine, if_exists="replace")
except Exception as e:
    print(e)
