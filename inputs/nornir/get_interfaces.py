import logging
import sys
import pandas as pd
from sqlalchemy import create_engine, text

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
from mutils_interfaces import *

# allow dummy
add_dummy = False

all_interfaces = []


def get_juniper():
    print_title("getting interfaces for JNP")
    all_juniper = nr.filter(type="juniper")
    show_juniper_optics = all_juniper.run(
        task=napalm_get, getters=["optics", "interfaces"], severity_level=logging.INFO
    )

    for i in show_juniper_optics.keys():
        if i not in show_juniper_optics.failed_hosts.keys():
            try:
                all_interfaces.append(
                    get_interfaces_jnp(i, show_juniper_optics[i][0].result)
                )
            except Exception as e:
                pass


def get_cisco_xr():
    print("getting interfaces for CISCO-XR")
    all_xr = nr.filter(type="cisco-xr")
    show_platform_xr = all_xr.run(task=xr_multiple, severity_level=logging.INFO)
    for i in show_platform_xr.keys():
        if i not in show_platform_xr.failed_hosts.keys():
            try:
                all_interfaces.append(
                    get_interfaces_xr(i, show_platform_xr[i][0].result)
                )
            except Exception as e:
                pass


def xr_multiple(task):
    g = task.run(
        task=netmiko_send_command, command_string=f"show controllers GigabitEthernet *"
    )
    te = task.run(
        task=netmiko_send_command, command_string=f"show controllers tenGigE *"
    )
    hu = task.run(
        task=netmiko_send_command, command_string=f"show controllers HundredGigE *"
    )
    return g.result + te.result + hu.result


print("Start Nornir")
nr = InitNornir(config_file="config.yaml", dry_run=False)

get_cisco_xr()
get_juniper()

try:
    dummy = [
        ["GigabitEthernet0/0/1/0", "Up", "1Gbps", "dummy-p10-lon"],
        [
            "GigabitEthernet0/0/1/1",
            "Down (Reason: Link loss or low light, no loopback)",
            "1Gbps",
            "dummy-p10-lon",
        ],
        [
            "HundredGigE0/1/0/0",
            "Down (Reason: Link loss or low light, no loopback)",
            "100Gbps",
            "dummy-p10-lon",
        ],
        ["HundredGigE0/1/0/1", "Up", "100Gbps", "dummy-p10-lon"],
        [
            "HundredGigE0/1/0/2",
            "Down (Reason: Link loss or low light, no loopback)",
            "100Gbps",
            "dummy-p10-lon",
        ],
        ["xe-0/0/0", "Up", "10Gbps", "dummy-p8-lon"],
        [
            "ge-0/0/1",
            "Down (Reason: The optics for the port are not present)",
            "1Gbps",
            "dummy-p8-lon",
        ],
        [
            "xe-0/0/2",
            "Down (Reason: The optics for the port are not present)",
            "10Gbps",
            "dummy-p8-lon",
        ],
        ["et-0/0/0", "Up", "100Gbps", "dummy-p8-lon"],
        ["et-0/0/1", "Up", "100Gbps", "dummy-p8-lon"],
        [
            "et-0/0/2",
            "Down (Reason: The optics for the port are not present)",
            "100Gbps",
            "dummy-p8-lon",
        ],
    ]
    labels = ["interface_name", "interface_status", "interface_speed", "router_name"]
    df = pd.DataFrame(dummy, columns=labels)
    if add_dummy:
        all_interfaces.append(df)
    # end dummy
    df = pd.concat(all_interfaces, ignore_index=True)
    print(df)
    disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
    df.to_sql("Inventory_interfaces", disk_engine, if_exists="replace")
except Exception as e:
    print(e)
