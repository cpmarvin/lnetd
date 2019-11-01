import sys

sys.dont_write_bytecode = True

from lxml import etree, objectify
from ncclient import manager
from ncclient.xml_ import *
from decode_lsp import *
from mutils import *
import pandas as pd
from sqlalchemy import create_engine

pd.options.mode.chained_assignment = None


# get router names first
print("Get Nokia ISIS Hostname via Netconf")
xml_req = xml_request_router_name("isis")
xml_state = get_netconf(xml_req)
print("Parse XML for ISIS Hostname")
routers_name_mapping = parse_xml_router_name(xml_state)


# get isis database from the router
print("Get Nokia ISIS Database via Netconf")
xml_req = xml_request("isis")
xml_state = get_netconf(xml_req)
isis_db = parse_xml(xml_state)
DUMMY_NR = 3

print("Decode ISIS binary lsp from netconf message")
lnetd_links = []

for entry in isis_db:
    lsp_dict = parseIsisMsg(DUMMY_NR, entry["lsp_encode"])
    tlv_22_root = lsp_dict["V"]["VFIELDS"][22]
    tlv_key_nr = len(tlv_22_root)
    tlv_key = 0
    while tlv_key < tlv_key_nr:
        tlv_key_str = 'TLV22-' + str(tlv_key)
        tlv_22_lsp_id = tlv_22_root[tlv_key][tlv_key_str][0]["lsp_id"]
        tlv_22_l_ip = tlv_22_root[tlv_key][tlv_key_str][0]["l_ip"]
        tlv_22_r_ip = tlv_22_root[tlv_key][tlv_key_str][0]["r_ip"]
        tlv_22_metric = tlv_22_root[tlv_key][tlv_key_str][0]["metric"]
        tlv_134_router_id = lsp_dict["V"]["VFIELDS"][134][0]["V"][0]
        tlv_137_router_name = lsp_dict["V"]["VFIELDS"][137][0]["V"][0].decode("utf-8")
        lnet_entry = {
            "source": tlv_137_router_name,
            "source_router_ip": id2str(tlv_134_router_id),
            "target": hex2isisd(tlv_22_lsp_id),
            "l_ip": id2str(tlv_22_l_ip),
            "r_ip": id2str(tlv_22_r_ip),
            "metric": str2dec(tlv_22_metric),
        }
        lnetd_links.insert(0, lnet_entry)

        print(
            f"""Decode LSP :
               source: {tlv_137_router_name},
               source_router_ip:{id2str(tlv_134_router_id)},
               target: {hex2isisd(tlv_22_lsp_id)},
               l_ip: {id2str(tlv_22_l_ip)},
               r_ip: {id2str(tlv_22_r_ip)},
               metric: {str2dec(tlv_22_metric)}"""
        )
        tlv_key = tlv_key + 1


labels = ["source", "source_router_ip", "target", "l_ip", "r_ip", "metric"]
df = pd.DataFrame.from_records(lnetd_links, columns=labels)
# replace target ( sys_id ) with router name
df["target"] = df.apply(lambda row: routers_name_mapping[row["target"]], axis=1)


# create rpc_routers and write to lnetd
print("\nGenerate LnetD routers info and write to db\n")
df_routers = df[["source", "source_router_ip"]]
df_routers.columns = ["name", "ip"]
df_routers.loc[:, "country"] = df_routers["name"].str[0:2]
df_routers = df_routers.drop_duplicates()
print(df_routers)
write_to_db("rpc_routers", df_routers)

# create rpc_links and write to lnetd
print("\nGenerate LnetD Links info and write to db\n")
df_links = df[["source", "target", "l_ip", "r_ip", "metric"]]
df_links.loc[:, "l_ip_r_ip"] = pd.Series(
    [
        tuple(sorted(each))
        for each in list(
            zip(df_links.l_ip.values.tolist(), df_links.r_ip.values.tolist())
        )
    ]
)
df_links["l_ip_r_ip"] = df_links["l_ip_r_ip"].astype(str)
print(df_links)
write_to_db("rpc_links", df_links)
