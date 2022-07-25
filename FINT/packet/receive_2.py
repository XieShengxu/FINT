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



_types = {
    0b00: "8 bit",
    0b01: "16 bit",
}


class INTInfo(Packet):
    name = 'INT TYPE'
    # XXField("name", a, 0):  a: default value, b: bit long
    fields_desc = [
        BitField("type", 0, 2),
        BitField("count", 0, 6),  # noqa: E501
        MultipleTypeField(
            [
                (BitField("bitmap_need", 0, 8), lambda pkt:pkt.type == 0),
                (BitField("bitmap_need", 0, 16), lambda pkt:pkt.type == 1)
            ], StrFixedLenField("bitmap_need", "", length=0)),
    ]

    # for i in range(5):
    #     bitmap_add = ConditionalField(MultipleTypeField(
    #             [
    #                 (BitField("bitmap_add %d" % i, 0, 8), lambda pkt:pkt.type == 0),
    #                 (BitField("bitmap_add %d" % i, 0, 16), lambda pkt:pkt.type == 1)
    #             ], StrFixedLenField("bitmap_add %d" % i, "", length=0)),
    #         lambda pkt, j=i: pkt.count - j > 0)
    #
    #     length = ConditionalField(
    #         FieldLenField("length %d" % i, None, fmt="B", length_of="metadata %d" % i, adjust=lambda pkt, l: l + 2),
    #         lambda pkt, j=i: pkt.count - j > 0)
    #     metadata = ConditionalField(
    #         StrLenField("metadata %d" % i, "", length_from=lambda pkt: pkt.length),
    #         lambda pkt, j=i: pkt.count - j > 0)

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_1", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 1 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_1", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 1 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_1", None, fmt="B", length_of="metadata_1", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 1 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_1", "", length_from=lambda pkt: pkt.length_1),
        lambda pkt: pkt.count - 1 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_2", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 2 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_2", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 2 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_2", None, fmt="B", length_of="metadata_2", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 2 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_2", "", length_from=lambda pkt: pkt.length_2),
        lambda pkt: pkt.count - 2 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_3", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 3 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_3", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 3 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_3", None, fmt="B", length_of="metadata_3", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 3 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_3", "", length_from=lambda pkt: pkt.length_3),
        lambda pkt: pkt.count - 3 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_4", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 4 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_4", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 4 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_4", None, fmt="B", length_of="metadata_4", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 4 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_4", "", length_from=lambda pkt: pkt.length_4),
        lambda pkt: pkt.count - 4 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_5", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 5 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_5", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 5 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_5", None, fmt="B", length_of="metadata_5", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 5 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_5", "", length_from=lambda pkt: pkt.length_5),
        lambda pkt: pkt.count - 5 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_6", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 6 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_6", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 6 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_6", None, fmt="B", length_of="metadata_6", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 6 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_6", "", length_from=lambda pkt: pkt.length_6),
        lambda pkt: pkt.count - 6 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_7", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 7 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_7", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 7 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_7", None, fmt="B", length_of="metadata_7", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 7 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_7", "", length_from=lambda pkt: pkt.length_7),
        lambda pkt: pkt.count - 7 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_8", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 8 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_8", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 8 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_8", None, fmt="B", length_of="metadata_8", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 8 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_8", "", length_from=lambda pkt: pkt.length_8),
        lambda pkt: pkt.count - 8 >= 0))

    fields_desc.append(ConditionalField(
        BitField("bitmap_add8_9", 0, 8), lambda pkt: pkt.type == 0 and pkt.count - 9 >= 0))
    fields_desc.append(ConditionalField(
        BitField("bitmap_add16_9", 0, 8), lambda pkt: pkt.type == 1 and pkt.count - 9 >= 0))
    fields_desc.append(ConditionalField(
        FieldLenField("length_9", None, fmt="B", length_of="metadata_9", adjust=lambda pkt, l: l + 1),
        lambda pkt: pkt.count - 9 >= 0))
    fields_desc.append(ConditionalField(
        StrLenField("metadata_9", "", length_from=lambda pkt: pkt.length_9),
        lambda pkt: pkt.count - 9 >= 0))

    def guess_payload_class(self, payload):
        return Packet.guess_payload_class(self, payload)


bind_layers(Ether, INTInfo, type=0x1727)
bind_layers(INTInfo, IP)


class PacketIn:
    def __init__(self, log_level=""):
        if log_level == "debug" or log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.log = logging.getLogger("Packet In")
        self.count = 0
        self.length = 0
        self.int_meta_length = 0
        self.f = open("receive_log.txt", "w")

        self.bitmap_need_len = 8

    def handle_pkt(self, pkt):
        print "\n\n=====Controller got a packet====="
        eth = Ether(str(pkt))
        if eth.type == 0x1727:
            self.f.write("time: %s\n" % time.time())
            self.f.write("pkt len: %d\n" % len(pkt))
            self.count += 1
            print("received int packet count: %d" % self.count)
            self.f.write("received int packet count: %d\n" % self.count)
            
            self.length += len(pkt)
            print("total int packet length: %d" % self.length)
            self.f.write("total int packet length: %d\n" % self.length)

            int_info = eth.getlayer(INTInfo)
            if int_info.type == 0:
                self.int_meta_length += 2 * (int_info.count + 1)
            elif int_info.type == 1:
                self.int_meta_length += 3 * (int_info.count + 1)

            length_list = {}

            for i in range(int_info.count):
                if i == 0:
                    length_list[i] = int_info.length_1
                if i == 1:
                    length_list[i] = int_info.length_1
                if i == 2:
                    length_list[i] = int_info.length_1
                if i == 3:
                    length_list[i] = int_info.length_1
                if i == 4:
                    length_list[i] = int_info.length_1
                if i == 5:
                    length_list[i] = int_info.length_1
                if i == 6:
                    length_list[i] = int_info.length_1
                if i == 7:
                    length_list[i] = int_info.length_1
                if i == 8:
                    length_list[i] = int_info.length_1
                if i == 9:
                    length_list[i] = int_info.length_1

            for i in range(int_info.count):
                self.int_meta_length += length_list[i]

            print("total int packet INT length: %d" % self.int_meta_length)
            self.f.write("total int data length: %d\n" % self.int_meta_length)
            
        sys.stdout.flush()

    def packet_in_listening(self):
        iface = "s17-eth1"
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
