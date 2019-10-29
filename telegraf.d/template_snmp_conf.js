# # Retrieves SNMP values from remote agents
 [[inputs.snmp]]
   agents = ["{{host}}:161"]
   timeout = "2s"
   interval = "5m"
   retries = 1
   version = 3
   max_repetitions = 10
   sec_name = "lab"
   auth_protocol = "md5"
   auth_password = "lab123123"
   sec_level = "authNoPriv"
   name = "snmp"
   [[inputs.snmp.field]]
    name = "hostname"
    oid = ".1.3.6.1.2.1.1.5.0"
    is_tag = true
   [[inputs.snmp.field]]
    name = "sysDesc"
    oid = ".1.3.6.1.2.1.1.1.0"
   [[inputs.snmp.table]]
    name = "interface_statistics"
    inherit_tags = [ "hostname" ]
   [[inputs.snmp.table.field]]
      name = "ifName"
      oid = ".1.3.6.1.2.1.31.1.1.1.1"
      is_tag = true
   [[inputs.snmp.table.field]]
      name = "ifHCInOctets"
      oid = ".1.3.6.1.2.1.31.1.1.1.6"
   [[inputs.snmp.table.field]]
      name = "ifHCOutOctets"
      oid = ".1.3.6.1.2.1.31.1.1.1.10"
  [[inputs.snmp.table.field]]
    name = "ifIndex"
    oid = ".1.3.6.1.2.1.2.2.1.1"
    is_tag = true
  [[inputs.snmp.table.field]]
    name = "ifHighSpeed"
    oid=".1.3.6.1.2.1.31.1.1.1.15"
  [[inputs.snmp.table.field]]
    name = "ifInErrors"
    oid=".1.3.6.1.2.1.2.2.1.14"
