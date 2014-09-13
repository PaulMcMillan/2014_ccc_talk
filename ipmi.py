import struct
import socket
import os

from collections import namedtuple



COMMANDS = namedtuple(
    'Commands',
    ['get_session_challenge', 'activate_session'])(0x39, 0x3a)



class Connection(object):
    seq_num = 1

    def __init__(self, host, port):
        self.remote_address = (host, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.local_address = sock.getsockname()  # (local_host, local_port)
        self.sock = sock

    def recv(self, bufsize=4096):
        return self.sock.recv(bufsize)

    def send(self, data):
        self.seq_num += 1
        return self.sock.sendto(data, self.remote_address)

    def checksum(self, data):
        res = sum([ord(byte) for byte in data])
        res ^= 0xff
        res += 1
        res &= 0xff
        return chr(res)

    def wrap_headers(self, ipmi_msg,
                     auth_type='\x00',
                     session_sequence_number='\x00\x00\x00\x00',
                     session_id='\x00\x00\x00\x00',
                     auth_code=''):
        ipmi_msg_length = len(ipmi_msg)
        msg  = ('\x06\x00\xff\x07'  # RMCP, Class IPMI
                + auth_type
                + session_sequence_number
                + session_id
                + auth_code
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
            + chr(self.seq_num << 2)  # source lun right most 2 bits are 0
            + chr(command)
            + data
            )
        body += self.checksum(body)
        return header + body

    def get_session_challenge(self, username):
        data = (
            '\x04'  # straight password authentication
            + struct.pack('16s', username)
        )
        packet = self.make_ipmi_msg(
            self.seq_num, COMMANDS.get_session_challenge, data)
        packet = self.wrap_headers(packet)
        return self.send(packet)

    def get_challenge_response(self):
        # yes, I know there could be all kinds of crap here. But there isn't.
        data = self.sock.recv(1024)
        response = data[-22:-1] # grab just the returned data from response
        res = {
            'completion_code': response[0],
            'session_id': response[1:5],
            'challenge': response[5:21],
            }
        return res


    def activate_session(self, username, password,
                         session_id, auth_code,
                         max_priv_level=0x04):
        data = (
            '\x04'  # straight password authentication
            + chr(max_priv_level)
            + auth_code
            + os.urandom(4)
        )
        packet = self.make_ipmi_msg(
            self.seq_num, COMMANDS.activate_session, data)
        packet = self.wrap_headers(packet,
                                   auth_type='\x04',  # password auth
                                   session_id=session_id,
                                   auth_code=auth_code)
        return self.send(packet)


c = Connection('192.168.253.200', 623)
print c.get_session_challenge('admin')
res =  c.get_challenge_response()
print res
print c.activate_session('admin', 'admin',
                         res['session_id'], res['challenge'])
