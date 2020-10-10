import json
import time
import logging
import sys
import ipaddress
import datetime
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


def get_lnetd_our_ans():
    """
    Get LnetD ASN configuration
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_config = pd.read_sql("SELECT * FROM App_config", conn)
        return int(df_config["asn"].values[0])
    except:
        return -1


def get_lnetd_bgp_peering_points():
    """
    get LnetD Peering Points
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_links = pd.read_sql("SELECT * FROM Bgp_peering_points", conn)
        df_links = df_links.drop(["index"], axis=1)
        return df_links.to_dict(orient="records")
    except:
        return {}


def get_lnetd_bgp_customers():
    """
    get LnetD BGP customers
    """
    try:
        conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
        df_links = pd.read_sql("SELECT * FROM Bgp_customers", conn)
        df_cst = df_links["ASN"].map(lambda x: x.split()[0])
        return df_cst.unique().tolist()
    except:
        return []


def get_bgp_peers(task):
    deploy = task.run(
        task=napalm_get,
        name="Get BGP peer from device",
        getters=["bgp_neighbors"],
        severity_level=logging.INFO,
    )


print("Start Nornir")
nr = InitNornir(config_file="config.yaml", dry_run=False)
print("Filter devices with tag peering")
all_devices = nr.filter(F(groups__contains="peering"))
# test XR
# all_devices = nr.filter(name='nl-p13-ams')

bgp_neighbours = []

ix_lans = get_lnetd_bgp_peering_points()
ipt_cst = get_lnetd_bgp_customers()
our_asn = get_lnetd_our_ans()
print("our_asn is :", our_asn)

r = all_devices.run(task=get_bgp_peers)

for i in r:
    if i in r.failed_hosts.keys():
        continue
    try:
        for n in r[i][1].result["bgp_neighbors"]["global"]["peers"]:
            work_level = r[i][1].result["bgp_neighbors"]["global"]["peers"][n]
            # print (r[i][1].result['bgp_neighbors']['global']['peers'][n])
            rtr = i
            neighbour = work_level["description"]
            neighbour_ip = n
            neighbour_version = ipaddress.ip_address(neighbour_ip).version
            if ipaddress.ip_address(neighbour_ip).version == 4:
                version = "ipv4"
            else:
                version = "ipv6"
            accepted_prefixes = work_level["address_family"][version][
                "accepted_prefixes"
            ]
            remote_as = work_level["remote_as"]
            is_up = work_level["is_up"]
            uptime = datetime.timedelta(seconds=work_level["uptime"])
            if remote_as == our_asn:
                type = "internal"
                ix_name = "n/a"
            else:
                type = type = get_type(str(remote_as), ipt_cst)
                entry = get_ix_name(neighbour_ip, neighbour_version, ix_lans)
                ix_name = entry["name"]
            bgp_neighbours.append(
                (
                    rtr,
                    neighbour,
                    neighbour_ip,
                    remote_as,
                    is_up,
                    type,
                    accepted_prefixes,
                    ix_name,
                    uptime,
                    neighbour_version,
                )
            )
    except:
        continue

labels = [
    "router",
    "neighbour",
    "neighbour_ip",
    "remote_as",
    "is_up",
    "type",
    "accepted_prefixes",
    "ix_name",
    "uptime",
    "version",
]

df = pd.DataFrame.from_records(bgp_neighbours, columns=labels)
df["uptime"] = df["uptime"].values.astype("timedelta64[m]")
df["uptime"] = df["uptime"].astype(str)
df["uptime"] = df["uptime"].map(lambda x: x[:-10])

print("\nthis is the panda before writing to db\n", df)

disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
df.to_sql("Bgp_peers", disk_engine, if_exists="replace")
