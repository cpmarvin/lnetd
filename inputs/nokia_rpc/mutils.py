from lxml import etree, objectify
from ncclient import manager
from ncclient.xml_ import *

from sqlalchemy import create_engine


def remove_ns(xml_string):
    """Remove namespace from xml string"""
    xml_string = xml_string.encode("utf-8")
    parser = etree.XMLParser(remove_blank_text=True, encoding="utf-8")
    tree = etree.fromstring(xml_string, parser)
    root = tree.getroottree()

    for elem in root.getiterator():
        if not hasattr(elem.tag, "find"):
            continue  # (1)
        i = elem.tag.find("}")
        if i >= 0:
            elem.tag = elem.tag[i + 1 :]
    objectify.deannotate(root, cleanup_namespaces=True)
    return root


def get_netconf(*args):
    """Get netconf state data,
  return xml """
    ios_xr = manager.connect(
        host="lab_device",
        username="admin",
        password="lab_password",
        port="9102",
        hostkey_verify=False,
        device_params={"name": "iosxr"},
    )
    for i in args:
        res = ios_xr.dispatch(to_ele(i))
        res = to_xml(res.data)
    return remove_ns(res)


def xml_request(entry):
    """Return xml request using nokia-state for isis database"""
    rpc_state_protocol = """
<get>
        <filter>
                <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
         <router>
           <{}>
                   <database/>
           </{}>
         </router>
                </state>
        </filter>
</get>
""".format(
        entry, entry
    )
    return rpc_state_protocol


def xml_request_router_name(entry):
    """Return xml request using nokia-state for isis hostname """
    rpc_state_protocol = """
<get>
        <filter>
                <state xmlns="urn:nokia.com:sros:ns:yang:sr:state">
                 <router>
                   <{}>
                   <hostname/>
                   </{}>
                 </router>
                </state>
        </filter>
</get>
""".format(
        entry, entry
    )
    return rpc_state_protocol


def parse_xml(result_tree):
    # list to keep isis_db lsp's
    isis_db = []
    for entry in result_tree.iter("database"):
        lsp_id = entry.xpath(".//lsp-id")[0].text
        sys_id = entry.xpath(".//system-id")[0].text
        lsp_encode = entry.xpath(".//value")[0].text
        lsp_encode_bytes = bytearray.fromhex(lsp_encode[2:])
        entry = {"source": sys_id, "lsp_encode": lsp_encode_bytes, "lsp_id": lsp_id}
        isis_db.insert(1, entry)
    return isis_db


def parse_xml_router_name(result_tree):
    # dict for isis sysid to router name
    routers_name_mapping = {}
    for entry in result_tree.iter("hostname"):
        router_name = entry.xpath(".//host-name")[0].text
        system_id = entry.xpath(".//system-id")[0].text
        entry = {system_id: router_name}
        routers_name_mapping.update(entry)
    return routers_name_mapping


def write_to_db(table, df):
    try:
        disk_engine = create_engine("sqlite:////opt/lnetd/web_app/database.db")
        df.to_sql(table, disk_engine, if_exists="replace")
    except Exception as e:
        print(e)
