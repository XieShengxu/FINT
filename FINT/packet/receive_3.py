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
from scapy.layers.inet import Packet, IP, Ether, ICMP


class PacketIn:
    def __init__(self, log_level=""):
        if log_level == "debug" or log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.log = logging.getLogger("Packet In")
        self.count = 0
        self.length2ctl = 0
        self.f = open("receive_log.txt", "w")

    def handle_pkt(self, pkt):
        print "\n\n=====Controller got a packet====="
        eth = Ether(str(pkt))
        if eth.type == 0x1727:
            self.f.write("time: %s\n" % time.time())
            self.f.write("pkt len: %d\n" % len(pkt))
            
            self.count += 1
            print("received int packet count: %d" % self.count)
            self.f.write("received int packet count: %d\n" % self.count)
            
            self.length2ctl += len(pkt)
            print("total length to ctl: %d" % self.length2ctl)
            self.f.write("total length ti ctl: %d\n" % self.length2ctl)
        sys.stdout.flush()

    def packet_in_listening(self):
        iface = "ctl-eth17"
        mac_addr = get_if_hwaddr(iface)
        print ("sniffing on %s / %s" % (iface, mac_addr))

        sys.stdout.flush()
        a = sniff(iface=iface, store=1, prn=lambda x: self.handle_pkt(x),
              filter="ether proto 5927")

        # wrpcap("INT-label.pcap", a)


if __name__ == '__main__':
    # packet_in = PacketIn("debug")
    packet_in = PacketIn()
    packet_in.packet_in_listening()
