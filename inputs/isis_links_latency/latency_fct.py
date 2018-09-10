from netmiko import ConnectHandler
import re
def get_ping_results(router,dst_ip):
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
        print"*connecting to:%s" %router
        net_connect = ConnectHandler(device_type=vendor, ip=router, username=username, password=password)
        #command = 'ping ' + dst_ip + ' count 5'
        print"--run %s" %command
        output = net_connect.send_command(command)
        print"--parse values"
        output_clean = ' '.join(output.split())
        output_list= output.splitlines()
        #print output_list
        for i in output_list:
            #print "line:%s" %i
            if pattern.findall(i):
                #print "pattern line : %s" %i
                summary = re.findall(pattern_res, i)[0]
                summary = summary.split('/')
                #print "summary : %s" %summary
                maximum = float(summary[1])
                #(minimum, average, maximum , ) = (float(x) for x in summary.split('/'))
                #print i
                #print "maximum : %s " %maximum
                break
            else:
                minimum = '0'
                average = '0' 
                maximum = '0'

        print "--all done and closing session to %s" %router
        net_connect.disconnect()
        #print "minimum:%s, average:%s, maximum:%s" %(minimum,average, maximum)
        print "--return value was:%s" %maximum
        return int(maximum)
    except Exception as e:
        print "error %s for :%s with ping source:%s" %(e,router,dst_ip)
        return -1
