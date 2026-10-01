#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MDMX_VERSION 0x01u
#define MDMX_TYPE_FRAMESET 0x01u
#define MDMX_HEADER_LEN 16u
#define MDMX_PORTS 4u
#define MDMX_SLOTS_PER_PORT 512u
#define MDMX_PAYLOAD_LEN (MDMX_PORTS * MDMX_SLOTS_PER_PORT)
#define MDMX_FRAME_LEN (MDMX_HEADER_LEN + MDMX_PAYLOAD_LEN + 4u)
#define MDMX_REPLY_LEN 8u

typedef enum {
    MDMX_ACK = 0x00,
    MDMX_ERR_CRC = 0x01,
    MDMX_ERR_FORMAT = 0x02,
    MDMX_ERR_SEQUENCE = 0x03,
} mdmx_status_t;

typedef enum {
    MDMX_SEQ_DUPLICATE = 0,
    MDMX_SEQ_NEW = 1,
    MDMX_SEQ_STALE = 2,
} mdmx_sequence_relation_t;

typedef struct {
    uint32_t sequence;
    uint16_t flags;
    const uint8_t *payload;
} mdmx_frame_view_t;

uint32_t mdmx_crc32_iso_hdlc(const uint8_t *data, size_t len);

mdmx_status_t mdmx_parse_frameset(
    const uint8_t frame[MDMX_FRAME_LEN],
    mdmx_frame_view_t *out
);

mdmx_sequence_relation_t mdmx_sequence_relation(
    uint32_t candidate,
    uint32_t last_committed
);

void mdmx_encode_reply(
    uint8_t out[MDMX_REPLY_LEN],
    mdmx_status_t status,
    uint32_t sequence
);
