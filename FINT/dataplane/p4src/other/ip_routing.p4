/* -*- P4_16 -*- */

/*
Version: 20210816
Version info: New packet length judgement. If the value exceeds the MTU, no INTinformation is added.
*/

#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_INT = 0x1727;  // for INT packet with ipv4
const bit<16> TYPE_IPV4 = 0x800;

const bit<16> MTU = 1500;


#define MAX_HOPS 6
#define MAX_PORTS 8

// 使用simple_switch_CLI修改时，0 表示第一个值
register<bit<8>>(1) switch_id_reg;

register<bit<16>>(1) bitmap_task_reg;       // the task from controller: 1000111000000000
register<bit<8>>(1) bitmap_num_reg;     // the number of metadata in the task: 4

register<bit<1>>(1) int_support_reg;    // 0: not support INT; 1: support INT
register<bit<48>>(1) int_period_reg;    // set the INT period

register<bit<16>>(1) bitmap_task_remain_reg;
register<bit<8>>(1) bitmap_num_remain_reg;


/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/


typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef bit<48> time_t;

// NOTE: BMv2 target only supports headers with fields totaling a multiple of 8 bits.

header ethernet_h {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_h {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata_s {
    
}

// FIXME: Only ipv4 packets can carry the INT, ipv6 will be support later.
struct headers {
    ethernet_h      ethernet;
    ipv4_h          ipv4;       // only ip packets can carry the INT
}


/************************************************************************
*********************** P A R S E R  ************************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata_s meta,
                inout standard_metadata_t standard_metadata) {

    state start{
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   **************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata_s meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata_s meta,
                  inout standard_metadata_t standard_metadata) {

    register<time_t>(MAX_PORTS) last_time_reg;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    // must to change the mac address
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action set_to_host_bit() {
        //meta.int_support_metadata.to_host = 1;  // for egress control
    }

    table egress_to_host{
        key = {
            standard_metadata.egress_spec : exact;
        }
        actions = {
	        set_to_host_bit;
        }
        size = 256;
    }

    table ipv4_exact {
        key = {
            // do not support two lpm, how to match the 5-tuples?
            hdr.ipv4.srcAddr: exact;
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_exact.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata_s meta,
                 inout standard_metadata_t standard_metadata) {

    apply { }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   ***************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata_s meta) {
     apply {
	    update_checksum(
                hdr.ipv4.isValid(),
                { hdr.ipv4.version,
                  hdr.ipv4.ihl,
                  hdr.ipv4.diffserv,
                  hdr.ipv4.totalLen,
                  hdr.ipv4.identification,
                  hdr.ipv4.flags,
                  hdr.ipv4.fragOffset,
                  hdr.ipv4.ttl,
                  hdr.ipv4.protocol,
                  hdr.ipv4.srcAddr,
                  hdr.ipv4.dstAddr },
                hdr.ipv4.hdrChecksum,
                HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  ********************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  ************************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
