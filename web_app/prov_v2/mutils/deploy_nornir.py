from nornir import InitNornir
from nornir.plugins.tasks import commands
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command, napalm_get, napalm_configure
import logging


def nornir_config(router, config):
    #import ipdb; ipdb.set_trace()
    nr = InitNornir(
        core={"num_workers": 1, "raise_on_error": False},
        logging={"to_console": True, "level": "debug", },
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": "/opt/lnetd/inputs/nornir/inventory/hosts.yaml",
                "group_file": "/opt/lnetd/inputs/nornir/inventory/groups.yaml",
            }})
    host = nr.filter(name=router)
    host.inventory.hosts[router]['config'] = config
    with host as nri:
        host.inventory.hosts[router].open_connection(
            "napalm", configuration=nr.config)
        deploy = host.run(task=napalm_configure,
                          name=f"Loading Configuration on the device {host.inventory.hosts}",
                          replace=False,
                          configuration=host.inventory.hosts[router]['config'],
                          )
        host.inventory.hosts[router].close_connection("napalm")
    return deploy
