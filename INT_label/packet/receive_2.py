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

class PacketIn:
    def __init__(self, log_level=""):
        if log_level == "debug" or log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.log = logging.getLogger("Packet In")
        self.log = logging.getLogger("Packet In")
        self.count = 0
        self.length = 0
        self.int_meta_length = 0
        self.f = open("receive_log2.txt", "w")

    def handle_pkt(self, pkt):
        eth = Ether(str(pkt))
        if eth.type == 0x0700:
            # print "\n\n=====receive SR packet====="
            sr_hdr = eth.getlayer(SR_hdr)
            type_hdr = sr_hdr.getlayer(Type2_hdr)
            int_hdr = type_hdr.getlayer(INT_hdr)
            # print sr_hdr.next_hdr
            if int_hdr.int_num != 0:
                print "\n\n=====receive INT packet====="
                self.f.write("time: %s\n" % time.time())
                self.f.write("pkt len: %d\n" % len(pkt))

                self.count += 1
                print("received int packet count: %d" % self.count)
                self.f.write("received int packet count: %d\n" % self.count)
                
                self.length += len(pkt)
                print("int packet total length: %d" % self.length)
                self.f.write("int packet total length: %d\n" % self.length)
                
                
                self.int_meta_length += int_hdr.int_num * 26 + 2 + sr_hdr.sr_length*2 +2
                print("total int data length: %d" % self.int_meta_length)
                self.f.write("total int data length: %d\n" % self.int_meta_length)
                
                
        sys.stdout.flush()

    def packet_in_listening(self):
        iface = "p3_t1-eth1"
        mac_addr = get_if_hwaddr(iface)
        print ("sniffing on %s / %s" % (iface, mac_addr))

        sys.stdout.flush()
        a = sniff(iface=iface, store=1, prn=lambda x: self.handle_pkt(x),
              filter="ether dst 00:00:00:03:01:01")

        # wrpcap("INT-label.pcap", a)


if __name__ == '__main__':
    # packet_in = PacketIn("debug")
    packet_in = PacketIn()
    packet_in.packet_in_listening()
