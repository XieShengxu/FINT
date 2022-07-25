#!/usr/bin/env python2
import argparse
import os
import json

from tools import convert


def get_witches(topo_file):
    switches = []
    with open(topo_file, 'r') as f:
        topo = convert(json.load(f))
        for switch in topo['switches']:
            switches.append(switch)
    return switches


def main(args):
    switches= get_witches(args.topo)

    print ("switches: %s" % switches)

    # print ("args.all: type: {}, value: {}".format(type(args.all), args.all))
    # print ("args.switch: type: {}, value: {}".format(type(args.switch), args.switch))
    # print ("args.bitmap_task: type: {}, value: {}".format(type(args.bitmap_task), args.bitmap_task))
    # print ("args.int_support: type: {}, value: {}".format(type(args.int_support), args.int_support))
    # print ("args.int_period: type: {}, value: {}".format(type(args.int_period), args.int_period))

    if args.all is True:
        with open("./tmp.txt", "w") as f:
            if args.bitmap_task is not None:
                if not isinstance(args.bitmap_task, int):
                    print("ERROR: bitmap task value type is not int!")
                    exit(0)
                f.write("register_write bitmap_task_reg 0 %d\n" % args.bitmap_task)
                count = 0
                bitmap_task = args.bitmap_task
                for i in range(16):
                    if bitmap_task & 0b1000000000000000 == 0b1000000000000000:
                        count += 1
                    bitmap_task = bitmap_task << 1
                f.write("register_write bitmap_num_reg 0 %d\n" % count)
            if args.int_support is not None:
                if not isinstance(args.int_support, int):
                    print("ERROR: INT support value type is not int!")
                    exit(0)
                f.write("register_write int_support_reg 0 %d\n" % args.int_support)
            if args.int_period is not None:
                if not isinstance(args.int_period, int):
                    print("ERROR: INT period value type is not int!")
                    exit(0)
                f.write("register_write int_period_reg 0 %d\n" % args.int_period)
            if args.int_para_n is not None:
                if not isinstance(args.int_para_n, int):
                    print("ERROR: INT parameter n, value type is not int!")
                    exit(0)
                f.write("register_write int_para_n_reg 0 %d\n" % args.int_para_n)

        for switch in switches:
            os.system('sudo simple_switch_CLI --thrift-port %d < ./tmp.txt' % (int(switch[1:]) - 1 + 9090))
        os.remove("./tmp.txt")

    else:
        if args.switch is not None:
            if not isinstance(args.switch, int):
                print("ERROR: switch id value type is not int!")
                exit(0)

            with open("./tmp.txt", "w") as f:
                if args.bitmap_task is not None:
                    if not isinstance(args.bitmap_task, int):
                        print("ERROR: bitmap task value type is not int!")
                        exit(0)
                    f.write("register_write bitmap_task_reg 0 %d\n" % args.bitmap_task)
                    count = 0
                    bitmap_task = args.bitmap_task
                    for i in range(16):
                        if bitmap_task & 0b1000000000000000 == 0b1000000000000000:
                            count += 1
                        bitmap_task = bitmap_task << 1
                    f.write("register_write bitmap_num_reg 0 %d\n" % count)
                if args.int_support is not None:
                    if not isinstance(args.int_support, int):
                        print("ERROR: INT support value type is not int!")
                        exit(0)
                    f.write("register_write int_support_reg 0 %d\n" % args.int_support)
                if args.int_period is not None:
                    if not isinstance(args.int_period, int):
                        print("ERROR: INT period value type is not int!")
                        exit(0)
                    f.write("register_write int_period_reg 0 %d\n" % args.int_period)
                if args.int_para_n is not None:
                    if not isinstance(args.int_para_n, int):
                        print("ERROR: INT parameter n, value type is not int!")
                        exit(0)
                    f.write("register_write int_para_n_reg 0 %d\n" % args.int_para_n)
            # print('sudo simple_switch_CLI --thrift-port %d = ./tmp.txt' % (args.switch - 1 + 9090))
            os.system('sudo simple_switch_CLI --thrift-port %d < ./tmp.txt' % (args.switch - 1 + 9090))
            os.remove("./tmp.txt")


def get_args():
    cwd = os.getcwd()
    default_topo_json_file = os.path.join(cwd, '../topology/topology.json')
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--topo', help='Path to topology json.',
                        type=str, required=False, default=default_topo_json_file)

    parser.add_argument('-a', '--all', help='Set all switches together.',
                        action='store_true', required=False, default=None)

    parser.add_argument('-s', '--switch', help='switch id for the switch setting, value 1 for s1.',
                        type=int, action="store", default=None)

    parser.add_argument('-bt', '--bitmap-task', help='bitmap task setting.',
                        type=int, action="store", required=False, default=None)

    parser.add_argument('-sp', '--int-support', help='INT supporting setting. 1 for support and 0 for not.',
                        type=int, action="store", required=False, default=None)

    parser.add_argument('-p', '--int-period', help='set int period.',
                        type=int, action="store", required=False, default=None)

    parser.add_argument('-n', '--int-para-n', help='set int parameter n.',
                        type=int, action="store", required=False, default=None)

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    main(args)
