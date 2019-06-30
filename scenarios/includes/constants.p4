
// max sizes
const bit<32> MAX_COUNTERS = 10;
const bit<32> MAX_NODES = 10;
const bit<32> MAX_WEIGHTS = 6;
const bit<32> PARAM_NUMBER = 7;

// aggregation results
const bit<2> RESULT_SEND = 0;
const bit<2> RESULT_DROP = 1;
const bit<2> RESULT_MCAST = 2;

// state messages
const bit<8> STATE_FINISHED = 0;
const bit<8> STATE_SETUP = 1;
const bit<8> STATE_LEARNING = 2;
const bit<8> STATE_ERROR = 3;
const bit<8> STATE_WRONG_STEP = 4;
const bit<8> STATE_RESET = 5;
const bit<8> STATE_CONFIGURE = 6;

// Counter indexes
const bit<32> NODES_IDX = 2;
const bit<32> STEP_IDX = 3;
const bit<32> STATE_IDX = 4;

// Parameter indexes
const bit<32> NODE_NUMBER_IDX = 0;
const bit<32> ITERATIONS_IDX = 1;
const bit<32> ETA_IDX = 2;
const bit<32> INPUT_SIZE_IDX = 3;
const bit<32> INPUT_FEATURES_IDX = 4;
const bit<32> OUTPUT_CLASSES_IDX = 5;
const bit<32> SCALE_FACTOR_IDX = 6;
