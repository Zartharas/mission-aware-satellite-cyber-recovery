#ifndef AERC_SIGNED_EVIDENCE_V2_H
#define AERC_SIGNED_EVIDENCE_V2_H

#include <stddef.h>
#include <stdint.h>

#define AERC_SIGNED_EVIDENCE_V2_BYTES 64u
#define AERC_SIGNED_EVIDENCE_V2_DOMAIN_BYTES 16u

#define AERC_SIGNED_EVIDENCE_ROLE_PRIMARY 1u
#define AERC_SIGNED_EVIDENCE_ROLE_CORROBORATOR 2u

typedef struct
{
    uint8_t producer_role;
    uint8_t authorization_value;
    uint32_t scenario_id;
    uint32_t source_id;
    uint32_t authority_id;
    uint32_t key_id;
    uint64_t evidence_epoch;
    uint64_t issued_logical_time;
    uint64_t evidence_sequence;
} AERC_SIGNED_EVIDENCE_V2_Fields_t;

int AERC_SIGNED_EVIDENCE_V2_Serialize(
    uint8_t out[AERC_SIGNED_EVIDENCE_V2_BYTES],
    const AERC_SIGNED_EVIDENCE_V2_Fields_t *fields);

int AERC_SIGNED_EVIDENCE_V2_Parse(
    AERC_SIGNED_EVIDENCE_V2_Fields_t *fields,
    const uint8_t in[AERC_SIGNED_EVIDENCE_V2_BYTES]);

#endif
