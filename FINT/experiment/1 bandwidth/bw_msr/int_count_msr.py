#!/usr/bin/env python
# -*-coding:utf-8-*-
import sys
import struct
import os
import logging
import binascii
import time
import argparse

from scapy.all import sniff, bind_layers
from scapy.all import BitField, ConditionalField, FieldLenField, StrLenField, MultipleTypeField, StrFixedLenField
from scapy.layers.inet import Packet, IP, Ether, ICMP

# import redis


_types = {
    0b00: "8 bit",
    0b01: "16 bit",
}

bitmap_metadata = {
    'msg': {
        0b1000000000000000: "switch id",  # ##
        0b0100000000000000: "ingress timestamp",
        0b0010000000000000: "egress timestamp",  # ##
        0b0001000000000000: "packet received count",
        0b0000100000000000: "packet looup count",
        0b0000010000000000: "pakcet match count",
        0b0000001000000000: "link speed",  # ##
        0b0000000100000000: "delay",
        0b0000000010000000: "packet dropped count",
        0b0000000001000000: "packet drop ratio",
        0b0000000000100000: "link utilization",  # ##
        0b0000000000010000: "flow count",
        0b0000000000001000: "queue depth",
        0b0000000000000100: "queue id",
        0b0000000000000010: "packet's input port",
        0b0000000000000001: "packet's output port"  # ##
    },
    'msr': {
        0b1000000000000000: "switch id",  # ##
        0b0100000000000000: "packet's input port",
        0b0010000000000000: "packet drop ratio",
        0b0001000000000000: "packet's output port",  # ##
        0b0000100000000000: "link speed",  # ##
        0b0000010000000000: "queue depth",
        0b0000001000000000: "delay",
        0b0000000100000000: "packet lookup count",
        0b0000000010000000: "ingress timestamp",
        0b0000000001000000: "packet dropped count",
        0b0000000000100000: "link utilization",  # ##
        0b0000000000010000: "queue id",
        0b0000000000001000: "packet match count",
        0b0000000000000100: "flow count",
        0b0000000000000010: "egress timestamp",  # ##
        0b0000000000000001: "packet received count"
    }
}

metadata_width = {
    'msg': {
        0b1000000000000000: 1,  #  **   ##
        0b0100000000000000: 6,
        0b0010000000000000: 6,  #  **   ##
        0b0001000000000000: 6,  #       ##
        0b0000100000000000: 6,  #       ##
        0b0000010000000000: 6,  #       ##
        0b0000001000000000: 4,  #  **   ##
        0b0000000100000000: 4,
        0b0000000010000000: 4,
        0b0000000001000000: 2,
        0b0000000000100000: 2,  #  **
        0b0000000000010000: 2,
        0b0000000000001000: 2,
        0b0000000000000100: 1,
        0b0000000000000010: 1,  #       ##
        0b0000000000000001: 1   #  **   ##
    },
    'msr': {
        0b1000000000000000: 1,  #  **   ##
        0b0100000000000000: 1,  #       ##
        0b0010000000000000: 2,
        0b0001000000000000: 1,  #  **   ##
        0b0000100000000000: 4,  #  **   ##
        0b0000010000000000: 2,
        0b0000001000000000: 4,
        0b0000000100000000: 6,
        0b0000000010000000: 6,  #       ##
        0b0000000001000000: 4,
        0b0000000000100000: 2,  #  **
        0b0000000000010000: 1,
        0b0000000000001000: 6,  #       ##
        0b0000000000000100: 2,
        0b0000000000000010: 6,  #  **   ##
        0b0000000000000001: 6   #        ##
    }
}


class INTInfo(Packet):
    name = 'INT TYPE'
    # XXField("name", a, 0):  a: default value, b: bit long
    fields_desc = [
        BitField("type", 0, 2),
        BitField("count", 0, 6),  # noqa: E501
        MultipleTypeField(
            [
                (BitField("bitmap_need", 0, 8), lambda pkt: pkt.type == 0),
                (BitField("bitmap_need", 0, 16), lambda pkt: pkt.type == 1)
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
    def __init__(self, log_level="", method='msg', bitmap_task=0b1010001000100001):
        if log_level == "debug" or log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        self.log = logging.getLogger("Packet In")

        # r_br: Redis for recording Bitmap Received
        # switch Id
        # self.r_br = redis.Redis(host='localhost', port=6379, decode_responses=True)

        self.bitmap_task = bitmap_task
        self.method = method
        self.bitmap_task_len = 16
        self.bitmap_task_location = {}

        self.bitmap_need_len = 8

        count = 0
        for i in range(self.bitmap_task_len):
            if (self.bitmap_task & pow(2, self.bitmap_task_len - i - 1)) == pow(2, self.bitmap_task_len - i - 1):
                self.bitmap_task_location[count] = pow(2, self.bitmap_task_len - i - 1)
                count += 1
        self.log.debug("bitmap task location: %s" % self.bitmap_task_location)

        self.load_sum = 0
        self.int_pkt_count = 0

        self.f = open("ctl_record.txt", "w")
        self.f.write("INT packet count  |  packet load of INT  |  INT load sum\n")

    def decode_bitmap(self, bitmap_add):
        bitmap_add2bitmap_task = 0
        for i in range(self.bitmap_need_len):
            if (bitmap_add & pow(2, self.bitmap_need_len - i - 1)) == pow(2, self.bitmap_need_len - i - 1):
                bitmap_add2bitmap_task = self.bitmap_task_location[i] | bitmap_add2bitmap_task
        self.log.debug("bitmap_add2bitmap_task: %s" % bin(bitmap_add2bitmap_task)[2:])
        return bitmap_add2bitmap_task

    def handle_pkt(self, pkt):
        # print "\n\n=====Controller got a packet====="
        eth = Ether(str(pkt))
        if eth.type == 0x1727:
            self.int_pkt_count += 1

            int_info = eth.getlayer(INTInfo)
            # int_info.show()

            print('\n')
            print(time.time())
            self.log.info('===*  INT packet  *===')
            self.log.info("INT type: %d" % int_info.type)
            self.log.info("INT count: %d" % int_info.count)
            self.log.debug("INT bitmap need: %s" % int_info.bitmap_need)
            self.log.info("INT bitmap need: %s" % bin(int_info.bitmap_need)[2:])
            if int_info.type == 0:
                self.bitmap_need_len = 8
            elif int_info.type == 1:
                self.bitmap_need_len = 16

            bitmap_add_list = {}
            metadata_list = {}
            if int_info.type == 0:
                for i in range(int_info.count):
                    if i == 0:
                        bitmap_add_list[i] = int_info.bitmap_add8_1
                        metadata_list[i] = bytes(int_info.metadata_1)
                    if i == 1:
                        bitmap_add_list[i] = int_info.bitmap_add8_2
                        metadata_list[i] = bytes(int_info.metadata_2)
                    if i == 2:
                        bitmap_add_list[i] = int_info.bitmap_add8_3
                        metadata_list[i] = bytes(int_info.metadata_3)
                    if i == 3:
                        bitmap_add_list[i] = int_info.bitmap_add8_4
                        metadata_list[i] = bytes(int_info.metadata_4)
                    if i == 4:
                        bitmap_add_list[i] = int_info.bitmap_add8_5
                        metadata_list[i] = bytes(int_info.metadata_5)
                    if i == 5:
                        bitmap_add_list[i] = int_info.bitmap_add8_6
                        metadata_list[i] = bytes(int_info.metadata_6)
                    if i == 6:
                        bitmap_add_list[i] = int_info.bitmap_add8_7
                        metadata_list[i] = bytes(int_info.metadata_7)
                    if i == 7:
                        bitmap_add_list[i] = int_info.bitmap_add8_8
                        metadata_list[i] = bytes(int_info.metadata_8)
                    if i == 8:
                        bitmap_add_list[i] = int_info.bitmap_add8_9
                        metadata_list[i] = bytes(int_info.metadata_9)
                    if i == 9:
                        bitmap_add_list[i] = int_info.bitmap_add8_10
                        metadata_list[i] = bytes(int_info.metadata_10)
            elif int_info.type == 1:
                for i in range(int_info.count):
                    if i == 0:
                        bitmap_add_list[i] = int_info.bitmap_add16_1
                        metadata_list[i] = bytes(int_info.metadata_1)
                    if i == 1:
                        bitmap_add_list[i] = int_info.bitmap_add16_2
                        metadata_list[i] = bytes(int_info.metadata_2)
                    if i == 2:
                        bitmap_add_list[i] = int_info.bitmap_add16_3
                        metadata_list[i] = bytes(int_info.metadata_3)
                    if i == 3:
                        bitmap_add_list[i] = int_info.bitmap_add16_4
                        metadata_list[i] = bytes(int_info.metadata_4)
                    if i == 4:
                        bitmap_add_list[i] = int_info.bitmap_add16_5
                        metadata_list[i] = bytes(int_info.metadata_5)
                    if i == 5:
                        bitmap_add_list[i] = int_info.bitmap_add16_6
                        metadata_list[i] = bytes(int_info.metadata_6)
                    if i == 6:
                        bitmap_add_list[i] = int_info.bitmap_add16_7
                        metadata_list[i] = bytes(int_info.metadata_7)
                    if i == 7:
                        bitmap_add_list[i] = int_info.bitmap_add16_8
                        metadata_list[i] = bytes(int_info.metadata_8)
                    if i == 8:
                        bitmap_add_list[i] = int_info.bitmap_add16_9
                        metadata_list[i] = bytes(int_info.metadata_9)
                    if i == 9:
                        bitmap_add_list[i] = int_info.bitmap_add16_10
                        metadata_list[i] = bytes(int_info.metadata_10)

            load = 0
            if int_info.type == 0:
                load += 2
            elif int_info.type == 1:
                load += 3

            for i in range(int_info.count):
                self.log.info("===>  int data %d" % (i + 1))
                bitmap_add = bitmap_add_list[i]  # int
                self.log.debug(bitmap_add)
                bitmap_add_task = self.decode_bitmap(bitmap_add)
                self.log.info("bitmap_add2task: %s" % bin(bitmap_add_task)[2:])
                if bitmap_add_task == self.bitmap_task:
                    self.log.debug("bitmap added done: %s" % bin(bitmap_add_task)[2:])
                data = metadata_list[i]

                if int_info.type == 0:
                    load += 2  # bitmap_add 1 bit; length 1 bit
                elif int_info.type == 1:
                    load += 3  # bitmap_add 2 bit; length 1 bit

                width = 0
                for j in range(self.bitmap_task_len):
                    position = pow(2, self.bitmap_task_len - j - 1)
                    if (bitmap_add_task & position) == position:
                        meta = bitmap_metadata[self.method][position]
                        # self.log.debug("width: %d" % width)
                        value = int(str(binascii.b2a_hex(data[width: width + metadata_width[self.method][position]])),
                                    16)
                        # self.log.debug("meta: %s" % meta)
                        # self.log.debug("value: %s" % value)
                        self.log.info("%s: %s" % (meta, value))
                        width += metadata_width[self.method][position]

                        # self.log.debug(str(binascii.b2a_hex(data[0])))  # to HEX str
                        # self.log.debug(int(str(binascii.b2a_hex(data[0])), 16))  # to DEC
                        # self.log.debug(bin(int('1'+str(binascii.b2a_hex(data[0])), 16))[3:])  # to BIN binary
                        # self.log.debug(bin(int('1'+str(binascii.b2a_hex(data[1:5])), 16))[3:])
                        # self.r_br.set('')
                        # int_info.bitmap_add8_1
                load += width
            self.load_sum += load

            self.f.write("INT packet %d:   %d   --   %d\n" % (self.int_pkt_count, load, self.load_sum))

        sys.stdout.flush()

    def packet_in_listening(self):
        if len(sys.argv) < 2:
            iface = 's17-eth999'
        else:
            iface = sys.argv[1]

        print "sniffing on %s" % iface
        sys.stdout.flush()
        sniff(iface=iface,
              prn=lambda x: self.handle_pkt(x))


if __name__ == '__main__':
    # bitmap_task msg: 0b1010001000100001 => 41505
    # bitmap_task msg: 0b1011111000000011 => 48643

    # bitmap_task msr: 0b1001100000100010 => 38946
    # bitmap_task msr: 0b1101100010001011 => 55435
    packet_in = PacketIn(bitmap_task=38946, method='msr')
    packet_in.packet_in_listening()
