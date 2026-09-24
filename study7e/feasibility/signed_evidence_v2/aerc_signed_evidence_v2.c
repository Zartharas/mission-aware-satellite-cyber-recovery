#include "aerc_signed_evidence_v2.h"

#include <string.h>

static const uint8_t AERC_DOMAIN[AERC_SIGNED_EVIDENCE_V2_DOMAIN_BYTES] = {
    'S','7','E','-','A','E','R','C','-','A','U','T','H','-','V','1'
};

static void put_u32_be(uint8_t *out, uint32_t value)
{
    out[0] = (uint8_t)(value >> 24);
    out[1] = (uint8_t)(value >> 16);
    out[2] = (uint8_t)(value >> 8);
    out[3] = (uint8_t)value;
}

static void put_u64_be(uint8_t *out, uint64_t value)
{
    out[0] = (uint8_t)(value >> 56);
    out[1] = (uint8_t)(value >> 48);
    out[2] = (uint8_t)(value >> 40);
    out[3] = (uint8_t)(value >> 32);
    out[4] = (uint8_t)(value >> 24);
    out[5] = (uint8_t)(value >> 16);
    out[6] = (uint8_t)(value >> 8);
    out[7] = (uint8_t)value;
}

static uint32_t get_u32_be(const uint8_t *in)
{
    return ((uint32_t)in[0] << 24) |
           ((uint32_t)in[1] << 16) |
           ((uint32_t)in[2] << 8) |
           (uint32_t)in[3];
}

static uint64_t get_u64_be(const uint8_t *in)
{
    return ((uint64_t)in[0] << 56) |
           ((uint64_t)in[1] << 48) |
           ((uint64_t)in[2] << 40) |
           ((uint64_t)in[3] << 32) |
           ((uint64_t)in[4] << 24) |
           ((uint64_t)in[5] << 16) |
           ((uint64_t)in[6] << 8) |
           (uint64_t)in[7];
}

static int fields_valid(const AERC_SIGNED_EVIDENCE_V2_Fields_t *fields)
{
    if (fields == NULL)
    {
        return 0;
    }

    if (fields->producer_role != AERC_SIGNED_EVIDENCE_ROLE_PRIMARY &&
        fields->producer_role != AERC_SIGNED_EVIDENCE_ROLE_CORROBORATOR)
    {
        return 0;
    }

    if (fields->authorization_value > 1u)
    {
        return 0;
    }

    if (fields->scenario_id == 0u ||
        fields->source_id == 0u ||
        fields->authority_id == 0u ||
        fields->key_id == 0u)
    {
        return 0;
    }

    return 1;
}

int AERC_SIGNED_EVIDENCE_V2_Serialize(
    uint8_t out[AERC_SIGNED_EVIDENCE_V2_BYTES],
    const AERC_SIGNED_EVIDENCE_V2_Fields_t *fields)
{
    if (out == NULL || !fields_valid(fields))
    {
        return -1;
    }

    memset(out, 0, AERC_SIGNED_EVIDENCE_V2_BYTES);
    memcpy(out, AERC_DOMAIN, sizeof(AERC_DOMAIN));

    out[16] = 1u;
    out[17] = fields->producer_role;
    out[18] = fields->authorization_value;
    out[19] = 0u;

    put_u32_be(&out[20], fields->scenario_id);
    put_u32_be(&out[24], fields->source_id);
    put_u32_be(&out[28], fields->authority_id);
    put_u32_be(&out[32], fields->key_id);
    put_u32_be(&out[36], 0u);

    put_u64_be(&out[40], fields->evidence_epoch);
    put_u64_be(&out[48], fields->issued_logical_time);
    put_u64_be(&out[56], fields->evidence_sequence);

    return 0;
}

int AERC_SIGNED_EVIDENCE_V2_Parse(
    AERC_SIGNED_EVIDENCE_V2_Fields_t *fields,
    const uint8_t in[AERC_SIGNED_EVIDENCE_V2_BYTES])
{
    AERC_SIGNED_EVIDENCE_V2_Fields_t parsed;

    if (fields == NULL || in == NULL)
    {
        return -1;
    }

    if (memcmp(in, AERC_DOMAIN, sizeof(AERC_DOMAIN)) != 0 ||
        in[16] != 1u ||
        in[19] != 0u ||
        get_u32_be(&in[36]) != 0u)
    {
        return -1;
    }

    memset(&parsed, 0, sizeof(parsed));
    parsed.producer_role = in[17];
    parsed.authorization_value = in[18];
    parsed.scenario_id = get_u32_be(&in[20]);
    parsed.source_id = get_u32_be(&in[24]);
    parsed.authority_id = get_u32_be(&in[28]);
    parsed.key_id = get_u32_be(&in[32]);
    parsed.evidence_epoch = get_u64_be(&in[40]);
    parsed.issued_logical_time = get_u64_be(&in[48]);
    parsed.evidence_sequence = get_u64_be(&in[56]);

    if (!fields_valid(&parsed))
    {
        return -1;
    }

    *fields = parsed;
    return 0;
}
