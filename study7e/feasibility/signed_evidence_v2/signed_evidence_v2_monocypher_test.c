#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "aerc_signed_evidence_v2.h"
#include "monocypher-ed25519.h"

static const uint8_t RFC8032_TEST1_SEED[32] = {
    0x9d,0x61,0xb1,0x9d,0xef,0xfd,0x5a,0x60,
    0xba,0x84,0x4a,0xf4,0x92,0xec,0x2c,0xc4,
    0x44,0x49,0xc5,0x69,0x7b,0x32,0x69,0x19,
    0x70,0x3b,0xac,0x03,0x1c,0xae,0x7f,0x60
};

static const uint8_t RFC8032_TEST1_PUBLIC[32] = {
    0xd7,0x5a,0x98,0x01,0x82,0xb1,0x0a,0xb7,
    0xd5,0x4b,0xfe,0xd3,0xc9,0x64,0x07,0x3a,
    0x0e,0xe1,0x72,0xf3,0xda,0xa6,0x23,0x25,
    0xaf,0x02,0x1a,0x68,0xf7,0x07,0x51,0x1a
};

static void print_hex(const char *label, const uint8_t *data, size_t size)
{
    size_t i;
    printf("%s=", label);
    for (i = 0; i < size; ++i)
    {
        printf("%02x", data[i]);
    }
    putchar('\n');
}

static int same_fields(const AERC_SIGNED_EVIDENCE_V2_Fields_t *a,
                       const AERC_SIGNED_EVIDENCE_V2_Fields_t *b)
{
    return a->producer_role == b->producer_role &&
           a->authorization_value == b->authorization_value &&
           a->scenario_id == b->scenario_id &&
           a->source_id == b->source_id &&
           a->authority_id == b->authority_id &&
           a->key_id == b->key_id &&
           a->evidence_epoch == b->evidence_epoch &&
           a->issued_logical_time == b->issued_logical_time &&
           a->evidence_sequence == b->evidence_sequence;
}

static int mutation_rejected(const uint8_t signature[64],
                             const uint8_t public_key[32],
                             const uint8_t body[64],
                             size_t index,
                             uint8_t xor_mask)
{
    uint8_t mutated[64];
    memcpy(mutated, body, sizeof(mutated));
    mutated[index] ^= xor_mask;
    return crypto_ed25519_check(signature, public_key, mutated, sizeof(mutated)) != 0;
}

int main(void)
{
    AERC_SIGNED_EVIDENCE_V2_Fields_t input = {
        .producer_role = AERC_SIGNED_EVIDENCE_ROLE_PRIMARY,
        .authorization_value = 1u,
        .scenario_id = 0x53374801u,
        .source_id = 0x00001001u,
        .authority_id = 0x00003001u,
        .key_id = 0x00002001u,
        .evidence_epoch = UINT64_C(7),
        .issued_logical_time = UINT64_C(1000),
        .evidence_sequence = UINT64_C(1)
    };
    AERC_SIGNED_EVIDENCE_V2_Fields_t parsed;
    AERC_SIGNED_EVIDENCE_V2_Fields_t invalid;
    uint8_t body[64];
    uint8_t malformed[64];
    uint8_t seed[32];
    uint8_t secret_key[64];
    uint8_t public_key[32];
    uint8_t signature[64];

    if (AERC_SIGNED_EVIDENCE_V2_Serialize(body, &input) != 0)
    {
        return 1;
    }

    if (AERC_SIGNED_EVIDENCE_V2_Parse(&parsed, body) != 0 || !same_fields(&input, &parsed))
    {
        return 2;
    }

    memcpy(seed, RFC8032_TEST1_SEED, sizeof(seed));
    crypto_ed25519_key_pair(secret_key, public_key, seed);
    if (memcmp(public_key, RFC8032_TEST1_PUBLIC, sizeof(public_key)) != 0)
    {
        return 3;
    }

    crypto_ed25519_sign(signature, secret_key, body, sizeof(body));
    if (crypto_ed25519_check(signature, public_key, body, sizeof(body)) != 0)
    {
        return 4;
    }

    if (!mutation_rejected(signature, public_key, body, 20u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 18u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 24u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 28u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 32u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 48u, 0x01u) ||
        !mutation_rejected(signature, public_key, body, 56u, 0x01u))
    {
        return 5;
    }

    memcpy(malformed, body, sizeof(malformed));
    malformed[19] = 1u;
    if (AERC_SIGNED_EVIDENCE_V2_Parse(&parsed, malformed) == 0)
    {
        return 6;
    }

    memcpy(malformed, body, sizeof(malformed));
    malformed[36] = 1u;
    if (AERC_SIGNED_EVIDENCE_V2_Parse(&parsed, malformed) == 0)
    {
        return 7;
    }

    memcpy(malformed, body, sizeof(malformed));
    malformed[16] = 2u;
    if (AERC_SIGNED_EVIDENCE_V2_Parse(&parsed, malformed) == 0)
    {
        return 8;
    }

    invalid = input;
    invalid.scenario_id = 0u;
    if (AERC_SIGNED_EVIDENCE_V2_Serialize(malformed, &invalid) == 0)
    {
        return 9;
    }

    invalid = input;
    invalid.producer_role = 3u;
    if (AERC_SIGNED_EVIDENCE_V2_Serialize(malformed, &invalid) == 0)
    {
        return 10;
    }

    invalid = input;
    invalid.authorization_value = 2u;
    if (AERC_SIGNED_EVIDENCE_V2_Serialize(malformed, &invalid) == 0)
    {
        return 11;
    }

    print_hex("SIGNED_EVIDENCE_V2_BODY_HEX", body, sizeof(body));
    print_hex("SIGNED_EVIDENCE_V2_PUBLIC_KEY_HEX", public_key, sizeof(public_key));
    print_hex("SIGNED_EVIDENCE_V2_SIGNATURE_HEX", signature, sizeof(signature));

    puts("SIGNED_EVIDENCE_V2_SERIALIZE_PARSE=PASS");
    puts("SIGNED_EVIDENCE_V2_RFC8032_KEY_DERIVATION=PASS");
    puts("SIGNED_EVIDENCE_V2_SIGN_VERIFY=PASS");
    puts("SIGNED_EVIDENCE_V2_PROTECTED_FIELD_MUTATIONS_REJECT=PASS");
    puts("SIGNED_EVIDENCE_V2_MALFORMED_RESERVED_REJECT=PASS");
    puts("SIGNED_EVIDENCE_V2_INVALID_FIELD_REJECT=PASS");
    puts("SIGNED_EVIDENCE_V2_SECRET_KEY_IN_CFS_FSW=false");
    puts("SIGNED_EVIDENCE_V2_FINAL_KEY_REGISTRY_FROZEN=false");
    puts("SIGNED_EVIDENCE_V2_POLICY_BINDING=false");
    puts("scientific_results_generated=false");
    return 0;
}
