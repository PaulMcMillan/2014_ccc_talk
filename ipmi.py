import struct
import socket

from collections import namedtuple



COMMANDS = namedtuple(
    'Commands',
    ['get_session_challenge', 'activate_session'])(0x39, 0x3a)



class Connection(object):
    def __init__(self, host, port):
        self.remote_address = (host, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.local_address = sock.getsockname()  # (local_host, local_port)
        self.sock = sock

    def recv(self, bufsize=4096):
        return self.sock.recv(bufsize)

    def send(self, data):
        return self.sock.sendto(data, self.remote_address)

    def checksum(self, data):
        res = sum([ord(byte) for byte in data])
        res ^= 0xff
        res += 1
        res &= 0xff
        return chr(res)

    def wrap_headers(self, ipmi_msg):
        ipmi_msg_length = len(ipmi_msg)
        msg  = ('\x06\x00\xff\x07'  # RMCP, Class IPMI
                '\x00'  # Authentication Type: None
                '\x00\x00\x00\x00'  # Session Sequence Number: 0
                '\x00\x00\x00\x00'  # Session ID: 0
                + chr(ipmi_msg_length)
                + ipmi_msg)
        return msg

    def make_ipmi_msg(self, seq_num, command, data):
        header = (
            '\x20'  # rsAddr - always 20 when talking to BMC
            '\x18'  # we're making requests
        )
        header += self.checksum(header)
        body = (
            '\x81'  # our source address
            + chr(seq_num << 2)  # source lun right most 2 bits are 0
            + chr(command)
            + data
            )
        body += self.checksum(body)
        return self.wrap_headers(header + body)

    def get_session_challenge(self, username, seq=2):
        data = (
            '\x04'  # straight password authentication
            + struct.pack('16s', username)
            )
        packet = self.make_ipmi_msg(seq, COMMANDS.get_session_challenge, data)
        return self.send(packet)


c = Connection('192.168.253.200', 623)
print c.get_session_challenge('admin')
