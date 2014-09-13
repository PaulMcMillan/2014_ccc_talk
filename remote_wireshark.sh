rm -f /tmp/remote_wireshark
mkfifo /tmp/remote_wireshark
wireshark -k -i /tmp/remote_wireshark &
ssh v2 "tcpdump -l -i eth2 -w - 'not tcp port 22' 2>/dev/null" > /tmp/remote_wireshark
rm -f /tmp/remote_wireshark
