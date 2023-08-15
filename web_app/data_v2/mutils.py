import pynetbox
import pandas as pd
import sys
import urllib3
import jinja2
import logging
from influxdb import InfluxDBClient

urllib3.disable_warnings()

def get_netbox_connections(nb_token,nb_url):
    NB_TOKEN = nb_token
    NB_URL = nb_url
    nb = pynetbox.api(url=NB_URL, token=NB_TOKEN, ssl_verify=False)
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s (%(lineno)s) - %(levelname)s: %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel('INFO')

    network_map = []

    logger.info('Get all routers from netbox')
    # get all routers
    routers = nb.dcim.devices.filter(
        role='router')
    # generate a list of strings instead of objects
    routers_list = ', '.join([str(x) for x in routers])
    for rtr in routers:
        logger.info('Get all interface connection for router %s' % rtr)
        interface_connection = nb.dcim.interface_connections.filter(
            device=rtr)
        rtr_interface = [
            interface for interface in interface_connection if interface.interface_a.device.name == str(rtr)]
        rtr_interface_flip = [
            interface for interface in interface_connection if interface.interface_b.device.name == str(rtr)]
        for interface in rtr_interface:
            if (interface.interface_a.device.name in routers_list) and (interface.interface_b.device.name in routers_list):
                entry = {'source': interface.interface_a.device.name,
                         'target': interface.interface_b.device.name,
                         'l_ip': interface.interface_a.name,
                         'r_ip': interface.interface_b.name}
                network_map.insert(0, entry)
        for interface in rtr_interface_flip:
            if (interface.interface_a.device.name in routers_list) and (interface.interface_b.device.name in routers_list):
                entry = {'source': interface.interface_b.device.name,
                         'target': interface.interface_a.device.name,
                         'l_ip': interface.interface_b.name,
                         'r_ip': interface.interface_a.name}
                network_map.insert(0, entry)
    logger.info('done with router connections')
    logger.info('get all circuits info')
    circuits = nb.circuits.circuit_terminations.all()
    logger.info('filter connected circuits')
    circuits_connected = [
        circ for circ in circuits if circ.connected_endpoint]
    parse_circuits = []
    entry = {}
    for circ in circuits_connected:
        if str(circ) in parse_circuits:
            entry[str(circ)].update(
                {'target': circ.connected_endpoint.device.name, 'r_ip': circ.connected_endpoint.name})
        else:
            entry[str(circ)] = {'source': circ.connected_endpoint.device.name,
                                'l_ip': circ.connected_endpoint.name}
            parse_circuits.insert(0, str(circ))
    connected_circuits = [key for key in entry if (
        'target' in entry[key].keys())]
    logger.info('filter connected circuits between routers only')
    for n in connected_circuits:
        if entry[n]['source'] and entry[n]['target'] in routers_list:
            reverse_entry = {'source': entry[n]['target'],
                             'l_ip': entry[n]['r_ip'],
                             'target': entry[n]['source'],
                             'r_ip': entry[n]['l_ip']}
            network_map.insert(0, entry[n])
            network_map.insert(0, reverse_entry)
    df = pd.DataFrame.from_records(network_map)
    logger.info('Generate l_ip r_ip pair')
    df.loc[:, 'l_ip_r_ip'] = pd.Series([tuple(sorted(each)) for each in list(
        zip(df.l_ip.values.tolist(), df.r_ip.values.tolist()))])
    logger.info('Set l_ip r_ip pair as string')
    df['l_ip_r_ip'] = df['l_ip_r_ip'].astype(str)
    logger.info('Fill NA values with 0')
    df = df.fillna(0)
    return df
