from netmiko import ConnectHandler
import re

def get_output(router,command):
    if router in ["gb-pe11-lon"]:
        vendor = 'cisco_xr'
        username = 'cpetrescu'
        password = 'lab123'
    try:
        print"*connecting to:%s" %router
        net_connect = ConnectHandler(device_type=vendor, ip=router, username=username, password=password)
        print"--run %s" %command
        output = net_connect.send_command(command)
        print"--parse values"
        return output
    except Exception as e:
        print "error %s for :%s " %(e,router)
        return -1
