#include "mdmx_ingest.h"

mdmx_status_t mdmx_ingest_frame(
    mdmx_state_t *state,
    const uint8_t frame[MDMX_FRAME_LEN],
    uint64_t now_us
) {
    mdmx_frame_view_t view;
    const mdmx_status_t parse_status = mdmx_parse_frameset(frame, &view);

    if (parse_status != MDMX_ACK) {
        return parse_status;
    }

    if (!state->has_committed_frame) {
        mdmx_state_stage(state, view.payload);
        mdmx_state_commit(state, view.sequence, now_us);
        return MDMX_ACK;
    }

    switch (mdmx_sequence_relation(view.sequence, state->last_sequence)) {
        case MDMX_SEQ_DUPLICATE:
            /* Valid retry: no second commit, but it is still a valid frame arrival. */
            state->last_valid_frame_us = now_us;
            return MDMX_ACK;

        case MDMX_SEQ_NEW:
            mdmx_state_stage(state, view.payload);
            mdmx_state_commit(state, view.sequence, now_us);
            return MDMX_ACK;

        case MDMX_SEQ_STALE:
        default:
            return MDMX_ERR_SEQUENCE;
    }
}
