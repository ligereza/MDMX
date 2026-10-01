#include "mdmx_protocol.h"

#include <string.h>

static uint16_t read_le16(const uint8_t *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static uint32_t read_le32(const uint8_t *p) {
    return (uint32_t)p[0]
        | ((uint32_t)p[1] << 8)
        | ((uint32_t)p[2] << 16)
        | ((uint32_t)p[3] << 24);
}

static void write_le32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v & 0xffu);
    p[1] = (uint8_t)((v >> 8) & 0xffu);
    p[2] = (uint8_t)((v >> 16) & 0xffu);
    p[3] = (uint8_t)((v >> 24) & 0xffu);
}

uint32_t mdmx_crc32_iso_hdlc(const uint8_t *data, size_t len) {
    uint32_t crc = 0xffffffffu;

    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            uint32_t mask = (uint32_t)-(int32_t)(crc & 1u);
            crc = (crc >> 1) ^ (0xedb88320u & mask);
        }
    }

    return crc ^ 0xffffffffu;
}

mdmx_status_t mdmx_parse_frameset(
    const uint8_t frame[MDMX_FRAME_LEN],
    mdmx_frame_view_t *out
) {
    if (frame == NULL || out == NULL) {
        return MDMX_ERR_FORMAT;
    }

    if (memcmp(frame, "MDMX", 4) != 0) {
        return MDMX_ERR_FORMAT;
    }
    if (frame[4] != MDMX_VERSION || frame[5] != MDMX_TYPE_FRAMESET) {
        return MDMX_ERR_FORMAT;
    }
    if (read_le16(&frame[6]) != MDMX_HEADER_LEN) {
        return MDMX_ERR_FORMAT;
    }
    if (read_le16(&frame[12]) != MDMX_PAYLOAD_LEN) {
        return MDMX_ERR_FORMAT;
    }

    const uint32_t stored_crc = read_le32(&frame[MDMX_FRAME_LEN - 4u]);
    const uint32_t computed_crc = mdmx_crc32_iso_hdlc(
        frame,
        MDMX_FRAME_LEN - 4u
    );
    if (stored_crc != computed_crc) {
        return MDMX_ERR_CRC;
    }

    out->sequence = read_le32(&frame[8]);
    out->flags = read_le16(&frame[14]);
    out->payload = &frame[MDMX_HEADER_LEN];
    return MDMX_ACK;
}

mdmx_sequence_relation_t mdmx_sequence_relation(
    uint32_t candidate,
    uint32_t last_committed
) {
    const uint32_t delta = candidate - last_committed;

    if (delta == 0u) {
        return MDMX_SEQ_DUPLICATE;
    }
    if (delta < 0x80000000u) {
        return MDMX_SEQ_NEW;
    }
    return MDMX_SEQ_STALE;
}

void mdmx_encode_reply(
    uint8_t out[MDMX_REPLY_LEN],
    mdmx_status_t status,
    uint32_t sequence
) {
    out[0] = 'M';
    out[1] = 'R';
    out[2] = MDMX_VERSION;
    out[3] = (uint8_t)status;
    write_le32(&out[4], sequence);
}
