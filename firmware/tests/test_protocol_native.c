#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "mdmx_protocol.h"

int main(void) {
    static const uint8_t vector[] = "123456789";
    assert(mdmx_crc32_iso_hdlc(vector, 9) == 0xCBF43926u);

    assert(mdmx_sequence_relation(10u, 9u) == MDMX_SEQ_NEW);
    assert(mdmx_sequence_relation(9u, 9u) == MDMX_SEQ_DUPLICATE);
    assert(mdmx_sequence_relation(8u, 9u) == MDMX_SEQ_STALE);
    assert(mdmx_sequence_relation(0u, 0xFFFFFFFFu) == MDMX_SEQ_NEW);

    uint8_t reply[MDMX_REPLY_LEN] = {0};
    mdmx_encode_reply(reply, MDMX_ACK, 0x12345678u);

    const uint8_t expected[MDMX_REPLY_LEN] = {
        'M', 'R', 0x01, 0x00, 0x78, 0x56, 0x34, 0x12
    };
    assert(memcmp(reply, expected, sizeof(expected)) == 0);

    puts("mdmx_protocol native tests: PASS");
    return 0;
}
