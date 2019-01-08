import socket
import threading
import struct 
import logging

import telemetry_pb2 #cisco
import ifstatsbag_generic_pb2 # cisco interface stats
import im_cmd_info_pb2 #cisco interface info 
import telemetry_top_pb2,logical_port_pb2 # juniper
import snmp_agen_oper_if_index_pb2 # cisco snmp ifindex

from gbp_parse_msg import * 

kafka_msg = False
influx_msg = True
#move this to anothe module
from influxdb import InfluxDBClient
client_influxdb = InfluxDBClient(host='127.0.0.1', port=8086, database='telemetry')
#kafka
#kafka = KafkaClient('127.0.0.1:9092')
#producer = SimpleProducer(kafka)

logging.basicConfig(format='%(asctime)s %(message)s' , level=logging.INFO)

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print 'address:{}'.format(address)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        while True:
            try:
                data = client.recv(12)
                if data:
                    print 'getting some data'
                    # Set the response to echo back the recieved data
                    header = data
                    msg_type, encode_type, msg_version, flags, msg_length = struct.unpack('>hhhhi',header)
                    msg_data = b''
                    print msg_type, encode_type, msg_version, flags, msg_length
                    if encode_type == 1:
                        while len(msg_data) < msg_length:
                            msg_data += client.recv(msg_length - len(msg_data))
                        gpb_parser = telemetry_pb2.Telemetry()
                        gpb_data = gpb_parser.ParseFromString(msg_data)
                        if gpb_parser.encoding_path == 'Cisco-IOS-XR-infra-statsd-oper:infra-statistics/interfaces/interface/latest/generic-counters':
                            row_key = ifstatsbag_generic_pb2.ifstatsbag_generic_KEYS()
                            row_data = ifstatsbag_generic_pb2.ifstatsbag_generic()
                            for new_row in gpb_parser.data_gpb.row:
                                row_data.ParseFromString(new_row.content)
                                row_key.ParseFromString(new_row.keys)
                                if kafka_msg:
                                    kafka_msg_parse = create_kafka_message(gpb_parser.encoding_path,gpb_parser.node_id_str,row_key,row_data)
                                    producer.send_messages(b'ios_xr_interface_counters',kafka_msg_parse)
                                    logging.info('Write {} to kafka topic'.format(gpb_parser.encoding_path))
                                elif influx_msg:
                                    influx_msg_parse = create_influx_message(gpb_parser.encoding_path,gpb_parser.node_id_str,row_key,row_data)
                                    client_influxdb.write_points([influx_msg_parse],time_precision = 's')
                                    logging.info('Write {} to InfluxDB'.format(gpb_parser.encoding_path))
                                else:
                                    print ('Row_key:{}\n,Row_data:{}').format(row_key,row_data)
                else:
                    raise error('Client disconnected')
            except Exception as e:
                print 'Error:{}'.format(e)
                client.close()
                return False

if __name__ == "__main__":
    while True:
        port_num = 50010
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('',port_num).listen()
