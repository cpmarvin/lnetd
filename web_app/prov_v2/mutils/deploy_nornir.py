import logging, sys

sys.path.append("/opt/lnetd/inputs/nornir/")

##nornir
from nornir import InitNornir
from nornir.core.filter import F

##Import and register custom inventory
from lnetd_nornir_inventory import LnetDInventory
from nornir.core.plugins.inventory import InventoryPluginRegister

InventoryPluginRegister.register("LnetDInventory", LnetDInventory)

##Import plugins
from nornir_napalm.plugins.tasks import napalm_get, napalm_configure


def nornir_config(router, config):
    nr = InitNornir(
        core={"raise_on_error": "False"},
        runner={"plugin": "SerialRunner"},
        logging={"to_console": True, "level": "INFO"},
        inventory={
            "plugin": "LnetDInventory",
            "options": {"lnetd_db": "/opt/lnetd/web_app/database.db"},
        },
    )

    host = nr.filter(name=router)
    host.inventory.hosts[router]["config"] = config
    with host as nri:
        host.inventory.hosts[router].open_connection("napalm", configuration=nr.config)
        deploy = host.run(
            task=napalm_configure,
            name=f"Loading Configuration on the device {host.inventory.hosts}",
            replace=False,
            configuration=host.inventory.hosts[router]["config"],
        )
        host.inventory.hosts[router].close_connection("napalm")
    return deploy
