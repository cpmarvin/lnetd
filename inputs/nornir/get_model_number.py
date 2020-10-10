import logging

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

# allow dummy
add_dummy = False

if add_dummy:
    insert_routers(
        "Routers",
        98,
        "dummy-p8-lon",
        "10.18.18.18",
        "gb",
        "juniper",
        "MX2008",
        "18.4",
        0,
    )
    insert_routers(
        "Routers",
        99,
        "dummy-p9-lon",
        "10.19.19.19",
        "gb",
        "huawei",
        "NE40E-X8A",
        "8.180",
        0,
    )
    insert_routers(
        "Routers",
        100,
        "dummy-p10-lon",
        "10.20.20.20",
        "gb",
        "cisco-xr",
        "ASR-9922",
        "6.5.3",
        0,
    )

print("Start Nornir")
nr = InitNornir(config_file="config.yaml", dry_run=False)

# filter all cisco-xr devices
all_cisco_xr = nr.filter(type="cisco-xr")
all_cisco_ios = nr.filter(type="cisco-ios")
all_juniper = nr.filter(type="juniper")
all_huawei = nr.filter(type="huawei")


def get_juniper():
    print_title("running show juniper facts")

    show_juniper_facts = all_juniper.run(
        task=napalm_get, getters=["facts"], severity_level=logging.INFO
    )

    for i in show_juniper_facts.keys():
        if i not in show_juniper_facts.failed_hosts.keys():
            try:
                version = show_juniper_facts[i][0].result["facts"]["os_version"]
                model = show_juniper_facts[i][0].result["facts"]["model"].upper()
                update_routers_sqlite3("Routers", i, version, model, "juniper")
            except Exception as e:
                print(e)
                pass


def get_huawei():
    print_title("running show huawei facts")
    # commands = ['NO','display version | incl VRP|HUAWEI']
    show_huawei_facts = all_huawei.run(
        task=netmiko_send_command,
        command_string="display version | incl VRP|HUAWEI",
        severity_level=logging.INFO,
    )
    # show_huawei_facts = all_huawei.run(task=netmiko_send_command,command_string=commands)
    for i in show_huawei_facts.keys():
        if i not in show_huawei_facts.failed_hosts.keys():
            try:
                version, model = huawei_parse_show_version(show_huawei_facts[i].result)
                update_routers_sqlite3("Routers", i, version, model, "huawei")
            except Exception as e:
                pass


def get_cisco_xr():
    print_title("running show cisco XR facts")
    show_facts = all_cisco_xr.run(
        task=napalm_get, getters=["facts"], severity_level=logging.INFO
    )
    for i in show_facts.keys():
        if i not in show_facts.failed_hosts.keys():
            try:
                version = show_facts[i][0].result["facts"]["os_version"]
                model = show_facts[i][0].result["facts"]["model"].upper()
                update_routers_sqlite3("Routers", i, version, model, "cisco-xr")
            except Exception as e:
                pass


def get_cisco_ios():
    print_title("running show cisco IOS facts")
    show_ios_facts = all_cisco_ios.run(
        task=napalm_get, getters=["facts"], severity_level=logging.INFO
    )
    for i in show_ios_facts.keys():
        if i not in show_ios_facts.failed_hosts.keys():
            try:
                version = show_ios_facts[i][0].result["facts"]["os_version"]
                version = version.split("Version")[1].split(",")[0].strip()
                model = show_ios_facts[i][0].result["facts"]["model"]
                update_routers_sqlite3("Routers", i, version, model, "cisco-ios")
            except Exception as e:
                pass


def collect_xr_multiple(task):
    task.run(
        task=netmiko_send_command, command_string=f"show inventory", use_genie=True
    )
    task.run(task=netmiko_send_command, command_string=f"show version", use_genie=True)


def get_cisco_xr_genie():
    print_title("Find XR model and version using Genie")

    show_facts = all_cisco_xr.run(
        task=collect_xr_multiple, on_failed=True, severity_level=logging.INFO
    )
    for i in show_facts.keys():
        if i not in show_facts.failed_hosts.keys():
            try:
                version = show_facts[i][2].result["software_version"]
                model = show_facts[i][1].result["module_name"]["Rack 0"]["pid"]
                update_routers_sqlite3("Routers", i, version, model, "cisco-xr")
            except Exception as e:
                pass


get_huawei()
get_cisco_ios()
get_cisco_xr()
get_cisco_xr_genie()
get_juniper()
