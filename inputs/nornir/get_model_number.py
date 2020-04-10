from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result

from mutils import update_routers_sqlite3, insert_routers

# disable warnings
import warnings

warnings.filterwarnings(action="ignore", module=".*paramiko.*")

from tqdm import tqdm

# allow dummy
add_dummy = True

if add_dummy:
    insert_routers('Routers',98,'dummy-p8-lon','10.18.18.18','gb','juniper','MX2008','18.4',0)
    insert_routers('Routers',99,'dummy-p9-lon','10.19.19.19','gb','huawei','NE40E-X8A','8.180',0)
    insert_routers('Routers',100,'dummy-p10-lon','10.20.20.20','gb','cisco-xr','ASR-9922','6.5.3',0)
import sys
sys.exit()
# load the config
print("init Nornir")
nr = InitNornir(config_file="config.yaml")

# filter all cisco-xr devices
all_cisco_xr = nr.filter(type="cisco-xr")
all_cisco_ios = nr.filter(type="cisco-ios")
all_juniper = nr.filter(type="juniper")
all_huawei = nr.filter(type="huawei")


def _napalm_get(task, progress_bar):
    r = task.run(networking.napalm_get, getters=["facts"])
    progress_bar.update()
    tqdm.write(f"{task.host}: Napalm Model discovery complete")


def get_juniper():
    print("running show juniper facts")
    with tqdm(
        total=len(all_juniper.inventory.hosts),
        desc="Get Model Number for Juniper using Napalm",
    ) as progress_bar:
        show_juniper_facts = all_juniper.run(
            task=_napalm_get, progress_bar=progress_bar
        )

    for i in show_juniper_facts.keys():
        if i not in show_juniper_facts.failed_hosts.keys():
            try:
                version = show_juniper_facts[i][0].result["facts"]["os_version"]
                model = show_juniper_facts[i][0].result["facts"]["model"].upper()
                update_routers_sqlite3("Routers", i, version, model, "juniper")
            except Exception as e:
                pass
        else:
            print(
                "failed juniper hosts:\n{}\n".format(
                    show_juniper_facts.failed_hosts.keys()
                )
            )


def get_huawei():
    print("running show huawei facts")
    # commands = ['NO','display version | incl VRP|HUAWEI']
    show_huawei_facts = all_huawei.run(
        task=netmiko_send_command, command_string="display version | incl VRP|HUAWEI"
    )
    # show_huawei_facts = all_huawei.run(task=netmiko_send_command,command_string=commands)
    print("process show facts huawei")
    for i in show_huawei_facts.keys():
        if i not in show_huawei_facts.failed_hosts.keys():
            try:
                version, model = huawei_parse_show_version(show_huawei_facts[i].result)
                update_routers_sqlite3("Routers", i, version, model, "huawei")
            except Exception as e:
                pass
        else:
            print(
                "failed huawei hosts:\n{}\n".format(
                    show_huawei_facts.failed_hosts.keys()
                )
            )


def get_cisco_xr():
    print("running show cisco XR facts")
    show_facts = all_cisco_xr.run(task=networking.napalm_get, getters=["facts"])
    print("process show facts cisco XR")

    for i in show_facts.keys():
        if i not in show_facts.failed_hosts.keys():
            try:
                version = show_facts[i][0].result["facts"]["os_version"]
                model = show_facts[i][0].result["facts"]["model"].upper()
                update_routers_sqlite3("Routers", i, version, model, "cisco-xr")
            except Exception as e:
                pass
        else:
            print("failed XR hosts:\n{}\n".format(show_facts.failed_hosts.keys()))


def get_cisco_ios():
    print("running show cisco IOS facts")
    show_ios_facts = all_cisco_ios.run(task=networking.napalm_get, getters=["facts"])

    print("process show facts cisco IOS")

    for i in show_ios_facts.keys():
        if i not in show_ios_facts.failed_hosts.keys():
            try:
                version = show_ios_facts[i][0].result["facts"]["os_version"]
                version = version.split("Version")[1].split(",")[0].strip()
                model = show_ios_facts[i][0].result["facts"]["model"]
                update_routers_sqlite3("Routers", i, version, model, "cisco-ios")
            except Exception as e:
                pass
        else:
            print("failed IOS hosts:\n{}\n".format(show_ios_facts.failed_hosts.keys()))


def collect_xr_multiple(task, progress_bar):
    task.run(
        task=netmiko_send_command, command_string=f"show inventory", use_genie=True
    )
    task.run(task=netmiko_send_command, command_string=f"show version", use_genie=True)
    progress_bar.update()
    tqdm.write(f"{task.host}: Model number  discovery complete")


def get_cisco_xr_genie():
    print("Find XR model and version using Genie")
    with tqdm(
        total=len(all_cisco_xr.inventory.hosts),
        desc="Get Model Number for XR using Genie parser",
    ) as progress_bar:
        show_facts = all_cisco_xr.run(
            task=collect_xr_multiple, progress_bar=progress_bar, on_failed=True
        )
    for i in show_facts.keys():
        if i not in show_facts.failed_hosts.keys():
            try:
                version = show_facts[i][2].result["software_version"]
                model = show_facts[i][1].result["module_name"]["Rack 0"]["pid"]
                update_routers_sqlite3("Routers", i, version, model, "cisco-xr")
            except Exception as e:
                pass
        else:
            print(
                "failed XR with Genie hosts:\n{}\n".format(
                    show_facts.failed_hosts.keys()
                )
            )


get_huawei()
get_cisco_ios()
get_cisco_xr()
get_cisco_xr_genie()
get_juniper()
