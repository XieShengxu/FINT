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


class SR_hdr(Packet):
    name = 'SR'
    # XXField("name", a, 0):  a: default value, b: bit long
    fields_desc = [
        BitField("next_hdr", 0, 1),
        BitField("rsvd", 0, 7),  # noqa: E501
        FieldLenField("sr_length", None, fmt="B", length_of="sr_s", adjust=lambda pkt, l: l + 1),  # noqa: E501
        StrLenField("sr_s", "", length_from=lambda pkt: pkt.sr_length * 2),
    ]

    def guess_payload_class(self, payload):
        return Packet.guess_payload_class(self, payload)


bind_layers(Ether, SR_hdr, type=0x700)


class INT_hdr(Packet):
    name = 'INT'
    # XXField("name", a, 0):  a: default value, b: bit long
    fields_desc = [
        BitField("type", 0, 1),
        BitField("rsvd", 0, 7),  # noqa: E501
        FieldLenField("int_num", None, fmt="B", length_of="int_s", adjust=lambda pkt, l: l + 1),  # noqa: E501
        StrLenField("int_s", "", length_from=lambda pkt: pkt.int_num * 26),
    ]

    def guess_payload_class(self, payload):
        return Packet.guess_payload_class(self, payload)


bind_layers(Ether, INT_hdr, type=0x701)


class Type2_hdr(Packet):
    name = 'Type2'
    # XXField("name", a, 0):  a: default value, b: bit long
    fields_desc = [
        BitField("type", 0, 16),
    ]

    def guess_payload_class(self, payload):
        return Packet.guess_payload_class(self, payload)


bind_layers(SR_hdr, Type2_hdr, next_hdr=1)
bind_layers(SR_hdr, Type2_hdr, next_hdr=0)
bind_layers(Type2_hdr, INT_hdr, type=0x701)



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
        self.log = logging.getLogger("Packet In")
        self.count = 0
        self.length2ctl = 0
        self.f = open("receive_log3.txt", "w")

    def handle_pkt(self, pkt):
        eth = Ether(str(pkt))
        if eth.type == 0x0701:
            int_hdr = eth.getlayer(INT_hdr)
            if int_hdr.int_num != 0:
                print "\n\n=====receive INT packet====="
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
