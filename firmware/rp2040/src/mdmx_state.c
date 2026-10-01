#include "mdmx_state.h"

#include <stddef.h>
#include <string.h>

#include "hardware/sync.h"

void mdmx_state_init(mdmx_state_t *state) {
    memset(state, 0, sizeof(*state));
    state->active_bank = 0u;
    state->pending_bank = 1u;
}

void mdmx_state_stage(
    mdmx_state_t *state,
    const uint8_t payload[MDMX_PAYLOAD_LEN]
) {
    memcpy(
        state->banks[state->pending_bank],
        payload,
        MDMX_PAYLOAD_LEN
    );
}

void mdmx_state_commit(
    mdmx_state_t *state,
    uint32_t sequence,
    uint64_t now_us
) {
    const uint32_t irq_state = save_and_disable_interrupts();

    const uint8_t old_active = state->active_bank;
    state->active_bank = state->pending_bank;
    state->pending_bank = old_active;
    state->last_sequence = sequence;
    state->generation++;
    state->has_committed_frame = true;
    state->last_valid_frame_us = now_us;

    restore_interrupts(irq_state);
}

const uint8_t *mdmx_state_active_universe(
    const mdmx_state_t *state,
    unsigned port
) {
    if (port >= MDMX_PORTS) {
        return NULL;
    }
    return state->banks[state->active_bank][port];
}

bool mdmx_state_hold_due(
    const mdmx_state_t *state,
    uint64_t now_us,
    uint64_t hold_after_us
) {
    if (!state->has_committed_frame) {
        return false;
    }
    return (now_us - state->last_valid_frame_us) >= hold_after_us;
}
