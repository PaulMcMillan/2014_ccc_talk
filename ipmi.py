import struct
import socket
import os
import time

from collections import namedtuple


COMMANDS = namedtuple(
    'Commands',
    'get_session_challenge,activate_session,close_session,get_authcode')(
        0x39, 0x3a, 0x3c, 0x3f)


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

    def pad(self, data, length=16):
        return struct.pack('%ss' % length, data)

    def wrap_headers(self, ipmi_msg,
                     auth_type='\x00',
                     session_sequence_number='\x00\x00\x00\x00',
                     session_id='\x00\x00\x00\x00',
                     auth_code='',
                     rmcp_seq='\xff',
                     rmcp_class='\x07',):
        ipmi_msg_length = len(ipmi_msg)
#        msg  = ('\x06\x00\xff\x07'  # RMCP, Class IPMI
        msg  = ('\x06\x00%s\x07' % rmcp_seq # RMCP, Class IPMI
                + auth_type
                + session_sequence_number
                + session_id
                + auth_code
                + chr(ipmi_msg_length)
                + ipmi_msg)
        return msg

    def ping(self):
        msg = (
            '\x06\x00\xff\x06' #RMCP, Class ASF
            '\x00\x00\x11\xbe' # IANA Alert
            '\x80'  # Ping
            '\x00'  # message tag
            '\x00'  # separator maybe?
            '\x00'  # data length 0
            )
        return self.send(msg)


    def make_ipmi_msg(self, seq_num, command, data):
        header = (
            '\x20'  # rsAddr - always 20 when talking to BMC
            '\x18'  # we're making requests
        )
        header += self.checksum(header)
        body = (
            '\x81'  # our source address
            + chr((self.seq_num % 64) << 2)  # source lun right most 2 bits are 0
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
                         session_id, challenge,
                         max_priv_level=0x04):
        data = (
            '\x04'  # straight password authentication
            + chr(max_priv_level)
            + challenge
            + os.urandom(4)
        )
        packet = self.make_ipmi_msg(
            self.seq_num, COMMANDS.activate_session, data)
        password = struct.pack('16s', password)
        packet = self.wrap_headers(packet,
                                   auth_type='\x04',  # password auth
                                   session_id=session_id,
                                   auth_code=password)
#                                   rmcp_seq='\x00')
        return self.send(packet)

    def close_session(self, session_id, password):
        data = session_id

        packet = self.make_ipmi_msg(
            self.seq_num, COMMANDS.close_session, data)
        password = struct.pack('16s', password)
        packet = self.wrap_headers(packet,
                                   auth_type='\x04',
                                   session_id=session_id,
                                   auth_code=password)
        return self.send(packet)

    # this doesn't seem to do anything useful
    def get_authcode(self, hash_data,
                     session_id, auth_code,
                     auth_type='\x04', channel_number='\x02', user_id='\x03',
                 ):
        data = auth_type + channel_number + user_id + self.pad(hash_data)
        packet = self.make_ipmi_msg(self.seq_num, COMMANDS.get_authcode, data)
        packet = self.wrap_headers(packet,
                                   auth_type='\x01',
                                   session_id=session_id,
                                   auth_code=self.pad(auth_code))
        return self.send(packet)




c = Connection('192.168.253.14', 623)

print c.get_session_challenge('maestro')
res =  c.get_challenge_response()

#print c.activate_session('admin', 'admin',
#                         res['session_id'], res['challenge'])

#for x in range(10):
import random
characters = '0123456789'
#while True:
for x in range(100):
    print c.activate_session('maestro', '01234%s0000' % random.choice(characters),
                             res['session_id'], res['challenge'])
#    print c.ping()
#    print c.ping()
#    print c.ping()
    time.sleep(0.02)
time.sleep(1)


#print c.get_authcode('admin', res['session_id'], 'admin')
# print c.activate_session('admin', 'admin',
#                          res['session_id'], res['challenge'])

#print c.activate_session('admin', 'admin',
#                         res['session_id'], res['challenge'],
#                         max_priv_level=0x05)



time.sleep(1)
c.close_session(res['session_id'], 'admin')
