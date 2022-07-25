#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import time
import multiprocessing as mp

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, get_if_addr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

sleep_time = 0.003  # s: for control the same pps 


class SendUdpPacket:
    def __init__(self, method='c'):
        self.iface = self.get_if()
        self.src_mac = get_if_hwaddr(self.iface)
        self.src_ip = get_if_addr(self.iface)


        if method == 'r':
            self.send_random_rate()
        elif method == "lr":
            self.send_law_random_rate()
        else:
            self.send_const_rate()

    def get_if(self):
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

    def send_const_rate(self):
        f = open("send_log.txt", "w")
        data = '\x77' * 300
        count = 0
        length = 0
        start_time = time.time()
        cur_time = time.time()
        while cur_time - start_time < 100:
            p = mp.Process(target=self.packet_send, args=(data,))
            p.start()
            # self.packet_send(data)

            pkt_len = len(data)+14+20+8
            count += 1
            print("udp packet send number: %d" % count)
            f.write("udp packet send number: %d\n" % count)
            length += pkt_len
            print("udp packet send length: %d" % length)
            f.write("udp packet send length: %d\n" % length)
            cur_time = time.time()
            time.sleep(sleep_time)


    def send_law_random_rate(self):
        f = open("send_log.txt", "w")
        count = 0
        length = 0
        start_time = time.time()
        cur_time = time.time()
        while cur_time - start_time < 100:
            payload_len = random.randint(20, 1000)
            data = '\x77' * payload_len
            p = mp.Process(target=self.packet_send, args=(data,))
            p.start()
            # self.packet_send(data)

            pkt_len = len(data)+14+20+8
            # print("len of pkt: {}".format(pkt_len))
            
            count += 1
            print("udp packet send number: %d" % count)
            f.write("udp packet send number: %d\n" % count)
            length += pkt_len
            print("udp packet send length: %d" % length)
            f.write("udp packet send length: %d\n" % length)
            cur_time = time.time()
            time.sleep(sleep_time)

    def send_random_rate(self):
        f = open("send_log.txt", "w")
        count = 0
        length = 0
        start_time = time.time()
        cur_time = time.time()
        while cur_time - start_time < 500:
            payload_len = random.randint(20, 1500 - 14 - 20 - 8)  # - len(eth_h) - len(ip_h) - len(udp_h)
            data = '\x77' * payload_len
            p = mp.Process(target=self.packet_send, args=(data,))
            p.start()
            # self.packet_send(data)

            pkt_len = len(data)+14+20+8+16  # sr_h
            print("len of pkt: {}".format(pkt_len))
            f.write("len of pkt: {}\n".format(pkt_len))
            # time.sleep(sleep_time)
            count += 1
            print("udp packet send number: %d" % count)
            f.write("udp packet send number: %d\n" % count)
            length += pkt_len
            print("udp packet send length: %d" % length)
            f.write("udp packet send length: %d\n" % length)
            cur_time = time.time()
            time.sleep(sleep_time)

    def packet_send(self, data):
        pkt = Ether(src=self.src_mac, dst='00:00:00:03:01:01', type=1792)
        pkt = pkt / '\x80\x05' / '\x00\x01' / '\x00\x01' / '\x00\x03' / '\x00\x03' / '\x80\x03' / '\x07\x01' / '\x00\x00'
        pkt = pkt / IP(src=self.src_ip, dst='10.3.1.1') / UDP(dport=9999)
        pkt = pkt / data
        if len(pkt) <= 1500:
            sendp(pkt, iface=self.iface, verbose=False)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sendPacket = SendUdpPacket()
    else:
        sendPacket = SendUdpPacket(method=sys.argv[1])
