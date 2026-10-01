#pragma once

#include <stddef.h>
#include <stdint.h>

#include "mdmx_protocol.h"
#include "mdmx_state.h"

mdmx_status_t mdmx_ingest_frame(
    mdmx_state_t *state,
    const uint8_t frame[MDMX_FRAME_LEN],
    uint64_t now_us
);
