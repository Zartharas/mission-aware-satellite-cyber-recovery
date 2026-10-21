#ifndef AERC_SIGVERIFY_H
#define AERC_SIGVERIFY_H

#include "cfe.h"
#include "aerc_ed25519_wrapper.h"

#define AERC_SIGVERIFY_REQUEST_MID_VALUE 0x0EE8u
#define AERC_SIGVERIFY_RESULT_MID_VALUE  0x0EE9u

#define AERC_SIGVERIFY_WIRE_VERSION 1u
#define AERC_SIGVERIFY_TEST_KEY_ID 1u

#define AERC_SIGVERIFY_RESULT_VALID 0u
#define AERC_SIGVERIFY_RESULT_CRYPTO_REJECT 1u

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint32 RequestSequence;
    uint8 WireVersion;
    uint8 KeyId;
    uint8 MessageLength;
    uint8 Reserved;
    uint8 Signature[AERC_ED25519_SIGNATURE_BYTES];
    uint8 Message[AERC_ED25519_MESSAGE_CAPACITY];
} AERC_SIGVERIFY_REQUEST_Message_t;

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint32 RequestSequence;
    uint32 VerificationSequence;
    uint8 VerificationValid;
    uint8 Reason;
    uint8 KeyId;
    uint8 MessageLength;
} AERC_SIGVERIFY_RESULT_Message_t;

void AERC_SIGV_Main(void);

#endif
