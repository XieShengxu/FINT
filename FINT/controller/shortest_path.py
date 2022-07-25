import json


class ShortestPath:

    def __init__(self, edges=[]):
        self.neighbors = {}
        for edge in edges:
            self.addEdge(*edge)

    def addEdge(self, a, b):
        if a not in self.neighbors: self.neighbors[a] = []
        if b not in self.neighbors[a]: self.neighbors[a].append(b)

        if b not in self.neighbors: self.neighbors[b] = []
        if a not in self.neighbors[b]: self.neighbors[b].append(a)

    def get(self, a, b, exclude=lambda node: False):
        # Shortest path from a to b
        return self._recPath(a, b, [], exclude)

    def _recPath(self, a, b, visited, exclude):
        if a == b: return [a]
        new_visited = visited + [a]
        paths = []
        for neighbor in self.neighbors[a]:
            if neighbor in new_visited: continue
            if exclude(neighbor) and neighbor != b: continue
            path = self._recPath(neighbor, b, new_visited, exclude)
            if path: paths.append(path)

        paths.sort(key=len)
        return [a] + paths[0] if len(paths) else None

if __name__ == '__main__':
    def convert(input):
        if isinstance(input, dict):
            return {convert(key): convert(value) for key, value in input.iteritems()}
        elif isinstance(input, list):
            return [convert(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    with open('./topology/topology.json', 'r') as f:
        topo = convert(json.load(f))
        hosts = topo['hosts']
        for host in hosts:
            del hosts[host]['commands']
        switches = []
        for switch in topo['switches']:
            switches.append(switch)
        links = {}
        print hosts
        print switches
        edges = []
        for link in topo['links']:
            link_left = link[0]
            link_right = link[1]
            if 's' in link_left:
                link_left = link_left.split('-')[0]
            if 's' in link_right:
                link_right = link_right.split('-')[0]
            if 's' in link_left:
                if link_left not in links:
                    links[link_left] = {link_right: link[0].split('-')[1]}
                else:
                    links[link_left][link_right] = link[0].split('-')[1]
            if 's' in link_right:
                if link_right not in links:
                    links[link_right] = {link_left: link[1].split('-')[1]}
                else:
                    links[link_right][link_left] = link[1].split('-')[1]
            edges.append((link_left, link_right))
        print 'links: {}'.format(links)
        print 'edges: {}'.format(edges)

    cntSwt = {}

    for switch in switches:
        name = switch
        address = '127.0.0.1:{}'.format(50050 + int(switch[1:]))
        device_id = int(switch[1:])
        print name, address, device_id
        cntSwt[name] = 'sdfa'

    sp = ShortestPath(edges)

    for src_host in hosts:
        for dst_host in hosts:
            if src_host != dst_host:
                path = sp.get(src_host, dst_host)
                print src_host + '->' + dst_host + ': {}'.format(path)
                for i in range(len(path) - 2):
                    ingress_sw = path[i+1]
                    pair_sw = path[i+2]
                    dst_ip_addr = hosts[path[len(path)-1]]['ip'].split('/')[0]
                    print int(links[ingress_sw][pair_sw][1:])
                    print dst_ip_addr