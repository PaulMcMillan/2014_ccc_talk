import time
import dpkt
import pdb
from dpkt import hexdump as h

with open('data/out.pcap') as f, open('data/out.pcap.parsed', 'w') as r:
    pcap = dpkt.pcap.Reader(f)
    current_run = []
    x = 0
    start = prev = time.time()
    prev += 1 # avoid divide by 0
    for ts, buf in pcap:
        if len(current_run) == 8:
            r.write(','.join(map(str, current_run)) + '\n')
            current_run = []
        elif len(current_run) > 0:
            current_run.append(ts)
            continue
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
            rmcp = dpkt.ipmi.RMCP(udp.data)
            if (type(rmcp.data) == dpkt.ipmi.IPMISessionWrapper
                and rmcp.data.auth_type == 0x04):
                current_run.append(ts)
