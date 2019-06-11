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
    /**
    *   Use enumns
        Use atomic anotation
        int type
        functions with return statemnt

    */
    action broadcast() {
        standard_metadata.mcast_grp = 1;
        hdr.ipv4.ttl = hdr.ipv4.ttl + 8w255;
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
        packetCounter.write( meta.index, 0);

    }
    
    action addCounter() {
        // hdr.pcounter.count = hdr.pcounter.count + 1;
        // get register myCount
        packetCounter.read( tmp, meta.index);        
        // add myCount header
        hdr.pcounter.count = tmp+1;
        // sum to the register
        packetCounter.write(meta.index, tmp+1);

        if (hdr.pcounter.count > 10){
            hdr.pcounter.count = 0;
        }
    }

    apply { 
         if (hdr.ipv4.isValid()){
            if (!hdr.pcounter.isValid()){
                setCounter();
            } 
            if (hdr.pcounter.isValid()) {
                addCounter();
            }
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
