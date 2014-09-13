#echo "Setting cpu 0 and 1 to performance governor. Enabling low latency mode."
#sudo sh -c "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
#sudo sh -c "echo performance > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor"
#sudo sh -c "echo 1 > /proc/sys/net/ipv4/tcp_low_latency"

#Pick one of these 3 tcpdump commands

# don't split, don't parse
sudo tcpdump -i eth2 -j adapter --time-stamp-precision=nanoseconds -w "data/out.pcap"

# parse after splitting
#sudo tcpdump -i eth1 -j adapter --time-stamp-precision=nanoseconds -G 30 -w "data/%Y-%m-%d-%H-%M-%S.pcap" -z `pwd`/parse_pcap.py

# split but don't parse
#sudo tcpdump -i eth1 -j adapter --time-stamp-precision=nanoseconds -G 30 -w "data/%Y-%m-%d-%H-%M-%S.pcap"
