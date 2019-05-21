
from lxml import etree as ETREE
import pandas as pd
from sqlalchemy import create_engine

from lxml import etree, objectify
from ncclient import manager
from ncclient.xml_ import *

sys.path.append('../utils/')
from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'DEBUG')

def remove_ns(xml_string):
    '''Remove namespace from xml string'''
    xml_string = xml_string.encode('utf-8')
    parser = etree.XMLParser(remove_blank_text=True,encoding='utf-8')
    tree = etree.fromstring(xml_string, parser)
    root = tree.getroottree()

    for elem in root.getiterator():
        if not hasattr(elem.tag, 'find'):
            continue  # (1)
        i = elem.tag.find('}')
        if i >= 0:
            elem.tag = elem.tag[i + 1:]
    objectify.deannotate(root, cleanup_namespaces=True)
    #return(etree.tostring(root, pretty_print=True))
    logger.info('Remove namespace done')
    return(root)


def get_netconf(*args):
    '''Get netconf operation data,
    return clean xml object'''
    results = []
    ios_xr = manager.connect(host='10.13.13.13',
                             username='cpetrescu',
                             password='lab123',
                             hostkey_verify=False,
                             device_params={'name': 'iosxr'})
    # just return static for now
    for i in args:
        logger.info('Get netconf data for %s' %i)
        res = ios_xr.dispatch(to_ele(i))
        res = to_xml(res.data)
        results.append(remove_ns(res))
    return results


def parse_xml(db, result_tree):
    if db == 'links':
        isis_db = []
        for isis_id in result_tree.iter('topology-brief'):
            source = isis_id.xpath(".//igp-node-id")[0].text[:-3]
            for link in isis_id.iter('topology-node-link'):
                l_ip = link.xpath(".//topology-link-interface-address")[0].text
                r_ip = link.xpath(".//topology-link-neighbor-address")[0].text
                metric = link.xpath(".//topology-link-igp-metric")[0].text
                target = link.xpath('topology-link-neighbor-system-id')[0].text[:-3]
                # print target, l_ip, r_ip, metric
                isis_dict = {'source': source, 'target': target, 'l_ip': l_ip, 'r_ip': r_ip, 'metric': metric}
                isis_db.append(isis_dict)
        df = pd.DataFrame(isis_db)
        return df
    if db == 'routers':
        routers_db = []
        for isis_id in result_tree.iter('topology-brief'):
            name = isis_id.xpath(".//igp-node-id")[0].text[:-3]
            ip = isis_id.xpath(".//topology-node-te-router-id")[0].text
            routers_dict = {'name': name, 'ip': ip}
            routers_db.append(routers_dict)
        df = pd.DataFrame(routers_db)
        return df
    elif db == 'hostname':
        hostname_db = {}
        for hostname in result_tree.iter('host-names'):
            for host_name in hostname:
                name = host_name.xpath(".//host-name")[0].text
                sys_id = host_name.xpath(".//system-id")[0].text
                name_map = {sys_id: name}
                hostname_db.update(name_map)
        return hostname_db
    else:
        return('work in progress')

def write_to_db(table,df):
    try:
        disk_engine = create_engine('sqlite:////opt/lnetd/web_app/database.db')
        df.to_sql(table, disk_engine, if_exists='replace')
    except Exception as e:
        print(e)
      
