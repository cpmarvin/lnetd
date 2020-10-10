import sys
import os

import requests
import json
import ipaddress

import functools

sys.path.append("/opt/lnetd/inputs/nornir/")

##nornir
from nornir import InitNornir
from nornir.core.filter import F

##Import and register custom inventory
from lnetd_nornir_inventory import LnetDInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
InventoryPluginRegister.register("LnetDInventory", LnetDInventory)

#Import runner
from nornir.plugins.runners import SerialRunner
from nornir.core.plugins.runners import RunnersPluginRegister
RunnersPluginRegister.register("SerialRunner", SerialRunner)

##Import plugins
from nornir_napalm.plugins.tasks import napalm_get, napalm_configure
from nornir_jinja2.plugins.tasks import template_file

def catch_exception(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            raise Exception("Caug an exception in {} : {}".format(f.__name__, e))

    return func


def prefix_limit_check(prefix):
    prefix = int(prefix)
    if prefix == 0:
        res = 10
    else:
        res = prefix * 1.1
    return int(res)


class peeringdb(object):
    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value, = value
            setattr(self, property, value)
        self.get_peeringdb()

    # @catch_exception

    def get_peeringdb(self):
        ASN = self.asn
        url = "https://peeringdb.com/api/net?asn=" + ASN
        resp = requests.get(url=url)
        if resp.ok:
            pdb_json = json.loads(resp.text)
            description = pdb_json["data"][0]["name"]
            self.description = "PEER::" + description.replace(" ", "-").upper()
            self.ipv4_limit = prefix_limit_check(pdb_json["data"][0]["info_prefixes4"])
            self.ipv6_limit = prefix_limit_check(pdb_json["data"][0]["info_prefixes6"])
            self.ip_version = ipaddress.ip_address(self.ip).version
        else:
            raise ValueError(
                "*** error in peeringdb ***\n this is was the request: \n ***{} \n and response: \n ***{}".format(
                    resp.url, resp.content
                )
            )

    def generate_vars(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("__") and not callable(key)
        }


def basic_template(task, vars):
    # Transform inventory data to configuration via a template file
    print(f"{task.host.platform}")
    r = task.run(
        task=template_file,
        name="Base Configuration",
        template="ix_bgp.j2",
        path=f"/opt/lnetd/web_app/prov_v2/mutils/jinja2_template/{task.host.platform}",
        vars=vars,
    )
    # Save the compiled configuration into a host variable
    task.host["config"] = r.result


def nornir_template(vars, router):
    try:
        nr = InitNornir(
            core = {"raise_on_error":"False"},
            runner={ "plugin": "SerialRunner" },
            logging={"to_console": True, "level": "INFO"},
            inventory={
                "plugin": "LnetDInventory",
                "options": {"lnetd_db": "/opt/lnetd/web_app/database.db"},
            },
        )
        filter_host = nr.filter(name=router)
        vars = peeringdb(**vars)
        result = filter_host.run(task=basic_template, vars=vars.generate_vars())
        return {"result": filter_host.inventory.hosts[router]["config"], "status": "OK"}
    except Exception as e:
        return {"result": str(e), "status": "NOK"}

t = nornir_template('d','r')
print(t)
