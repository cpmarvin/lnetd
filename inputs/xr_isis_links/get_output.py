from netmiko import ConnectHandler
import re

import sys
sys.path.append('../utils/')

from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'DEBUG')

def get_output(router,command):
    if router in ["gb-pe11-lon"]:
        vendor = 'cisco_xr'
        username = 'cpetrescu'
        password = 'lab123'
    try:
        logger.info('connect to  %s' %(router))
        net_connect = ConnectHandler(device_type=vendor, ip=router, username=username, password=password)
        logger.info('run command  %s on %s' %(command,router))
        output = net_connect.send_command(command)
        logger.info('all done returning the output')
        return output
    except Exception as e:
        logger.error('Connection to %s failed due to : \n %s' %(router,e))
        return -1
