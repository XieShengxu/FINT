#!/usr/bin/env python2
import argparse
import os
import json
from tools import convert, int2mac
from shortest_path import ShortestPath


def parse_topo(topo_file, port_mapping_file):

    hosts = {}  # {'h1': {'ip': '10.0.1.1/24', 'mac': '08:00:00:00:01:11'}, ...}
    switches = {}  # {'s1': '00:00:00:00:00:01', ...}
    links = {}  # {'s1':{'s2':2, 's3':3, ...}, ...}   -> s1:2-s2, s1:3-s3,..


    port_mapping = {}
    with open(port_mapping_file, 'r') as f:
        port_mapping = convert(json.load(f))

    with open(topo_file, 'r') as f:
        topo = convert(json.load(f))
        hosts = topo['hosts']
        for host in hosts:
            del hosts[host]['commands']
        for switch in topo['switches']:
            switches[switch] = int2mac(int(switch[1:]))
        edges = []
        for link in topo['links']:
            link_left = link[0]
            link_right = link[1]
            if 's' in link_left:
                if link_left not in links:
                    links[link_left] = {link_right: port_mapping[link_left][link_right]}
                else:
                    links[link_left][link_right] = port_mapping[link_left][link_right]
            if 's' in link_right:
                if link_right not in links:
                    links[link_right] = {link_left: port_mapping[link_right][link_left]}
                else:
                    links[link_right][link_left] = port_mapping[link_right][link_left]
            edges.append((link_left, link_right))
    # print ("edges: %s" % edges)
    return edges, hosts, switches, links


def main(entry_dir, topo_path, port_mapping_file, choose_meta):
    if not os.path.isdir(entry_dir):
        if os.path.exists(entry_dir):
            raise Exception("'%s' exists and is not a directory!" % entry_dir)
        os.mkdir(entry_dir)

    entries = {}  # {'s1':[entry1, entry2,...], }

    edges, hosts, switches, links = parse_topo(topo_path, port_mapping_file)

    sp = ShortestPath(edges)

    # print (sp.get("h1", "h4"))

    #print ("host: %s" % hosts)
    #print ("switches: %s" % switches)
    #print ("links: %s" % links)

    # Write the rules for ipv4 forwarding
    for src_host in hosts:
        for dst_host in hosts:
            if src_host != dst_host:
                path = sp.get(src_host, dst_host)
                src_ip_addr = hosts[src_host]['ip'].split('/')[0]
                dst_ip_addr = hosts[dst_host]['ip'].split('/')[0]
                # print ('Path is: %s' % path)
                for i in range(len(path) - 2):
                    ingress_sw = path[i + 1]
                    pair_node = path[i + 2]

                    port = links[ingress_sw][pair_node]
                    if 's' in pair_node:
                        dst_mac_addr = switches[pair_node]
                    elif 'h' in pair_node:
                        dst_mac_addr = hosts[dst_host]['mac']
                    else:
                        raise Exception('Error: the node is not switch or host with \'s\' or \'h\'')
                    # print ingress_sw, pair_node, port, dst_mac_addr
                    if ingress_sw not in entries:
                        entries[ingress_sw] = []
                    # table_add table_name action_name match_fields => parameters
                    entries[ingress_sw].append("table_add ipv4_exact ipv4_forward {} {} => {} {}\n"
                                               .format(src_ip_addr, dst_ip_addr, dst_mac_addr, port))
    # print ("entries: %s" % entries)

    for switch in links:
        if switch not in entries:
            entries[switch] = []
        # print (entries[switch])

    for switch in links:
        for pair_node in links[switch]:
            if 'h' in pair_node:
                port2host = links[switch][pair_node]
                if switch not in entries:
                    entries[switch] = []
                entries[switch].append("table_add egress_to_host set_to_host_bit {} => \n".format(int(port2host)))

        if switch not in entries:
            entries[switch] = []

        # # print ("the port number of %s is %s" % (switch, len(links[switch])))
        # add mirroring table with session 100 and egress port 3
        entries[switch].append("mirroring_add 100 %s\n" % (len(links[switch]) + 1))

        entries[switch].append("register_write switch_id_reg 0 {}\n".format(int(switch[1:])))
        if choose_meta == "msr":
            entries[switch].append("register_write bitmap_task_reg 0 {}\n".format(0b1001100000100010))  # for msr
        else:
            entries[switch].append("register_write bitmap_task_reg 0 {}\n".format(0b1010001000100001))  # for msg
        entries[switch].append("register_write bitmap_num_reg 0 5\n")
        entries[switch].append("register_write int_support_reg 0 1\n")
        entries[switch].append("register_write int_period_reg 0 100000\n")      # 100ms
        entries[switch].append("register_write int_para_n_reg 0 3\n")       # para_n = 3

    for switch in links:
        with open("./%s/switch%s.txt" % (entry_dir, switch[1:]), "w") as f:
            for entry in entries[switch]:
                f.write(entry)

        os.system('sudo ./simple_switch_CLI --thrift-port %d < ./%s/switch%s.txt'
                  % (int(switch[1:])-1 + 9090, entry_dir, switch[1:]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('-e', '--entry_dir', help='Path to entries txt',
                        type=str, required=False, default='entries')
    parser.add_argument('-t', '--topo', help='Path to topology json',
                        type=str, required=False, default="../topology/topology.json")
    parser.add_argument('-p', '--port_mapping', help='Path to port_mapping file created by data plane',
                        type=str, required=False, default="../dataplane/topology.json")
    parser.add_argument('-c', '--choose-meta', help='Choose metadata method: msg or msr',
                        type=str, required=False, default="msg")

    args = parser.parse_args()
    if args.choose_meta == "msr":
        print("install entries and set default value of msr!")
    else:
        print("install entries and set default value of msg!")
    main(args.entry_dir, args.topo, args.port_mapping, args.choose_meta)
