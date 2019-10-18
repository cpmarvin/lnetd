from nornir import InitNornir
from nornir.plugins.tasks.networking import (
    netmiko_send_command,
    napalm_get,
    napalm_configure,
)
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import commands
import logging
import sys

#
from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine, text

#
def netflow_configuration(task, progress_bar):
    deploy = task.run(
        task=napalm_get,
        name="Get BGP config from device",
        getters=["get_bgp_config"],
        severity_level=logging.DEBUG,
    )
    tqdm.write(f"{task.host}: BGP config from device complete")
    progress_bar.update()


def process_tasks(task):
    if task.failed:
        print_result(task)
        print("Exiting script before we break anything else!")
        sys.exit(1)
    else:
        print(f"Task {task.name} completed successfully!")


nr = InitNornir(config_file="config.yaml", dry_run=False)

all_devices = nr.filter(type="juniper")

with tqdm(
    total=len(all_devices.inventory.hosts), desc="Get BGP Config"
) as progress_bar:
    deploy_netflow_config = all_devices.run(
        task=netflow_configuration, progress_bar=progress_bar
    )

process_tasks(deploy_netflow_config)
# print_result(deploy_netflow_config)
# import ipdb; ipdb.set_trace()
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
print(f"Write to db")
disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
df.to_sql("bgp_groups", disk_engine, if_exists="replace")
