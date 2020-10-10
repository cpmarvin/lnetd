import sqlite3
import re
import pandas as pd
from netaddr import IPNetwork, IPAddress

def insert_routers(table,index,name,ip,country,vendor,model,version,tacacs_id):
    try:
        conn = sqlite3.connect('/opt/lnetd/web_app/database.db')
        sql = ''' INSERT OR REPLACE INTO %s values('%s','%s','%s','%s','%s','%s','%s','%s') ''' %(table,index,name,ip,country,vendor,model,version,tacacs_id)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print (e)
def update_routers_sqlite3(table,router,version,model,vendor):
        try:
                conn = sqlite3.connect('/opt/lnetd/web_app/database.db')
                sql = ''' UPDATE %s SET version = '%s' , model = '%s' , vendor = '%s' WHERE name = '%s' ''' %(table,version,model,vendor,router)
                print (sql)
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
        except Exception as e:
                print (e)

def huawei_parse_show_version(input_text):
        version = 'NA'
        model = 'NA'
        for i in input_text.splitlines():
                i = i.strip(' ')
                if re.search(r'.+Version',i):
                        version = i.split()[4]
                elif re.search(r".uptime is",i):
                        model =  i.split()[1]
        return (version,model)

import yaml
import pandas as pd
import re

from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.op.fpc import FpcHwTable
from jnpr.junos.op.fpc import FpcInfoTable,FpcMiReHwTable
from jnpr.junos.op.inventory import ModuleTable

def get_cards_jnp(task):
    modules = []
    hostname = task.host.name
    username = task.host.username
    password = task.host.password

    dev = Device(host=hostname, user=username, password=password, port='830', gather_facts=False)
    try:
      dev.open()
      dev.timeout = 10
      module = ModuleTable(dev).get()
      #print('hostname:',hostname)
      for slot in module:
        module = slot.jname
        module_type = slot.type
        if module is None:
            continue
        if re.search(r"FPC|Routing|PIC",module):
          modules.append((module,module_type))
          #print (module,module_type)
      labels = ['card_slot','card_name']
      df = pd.DataFrame(modules,columns=labels)
      df['router_name'] = hostname
      df['card_status'] = 'online'
      return(df)
    except Exception as e:
      print('Failed',e)
      raise Exception

def get_cards_xr(router,output):
    try:
        df = pd.DataFrame(output)
        df = df.drop(['config_state'], axis=1)
        df.columns = ['card_slot','card_name','card_status']
        df['router_name'] = router
        return(df)
    except Exception as e:
        print('Failed', e)
        raise Exception

def get_cards_huawei(display_version):
  cards = {}
  line = 0

  try:
    for i in display_version.splitlines():
      if re.match("^(LPU|MPU.+|SRU).[0-9].", i):
        # print(i).split(":")[0]
        slot_nr = i.split(":")[0].split()[1]
        slot_nr1 = i.split(":")[0]
        # print(slot_nr)
        #slot_description = i.split(":")[0].split()[0]
        # print(slot_description)
        cards[line] = [slot_nr]
        cards[line].append('0')
        cards[line].append(slot_nr1)
        # cards[line].append(slot_description)
        line = line + 1

    labels = ['slot_nr', 'pic_nr', 'card_name']
    df_cards = pd.DataFrame(list(cards.values()), columns=labels)
  except Exception as e:
    print(e)

    # print(df_cards)
  pics = {}
  line = 0
  try:
    for i in display_version.splitlines():
      if re.search("Registered", i):
        # print(i.split())
        pics[line] = i.split()
        line = line + 1
    labels = ['slot_nr', 'pic_nr', 'status', 'card_name', 'nr_ports', 'status1', 'status2']
    df_pics = pd.DataFrame(list(pics.values()), columns=labels)
    df_pics = df_pics.drop(['status', 'nr_ports', 'status1', 'status2'], axis=1)
  except Exception as e:
    print(e)

  try:
    df_final = pd.concat([df_cards, df_pics], ignore_index=True)
    df_final['slot_nr'] = df_final['slot_nr'].astype(int)
    df_final = df_final.sort_values('slot_nr')
    df_final['slot_nr'] = df_final['slot_nr'].astype(str)
    df_final['card_slot'] = df_final['slot_nr'].str.cat(df_final['pic_nr'], sep='/')
    df_final['card_status'] = 'online'
    df_final = df_final.sort_values('slot_nr')
    df_final = df_final[['card_name', 'card_slot', 'card_status']]
    return df_final
  except Exception as e:
    print(e)


def get_type(asn,ipt_cst):
    if asn in ipt_cst:
        return 'customer'
    else:
        return 'peering'

def get_ix_name(ip,version,ix_lans):
    default = {'name': 'n/a', 'ipv4': 'n/a', 'ipv6': 'n/a'}
    try:
        for i in ix_lans:
            if version == 4:
                if IPAddress(ip) in IPNetwork(i['ipv4']):
                    return i
            elif version == 6:
                if IPAddress(ip) in IPNetwork(i['ipv6']):
                    return i
        else:
            return default
    except Exception as e:
        print('error',e)
        return default


def get_cards_huawei(display_version):
  cards = {}
  line = 0

  try:
    for i in display_version.splitlines():
      #print('this is i in splitlines',i)
      if re.match("^(LPU|MPU.+|SRU|ETH).[0-9].", i):
        print(i).split(":")[0]
        slot_nr = i.split(":")[0].split()[1]
        slot_nr1 = i.split(":")[0]
        print(slot_nr)
        #slot_description = i.split(":")[0].split()[0]
        # print(slot_description)
        cards[line] = [slot_nr]
        cards[line].append('0')
        cards[line].append(slot_nr1)
        # cards[line].append(slot_description)
        line = line + 1
     #try power
    for i in display_version.splitlines():
       if re.match("^[5-6]",i):
        print('This is i',i)
        print(i.split(" "))
        slot_nr = i.split(" ")
        card_status = slot_nr[10]
        if card_status != "Normal":
            card_status = 'FAILED'
        else:
            card_status = 'OPERATIONAL'
        print('slot_nr',slot_nr[0])
        cards[line] = [slot_nr[0]]
        cards[line].append('0')
        cards[line].append('POWER')
        cards[line].append(card_status)
        line = line + 1

    labels = ['slot_nr', 'pic_nr', 'card_name','card_status']
    #t = [(2,0,"ETH_4x10GE_16xGE_8xGE")]
    df_cards = pd.DataFrame(list(cards.values()), columns=labels)
    #df_cards = pd.DataFrame(t)
  except Exception as e:
    print(e)

    # print(df_cards)
  pics = {}
  line = 0
  try:
    for i in display_version.splitlines():
      if re.search("Registered", i):
        #print('this is the pics',i.split())
        pics[line] = i.split()
        line = line + 1
    labels = ['slot_nr', 'status', 'card_name', 'nr_ports', 'status1']
    df_pics = pd.DataFrame(list(pics.values()), columns=labels)
    df_pics['pic_nr'] = '0'
    df_pics = df_pics.drop(['status', 'nr_ports', 'status1'], axis=1)
    df_pics['card_status'] = 'OPERATIONAL'
  except Exception as e:
    print('exception in pics parse',e)

  try:
    df_final = pd.concat([df_cards, df_pics], ignore_index=True)
    df_final['slot_nr'] = df_final['slot_nr'].astype(int)
    df_final = df_final.sort_values('slot_nr')
    df_final['slot_nr'] = df_final['slot_nr'].astype(str)
    df_final['card_slot'] = df_final['slot_nr'].str.cat(df_final['pic_nr'], sep='/')
    #df_final['card_status'] = 'online'
    df_final = df_final.sort_values('slot_nr')
    df_final = df_final[['card_name', 'card_slot', 'card_status']]
    return df_final
  except Exception as e:
    print(e)
