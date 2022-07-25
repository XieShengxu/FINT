#!/usr/bin/env python
# -*-coding:utf-8-*-
import sys
import struct
import os
import logging
import binascii
import time

from scapy.all import sniff, bind_layers, get_if_list, get_if_hwaddr, wrpcap
from scapy.all import BitField, ConditionalField, FieldLenField, StrLenField, MultipleTypeField, StrFixedLenField
from scapy.layers.inet import Packet, IP, Ether, ICMP, UDP


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in ifs:
        if "eth0" in i:
            iface=i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface
    
    
class PacketIn:
    def __init__(self, log_level=""):
        if log_level == "debug" or log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.log = logging.getLogger("Packet In")
        self.count = 0
        self.length = 0
        self.f = open("receive_log.txt", "w")

    def handle_pkt(self, pkt):
        print "\n\n=====receive a packet====="
        eth = Ether(str(pkt))
        if eth.type == 0x0800:
            ip = eth.getlayer(IP)
            if ip.proto == 17:
                udp = ip.getlayer(UDP)
                if udp.dport == 9999:
                    # print("time: %s" % time.time())
                    self.f.write("time: %s\n" % time.time())
                    # print("pkt len: %d" % len(pkt))
                    self.f.write("pkt len: %d\n" % len(pkt))
                    self.count += 1
                    print("received packet count: %d" % self.count)
                    self.f.write("received packet count: %d\n" % self.count)
        sys.stdout.flush()

    def packet_in_listening(self):
        iface = get_if()
        mac_addr = get_if_hwaddr(iface)
        print ("sniffing on %s / %s" % (iface, mac_addr))

        sys.stdout.flush()
        a = sniff(iface=iface, store=1, prn=lambda x: self.handle_pkt(x),
              filter="ether dst {}".format(mac_addr))

        # wrpcap("INT-label.pcap", a)


if __name__ == '__main__':
    # packet_in = PacketIn("debug")
    packet_in = PacketIn()
    packet_in.packet_in_listening()
