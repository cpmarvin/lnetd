import logging
import sys
import pandas as pd
from sqlalchemy import create_engine, text
import re

##nornir
from nornir import InitNornir
from nornir.core.filter import F

##Import and register custom runner
from nornir.core.plugins.runners import RunnersPluginRegister
from custom_runners import (
    runner_as_completed,
    runner_as_completed_tqdm,
    runner_as_completed_rich,
)

RunnersPluginRegister.register("my_runner", runner_as_completed_rich)
# RunnersPluginRegister.register("my_runner", runner_as_completed_tqdm)
# RunnersPluginRegister.register("my_runner", runner_as_completed)
##Import and register custom inventory
from lnetd_nornir_inventory import LnetDInventory
from nornir.core.plugins.inventory import InventoryPluginRegister

InventoryPluginRegister.register("LnetDInventory", LnetDInventory)

##Import plugins
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko import netmiko_send_command
from nornir_utils.plugins.functions import print_title

# custom
from mutils import *

# disable warnings
import warnings

warnings.filterwarnings(action="ignore", module=".*paramiko.*")

# fix ntc-templates
import os

os.environ["NET_TEXTFSM"] = "/opt/lnetd/inputs/nornir/ntc-templates/"

# allow dummy
add_dummy = False

# load the config
print("init Nornir")
nr = InitNornir(config_file="config.yaml")

all_cards = []


def get_juniper():
    print_title("running show juniper facts")
    all_juniper = nr.filter(type="juniper")
    show_juniper_facts = all_juniper.run(
        task=get_cards_jnp, severity_level=logging.INFO
    )

    for i in show_juniper_facts.keys():
        if i not in show_juniper_facts.failed_hosts.keys():
            try:
                all_cards.append(show_juniper_facts[i][0].result)
            except Exception as e:
                pass


def get_cisco_xr():
    print_title("runing show platform XR")
    all_xr = nr.filter(type="cisco-xr")
    show_platform_xr = all_xr.run(
        task=netmiko_send_command,
        command_string=f"admin show platform",
        use_textfsm=True,
        severity_level=logging.INFO,
    )
    # print(show_platform_xr)
    for i in show_platform_xr.keys():
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                all_cards.append(get_cards_xr(i, show_platform_xr[i][0].result))
            except Exception as e:
                pass


def huawei_multiple(task):
    temp = task.run(
        task=netmiko_send_command, command_string="screen-length 0 temporary"
    )
    r = task.run(task=netmiko_send_command, command_string=f"display version")
    p = task.run(task=netmiko_send_command, command_string="display device pic-status")
    return r.result + p.result


def get_huawei():
    print_title("runing display version and display device pic-status")
    all_xr = nr.filter(type="huawei")
    show_platform_xr = all_xr.run(task=huawei_multiple)
    for i in show_platform_xr.keys():
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                df = get_cards_huawei(show_platform_xr[i][0].result)
                df["router_name"] = i
                all_cards.append(df)
            except Exception as e:
                print(e)
                pass


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
