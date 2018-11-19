import json
import logging
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen
from tornado.ioloop import IOLoop
from struct import Struct, unpack
from telemetry_pb2 import Telemetry

class TelemetryServer(TCPServer):
    def __init__(self):
        #super().__init__()
        self.header_size = 12
        self.header_struct = Struct('>hhhhi')
        self._UNPACK_HEADER = self.header_struct.unpack

    @gen.coroutine
    def handle_stream(self, stream, address):
        print("Got connection from:{}".format(address))
        while not stream.closed():
            try:
                header_data = yield stream.read_bytes(self.header_size)
                msg_type, encode_type, msg_version, flags, msg_length = self._UNPACK_HEADER(header_data)
                encoding = {1:'gpb', 2:'json'}[encode_type]
                msg_data = b''
                print(encode_type)
                if encode_type == 1:
                    print('Got {} bytes from {} with encoding {}'.format())
                    while len(msg_data) < msg_length:
                        packet = yield stream.read_bytes(msg_length - len(msg_data))
                        msg_data += packet
                    print(msg_data)
                    gpb_parser =Telemetry()
                    gpb_data = gpb_parser.ParseFromString(msg_data.decode('ascii'))
                    print(gpb_data.node_id)
                else:
                    print('Got {} bytes from {} with encoding {}'.format())
                    while len(msg_data) < msg_length:
                        packet = yield stream.read_bytes(msg_length - len(msg_data))
                        msg_data += packet
                    json_data = json.loads(msg_data.decode("ascii"))
            except Exception as e:
                print(e)
                stream.close()



def main():
    server = TelemetryServer()
    server.bind(5556)
    server.start(0)
    IOLoop.current().start()

if __name__ == '__main__':
    main()