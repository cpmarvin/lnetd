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

# custom
from mutils import *


def netflow_configuration(task):
    deploy = task.run(
        task=napalm_get,
        name="Get BGP config from device",
        getters=["get_bgp_config"],
        severity_level=logging.INFO,
    )


print("Start Nornir")
nr = InitNornir(config_file="config.yaml", dry_run=False)
print("Filter devices with tag peering")
all_devices = nr.filter(F(groups__contains="peering"))


deploy_netflow_config = all_devices.run(task=netflow_configuration)


def parse_bgp_config(nornir_object):
    bgp_groups = []
    for host, host_data in nornir_object.items():
        if host not in nornir_object.failed_hosts:
            root = dict(host_data[1].result)
            for group in root["get_bgp_config"]:
                entry = {"group": group, "router": host}
                bgp_groups.insert(1, entry)
    return bgp_groups


result_nornir = parse_bgp_config(deploy_netflow_config)
df = pd.DataFrame(result_nornir)
# need to remove type internal
result = df.groupby("router")["group"].apply(list).to_dict()
print("\nthis is the panda before writing to db\n", df)
disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
df.to_sql("bgp_groups", disk_engine, if_exists="replace")
