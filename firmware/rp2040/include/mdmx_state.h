#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "mdmx_protocol.h"

typedef struct {
    uint8_t banks[2][MDMX_PORTS][MDMX_SLOTS_PER_PORT];
    volatile uint8_t active_bank;
    uint8_t pending_bank;
    uint32_t generation;
    uint32_t last_sequence;
    bool has_committed_frame;
    uint64_t last_valid_frame_us;
} mdmx_state_t;

void mdmx_state_init(mdmx_state_t *state);

void mdmx_state_stage(
    mdmx_state_t *state,
    const uint8_t payload[MDMX_PAYLOAD_LEN]
);

void mdmx_state_commit(
    mdmx_state_t *state,
    uint32_t sequence,
    uint64_t now_us
);

const uint8_t *mdmx_state_active_universe(
    const mdmx_state_t *state,
    unsigned port
);

bool mdmx_state_hold_due(
    const mdmx_state_t *state,
    uint64_t now_us,
    uint64_t hold_after_us
);
