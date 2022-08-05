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


#define MAX_HOPS 5
#define MAX_PORTS 8

// 使用simple_switch_CLI修改时，0 表示第一个值
register<bit<8>>(1) switch_id_reg;

register<bit<16>>(1) bitmap_task_reg;       // the task from controller: 1000111000000000
register<bit<8>>(1) bitmap_num_reg;     // the number of metadata in the task: 4

register<bit<1>>(1) int_support_reg;    // 0: not support INT; 1: support INT
register<bit<48>>(1) int_period_reg;    // set the INT period
register<bit<16>>(1)  int_para_n_reg;   // set the parameter of n

register<bit<16>>(MAX_PORTS) bitmap_task_remain_reg;
register<bit<1>>(MAX_PORTS) int_processing_reg;

// bytes
// enum bit<8> md_width {
#define MDW1 1
#define MDW2 1
#define MDW3 2
#define MDW4 1
#define MDW5 4
#define MDW6 2
#define MDW7 4
#define MDW8 6
#define MDW9 6
#define MDW10 4
#define MDW11 2
#define MDW12 1
#define MDW13 6
#define MDW14 2
#define MDW15 6
#define MDW16 6
//}

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

/*

0      1       7
|| type | count | bitmap_need || bitmap_add | length | metadata ||

*/


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

//****** INT Stack ********//

// INT header
header intType_8_h {
    bit<2>      type;
    bit<6>      count;
    bit<8>      bitmap_need;
}
header intType_16_h {
    bit<2>      type;
    bit<6>      count;
    bit<16>     bitmap_need;
}

struct intType_top {
    bit<2>      type;
    bit<6>      count;
}

// headers of bitmap_add
header intData_8_h {
    bit<8>  bitmap_add;
    bit<8>  length;
    varbit<1464> metadata;
}
header intData_16_h {
    bit<16>  bitmap_add;
    bit<8>  length;
    varbit<1464> metadata;
}

struct intData_8_top {
    bit<8>  bitmap_add;
    bit<8>  length;
}
struct intData_16_top {
    bit<16>  bitmap_add;
    bit<8>  length;
}


// headers of bitmap_add
header intData_add_8_h {
    bit<8>  bitmap_add;
    bit<8>  length;
}
header intData_add_16_h {
    bit<16>  bitmap_add;
    bit<8>  length;
}

/*******  metadata  ********/

header md_swId_h {
    bit<8>  swId;  // switch
}
header md_inTs_h {
    bit<48>     inTs;  // ingress timestamp
}
header md_egTs_h {
    bit<48>     egTs;  // egress timestamp
}
header md_prc_h {
    bit<48>     prc;      // packet received count
}
header md_plc_h {
    bit<48> plc;  // packet looup count
}
header md_pmc_h {
    bit<48>     pmc;  // pakcet match count
}
header md_ls_h {
    bit<32> ls;  // link speed
}
header md_delay_h {
    bit<32>     delay;  // delay
}
header md_pdc_h {
    bit<32>      pdc; // packet dropped count
}
header md_pdr_h {
    bit<16>     pdr;  // packet drop ratio
}
header md_lu_h {
    bit<16>     lu;   // link utilization
}
header md_fc_h {
    bit<16>     fc;  // flow count
}
header md_qd_h {
    bit<16>    qd;  // queue depth
}
header md_qId_h {
    bit<8>      qId;  // queue id
}
header md_pip_h {
    bit<8>      pip;  // packet's input port
}
header md_pop_h {
    bit<8>    pop;  // packet's output port
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

struct parser_metadata_s {
    bit<6>  remaining;

    bit<2>  intType_type;
}

struct int_support_metadata_s {
    bit<1>  to_host;    // to_host = 1; means the pair of the port that the packet egress is host
    bit<1>  bitmap_need_flag;
    bit<16> bitmap_need;
    bit<32> egress_port;

    bit<1>  int_processing;
    bit<16> int_length;
}

struct metadata_s {
    parser_metadata_s       parser_metadata;
    int_support_metadata_s  int_support_metadata;
}

// FIXME: Only ipv4 packets can carry the INT, ipv6 will be support later.
struct headers {
    ethernet_h      ethernet;
    intType_8_h     intType_8;
    intType_16_h    intType_16;

    // add int data
    intData_add_8_h     intData_add_8;
    intData_add_16_h    intData_add_16;
    md_swId_h       md_swId;
    md_pip_h        md_pip;
    md_pdr_h        md_pdr;
    md_pop_h        md_pop;
    md_ls_h         md_ls;
    md_qd_h         md_qd;
    md_delay_h      md_delay;
    md_plc_h        md_plc;
    md_inTs_h       md_inTs;
    md_pdc_h        md_pdc;
    md_lu_h         md_lu;
    md_qId_h        md_qId;
    md_pmc_h        md_pmc;
    md_fc_h         md_fc;
    md_egTs_h       md_egTs;
    md_prc_h        md_prc;

    intData_8_h[MAX_HOPS]     intData_8;
    intData_16_h[MAX_HOPS]    intData_16;
    ipv4_h                  ipv4;       // only ip packets can carry the INT
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
            TYPE_INT: parse_intType;
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_intType {
        meta.parser_metadata.intType_type = packet.lookahead<intType_top>().type;
        transition select (meta.parser_metadata.intType_type){
            0: parse_intType_8;
            1: parse_intType_16;
            default: accept;
        }
    }

    state parse_intType_8 {
        packet.extract(hdr.intType_8);
        meta.parser_metadata.remaining = hdr.intType_8.count;
        meta.int_support_metadata.int_length = 2;
        transition select(meta.parser_metadata.remaining) {
            0: parse_ipv4;
            default: parse_intData_8;
        }
    }
    state parse_intData_8 {
        bit<16> n = (bit<16>)packet.lookahead<intData_8_top>().length;
        meta.int_support_metadata.int_length = meta.int_support_metadata.int_length + 2 + n;
        packet.extract(hdr.intData_8.next, (bit<32>)(n * 8));

        meta.parser_metadata.remaining = meta.parser_metadata.remaining - 1;
        transition select(meta.parser_metadata.remaining) {
            0: parse_ipv4;
            default: parse_intData_8;
        }
    }

    state parse_intType_16 {
        packet.extract(hdr.intType_16);
        meta.parser_metadata.remaining = hdr.intType_16.count;
        meta.int_support_metadata.int_length = 3;
        transition select(meta.parser_metadata.remaining) {
            0: parse_ipv4;
            default: parse_intData_16;
        }
    }
    state parse_intData_16 {
        bit<16> n = (bit<16>)packet.lookahead<intData_16_top>().length;
        meta.int_support_metadata.int_length = meta.int_support_metadata.int_length + 3 + n;
        packet.extract(hdr.intData_16.next, (bit<32>)(n * 8));

        meta.parser_metadata.remaining = meta.parser_metadata.remaining - 1;
        transition select(meta.parser_metadata.remaining) {
            0: parse_ipv4;
            default: parse_intData_16;
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
        meta.int_support_metadata.to_host = 1;  // for egress control
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
            meta.int_support_metadata.to_host = 0;
            egress_to_host.apply();
            meta.int_support_metadata.egress_port = (bit<32>)standard_metadata.egress_spec;

            /***************************************************
            ****  calculate the INT info should maintained  ****
            ***************************************************/
            bit<1> int_support;
            int_support_reg.read(int_support, 0);
            if (int_support == 1) {
                bit<1> int_processing;
                int_processing_reg.read(int_processing, meta.int_support_metadata.egress_port);
                if (int_processing == 0){
                    int_processing_reg.write(meta.int_support_metadata.egress_port, 1);
                    meta.int_support_metadata.int_processing = 1;
                    time_t cur_time = standard_metadata.ingress_global_timestamp;
                    time_t last_time;
                    last_time_reg.read(last_time, meta.int_support_metadata.egress_port);

                    bit<16> bitmap_task;
                    bitmap_task_reg.read(bitmap_task, 0);
                    bit<16> bitmap_task_remain;
                    bitmap_task_remain_reg.read(bitmap_task_remain, meta.int_support_metadata.egress_port);

                    //log_msg("cur_time={}, last_time={}",{cur_time, last_time});
                    time_t int_period;
                    int_period_reg.read(int_period, 0);
                    // 如果超过遥测周期，则重置所有需要遥测的数据
                    if (cur_time - last_time > int_period){
                        bitmap_task_reg.read(bitmap_task_remain, 0);
                        bitmap_task_remain_reg.write(meta.int_support_metadata.egress_port, bitmap_task_remain);

                        last_time_reg.write(meta.int_support_metadata.egress_port, cur_time);
                    }

                    // for a new packet
                    if (hdr.ethernet.etherType == TYPE_IPV4){
                        /*
                          **** 每个数据包在MTU限制内都添加满  ****
                        */
                        bit<16> delta_tmp = (bit<16>)MTU - (bit<16>)standard_metadata.packet_length;
                        // log_msg("packet length: {}", {standard_metadata.packet_length}); // 包含头部字段的长度
                        bit<16> para_n = 0;
                        int_para_n_reg.read(para_n, 0);
                        bit<16> delta = (bit<16>)standard_metadata.packet_length * para_n;
                        if (delta_tmp < delta){
                            delta = delta_tmp;
                        }
                        bit<16> bitmap_need = 0;

                        // 如果还在遥测周期内，则检查是否有需要遥测的数据
                        if (bitmap_task_remain > 0 && (delta > (3 + 3 * MAX_HOPS))){
                            /*
                              **** 计算bitmap_need, 根据贪心算法选择元数据  ****
                            */
                            delta = delta - 3 - 3 * MAX_HOPS;
                            if ( bitmap_task & 0b1000000000000000 == 0b1000000000000000){
                                // 先按16位不断左移填，最后再根据bitmap_num，将数据移到最左边，16(8) - bitmap_num;
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b1000000000000000 == 0b1000000000000000) && (delta > (bit<16>)(MDW1*MAX_HOPS))){ // ******* delta ******
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW1 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0100000000000000 == 0b0100000000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0100000000000000 == 0b0100000000000000) && (delta > (bit<16>)(MDW2*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW2 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0010000000000000 == 0b0010000000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0010000000000000 == 0b0010000000000000) && (delta > (bit<16>)(MDW3*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW3 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0001000000000000 == 0b0001000000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0001000000000000 == 0b0001000000000000) && (delta > (bit<16>)(MDW4*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW4 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000100000000000 == 0b0000100000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000100000000000 == 0b0000100000000000) && (delta > (bit<16>)(MDW5*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW5 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000010000000000 == 0b0000010000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000010000000000 == 0b0000010000000000) && (delta > (bit<16>)(MDW6*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW6 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000001000000000 == 0b0000001000000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000001000000000 == 0b0000001000000000) && (delta > (bit<16>)(MDW7*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW7 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000100000000 == 0b0000000100000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000100000000 == 0b0000000100000000) && (delta > (bit<16>)(MDW8*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW8 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000010000000 == 0b0000000010000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000010000000 == 0b0000000010000000) && (delta > (bit<16>)(MDW9*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW9 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000001000000 == 0b0000000001000000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000001000000 == 0b0000000001000000) && (delta > (bit<16>)(MDW10*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW10 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000100000 == 0b0000000000100000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000100000 == 0b0000000000100000) && (delta > (bit<16>)(MDW11*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW11 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000010000 == 0b0000000000010000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000010000 == 0b0000000000010000) && (delta > (bit<16>)(MDW12*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW12 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000001000 == 0b0000000000001000){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000001000 == 0b0000000000001000) && (delta > (bit<16>)(MDW13*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW13 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000000100 == 0b0000000000000100){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000000100 == 0b0000000000000100) && (delta > (bit<16>)(MDW14*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW14 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000000010 == 0b0000000000000010){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000000010 == 0b0000000000000010) && (delta > (bit<16>)(MDW15*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW15 * MAX_HOPS);
                                }
                            }
                            if ( bitmap_task & 0b0000000000000001 == 0b0000000000000001){
                                bitmap_need = bitmap_need << 1;
                                if ((bitmap_task_remain & 0b0000000000000001 == 0b0000000000000001) && (delta > (bit<16>)(MDW16*MAX_HOPS))){
                                    bitmap_need = bitmap_need + 1;
                                    delta = delta - (bit<16>)(MDW16 * MAX_HOPS);
                                }
                            }
                        }

                        if (bitmap_need > 0){
                            meta.int_support_metadata.bitmap_need_flag = 1;

                            bit<8> bitmap_num;
                            bitmap_num_reg.read(bitmap_num, 0);
                            meta.int_support_metadata.bitmap_need = bitmap_need << (bit<8>)(16 - bitmap_num);
                        }
                        else {
                            int_processing_reg.write(meta.int_support_metadata.egress_port, 0);
                        }
                    }
                }
            }

            if ((hdr.ethernet.etherType == TYPE_INT || meta.int_support_metadata.bitmap_need_flag == 1) && meta.int_support_metadata.to_host == 1 && standard_metadata.instance_type == 0){
                //non clonned packets have an instance_type of 0, so then we clone it.
                // using the mirror ID = 100. That in combination with the control plane, will
                //select to which port the packet has to be cloned to.
                clone3(CloneType.I2E, 100, meta);
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata_s meta,
                 inout standard_metadata_t standard_metadata) {

    apply {
        if (hdr.ipv4.isValid()){
            // for a int packet
            bit<1> int_support;
            int_support_reg.read(int_support, 0);
            if (int_support == 1) {
                if(meta.int_support_metadata.int_processing == 1 && (hdr.ethernet.etherType == TYPE_INT || meta.int_support_metadata.bitmap_need_flag == 1) && !(meta.int_support_metadata.to_host == 1 && standard_metadata.instance_type == 0)){
                    bit<16> bitmap_task_remain;
                    bitmap_task_remain_reg.read(bitmap_task_remain, meta.int_support_metadata.egress_port);

                    bit<8> bitmap_num;
                    bitmap_num_reg.read(bitmap_num, 0);
                    bit<16> bitmap_task;
                    bitmap_task_reg.read(bitmap_task, 0);

                    if (bitmap_task_remain > 0){
                        bit<8>  length = 0;
                        bit<16> bitmap_need = 0;  // MAX metadata number
                        bit<16> bitmap_add = 0;  // MAX metadata number
                        bit<6>  count = 0;
                        if (hdr.ethernet.etherType == TYPE_INT){
                            if (bitmap_num <= 8){
                                meta.int_support_metadata.bitmap_need = ((bit<16>)hdr.intType_8.bitmap_need) << 8;
                                count = hdr.intType_8.count;
                            }
                            else if (bitmap_num <=16){
                                meta.int_support_metadata.bitmap_need = (bit<16>)hdr.intType_16.bitmap_need;
                                count = hdr.intType_16.count;
                            }
                        }
                        bitmap_need = meta.int_support_metadata.bitmap_need;

                        // 根据bitmap_need 添加遥测元数据， 并更新bimap_add
                        // 添加原则，贪心添加
                        // 先判断任务的位置，在判断bitmap_need对应位是否为1
                        if ( bitmap_task & 0b1000000000000000 == 0b1000000000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b1000000000000000 == 0b1000000000000000){
                                hdr.md_swId.setValid();
                                switch_id_reg.read(hdr.md_swId.swId, 0);
                                length = length + MDW1;
                                bitmap_task_remain = bitmap_task_remain & 0b0111111111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0100000000000000 == 0b0100000000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0100000000000000 == 0b0100000000000000){
                                hdr.md_pip.setValid();
                                hdr.md_pip.pip = (bit<8>)standard_metadata.ingress_port;
                                length = length + MDW2;
                                bitmap_task_remain = bitmap_task_remain & 0b1011111111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0010000000000000 == 0b0010000000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0010000000000000 == 0b0010000000000000){
                                hdr.md_pdr.setValid();
                                hdr.md_pdr.pdr = 9;
                                length = length + MDW3;
                                bitmap_task_remain = bitmap_task_remain & 0b1101111111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0001000000000000 == 0b0001000000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0001000000000000 == 0b0001000000000000){
                                hdr.md_pop.setValid();
                                hdr.md_pop.pop = (bit<8>)meta.int_support_metadata.egress_port;
                                length = length + MDW4;
                                bitmap_task_remain = bitmap_task_remain & 0b1110111111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000100000000000 == 0b0000100000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000100000000000 == 0b0000100000000000){
                                hdr.md_ls.setValid();
                                hdr.md_ls.ls = 6;
                                length = length + MDW5;
                                bitmap_task_remain = bitmap_task_remain & 0b1111011111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000010000000000 == 0b0000010000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000010000000000 == 0b0000010000000000){
                                hdr.md_qd.setValid();
                                hdr.md_qd.qd = 12;
                                length = length + MDW6;
                                bitmap_task_remain = bitmap_task_remain & 0b1111101111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000001000000000 == 0b0000001000000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000001000000000 == 0b0000001000000000){
                                hdr.md_delay.setValid();
                                hdr.md_delay.delay = 7;
                                length = length + MDW7;
                                bitmap_task_remain = bitmap_task_remain & 0b1111110111111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000100000000 == 0b0000000100000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000100000000 == 0b0000000100000000){
                                hdr.md_plc.setValid();
                                hdr.md_plc.plc = 4;
                                length = length + MDW8;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111011111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000010000000 == 0b0000000010000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000010000000 == 0b0000000010000000){
                                hdr.md_inTs.setValid();
                                hdr.md_inTs.inTs = (time_t)standard_metadata.ingress_global_timestamp;
                                length = length + MDW9;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111101111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000001000000 == 0b0000000001000000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000001000000 == 0b0000000001000000){
                                hdr.md_pdc.setValid();
                                hdr.md_pdc.pdc = 8;
                                length = length + MDW10;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111110111111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000100000 == 0b0000000000100000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000100000 == 0b0000000000100000){
                                hdr.md_lu.setValid();
                                hdr.md_lu.lu = 10;
                                length = length + MDW11;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111011111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000010000 == 0b0000000000010000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000010000 == 0b0000000000010000){
                                hdr.md_qId.setValid();
                                hdr.md_qId.qId = 13;
                                length = length + MDW12;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111101111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000001000 == 0b0000000000001000 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000001000 == 0b0000000000001000){
                                hdr.md_pmc.setValid();
                                hdr.md_pmc.pmc = 5;
                                length = length + MDW13;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111110111;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000000100 == 0b0000000000000100 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000000100 == 0b0000000000000100){
                                hdr.md_fc.setValid();
                                hdr.md_fc.fc = 11;
                                length = length + MDW14;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111111011;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000000010 == 0b0000000000000010 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000000010 == 0b0000000000000010){
                                hdr.md_egTs.setValid();
                                hdr.md_egTs.egTs = (time_t)standard_metadata.egress_global_timestamp;
                                length = length + MDW15;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111111101;
                                bitmap_add = bitmap_add + 1;
                            }
                            bitmap_need = bitmap_need << 1;
                        }
                        if ( bitmap_task & 0b0000000000000001 == 0b0000000000000001 ){
                            bitmap_add = bitmap_add << 1;
                            if (bitmap_need & 0b1000000000000000 == 0b1000000000000000 && bitmap_task_remain & 0b0000000000000001 == 0b0000000000000001){
                                hdr.md_prc.setValid();
                                hdr.md_prc.prc = 3;
                                length = length + MDW16;
                                bitmap_task_remain = bitmap_task_remain & 0b1111111111111110;
                                bitmap_add = bitmap_add + 1;
                            }
                        }

                        if (bitmap_add > 0){
                            if (bitmap_num <= 8){
                                hdr.ethernet.etherType = TYPE_INT;
                                hdr.intType_8.setValid();
                                hdr.intType_8.type = 0b00;
                                hdr.intType_8.count = count + 1;
                                hdr.intType_8.bitmap_need = (bit<8>)(meta.int_support_metadata.bitmap_need >> 8);

                                hdr.intData_add_8.setValid();
                                hdr.intData_add_8.bitmap_add = (bit<8>)(bitmap_add << (bit<8>)(8 - bitmap_num));
                                hdr.intData_add_8.length = length;

                                if (meta.int_support_metadata.bitmap_need_flag == 1){
                                    length = length + 2;
                                }
                                meta.int_support_metadata.int_length = meta.int_support_metadata.int_length + 2 + (bit<16>)length;
                            }
                            else if (bitmap_num <=16){
                                hdr.ethernet.etherType = TYPE_INT;
                                hdr.intType_16.setValid();
                                hdr.intType_16.type = 0b01;
                                hdr.intType_16.count = count + 1;
                                hdr.intType_16.bitmap_need = meta.int_support_metadata.bitmap_need;

                                hdr.intData_add_16.setValid();
                                hdr.intData_add_16.bitmap_add = (bit<16>)(bitmap_add << (bit<8>)(16 - bitmap_num));
                                hdr.intData_add_16.length = length;

                                if (meta.int_support_metadata.bitmap_need_flag == 1){
                                    length = length + 3;
                                }
                                meta.int_support_metadata.int_length = meta.int_support_metadata.int_length + 3 + (bit<16>)length;
                            }
                        }
                        bitmap_task_remain_reg.write(meta.int_support_metadata.egress_port, bitmap_task_remain);
                    }
                    int_processing_reg.write(meta.int_support_metadata.egress_port, 0);
                }
            }

            if (hdr.ethernet.etherType == TYPE_INT && meta.int_support_metadata.to_host == 1 && standard_metadata.instance_type == 0){
                // just delete the setting number, if the stack is less than the num, it will clear all stack!!!
                hdr.intType_8.setInvalid();
                hdr.intType_16.setInvalid();
                hdr.intData_add_8.setInvalid();
                hdr.intData_add_16.setInvalid();
                hdr.md_swId.setInvalid();
                hdr.md_pip.setInvalid();
                hdr.md_pdr.setInvalid();
                hdr.md_pop.setInvalid();
                hdr.md_ls.setInvalid();
                hdr.md_qd.setInvalid();
                hdr.md_delay.setInvalid();
                hdr.md_plc.setInvalid();
                hdr.md_inTs.setInvalid();
                hdr.md_pdc.setInvalid();
                hdr.md_lu.setInvalid();
                hdr.md_qId.setInvalid();
                hdr.md_pmc.setInvalid();
                hdr.md_fc.setInvalid();
                hdr.md_egTs.setInvalid();
                hdr.md_prc.setInvalid();

                hdr.intData_8.pop_front(MAX_HOPS);
                hdr.intData_16.pop_front(MAX_HOPS);

                hdr.ethernet.etherType = TYPE_IPV4;     //change the etherType
            }
            // cloned packet
            if (standard_metadata.instance_type != 0){
                // C语言中，用来改变文件大小。
                // 此处用来控制克隆包的大小，从deparser的第一个字段开始的字节数。
                truncate((bit<32>)(meta.int_support_metadata.int_length + 14));
            }
        }
    }
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
        packet.emit(hdr.intType_8);
        packet.emit(hdr.intType_16);

        packet.emit(hdr.intData_add_8);
        packet.emit(hdr.intData_add_16);
        packet.emit(hdr.md_swId);
        packet.emit(hdr.md_pip);
        packet.emit(hdr.md_pdr);
        packet.emit(hdr.md_pop);
        packet.emit(hdr.md_ls);
        packet.emit(hdr.md_qd);
        packet.emit(hdr.md_delay);
        packet.emit(hdr.md_plc);
        packet.emit(hdr.md_inTs);
        packet.emit(hdr.md_pdc);
        packet.emit(hdr.md_lu);
        packet.emit(hdr.md_qId);
        packet.emit(hdr.md_pmc);
        packet.emit(hdr.md_fc);
        packet.emit(hdr.md_egTs);
        packet.emit(hdr.md_prc);

        packet.emit(hdr.intData_8);
        packet.emit(hdr.intData_16);
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
