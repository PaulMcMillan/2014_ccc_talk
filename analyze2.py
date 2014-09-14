import time
import dpkt
import pdb
from dpkt import hexdump as h

with open('data/out.pcap') as f, open('data/out.pcap.parsed', 'w') as r:
    pcap = dpkt.pcap.Reader(f)
    current_run = []
    current_category = None
    x = 0
    start = prev = time.time()
    prev += 1 # avoid divide by 0
    for ts, buf in pcap:
        x += 1
        if x % 3000 == 0:
            now = time.time()
            diff = now-prev
            print '%04.d' % (now-start), x, 3000/diff
            prev = now
        eth = dpkt.ethernet.Ethernet(buf)
        if (type(eth.data) == dpkt.ip.IP and
            type(eth.data.data) == dpkt.udp.UDP):
            udp = eth.data.data
        else:
            continue

        if udp.dport == 623 or udp.sport == 623:
            if len(current_run) == 9:
                r.write(','.join(map(str, current_run)) + '\n')
                r.flush()
                current_run = []
            elif len(current_run) > 0:
                current_run.append(ts)
                continue
            rmcp = dpkt.ipmi.RMCP(udp.data)
            if type(rmcp.data) == dpkt.ipmi.IPMIAuthenticatedSessionWrapper:
                current_run = [rmcp.data.auth_code.strip('\x00'), ts,]
