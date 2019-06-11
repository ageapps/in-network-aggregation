#ifndef _HEADERS_P4_
#define _HEADERS_P4_

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
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
    bit<32> dstAddr;
}
// NOTE: added new header type
header pcounter_t {
    bit<16> pid;
    bit<32> count;
}

struct headers {
    ethernet_t   ethernet;
    pcounter_t   pcounter;
    ipv4_t       ipv4;
}

#endif
