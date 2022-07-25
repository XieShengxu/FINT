# coding=utf-8
import json
import sys
import os
import argparse


class FatTree:
    def __init__(self, k, topo_dir):
        self.k = k
        self.topo_dir = topo_dir
        try:
            self.k = int(k)
        except :
            pass

    def creat_topo(self):
        topo = {}
        topo["hosts"] = {}
        topo["switches"] = {}
        topo["links"] = []

        s_core_num = pow(self.k/2, 2)
        s_aggr_num = pow(self.k, 2)/2
        s_acce_num = pow(self.k, 2)/2
        host_num = self.k * self.k * self.k / 4
        host_num_pod = self.k * self.k / 4

        for i in range(1, 1 + host_num):
            host = {}
            pod_num = (i-1) / (self.k * self.k / 4) + 1
            host_id = (i-1) % (self.k * self.k / 4) + 1

            host.setdefault("ip", "10.0.%d.%d/24" % (pod_num, host_id))
            host.setdefault("mac", "08:00:00:00:%02x:%02x" % (pod_num, host_id))
            host.setdefault("commands", ["route add default gw 10.0.%d.254 dev eth0" % pod_num,
                                         "arp -i eth0 -s 10.0.%d.254 08:00:00:00:%02x:00" % (pod_num, pod_num)])

            for j in range(1, 1 + host_num_pod):
                if j != host_id:
                    # host["commands"].append(
                    #     "arp -i eth0 -s 10.0.%d.%d 08:00:00:00:%02x:%02x" % (pod_num, j, pod_num, j))
                    host["commands"].append(
                        "arp -i eth0 -s 10.0.%d.%d 00:00:00:00:00:%02x" %
                        (pod_num, j, s_core_num + s_aggr_num + ((host_id - 1)/(self.k/2) + 1)))

            topo["hosts"].setdefault("h{}".format(i), host)

        for i in range(1, 1 + s_core_num + s_aggr_num + s_acce_num):
            topo["switches"].setdefault("s%d" % i, {})

        # add link between core switches and aggregate switches
        for i in range(1, 1 + s_core_num):
            for j in range(self.k):
                topo["links"].append(["s%d" % i, "s%d" % (1 + (i-1) / (self.k/2) + s_core_num + j * (self.k / 2))])

        # add link between aggregate switches and access switches
        for i in range(1, 1 + self.k):
            for j in range(1, 1 + self.k/2):
                for k in range(1, 1 + self.k/2):
                    topo["links"].append(["s%d" % ((i-1)*(self.k/2) + s_core_num + j),
                                          "s%d" % ((i-1)*(self.k/2) + s_core_num + s_aggr_num + k)])

        # add link between access switches and hosts
        for i in range(1, 1 + s_acce_num):
            for j in range(1, 1 + self.k/2):
                topo["links"].append(["s%d" % (i + s_core_num + s_aggr_num),
                                      "h%d" % ((i-1)*(self.k/2) + j)])

        with open(self.topo_dir, 'w') as json_file:
            json_file.write(json.dumps(topo))

        print ("fattree.py=>topology file created!")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topo_dir', help='Path to topology json',
                        type=str, required=False, default='./topology.json')
    parser.add_argument('-k', '--k_value', help='The FatRree scale of value K.',
                        type=int, action="store", default=4)
    return parser.parse_args()


if __name__ == "__main__":
    print("-----fattree.py-------")
    args = get_args()
    fat_tree = FatTree(args.k_value, args.topo_dir)
    fat_tree.creat_topo()