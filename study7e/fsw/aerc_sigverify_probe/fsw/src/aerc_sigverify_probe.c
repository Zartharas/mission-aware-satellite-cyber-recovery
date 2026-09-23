#include "aerc_sigverify_probe.h"

#include "osapi.h"
#include <string.h>

#define AERC_SVPROBE_INIT_EID 1
#define AERC_SVPROBE_PASS_EID 2
#define AERC_SVPROBE_ERR_EID 3

#define AERC_SV_POS1_SCENARIO 0x53374701u
#define AERC_SV_MUT_SCENARIO 0x53374702u
#define AERC_SV_ZERO_SCENARIO 0x53374703u
#define AERC_SV_CHANGED_SCENARIO 0x53374704u
#define AERC_SV_FINAL_SCENARIO 0x53374705u
#define AERC_SV_SHORT_SCENARIO 0x5337470Bu
#define AERC_SV_VERSION_SCENARIO 0x5337470Cu
#define AERC_SV_KEY_SCENARIO 0x5337470Du
#define AERC_SV_LENGTH_SCENARIO 0x5337470Eu
#define AERC_SV_PADDING_SCENARIO 0x5337470Fu

static const uint8 AERC_SV_Signature[AERC_ED25519_SIGNATURE_BYTES] = {
    0xe5,0x56,0x43,0x00,0xc3,0x60,0xac,0x72,
    0x90,0x86,0xe2,0xcc,0x80,0x6e,0x82,0x8a,
    0x84,0x87,0x7f,0x1e,0xb8,0xe5,0xd9,0x74,
    0xd8,0x73,0xe0,0x65,0x22,0x49,0x01,0x55,
    0x5f,0xb8,0x82,0x15,0x90,0xa3,0x3b,0xac,
    0xc6,0x1e,0x39,0x70,0x1c,0xf9,0xb4,0x6b,
    0xd2,0x5b,0xf5,0xf0,0x59,0x5b,0xbe,0x24,
    0x65,0x51,0x41,0x43,0x8e,0x7a,0x10,0x0b
};

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
} AERC_SVPROBE_ShortRequest_t;

static CFE_Status_t AERC_SVPROBE_Send(
    CFE_SB_MsgId_t request_mid,
    uint32 scenario_id,
    uint32 request_sequence,
    const uint8 signature[AERC_ED25519_SIGNATURE_BYTES],
    uint8 wire_version,
    uint8 key_id,
    uint8 message_length,
    uint8 first_message_byte,
    bool bad_padding)
{
    AERC_SIGVERIFY_REQUEST_Message_t request;
    CFE_Status_t status;

    memset(&request, 0, sizeof(request));
    status = CFE_MSG_Init(&request.TelemetryHeader.Msg, request_mid, sizeof(request));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    request.ScenarioId = scenario_id;
    request.RequestSequence = request_sequence;
    request.WireVersion = wire_version;
    request.KeyId = key_id;
    request.MessageLength = message_length;
    memcpy(request.Signature, signature, sizeof(request.Signature));

    if (message_length > 0u && message_length <= AERC_ED25519_MESSAGE_CAPACITY)
    {
        request.Message[0] = first_message_byte;
    }
    if (bad_padding)
    {
        request.Message[AERC_ED25519_MESSAGE_CAPACITY - 1u] = 1u;
    }

    return CFE_SB_TransmitMsg(&request.TelemetryHeader.Msg, true);
}

static CFE_Status_t AERC_SVPROBE_SendShort(CFE_SB_MsgId_t request_mid)
{
    AERC_SVPROBE_ShortRequest_t request;
    CFE_Status_t status;

    memset(&request, 0, sizeof(request));
    status = CFE_MSG_Init(&request.TelemetryHeader.Msg, request_mid, sizeof(request));
    if (status == CFE_SUCCESS)
    {
        request.ScenarioId = AERC_SV_SHORT_SCENARIO;
        status = CFE_SB_TransmitMsg(&request.TelemetryHeader.Msg, true);
    }
    return status;
}

static bool AERC_SVPROBE_ResultMatches(const CFE_SB_Buffer_t *received,
                                       uint32 scenario_id,
                                       uint32 request_sequence,
                                       uint32 verification_sequence,
                                       uint8 valid,
                                       uint8 reason,
                                       uint8 message_length)
{
    CFE_MSG_Size_t size = 0;
    const AERC_SIGVERIFY_RESULT_Message_t *result;

    if (CFE_MSG_GetSize(&received->Msg, &size) != CFE_SUCCESS ||
        size != sizeof(AERC_SIGVERIFY_RESULT_Message_t))
    {
        return false;
    }

    result = (const AERC_SIGVERIFY_RESULT_Message_t *)received;
    return result->ScenarioId == scenario_id &&
           result->RequestSequence == request_sequence &&
           result->VerificationSequence == verification_sequence &&
           result->VerificationValid == valid &&
           result->Reason == reason &&
           result->KeyId == AERC_SIGVERIFY_TEST_KEY_ID &&
           result->MessageLength == message_length;
}

static bool AERC_SVPROBE_SendAndExpect(CFE_SB_MsgId_t request_mid,
                                      CFE_SB_PipeId_t result_pipe,
                                      uint32 scenario_id,
                                      uint32 request_sequence,
                                      const uint8 signature[AERC_ED25519_SIGNATURE_BYTES],
                                      uint8 message_length,
                                      uint8 first_message_byte,
                                      uint32 verification_sequence,
                                      uint8 valid,
                                      uint8 reason)
{
    CFE_Status_t status;
    CFE_SB_Buffer_t *received = NULL;

    status = AERC_SVPROBE_Send(request_mid,
                               scenario_id,
                               request_sequence,
                               signature,
                               AERC_SIGVERIFY_WIRE_VERSION,
                               AERC_SIGVERIFY_TEST_KEY_ID,
                               message_length,
                               first_message_byte,
                               false);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_ReceiveBuffer(&received, result_pipe, 2000);
    }

    return status == CFE_SUCCESS &&
           received != NULL &&
           AERC_SVPROBE_ResultMatches(received,
                                      scenario_id,
                                      request_sequence,
                                      verification_sequence,
                                      valid,
                                      reason,
                                      message_length);
}

static bool AERC_SVPROBE_ExpectNoResult(CFE_SB_PipeId_t result_pipe)
{
    CFE_SB_Buffer_t *received = NULL;
    CFE_Status_t status = CFE_SB_ReceiveBuffer(&received, result_pipe, 300);
    return status == CFE_SB_TIME_OUT && received == NULL;
}

void AERC_SVPROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t result_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_MsgId_t request_mid = CFE_SB_ValueToMsgId(AERC_SIGVERIFY_REQUEST_MID_VALUE);
    CFE_SB_MsgId_t result_mid = CFE_SB_ValueToMsgId(AERC_SIGVERIFY_RESULT_MID_VALUE);
    uint8 mutated[AERC_ED25519_SIGNATURE_BYTES];
    uint8 zero[AERC_ED25519_SIGNATURE_BYTES] = {0};

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&result_pipe, 8, "AERC_SV_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(result_mid, result_pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_SVPROBE initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    memcpy(mutated, AERC_SV_Signature, sizeof(mutated));
    mutated[0] ^= 0x01u;

    CFE_EVS_SendEvent(AERC_SVPROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SVPROBE starting cFE Ed25519 verification smoke");

    OS_TaskDelay(1200);

    if (!AERC_SVPROBE_SendAndExpect(request_mid, result_pipe,
                                    AERC_SV_POS1_SCENARIO, 1u,
                                    AERC_SV_Signature, 0u, 0u,
                                    1u, 1u, AERC_SIGVERIFY_RESULT_VALID) ||
        !AERC_SVPROBE_SendAndExpect(request_mid, result_pipe,
                                    AERC_SV_MUT_SCENARIO, 2u,
                                    mutated, 0u, 0u,
                                    2u, 0u, AERC_SIGVERIFY_RESULT_CRYPTO_REJECT) ||
        !AERC_SVPROBE_SendAndExpect(request_mid, result_pipe,
                                    AERC_SV_ZERO_SCENARIO, 3u,
                                    zero, 0u, 0u,
                                    3u, 0u, AERC_SIGVERIFY_RESULT_CRYPTO_REJECT) ||
        !AERC_SVPROBE_SendAndExpect(request_mid, result_pipe,
                                    AERC_SV_CHANGED_SCENARIO, 4u,
                                    AERC_SV_Signature, 1u, 0u,
                                    4u, 0u, AERC_SIGVERIFY_RESULT_CRYPTO_REJECT))
    {
        goto fail;
    }

    status = AERC_SVPROBE_SendShort(request_mid);
    if (status != CFE_SUCCESS || !AERC_SVPROBE_ExpectNoResult(result_pipe))
    {
        goto fail;
    }

    status = AERC_SVPROBE_Send(request_mid,
                               AERC_SV_VERSION_SCENARIO, 6u,
                               AERC_SV_Signature, 2u,
                               AERC_SIGVERIFY_TEST_KEY_ID, 0u, 0u, false);
    if (status != CFE_SUCCESS || !AERC_SVPROBE_ExpectNoResult(result_pipe))
    {
        goto fail;
    }

    status = AERC_SVPROBE_Send(request_mid,
                               AERC_SV_KEY_SCENARIO, 7u,
                               AERC_SV_Signature, AERC_SIGVERIFY_WIRE_VERSION,
                               2u, 0u, 0u, false);
    if (status != CFE_SUCCESS || !AERC_SVPROBE_ExpectNoResult(result_pipe))
    {
        goto fail;
    }

    status = AERC_SVPROBE_Send(request_mid,
                               AERC_SV_LENGTH_SCENARIO, 8u,
                               AERC_SV_Signature, AERC_SIGVERIFY_WIRE_VERSION,
                               AERC_SIGVERIFY_TEST_KEY_ID,
                               AERC_ED25519_MESSAGE_CAPACITY + 1u, 0u, false);
    if (status != CFE_SUCCESS || !AERC_SVPROBE_ExpectNoResult(result_pipe))
    {
        goto fail;
    }

    status = AERC_SVPROBE_Send(request_mid,
                               AERC_SV_PADDING_SCENARIO, 9u,
                               AERC_SV_Signature, AERC_SIGVERIFY_WIRE_VERSION,
                               AERC_SIGVERIFY_TEST_KEY_ID, 0u, 0u, true);
    if (status != CFE_SUCCESS || !AERC_SVPROBE_ExpectNoResult(result_pipe))
    {
        goto fail;
    }

    if (!AERC_SVPROBE_SendAndExpect(request_mid, result_pipe,
                                    AERC_SV_FINAL_SCENARIO, 10u,
                                    AERC_SV_Signature, 0u, 0u,
                                    5u, 1u, AERC_SIGVERIFY_RESULT_VALID))
    {
        goto fail;
    }

    CFE_ES_WriteToSysLog(
        "AERC_SIGVERIFY_PROBE PASS valid=2 crypto_reject=3 malformed_reject=5 final_sequence=5\n");
    CFE_EVS_SendEvent(AERC_SVPROBE_PASS_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SIGVERIFY_PROBE PASS cFE Ed25519 boundary verified");

    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
    return;

fail:
    CFE_EVS_SendEvent(AERC_SVPROBE_ERR_EID,
                      CFE_EVS_EventType_ERROR,
                      "AERC_SVPROBE validation failed RC=0x%08lX",
                      (unsigned long)status);
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
}
