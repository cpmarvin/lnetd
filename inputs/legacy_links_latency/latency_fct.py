from netmiko import ConnectHandler
import re

import sys
sys.path.append('../utils/')

from lnetd_log import get_module_logger

logger = get_module_logger(__name__,'INFO')

def get_ping_results(router,dst_ip):
    logger.info('trying to parse ping request for: %s with %s' %(router,dst_ip))
    pattern = re.compile(r'\bround-trip\b',flags=re.I)
    if router in ["gb-pe11-lon"]:
        vendor = 'cisco_xr'
        username = 'cpetrescu'
        password = 'lab123'
        command = 'ping ' + dst_ip
        pattern_res = r'min/avg/max = (\S+)'
    else:
        vendor = 'juniper_junos'
        username = 'lab'
        password = 'lab123'
        command = 'ping ' + dst_ip + ' count 5 rapid'
        pattern_res = r'min/avg/max.+ = (\S+)'

    try:
        logger.info('connect to router')
        net_connect = ConnectHandler(device_type=vendor, ip=router, username=username, password=password)
        logger.debug('run command %s on router %s' %(router,command))
        output = net_connect.send_command(command)
        output_clean = ' '.join(output.split())
        output_list= output.splitlines()
        for i in output_list:
            logger.debug('line: %s' %(i))
            if pattern.findall(i):
                logger.debug('matched line: %s' %(i))
                summary = re.findall(pattern_res, i)[0]
                summary = summary.split('/')
                logger.debug('summary: %s' %(summary))
                maximum = float(summary[1])
                logger.debug('maximum: %s' %(maximum))
                break
            else:
                minimum = '0'
                average = '0' 
                maximum = '0'

        logger.info('all done with router : %s with : %s' %(router,command))
        net_connect.disconnect()
        logger.debug('all done with router : %s with : %s and the result is : %s' %(router,command,maximum))
        return int(maximum)
    except Exception as e:
        logger.error('Exception found: %s' %e)
        return -1
