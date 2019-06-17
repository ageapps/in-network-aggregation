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
    ip4Addr_t dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

/*
  0                1                2                3               4
  +----------------+----------------+                                 
  |      State     |  Node count    |
  +----------------+----------------+----------------+---------------+
  |                               Step                               |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 0                         |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 1                         |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 2                         |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 3                         |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 4                         |
  +----------------+----------------+----------------+---------------+
  |                              Parameter 5                         |
  +----------------+----------------+----------------+---------------+
*/

header agg_t {
    bit<8> state;
    bit<8> node_count;
    bit<32> step;
    bit<32> param_0;
    bit<32> param_1;
    bit<32> param_2;
    bit<32> param_3;
    bit<32> param_4;
    bit<32> param_5;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    udp_t        udp;
    agg_t        agg;
}

#endif
