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
   [[inputs.snmp.field]]
    name = "hostname"
    oid = ".1.3.6.1.2.1.1.5.0"
    is_tag = true
   [[inputs.snmp.table]]
    name = "interface_address"
    inherit_tags = [ "hostname" ]
    index_as_tag = true
   [[inputs.snmp.table.field]]
    name = "Ifindex"
    oid = ".1.3.6.1.2.1.4.20.1.2"

