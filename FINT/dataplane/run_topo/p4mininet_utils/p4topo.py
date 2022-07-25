import json

from mininet.topo import Topo
from mininet.nodelib import LinuxBridge
import re
from ipaddress import IPv4Network


def ip_address_to_mac(ip):

    if "/" in ip:
        ip = ip.split("/")[0]

    split_ip = map(int, ip.split("."))
    mac_address = '00:%02x' + ':%02x:%02x:%02x:%02x' % tuple(split_ip)
    return mac_address


class AppTopo(Topo):
    """The mininet topology class.

    A custom class is used because the exercises make a few topology assumptions,
    mostly about the IP and MAC addresses.
    """

    def __init__(self, hosts, switches, links, log_dir, bmv2_exe, controlplane=False, **opts):

        Topo.__init__(self, **opts)

        self._hosts = hosts
        self._switches = switches
        self._links = links
        self.log_dir = log_dir

        self.controlplane = controlplane

        self.sw_port_mapping = {}
        self.hosts_info = {}

        self.already_assigned_ips = set()
        self.reserved_ips = {}

        self.create_topo()

    def node_sorting(self, node):

        index = re.findall(r'\d+', node)
        if index:
            index = int(index[0])
        else:
            index = 0
            for i, c in enumerate(node):
                index += ord(c) * (255 * (len(node) - i))
        return index

    def add_switches(self):

        sw_to_id = {}
        sw_id = 1

        for sw in self._switches.keys():
            id = re.findall(r'\d+', sw)
            if id and sw[0] == 's':
                id = int(id[0])
                sw_to_id[sw] = id

        # the sorting does not matter anymore
        # make sure each link's endpoints are ordered alphabetically
        for sw in sorted(self._switches.keys(), key=self.node_sorting):
            sw_attributes = self._switches.get(sw)

            id = sw_to_id.get(sw, None)
            if not id:
                while sw_id in sw_to_id.values():
                    sw_id += 1
                id = sw_id
            if "program" in sw_attributes:
                json_file = sw_attributes["program"]
                self.addP4Switch(sw, log_file="%s/%s.log" % (self.log_dir, sw),
                                 json_path=json_file, device_id=id, **sw_attributes)
            else:
                self.addP4Switch(sw, log_file="%s/%s.log" % (self.log_dir, sw),
                                 device_id=id, **sw_attributes)
            sw_to_id[sw] = id

        return sw_to_id

    def is_host_link(self, link):

        return link['node1'] in self._hosts or link['node2'] in self._hosts

    def get_host_position(self, link):

        return 'node1' if link['node1'] in self._hosts else 'node2'

    def get_sw_position(self, link):

        return 'node1' if link['node1'] in self._switches else 'node2'

    def check_host_valid_ip_from_name(self, host):
        valid = True
        if host[0] == 'h':
            try:
                int(host[1:])
            except:
                valid = False
        else:

            valid = False
        return valid

    def add_cpu_port(self):
        add_bridge = True  # We use the bridge but at the same time we use the bug it has so the interfaces are not
        # added to it, but at least we can clean easily thanks to that

        if self.controlplane:
            sw = None
            for switch in self._switches:
                if self.g.node.get(switch).get('isP4Switch', False):
                    if add_bridge:
                        sw = self.addSwitch("controller", cls=LinuxBridge, dpid='999888777')
                        self.addSwitchPort(switch, sw)
                        print("The switch of controller is added.")
                        add_bridge = False
                    self.addLink(switch, sw, intfName1='%s-eth999' % switch, intfName2='ctl-eth%s' % switch[1:],
                                 deleteIntfs=True)
                    print("The link of %s to controller switch is added." % (switch))
        else:
            print("The controller switch is not set to create.")

    def create_topo(self):

        # adds switches to the topology and sets an ID
        self.add_switches()

        ip_generator = IPv4Network(unicode("10.0.0.0/24")).hosts()

        # add links and configure them: ips, macs, etc
        # assumes hosts are connected to one switch only

        # reserve ips for normal hosts
        for host_name in self._hosts:
            if "ip" not in self._hosts[host_name]:
                if self.check_host_valid_ip_from_name(host_name):
                    host_num = int(host_name[1:])
                    upper_byte = (host_num & 0xff00) >> 8
                    lower_byte = (host_num & 0x00ff)
                    host_ip = "10.0.%d.%d" % (upper_byte, lower_byte)
                    self.reserved_ips[host_name] = host_ip
            else:
                self.reserved_ips[host_name] = self._hosts[host_name]["ip"].split("/")[0]

        for link in self._links:

            if self.is_host_link(link):
                host_name = link[self.get_host_position(link)]
                direct_sw = link[self.get_sw_position(link)]

                if self.check_host_valid_ip_from_name(host_name):
                    host_ip = self.reserved_ips[host_name]

                    # we check if for some reason the ip was already given by the ip_generator. This
                    # can only happen if the host naming is not <h_x>
                    # this should not be possible anymore since we reserve ips for h_x hosts
                    while host_ip in self.already_assigned_ips:
                        host_ip = str(next(ip_generator).compressed)
                    self.already_assigned_ips.add(host_ip)
                else:
                    host_ip = next(ip_generator).compressed
                    # we check if for some reason the ip was already given by the ip_generator. This
                    # can only happen if the host naming is not <h_x>
                    while host_ip in self.already_assigned_ips or host_ip in self.reserved_ips.values():
                        host_ip = str(next(ip_generator).compressed)
                    self.already_assigned_ips.add(host_ip)

                if "mac" not in self._hosts[host_name]:
                    host_mac = ip_address_to_mac(host_ip) % (0)
                else:
                    host_mac = self._hosts[host_name]["mac"]

                # direct_sw_mac = int2mac(direct_sw[1:])

                host_ip = host_ip + "/16"
                if 'ip' in self._hosts[host_name]:
                    host_ip = self._hosts[host_name]['ip']

                self.addHost(host_name, ip=host_ip, mac=host_mac)
                self.addLink(host_name, direct_sw,
                             delay=link['latency'], bw=link['bandwidth'], loss=link['loss'],
                             addr1=host_mac, weight=link["weight"],
                             max_queue_size=link["queue_length"])
                self.addSwitchPort(direct_sw, host_name)
                self.hosts_info[host_name] = {"sw": direct_sw, "ip": host_ip, "mac": host_mac, "mask": 24}

            # switch to switch link
            else:
                self.addLink(link['node1'], link['node2'],
                             delay=link['latency'], bw=link['bandwidth'], loss=link['loss'], weight=link["weight"],
                             max_queue_size=link["queue_length"])
                self.addSwitchPort(link['node1'], link['node2'])
                self.addSwitchPort(link['node2'], link['node1'])

        self.add_cpu_port()
        self.printPortMapping()

    def addP4Switch(self, name, **opts):
        """Add P4 switch to Mininet topology.

        Params:
            name: switch name
            opts: switch options

        Returns:
            switch name
        """
        if not opts and self.sopts:
            opts = self.sopts
        return self.addNode(name, isSwitch=True, isP4Switch=True, **opts)

    def isHiddenNode(self, node):
        """Check if node is a Hidden Node

        Params:
            node: Mininet node

        Returns:
            True if its a hidden node
        """
        return self.g.node[node].get('isHiddenNode', False)

    def isP4Switch(self, node):
        """Check if node is a P4 switch.

        Params:
            node: Mininet node

        Returns:
            True if node is a P4 switch
        """
        return self.g.node[node].get('isP4Switch', False)

    def addSwitchPort(self, sw, node2):
        if sw not in self.sw_port_mapping:
            self.sw_port_mapping[sw] = []
        portno = len(self.sw_port_mapping[sw]) + 1
        self.sw_port_mapping[sw].append((portno, node2))

    def printPortMapping(self):
        port_mapping = {}
        print "Switch port mapping:"
        for sw in sorted(self.sw_port_mapping.keys()):
            print "%s: " % sw,
            port_mapping[sw] = {}
            for portno, node2 in self.sw_port_mapping[sw]:
                print "%d:%s\t" % (portno, node2),
                port_mapping[sw][node2] = portno
            print
        with open('port_mapping.json', 'w') as json_file:
            json_file.write(json.dumps(port_mapping))

def int2mac(switch_number):
    """
    auto generate mac address with the number in string
    @param switch_number: mac address number (int)
    @return: mac address in string
    """
    str_swt = str(hex(switch_number))[2:]
    mac_addr = ''
    for i in range(12):
        if i < 12 - len(str_swt):
            mac_addr += '0'
        else:
            mac_addr += str_swt[i - 12 + len(str_swt)]
        if i % 2 == 1 and i != 11:
            mac_addr += ':'
    return mac_addr