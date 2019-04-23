import re
import pandas as pd

def get_interfaces_jnp(router,output):
    try:
        #print(router,output)
        filter_result = [(key) for key  in output['interfaces'].keys() if (re.search(r"ge-|et-|xe-",key) and not re.search(r"\.",key))]
        interfaces = []
        for i in filter_result:
            is_up = output['interfaces'][i]['is_up']
            speed = str(output['interfaces'][i]['speed'] / 1000) + 'Gbps'
            if is_up == False:
                try:
                    check_optics = output['optics'][i]
                    is_up = 'Down (Reason: Link loss or low light, no loopback)'
                except Exception as e:
                    is_up = 'Down (Reason: The optics for the port are not present)'
            else:
                is_up ='Up'
            interfaces.append((i,is_up,speed,router))
        labels = ['interface_name', 'interface_status','interface_speed','router_name']
        df = pd.DataFrame(interfaces, columns=labels)
        return(df)
    except Exception as e:
        print(e)

def get_interfaces_xr(router,output_list):
    try:
        interface = {}
        line = 0
        #print(output_list)
        for i in output_list.splitlines():
            i = i.strip(' ')
            #print i
            if re.match("^Operational data for interface",i):
                #print i
                interface[line] = [i[31:][:-1]]
                #line = line + 1
            elif re.match("^Operational state:",i):
                #print i
                interface[line].append(i[19:])
                #line = line +1
            elif re.match("^Speed:",i):
                #print i
                interface[line].append(i[6:].strip())
                line = line + 1
        #print(interface)
        labels = ['interface_name', 'interface_status','interface_speed']
        df = pd.DataFrame(list(interface.values()), columns=labels)
        #df = pd.DataFrame(interface.values(),columns=labels)
        #df = pd.DataFrame(interface.values())
        #df = df.drop([2, 4, 5], axis=1)
        df['router_name'] = router
        #print df
        #print sql_qry
        return df 
    except Exception as e:
        print('Error',e)
