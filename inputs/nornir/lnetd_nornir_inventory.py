import os, redis, sqlite3
import pandas as pd
import warnings
from typing import Any, Dict, List, Optional, Union, Type

from nornir.core.inventory import ConnectionOptions
from nornir.core.inventory import Defaults
from nornir.core.inventory import Groups, Group
from nornir.core.inventory import Host
from nornir.core.inventory import HostOrGroup
from nornir.core.inventory import Hosts
from nornir.core.inventory import Inventory, ParentGroups


from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode
import pickle
import ipdb


def update_redis(key_name, data):
    conn = redis.Redis("localhost")
    redis_data = pickle.dumps(data)
    conn.set(key_name, redis_data)
    conn.expire(key_name, 600)


def check_redis(key_name):
    conn = redis.Redis("localhost")
    redis_data = conn.get(key_name)
    # print("this is the redis data", redis_data)
    if redis_data:
        data = pickle.loads(redis_data)
        # print("this is the redis data", data)
        return data
    else:
        return {}


def reverse_password(master_key, password):
    try:
        cipher = b64decode(password)
        plaintext = decrypt(master_key, cipher)
        return str(plaintext, "utf-8")
    except:
        raise ValueError(f"Failed to decrypt password , check if master_key is correct")


def _get_connection_options(data: Dict[str, Any]) -> Dict[str, ConnectionOptions]:
    cp = {}
    for cn, c in data.items():
        cp[cn] = ConnectionOptions(
            hostname=c.get("hostname"),
            port=c.get("port"),
            username=c.get("username"),
            password=c.get("password"),
            platform=c.get("platform"),
            extras=c.get("extras"),
        )
    return cp


def _get_inventory_element(
    typ: Type[HostOrGroup], data: Dict[str, Any], name: str, defaults: Defaults
) -> HostOrGroup:
    return typ(
        name=name,
        hostname=data.get("hostname"),
        port=data.get("port"),
        username=data.get("username"),
        password=data.get("password"),
        platform=data.get("platform"),
        data=data.get("data"),
        groups=data.get(
            "groups"
        ),  # this is a hack, we will convert it later to the correct type via parent group ?!
        defaults=defaults,
        connection_options=_get_connection_options(data.get("connection_options", {})),
    )


def _lnetd_get_groups(lnetd_db):
    conn = sqlite3.connect(lnetd_db)
    sql_groups = "select * from tag join tags on tag.id = tags.tag_id"
    df_groups = pd.read_sql(sql_groups, conn)
    df_groups.replace("", float("NaN"), inplace=True)  # replace empty tags with NaN
    df_groups.dropna(inplace=True)  # drop NaN values
    lnetd_groups = df_groups.to_dict(orient="records")
    groups_initial = {}
    groups = Groups()
    defaults = Defaults()
    for gr in lnetd_groups:
        group: GroupDict = {"data": {}}
        group["data"]["role"] = gr["name"]
        groups_initial[gr["name"]] = group

    for group_name, group_data in groups_initial.items():

        groups[group_name] = _get_inventory_element(
            Group, group_data, group_name, defaults
        )
    return groups, lnetd_groups


def _lnetd_get_hosts(lnetd_db, lnetd_groups):
    hosts = Hosts()
    defaults = Defaults()
    conn = sqlite3.connect(lnetd_db)
    sql_app_config = "select * from App_config"
    df_app_config = pd.read_sql(sql_app_config, conn)
    master_key = df_app_config["master_key"].values[0]
    sql_routers = "select Routers.*,Tacacs.username from Routers join Tacacs on Routers.tacacs_id = Tacacs.id"
    sql_tacacs = "SELECT * FROM Tacacs"
    df_routers = pd.read_sql(sql_routers, conn)
    df_tacacs = pd.read_sql(sql_tacacs, conn)
    print(f"Decrypting password ... this will take a while")
    df_tacacs["password"] = df_tacacs.apply(
        lambda row: reverse_password(master_key, row["password"]), axis=1
    )
    lnetd_devices = df_routers.to_dict(orient="records")
    lnetd_tacacs = df_tacacs.to_dict(orient="records")

    for dev in lnetd_devices:
        tacacs_id = dev["tacacs_id"]
        router_name = dev["name"]
        host: HostsDict = {"data": {}}
        if dev.get("ip", {}):
            host["hostname"] = dev["ip"]
            host["data"]["vendor"] = dev["vendor"]
            host["data"]["type"] = dev["vendor"]
            host["data"]["site"] = dev["country"]
            # host["data"]["model"] = dev["model"]
            host["username"] = dev["username"]
            host["groups"] = []
            if dev["vendor"] == "juniper":
                host["platform"] = "junos"
            elif dev["vendor"] == "cisco-xr":
                host["platform"] = "iosxr"
            elif dev["vendor"] == "huawei":
                host["platform"] = "iosxr"
            else:
                dev["vendor"] == None
            for tacacs in lnetd_tacacs:
                if tacacs["id"] == tacacs_id:
                    host["password"] = tacacs["password"]

            for gr in lnetd_groups:
                if gr["router_name"] == router_name:
                    host["groups"].append(gr["name"])

            hosts[router_name] = _get_inventory_element(
                Host, host, router_name, defaults
            )

    return hosts


class LnetDInventory:
    """
    Inventory plugin that uses `LnetD https://github.com/cpmarvin/lnetd`_ as backend.
    Note:
        Redis Server needs to be enable to cache the user/passwords
    Arguments:
        lnetd_db: LnetD sqlite3 database path

    """

    def __init__(self, lnetd_db: Optional[str] = None) -> None:

        lnetd_db = lnetd_db or "/opt/lnetd/web_app/database.db"
        # print(lnetd_db)

        self.lnetd_db = lnetd_db

    def load(self) -> Inventory:

        hosts = Hosts()
        groups = Groups()
        defaults = Defaults()

        hosts_redis = check_redis("nornir_hosts")
        groups_redis = check_redis("nornir_groups")

        if len(hosts_redis) > 0 and len(groups_redis) > 0:
            print(f"Found cached info in Redis and will used that")
            serialized_groups = groups_redis
            serialized_hosts = hosts_redis

        else:
            serialized_groups, lnetd_groups = _lnetd_get_groups(self.lnetd_db)
            serialized_hosts = _lnetd_get_hosts(self.lnetd_db, lnetd_groups)
            for h in serialized_hosts.values():
                h.groups = ParentGroups([serialized_groups[g] for g in h.groups])

            update_redis("nornir_hosts", serialized_hosts)
            update_redis("nornir_groups", serialized_groups)

        return Inventory(
            hosts=serialized_hosts, groups=serialized_groups, defaults=defaults
        )

