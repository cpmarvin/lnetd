import datetime
import json
import re

def create_kafka_message(encoding_path,hostname,row_key,row_data):
	if encoding_path == 'Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface/latest/generic-counters':
		metrics = {}
		metrics['hostname'] = hostname
		metrics['ifName'] = row_key.interface_name
		metrics['ifHCOutOctets'] = row_data.bytes_sent
		metrics['ifInErrors'] = row_data.input_drops
		metrics['timestamp'] = datetime.datetime.utcnow().isoformat()
		jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(jd)
		return jd
	elif encoding_path == 'Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface':
		metrics = {}
		metrics['hostname'] = hostname
		metrics['ifName'] = row_key.interface_name
		metrics['ipAddress'] = row_data.ip_information.ip_address
		metrics['ifHighSpeed'] = row_data.speed
		metrics['timestamp'] = datetime.datetime.utcnow().isoformat()
		jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(jd)
		return jd
	elif encoding_path == 'Cisco-IOS-XR-snmp-agent-oper:snmp/if-indexes/if-index':
		metrics = {}
		metrics['hostname'] = hostname
		metrics['ifName'] = row_data.interface_name.replace("_", "/")
		metrics['ifIndex'] = row_key.interface_index
		metrics['timestamp'] = datetime.datetime.utcnow().isoformat()
		jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(jd)
		return jd
	elif encoding_path == 'LOGICAL-INTERFACE-SENSOR:/junos/system/linecard/interface/logical/usage/:/junos/system/linecard/interface/logical/usage/:PFE':
		metrics = {}
		metrics['hostname'] = hostname
		metrics['ifName'] = row_data.if_name
		metrics['ifHCOutOctets'] = row_data.egress_stats.if_octets
		metrics['ifIndex'] = row_data.snmp_if_index
		if re.match("^ge-",row_data.if_name):
			metrics['ifHighSpeed'] = 1000
		elif re.match("^xe-",row_data.if_name):
			metrics['ifHighSpeed'] = 10000
		elif re.match("^et-",row_data.if_name):
			metrics['ifHighSpeed'] = 100000
		else:
			metrics['ifHighSpeed'] = 0
		jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(jd)
		return jd

def create_influx_message(encoding_path,hostname,row_key,row_data,timestamp):
	if encoding_path == 'Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface/latest/generic-counters':
		metrics = {}
		metrics['measurement'] = "ios_xr_interface_counters"
		metrics['tags'] = {}
		metrics['fields'] ={}
		metrics['tags']['hostname'] = hostname
		metrics['tags']['ifName'] = row_key.interface_name
		metrics['fields']['ifHCOutOctets'] = row_data.bytes_sent
		metrics['fields']['ifInErrors'] = row_data.input_drops
                metrics['time'] = timestamp
		#jd = json.dumps(metrics)
                if row_key.interface_name == 'TenGigE0/0/0/13':
                    print 'this is the json:\n{}'.format(metrics)
		return metrics
	elif encoding_path == 'Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface':
		metrics = {}
		metrics['measurement'] = "ios_xr_interface_info"
		metrics['tags'] = {}
		metrics['fields'] ={}
		metrics['tags']['hostname'] = hostname
		metrics['tags']['ifName'] = row_key.interface_name
		metrics['tags']['ipAddress'] = row_data.ip_information.ip_address
		metrics['fields']['ifHighSpeed'] = int(row_data.speed)/1000
                metrics['time'] = timestamp
		#jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(metrics)
		return metrics
	elif encoding_path == 'Cisco-IOS-XR-snmp-agent-oper:snmp/if-indexes/if-index':
		metrics = {}
		metrics['measurement'] = "ios_xr_interface_snmp"
		metrics['tags'] = {}
		metrics['fields'] ={}
		metrics['tags']['hostname'] = hostname
		metrics['tags']['ifName'] = row_data.interface_name.replace("_", "/")
		metrics['fields']['ifIndex'] = row_key.interface_index
                metrics['time'] = timestamp
		#jd = json.dumps(metrics)
		#print 'this is the json:\n{}'.format(metrics)
		return metrics
	elif encoding_path == 'LOGICAL-INTERFACE-SENSOR:/junos/system/linecard/interface/logical/usage/:/junos/system/linecard/interface/logical/usage/:PFE':
		metrics = {}
		metrics['measurement'] = "jnp_interface_stats"
		metrics['tags'] = {}
		metrics['fields'] ={}
		metrics['tags']['hostname'] = hostname
		metrics['tags']['ifName'] = row_data.if_name
		metrics['tags']['ifIndex'] = row_data.snmp_if_index
		metrics['fields']['ifHCOutOctets'] = row_data.egress_stats.if_octets
                metrics['time'] = timestamp
		#print 'this is the json:\n{}'.format(jd)
		return metrics
