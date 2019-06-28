
action _nop() {
}

#ifdef ENABLE_DEBUG_TABLES

#define DEBUG_FIELD_LIST \
        standard_metadata.ingress_port: exact; \
        standard_metadata.egress_spec: exact; \
        standard_metadata.egress_port: exact; \
        hdr.ethernet.dstAddr: exact; \
        hdr.ethernet.srcAddr: exact;

#endif  // ENABLE_DEBUG_TABLE

control DebugIngress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata){

  #ifdef ENABLE_DEBUG_TABLES
    table ing_debug_table {
        key = { DEBUG_FIELD_LIST }
        actions = { _nop; }
        default_action = _nop();
    }
  #endif  // ENABLE_DEBUG_TABLE

    apply {
      #ifdef ENABLE_DEBUG_TABLES 
      ing_debug_table.apply();
      #endif  // ENABLE_DEBUG_TABLE
    }

}

control DebugEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata){
  #ifdef ENABLE_DEBUG_TABLES
    table egr_debug_table {
        key = { DEBUG_FIELD_LIST }
        actions = { _nop; }
        default_action = _nop();
    }
  #endif  
    apply {
      #ifdef ENABLE_DEBUG_TABLES 
        egr_debug_table.apply();
      #endif  // ENABLE_DEBUG_TABLE
    }

}

