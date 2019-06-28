/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "includes/header.p4"
#include "includes/parser.p4"

const bit<32> MAX_COUNTER_VALUE = 1 << 16;

// enu1ALUE_A = 1,
//     VALUE_B = 2,
//     VALUE_C = 3
// } 

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop();
    }

    action broadcast() {
        standard_metadata.mcast_grp = 1;
    }

    action echo() {
        standard_metadata.egress_port = standard_metadata.ingress_port;
    }

    apply {

        if (hdr.ipv4.isValid()) {
            if (hdr.udp.dstPort == 8888){
                echo();
            } else {
                broadcast();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    
    // Declarations
    // register<bit<32>>(MAX_COUNTER_VALUE) packetCounter;
    bit<32> tmp;

    action _drop() {
        mark_to_drop();
    }

    action set_values(macAddr_t dstMac, ip4Addr_t dstIp) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr  = dstMac;

        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr  = dstIp;
        
        bit<16> tmp = hdr.udp.dstPort;
        hdr.udp.dstPort = hdr.udp.srcPort;
        hdr.udp.srcPort = tmp;
        hdr.udp.checksum = 0;
    }

    table send_answer {
        actions = {
            set_values;
            _drop;
            NoAction;
        }
        key = {
            standard_metadata.egress_port: exact;
        }
        size = 256;
        default_action = NoAction();
    }

    apply { 
         if (hdr.ipv4.isValid()){
            send_answer.apply();
         }
     }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
