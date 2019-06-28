
// max sizes
const bit<32> MAX_COUNTERS = 10;
const bit<32> MAX_NODES = 5;
const bit<32> PARAM_NUMBER = 6;

// aggregation results
const bit<2> RESULT_SEND = 0;
const bit<2> RESULT_DROP = 1;
const bit<2> RESULT_MCAST = 2;

// state messages
const bit<8> STATE_SETUP = 0;
const bit<8> STATE_LEARNING = 1;
const bit<8> STATE_FINISHED = 2;
const bit<8> STATE_ERROR = 3;
const bit<8> STATE_WRONG_STEP = 4;

// Counter indexes
const bit<32> NODES_IDX = 2;
const bit<32> STEP_IDX = 3;
const bit<32> STATE_IDX = 4;
const bit<32> MEDIANS_IDX = 5;
