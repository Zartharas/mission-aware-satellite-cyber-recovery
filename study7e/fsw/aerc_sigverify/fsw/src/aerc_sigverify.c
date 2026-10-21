#include "aerc_sigverify.h"

#include <string.h>

#define AERC_SIGV_INIT_EID 1
#define AERC_SIGV_RESULT_EID 2
#define AERC_SIGV_REJECT_EID 3
#define AERC_SIGV_ERR_EID 4

typedef enum
{
    AERC_SIGV_VALID = 0,
    AERC_SIGV_BAD_VERSION = 1,
    AERC_SIGV_BAD_KEY_ID = 2,
    AERC_SIGV_BAD_MESSAGE_LENGTH = 3,
    AERC_SIGV_BAD_RESERVED = 4,
    AERC_SIGV_BAD_PADDING = 5
} AERC_SIGV_Validation_t;

static const uint8 AERC_SIGV_TestPublicKey[AERC_ED25519_PUBLIC_KEY_BYTES] = {
    0xd7,0x5a,0x98,0x01,0x82,0xb1,0x0a,0xb7,
    0xd5,0x4b,0xfe,0xd3,0xc9,0x64,0x07,0x3a,
    0x0e,0xe1,0x72,0xf3,0xda,0xa6,0x23,0x25,
    0xaf,0x02,0x1a,0x68,0xf7,0x07,0x51,0x1a
};

static AERC_SIGV_Validation_t AERC_SIGV_ValidateRequest(
    const AERC_SIGVERIFY_REQUEST_Message_t *request,
    uint8 *bad_index)
{
    uint8 i;

    *bad_index = 0u;

    if (request->WireVersion != AERC_SIGVERIFY_WIRE_VERSION)
    {
        return AERC_SIGV_BAD_VERSION;
    }

    if (request->KeyId != AERC_SIGVERIFY_TEST_KEY_ID)
    {
        return AERC_SIGV_BAD_KEY_ID;
    }

    if (request->MessageLength > AERC_ED25519_MESSAGE_CAPACITY)
    {
        return AERC_SIGV_BAD_MESSAGE_LENGTH;
    }

    if (request->Reserved != 0u)
    {
        return AERC_SIGV_BAD_RESERVED;
    }

    for (i = request->MessageLength; i < AERC_ED25519_MESSAGE_CAPACITY; ++i)
    {
        if (request->Message[i] != 0u)
        {
            *bad_index = i;
            return AERC_SIGV_BAD_PADDING;
        }
    }

    return AERC_SIGV_VALID;
}

void AERC_SIGV_Main(void)
{
    CFE_Status_t status;
    uint32 run_status = CFE_ES_RunStatus_APP_RUN;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t request_mid = CFE_SB_ValueToMsgId(AERC_SIGVERIFY_REQUEST_MID_VALUE);
    CFE_SB_MsgId_t result_mid = CFE_SB_ValueToMsgId(AERC_SIGVERIFY_RESULT_MID_VALUE);
    uint32 verification_sequence = 0u;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 8, "AERC_SIGV_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(request_mid, pipe);
    }

    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_SIGV initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_SIGV_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SIGV initialized Monocypher verification-only boundary");

    while (CFE_ES_RunLoop(&run_status) == true)
    {
        CFE_MSG_Size_t size = 0;
        const AERC_SIGVERIFY_REQUEST_Message_t *request;
        AERC_SIGVERIFY_RESULT_Message_t result;
        AERC_SIGV_Validation_t validation;
        uint8 bad_index = 0u;
        int verify_rc;

        status = CFE_SB_ReceiveBuffer(&received, pipe, CFE_SB_PEND_FOREVER);
        if (status != CFE_SUCCESS || received == NULL)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        status = CFE_MSG_GetSize(&received->Msg, &size);
        if (status != CFE_SUCCESS || size != sizeof(AERC_SIGVERIFY_REQUEST_Message_t))
        {
            CFE_ES_WriteToSysLog(
                "AERC_SIGV REJECT_LENGTH expected=%lu actual=%lu status=0x%08lX\n",
                (unsigned long)sizeof(AERC_SIGVERIFY_REQUEST_Message_t),
                (unsigned long)size,
                (unsigned long)status);
            continue;
        }

        request = (const AERC_SIGVERIFY_REQUEST_Message_t *)received;
        validation = AERC_SIGV_ValidateRequest(request, &bad_index);
        if (validation != AERC_SIGV_VALID)
        {
            CFE_ES_WriteToSysLog(
                "AERC_SIGV REJECT_CONTRACT scenario=0x%08lX reason=%u key_id=%u message_len=%u index=%u\n",
                (unsigned long)request->ScenarioId,
                (unsigned int)validation,
                (unsigned int)request->KeyId,
                (unsigned int)request->MessageLength,
                (unsigned int)bad_index);
            CFE_EVS_SendEvent(AERC_SIGV_REJECT_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_SIGV rejected malformed verification request reason=%u",
                              (unsigned int)validation);
            continue;
        }

        verify_rc = AERC_ED25519_Verify(request->Signature,
                                       sizeof(request->Signature),
                                       AERC_SIGV_TestPublicKey,
                                       sizeof(AERC_SIGV_TestPublicKey),
                                       request->Message,
                                       request->MessageLength);
        if (verify_rc == AERC_ED25519_VERIFY_INPUT_ERROR)
        {
            CFE_EVS_SendEvent(AERC_SIGV_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_SIGV internal wrapper input guard failed");
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        memset(&result, 0, sizeof(result));
        status = CFE_MSG_Init(&result.TelemetryHeader.Msg, result_mid, sizeof(result));
        if (status != CFE_SUCCESS)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        ++verification_sequence;
        result.ScenarioId = request->ScenarioId;
        result.RequestSequence = request->RequestSequence;
        result.VerificationSequence = verification_sequence;
        result.VerificationValid = verify_rc == AERC_ED25519_VERIFY_OK ? 1u : 0u;
        result.Reason = verify_rc == AERC_ED25519_VERIFY_OK
                            ? AERC_SIGVERIFY_RESULT_VALID
                            : AERC_SIGVERIFY_RESULT_CRYPTO_REJECT;
        result.KeyId = request->KeyId;
        result.MessageLength = request->MessageLength;

        status = CFE_SB_TransmitMsg(&result.TelemetryHeader.Msg, true);
        if (status != CFE_SUCCESS)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        CFE_ES_WriteToSysLog(
            "AERC_SIGV RESULT scenario=0x%08lX request=%lu verify_sequence=%lu valid=%u reason=%u key_id=%u message_len=%u\n",
            (unsigned long)result.ScenarioId,
            (unsigned long)result.RequestSequence,
            (unsigned long)result.VerificationSequence,
            (unsigned int)result.VerificationValid,
            (unsigned int)result.Reason,
            (unsigned int)result.KeyId,
            (unsigned int)result.MessageLength);

        CFE_EVS_SendEvent(AERC_SIGV_RESULT_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_SIGV verification result valid=%u sequence=%lu",
                          (unsigned int)result.VerificationValid,
                          (unsigned long)result.VerificationSequence);
    }

    CFE_ES_ExitApp(run_status);
}
