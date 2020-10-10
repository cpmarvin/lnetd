import os
import pandas as pd
import sqlite3
from typing import Any, Dict, List, Optional, Union

from nornir.core.deserializer.inventory import Inventory, HostsDict


import requests

from simplecrypt import encrypt, decrypt
from base64 import b64encode, b64decode
import redis, pickle, sys


def update_redis(key_name, data):
    conn = redis.Redis("localhost")
    redis_data = pickle.dumps(data)
    conn.set(key_name, redis_data)
    conn.expire(key_name, 600)


def check_redis(key_name):
    conn = redis.Redis("localhost")
    redis_data = conn.get(key_name)
    if redis_data:
        data = pickle.loads(redis_data)
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


class LnetDInventory(Inventory):
    def __init__(self, lnetd_db: Optional[str] = None, **kwargs: Any) -> None:
        hosts_redis = check_redis("nornir_hosts")
        groups_redis = check_redis("nornir_groups")
        if len(hosts_redis) > 1 and len(groups_redis) > 1:
            print(f"Found cached info in Redis and will used that")
            super().__init__(
                hosts=hosts_redis, groups=groups_redis, defaults={}, **kwargs
            )
        else:
            try:
                conn = sqlite3.connect(lnetd_db)
                sql_groups = "select * from tag join tags on tag.id = tags.tag_id"
                df_groups = pd.read_sql(sql_groups, conn)
                lnetd_groups = df_groups.to_dict(orient="records")
                #print(df_groups, lnetd_groups)
                groups = {}
                for gr in lnetd_groups:
                    group: GroupDict = {"data": {}}
                    group["data"]["role"] = gr["name"]
                    # Assign temporary dict to outer dict
                    groups[gr["name"]] = group
                #print(groups)
                # sys.exit()
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
                print(f"All done")
                lnetd_devices = df_routers.to_dict(orient="records")
                lnetd_tacacs = df_tacacs.to_dict(orient="records")
                hosts = {}
                for d in lnetd_devices:
                    tacacs_id = d["tacacs_id"]
                    router_name = d["name"]
                    host: HostsDict = {"data": {}}
                    if d.get("ip", {}):
                        host["hostname"] = d["ip"]
                    host["data"]["vendor"] = d["vendor"]
                    host["data"]["type"] = d["vendor"]
                    host["data"]["site"] = d["country"]
                    host["data"]["model"] = d["model"]
                    host["username"] = d["username"]
                    host["groups"] = []
                    # Add platform , need to do this better
                    if d["vendor"] == "juniper":
                        host["platform"] = "junos"
                    elif d["vendor"] == "cisco-xr":
                        host["platform"] = "iosxr"
                    elif d["vendor"] == "huawei":
                        host["platform"] = "iosxr"
                    else:
                        d["vendor"] == None

                    for t in lnetd_tacacs:
                        if t["id"] == tacacs_id:
                            host["password"] = t["password"]
                    for gr in lnetd_groups:
                        if gr["router_name"] == router_name:
                            host["groups"].append(gr["name"])

                    # Assign temporary dict to outer dict
                    hosts[d["name"]] = host
                #print(hosts)
                # update redis
                update_redis("nornir_hosts", hosts)
                update_redis("nornir_groups", groups)
                # Pass the data back to the parent class
                super().__init__(hosts=hosts, groups=groups, defaults={}, **kwargs)
            except Exception:
                raise ValueError(
                    f"Failed to get devices from LnetD database {lnetd_db}"
                )
