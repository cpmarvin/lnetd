import sys
import logging
import jinja2
import sqlite3

import pandas as pd

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s (%(lineno)s) - %(levelname)s: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("INFO")

logger.info("Open jinja2 template")

try:
    conn = sqlite3.connect("/opt/lnetd/web_app/database.db")
    sql = "SELECT * FROM Routers"
    df_routers = pd.read_sql(sql, conn)
    lnetd_devices = df_routers.to_dict(orient="records")
except Exception as e:
    logger.error("Failed to query database for existing routers... exiting now")
    sys.exit()

for device in lnetd_devices:
    template_snmp = jinja2.Template(open("template_snmp_conf.js").read())
    template_if_address = jinja2.Template(
        open("template_snmp_if_address_conf.js").read()
    )

    logger.info("Generate Telegraf configuration for : %s" % (device["name"]))
    rendered_snmp = template_snmp.stream(host=device["ip"]).dump(
        f'/etc/telegraf/telegraf.d/{device["name"]}_snmp.conf'
    )
    rendered_if_address = template_if_address.stream(host=device["ip"]).dump(
        f'/etc/telegraf/telegraf.d/{device["name"]}_if_address.conf'
    )
