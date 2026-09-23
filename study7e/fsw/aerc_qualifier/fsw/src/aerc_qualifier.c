#include "aerc_qualifier.h"

#include "aerc_ed25519_wrapper.h"
#include "aerc_policy.h"

#include <string.h>

#define AERC_QUAL_INIT_EID 1
#define AERC_QUAL_SNAP_EID 2
#define AERC_QUAL_ERR_EID  3

#define AERC_QUAL_DOMAIN_BYTES 16u
#define AERC_QUAL_PATH_FEATURES 7u

typedef struct
{
    uint8 Role;
    uint8 Authorization;
    uint32 ScenarioId;
    uint32 SourceId;
    uint32 AuthorityId;
    uint32 KeyId;
    uint64 Epoch;
    uint64 IssuedTick;
    uint64 Sequence;
} AERC_QUAL_Parsed_t;

typedef struct
{
    bool Available;
    bool SequenceSet;
    bool Contradicted;
    uint64 LastSequence;
    uint8 LastBody[AERC_EVIDENCE_BODY_BYTES];
    uint8 Features[AERC_QUAL_PATH_FEATURES];
} AERC_QUAL_PathState_t;

typedef struct
{
    bool Available;
    uint32 ScenarioId;
    uint64 ExpectedEpoch;
    uint64 NowTick;
    uint32 FreshnessMaxAgeTicks;
    uint8 ObservedHealthReady;
    uint8 SecuritySignal;
} AERC_QUAL_Context_t;

static const uint8 AERC_QUAL_Domain[AERC_QUAL_DOMAIN_BYTES] = {
    'S','7','E','-','A','E','R','C','-','A','U','T','H','-','V','1'
};

static const uint8 AERC_QUAL_PrimaryPublicKey[AERC_ED25519_PUBLIC_KEY_BYTES] = {
    0xd7,0x5a,0x98,0x01,0x82,0xb1,0x0a,0xb7,
    0xd5,0x4b,0xfe,0xd3,0xc9,0x64,0x07,0x3a,
    0x0e,0xe1,0x72,0xf3,0xda,0xa6,0x23,0x25,
    0xaf,0x02,0x1a,0x68,0xf7,0x07,0x51,0x1a
};

static const uint8 AERC_QUAL_CorrPublicKey[AERC_ED25519_PUBLIC_KEY_BYTES] = {
    0x3d,0x40,0x17,0xc3,0xe8,0x43,0x89,0x5a,
    0x92,0xb7,0x0a,0xa7,0x4d,0x1b,0x7e,0xbc,
    0x9c,0x98,0x2c,0xcf,0x2e,0xc4,0x96,0x8c,
    0xc0,0xcd,0x55,0xf1,0x2a,0xf4,0x66,0x0c
};

static AERC_QUAL_Context_t AERC_QUAL_Context;
static AERC_QUAL_PathState_t AERC_QUAL_Primary;
static AERC_QUAL_PathState_t AERC_QUAL_Corr;

static uint32 AERC_QUAL_GetU32(const uint8 *in)
{
    return ((uint32)in[0] << 24) |
           ((uint32)in[1] << 16) |
           ((uint32)in[2] << 8) |
           (uint32)in[3];
}

static uint64 AERC_QUAL_GetU64(const uint8 *in)
{
    return ((uint64)in[0] << 56) |
           ((uint64)in[1] << 48) |
           ((uint64)in[2] << 40) |
           ((uint64)in[3] << 32) |
           ((uint64)in[4] << 24) |
           ((uint64)in[5] << 16) |
           ((uint64)in[6] << 8) |
           (uint64)in[7];
}

static void AERC_QUAL_ResetPaths(void)
{
    memset(&AERC_QUAL_Primary, 0, sizeof(AERC_QUAL_Primary));
    memset(&AERC_QUAL_Corr, 0, sizeof(AERC_QUAL_Corr));
}

static bool AERC_QUAL_Parse(const uint8 body[AERC_EVIDENCE_BODY_BYTES], AERC_QUAL_Parsed_t *parsed)
{
    if (body == NULL || parsed == NULL)
    {
        return false;
    }

    if (memcmp(body, AERC_QUAL_Domain, AERC_QUAL_DOMAIN_BYTES) != 0 ||
        body[16] != 1u ||
        (body[17] != AERC_EVIDENCE_ROLE_PRIMARY && body[17] != AERC_EVIDENCE_ROLE_CORROBORATOR) ||
        body[18] > 1u ||
        body[19] != 0u ||
        AERC_QUAL_GetU32(&body[36]) != 0u)
    {
        return false;
    }

    memset(parsed, 0, sizeof(*parsed));
    parsed->Role = body[17];
    parsed->Authorization = body[18];
    parsed->ScenarioId = AERC_QUAL_GetU32(&body[20]);
    parsed->SourceId = AERC_QUAL_GetU32(&body[24]);
    parsed->AuthorityId = AERC_QUAL_GetU32(&body[28]);
    parsed->KeyId = AERC_QUAL_GetU32(&body[32]);
    parsed->Epoch = AERC_QUAL_GetU64(&body[40]);
    parsed->IssuedTick = AERC_QUAL_GetU64(&body[48]);
    parsed->Sequence = AERC_QUAL_GetU64(&body[56]);

    return parsed->ScenarioId != 0u &&
           parsed->SourceId != 0u &&
           parsed->AuthorityId != 0u &&
           parsed->KeyId != 0u;
}

static bool AERC_QUAL_SourceTrusted(const AERC_QUAL_Parsed_t *parsed)
{
    if (parsed->Role == AERC_EVIDENCE_ROLE_PRIMARY)
    {
        return parsed->SourceId == 0x00001001u;
    }

    return parsed->SourceId == 0x00001002u;
}

static const uint8 *AERC_QUAL_PublicKey(const AERC_QUAL_Parsed_t *parsed)
{
    if (parsed->Role == AERC_EVIDENCE_ROLE_PRIMARY && parsed->KeyId == 0x00002001u)
    {
        return AERC_QUAL_PrimaryPublicKey;
    }

    if (parsed->Role == AERC_EVIDENCE_ROLE_CORROBORATOR && parsed->KeyId == 0x00002002u)
    {
        return AERC_QUAL_CorrPublicKey;
    }

    return NULL;
}

static bool AERC_QUAL_Fresh(uint64 issued_tick)
{
    if (issued_tick > AERC_QUAL_Context.NowTick)
    {
        return false;
    }

    return (AERC_QUAL_Context.NowTick - issued_tick) <= AERC_QUAL_Context.FreshnessMaxAgeTicks;
}

static void AERC_QUAL_UpdateSequence(
    AERC_QUAL_PathState_t *state,
    uint64 sequence,
    const uint8 body[AERC_EVIDENCE_BODY_BYTES],
    bool signature_valid)
{
    if (!signature_valid)
    {
        return;
    }

    if (!state->SequenceSet)
    {
        state->SequenceSet = true;
        state->LastSequence = sequence;
        memcpy(state->LastBody, body, sizeof(state->LastBody));
        return;
    }

    if (sequence > state->LastSequence)
    {
        state->LastSequence = sequence;
        memcpy(state->LastBody, body, sizeof(state->LastBody));
        return;
    }

    if (sequence == state->LastSequence)
    {
        if (memcmp(state->LastBody, body, sizeof(state->LastBody)) != 0)
        {
            state->Contradicted = true;
        }
        return;
    }

    state->Contradicted = true;
}

static CFE_Status_t AERC_QUAL_EmitSnapshot(
    uint8 role,
    const AERC_QUAL_Parsed_t *parsed,
    CFE_SB_MsgId_t base_mid,
    CFE_SB_MsgId_t corr_mid)
{
    AERC_POLICY_SNAPSHOT_Message_t snapshot;
    CFE_SB_MsgId_t mid;
    CFE_Status_t status;

    memset(&snapshot, 0, sizeof(snapshot));

    if (role == AERC_EVIDENCE_ROLE_PRIMARY)
    {
        mid = base_mid;
        snapshot.FeatureCount = AERC_POLICY_BASE_FEATURE_COUNT;
    }
    else
    {
        if (!AERC_QUAL_Primary.Available)
        {
            CFE_ES_WriteToSysLog(
                "AERC_QUAL WAIT_PRIMARY scenario=0x%08lX role=corroborator\n",
                (unsigned long)parsed->ScenarioId);
            return CFE_SUCCESS;
        }

        mid = corr_mid;
        snapshot.FeatureCount = AERC_POLICY_CORR_FEATURE_COUNT;
    }

    status = CFE_MSG_Init(&snapshot.TelemetryHeader.Msg, mid, sizeof(snapshot));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    snapshot.ScenarioId = parsed->ScenarioId;

    memcpy(&snapshot.Features[AERC_FEATURE_PRIMARY_SIGNATURE_VALID],
           AERC_QUAL_Primary.Features,
           AERC_QUAL_PATH_FEATURES);
    snapshot.Features[AERC_FEATURE_HEALTH_READY] = AERC_QUAL_Context.ObservedHealthReady;
    snapshot.Features[AERC_FEATURE_SECURITY_SIGNAL] = AERC_QUAL_Context.SecuritySignal;

    if (role == AERC_EVIDENCE_ROLE_CORROBORATOR)
    {
        memcpy(&snapshot.Features[AERC_FEATURE_CORR_SIGNATURE_VALID],
               AERC_QUAL_Corr.Features,
               AERC_QUAL_PATH_FEATURES);
    }

    return CFE_SB_TransmitMsg(&snapshot.TelemetryHeader.Msg, true);
}

static CFE_Status_t AERC_QUAL_HandleContext(const AERC_QUALIFIER_CONTEXT_Message_t *context)
{
    bool reset;

    if (context->ScenarioId == 0u ||
        context->ObservedHealthReady > 1u ||
        context->SecuritySignal > 1u ||
        context->Reserved[0] != 0u ||
        context->Reserved[1] != 0u)
    {
        return CFE_STATUS_BAD_ARGUMENT;
    }

    reset = !AERC_QUAL_Context.Available ||
            context->ScenarioId != AERC_QUAL_Context.ScenarioId ||
            context->ExpectedEpoch != AERC_QUAL_Context.ExpectedEpoch;

    AERC_QUAL_Context.Available = true;
    AERC_QUAL_Context.ScenarioId = context->ScenarioId;
    AERC_QUAL_Context.ExpectedEpoch = context->ExpectedEpoch;
    AERC_QUAL_Context.NowTick = context->NowTick;
    AERC_QUAL_Context.FreshnessMaxAgeTicks = context->FreshnessMaxAgeTicks;
    AERC_QUAL_Context.ObservedHealthReady = context->ObservedHealthReady;
    AERC_QUAL_Context.SecuritySignal = context->SecuritySignal;

    if (reset)
    {
        AERC_QUAL_ResetPaths();
    }

    CFE_ES_WriteToSysLog(
        "AERC_QUAL CONTEXT scenario=0x%08lX freshness_max_age=%lu health=%u security=%u reset=%u\n",
        (unsigned long)context->ScenarioId,
        (unsigned long)context->FreshnessMaxAgeTicks,
        (unsigned int)context->ObservedHealthReady,
        (unsigned int)context->SecuritySignal,
        reset ? 1u : 0u);

    return CFE_SUCCESS;
}

static CFE_Status_t AERC_QUAL_HandleEvidence(
    const AERC_EVIDENCE_Message_t *message,
    CFE_SB_MsgId_t base_mid,
    CFE_SB_MsgId_t corr_mid)
{
    AERC_QUAL_Parsed_t parsed;
    AERC_QUAL_PathState_t *state;
    const uint8 *public_key;
    bool signature_valid;
    bool source_trusted;
    bool fresh;
    bool epoch_valid;
    CFE_Status_t status;

    if (!AERC_QUAL_Context.Available)
    {
        CFE_ES_WriteToSysLog("AERC_QUAL REJECT_NO_CONTEXT request=%lu\n",
                             (unsigned long)message->RequestSequence);
        return CFE_SUCCESS;
    }

    if (!AERC_QUAL_Parse(message->Body, &parsed))
    {
        CFE_ES_WriteToSysLog("AERC_QUAL REJECT_STRUCTURE request=%lu\n",
                             (unsigned long)message->RequestSequence);
        return CFE_SUCCESS;
    }

    if (parsed.ScenarioId != AERC_QUAL_Context.ScenarioId)
    {
        CFE_ES_WriteToSysLog(
            "AERC_QUAL REJECT_CONTEXT request=%lu signed_scenario=0x%08lX expected_scenario=0x%08lX\n",
            (unsigned long)message->RequestSequence,
            (unsigned long)parsed.ScenarioId,
            (unsigned long)AERC_QUAL_Context.ScenarioId);
        return CFE_SUCCESS;
    }

    state = parsed.Role == AERC_EVIDENCE_ROLE_PRIMARY ? &AERC_QUAL_Primary : &AERC_QUAL_Corr;
    public_key = AERC_QUAL_PublicKey(&parsed);
    source_trusted = AERC_QUAL_SourceTrusted(&parsed);
    fresh = AERC_QUAL_Fresh(parsed.IssuedTick);
    epoch_valid = parsed.Epoch == AERC_QUAL_Context.ExpectedEpoch;

    signature_valid = public_key != NULL &&
                      AERC_ED25519_Verify(message->Signature,
                                         AERC_EVIDENCE_SIGNATURE_BYTES,
                                         public_key,
                                         AERC_ED25519_PUBLIC_KEY_BYTES,
                                         message->Body,
                                         AERC_EVIDENCE_BODY_BYTES) == AERC_ED25519_VERIFY_OK;

    AERC_QUAL_UpdateSequence(state, parsed.Sequence, message->Body, signature_valid);

    state->Features[0] = signature_valid ? 1u : 0u;
    state->Features[1] = source_trusted ? 1u : 0u;
    state->Features[2] = fresh ? 1u : 0u;
    state->Features[3] = epoch_valid ? 1u : 0u;
    state->Features[4] = state->Contradicted ? 0u : 1u;
    state->Features[5] = 1u;
    state->Features[6] = parsed.Authorization;
    state->Available = true;

    status = AERC_QUAL_EmitSnapshot(parsed.Role, &parsed, base_mid, corr_mid);
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    CFE_ES_WriteToSysLog(
        "AERC_QUAL SNAPSHOT scenario=0x%08lX kind=%s sig=%u trust=%u fresh=%u epoch=%u noncontra=%u complete=%u auth=%u\n",
        (unsigned long)parsed.ScenarioId,
        parsed.Role == AERC_EVIDENCE_ROLE_PRIMARY ? "BASE" : "CORR",
        (unsigned int)state->Features[0],
        (unsigned int)state->Features[1],
        (unsigned int)state->Features[2],
        (unsigned int)state->Features[3],
        (unsigned int)state->Features[4],
        (unsigned int)state->Features[5],
        (unsigned int)state->Features[6]);

    CFE_EVS_SendEvent(AERC_QUAL_SNAP_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_QUAL emitted %s snapshot request=%lu",
                      parsed.Role == AERC_EVIDENCE_ROLE_PRIMARY ? "base" : "corroborated",
                      (unsigned long)message->RequestSequence);

    return CFE_SUCCESS;
}

void AERC_QUAL_Main(void)
{
    CFE_Status_t status;
    uint32 run_status = CFE_ES_RunStatus_APP_RUN;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t evidence_mid = CFE_SB_ValueToMsgId(AERC_EVIDENCE_QUALIFIER_MID_VALUE);
    CFE_SB_MsgId_t context_mid = CFE_SB_ValueToMsgId(AERC_QUALIFIER_CONTEXT_MID_VALUE);
    CFE_SB_MsgId_t base_mid = CFE_SB_ValueToMsgId(AERC_POLICY_BASE_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t corr_mid = CFE_SB_ValueToMsgId(AERC_POLICY_CORR_SNAPSHOT_MID_VALUE);

    memset(&AERC_QUAL_Context, 0, sizeof(AERC_QUAL_Context));
    AERC_QUAL_ResetPaths();

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 12, "AERC_QUAL_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(evidence_mid, pipe);
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(context_mid, pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_QUAL initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_QUAL_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_QUAL initialized pre-canonical signed-evidence qualifier");

    while (CFE_ES_RunLoop(&run_status) == true)
    {
        CFE_MSG_Size_t size = 0;
        CFE_SB_MsgId_t msg_id = CFE_SB_INVALID_MSG_ID;

        status = CFE_SB_ReceiveBuffer(&received, pipe, CFE_SB_PEND_FOREVER);
        if (status != CFE_SUCCESS || received == NULL)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        if (CFE_MSG_GetMsgId(&received->Msg, &msg_id) != CFE_SUCCESS ||
            CFE_MSG_GetSize(&received->Msg, &size) != CFE_SUCCESS)
        {
            continue;
        }

        if (CFE_SB_MsgId_Equal(msg_id, context_mid))
        {
            if (size != sizeof(AERC_QUALIFIER_CONTEXT_Message_t))
            {
                CFE_ES_WriteToSysLog("AERC_QUAL REJECT_CONTEXT_LENGTH expected=%lu actual=%lu\n",
                                     (unsigned long)sizeof(AERC_QUALIFIER_CONTEXT_Message_t),
                                     (unsigned long)size);
                continue;
            }

            status = AERC_QUAL_HandleContext((const AERC_QUALIFIER_CONTEXT_Message_t *)received);
        }
        else if (CFE_SB_MsgId_Equal(msg_id, evidence_mid))
        {
            if (size != sizeof(AERC_EVIDENCE_Message_t))
            {
                CFE_ES_WriteToSysLog("AERC_QUAL REJECT_EVIDENCE_LENGTH expected=%lu actual=%lu\n",
                                     (unsigned long)sizeof(AERC_EVIDENCE_Message_t),
                                     (unsigned long)size);
                continue;
            }

            status = AERC_QUAL_HandleEvidence((const AERC_EVIDENCE_Message_t *)received,
                                              base_mid,
                                              corr_mid);
        }
        else
        {
            status = CFE_SUCCESS;
        }

        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_QUAL_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_QUAL handler error RC=0x%08lX",
                              (unsigned long)status);
        }
    }

    CFE_ES_ExitApp(run_status);
}
