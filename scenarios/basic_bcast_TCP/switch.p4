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
        hdr.ipv4.ttl = hdr.ipv4.ttl + 8w255;
        meta.index = (bit<32>)standard_metadata.ingress_port;
    }

    apply {

        if (hdr.ipv4.isValid()) {
            broadcast();
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
    register<bit<32>>(MAX_COUNTER_VALUE) packetCounter;
    bit<32> tmp;

     action setCounter() {
        hdr.pcounter.setValid();
        hdr.pcounter.count = 0;
        hdr.pcounter.pid = hdr.ethernet.etherType;
        hdr.ethernet.etherType = TYPE_pcounter;
    }
    action addCounter() {
        @atomic {
            // hdr.pcounter.count = hdr.pcounter.count + 1;
            // get register myCount
            packetCounter.read( tmp, meta.index);        
            // add myCount header
            hdr.pcounter.count = tmp+1;
            // sum to the register
            packetCounter.write(meta.index, tmp+1);
        }
    }

    action _drop() {
        mark_to_drop();
    }

    action set_values(macAddr_t dstMac) {
        macAddr_t tmp_mac = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstMac;
        hdr.ethernet.srcAddr = tmp_mac;
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
            if (!hdr.pcounter.isValid()){
                setCounter();
            } 
            if (hdr.pcounter.isValid()) {
                addCounter();
            }
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
