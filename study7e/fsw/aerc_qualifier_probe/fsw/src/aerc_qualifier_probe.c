#include "aerc_qualifier_probe.h"

#include "osapi.h"
#include <string.h>

#define AERC_QPROBE_INIT_EID 1
#define AERC_QPROBE_PASS_EID 2
#define AERC_QPROBE_ERR_EID  3

#define AERC_Q_SCENARIO_A1 0x53374A01u
#define AERC_Q_SCENARIO_A2 0x53374A02u
#define AERC_Q_SCENARIO_A3 0x53374A03u

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 RequestSequence;
} AERC_QPROBE_ShortIngress_t;

static const uint8 A1_PRIMARY_BODY[64] = {
    0x53,0x37,0x45,0x2d,0x41,0x45,0x52,0x43,
    0x2d,0x41,0x55,0x54,0x48,0x2d,0x56,0x31,
    0x01,0x01,0x01,0x00,0x53,0x37,0x4a,0x01,
    0x00,0x00,0x10,0x01,0x00,0x00,0x30,0x01,
    0x00,0x00,0x20,0x01,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,
    0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xe8,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01
};

static const uint8 A1_PRIMARY_SIG[64] = {
    0x5d,0x19,0xdc,0x8f,0xdd,0x02,0x0e,0xf6,
    0x01,0xc1,0x24,0x28,0xd4,0x3c,0xb1,0x4f,
    0xa8,0x45,0x94,0x87,0xec,0x15,0x39,0x73,
    0xfc,0x7b,0x9f,0xfc,0xf1,0xc9,0x1b,0x5f,
    0x87,0xd6,0xe6,0x81,0x5e,0x67,0xe8,0x33,
    0x63,0xe5,0x9e,0x8f,0x68,0xe8,0xed,0x6c,
    0x13,0x6b,0x94,0x16,0xba,0xe0,0x0b,0xa3,
    0x53,0xa8,0x54,0xa4,0x55,0xd7,0xa5,0x06
};

static const uint8 A1_CORR_BODY[64] = {
    0x53,0x37,0x45,0x2d,0x41,0x45,0x52,0x43,
    0x2d,0x41,0x55,0x54,0x48,0x2d,0x56,0x31,
    0x01,0x02,0x01,0x00,0x53,0x37,0x4a,0x01,
    0x00,0x00,0x10,0x02,0x00,0x00,0x30,0x02,
    0x00,0x00,0x20,0x02,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,
    0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xe8,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01
};

static const uint8 A1_CORR_SIG[64] = {
    0xc2,0x76,0x82,0x2b,0x0a,0xcd,0xd9,0x5c,
    0x43,0x0d,0x15,0xd5,0x22,0xca,0xab,0xa9,
    0x82,0xc2,0x10,0xed,0x54,0xbc,0x3d,0xfa,
    0xe3,0xf6,0x76,0x0c,0xe2,0x50,0xb8,0x78,
    0x3f,0xa9,0xce,0x87,0x0d,0x84,0x82,0x0d,
    0x69,0xa0,0x64,0xc4,0x8c,0xee,0x8c,0xf1,
    0xc4,0xb4,0xd5,0x5d,0x71,0x04,0x53,0x84,
    0x68,0x7c,0xd7,0x4e,0xbc,0x24,0xe5,0x00
};

static const uint8 A2_PRIMARY_BODY[64] = {
    0x53,0x37,0x45,0x2d,0x41,0x45,0x52,0x43,
    0x2d,0x41,0x55,0x54,0x48,0x2d,0x56,0x31,
    0x01,0x01,0x01,0x00,0x53,0x37,0x4a,0x02,
    0x00,0x00,0x10,0x01,0x00,0x00,0x30,0x01,
    0x00,0x00,0x20,0x01,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,
    0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xe8,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01
};

static const uint8 A2_PRIMARY_SIG[64] = {
    0x81,0xd2,0x06,0xce,0xbd,0x0c,0xcc,0xf3,
    0x0d,0x17,0x90,0xfb,0x82,0x45,0xcf,0x15,
    0xc5,0x97,0xaa,0x05,0xe7,0x4e,0x12,0xdf,
    0xfb,0x12,0x0c,0x4e,0x38,0x6d,0xf7,0xc0,
    0x93,0x99,0x05,0x3e,0x42,0xf9,0xe4,0xb9,
    0x62,0xda,0xae,0x63,0x05,0xde,0x3b,0x07,
    0xc0,0xe0,0x1c,0x64,0xe3,0x72,0x4e,0x75,
    0x02,0xbf,0xaf,0x57,0x54,0x25,0x51,0x03
};

static const uint8 A3_TRUE_BODY[64] = {
    0x53,0x37,0x45,0x2d,0x41,0x45,0x52,0x43,
    0x2d,0x41,0x55,0x54,0x48,0x2d,0x56,0x31,
    0x01,0x01,0x01,0x00,0x53,0x37,0x4a,0x03,
    0x00,0x00,0x10,0x01,0x00,0x00,0x30,0x01,
    0x00,0x00,0x20,0x01,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,
    0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xe8,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01
};

static const uint8 A3_TRUE_SIG[64] = {
    0x3e,0xb8,0x92,0x99,0xae,0x03,0x72,0x33,
    0xe4,0xe9,0x1a,0xb6,0x07,0x95,0x65,0xac,
    0xcb,0xd1,0xe3,0xd2,0xa2,0x58,0x2e,0x52,
    0x8c,0x66,0x72,0x6b,0x47,0x7e,0x84,0x1e,
    0xd7,0xd9,0x36,0xf0,0x67,0x46,0x74,0x6e,
    0xbc,0x13,0x1b,0xa9,0x5c,0x07,0xba,0x77,
    0x55,0xf3,0x01,0x26,0x7c,0x56,0xc0,0xfe,
    0x1f,0x89,0x7c,0xda,0xdc,0x00,0xfb,0x07
};

static const uint8 A3_FALSE_BODY[64] = {
    0x53,0x37,0x45,0x2d,0x41,0x45,0x52,0x43,
    0x2d,0x41,0x55,0x54,0x48,0x2d,0x56,0x31,
    0x01,0x01,0x00,0x00,0x53,0x37,0x4a,0x03,
    0x00,0x00,0x10,0x01,0x00,0x00,0x30,0x01,
    0x00,0x00,0x20,0x01,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,
    0x00,0x00,0x00,0x00,0x00,0x00,0x03,0xe8,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01
};

static const uint8 A3_FALSE_SIG[64] = {
    0x0e,0xc9,0x43,0x91,0xb9,0x2b,0x46,0x29,
    0x45,0xbd,0xeb,0xb3,0xd5,0xaf,0x76,0x12,
    0x23,0xf6,0x20,0xe3,0x1b,0x58,0x95,0x3c,
    0x71,0xe7,0xbb,0x7d,0xa8,0x86,0xdf,0x18,
    0x53,0xde,0x7a,0x9b,0xad,0xc2,0x31,0x83,
    0x00,0x97,0x7a,0xec,0x5c,0xe4,0x98,0x88,
    0x57,0xbb,0x22,0xdd,0x93,0x99,0xf7,0x76,
    0xe5,0x4c,0x18,0x54,0x76,0x48,0x94,0x00
};

static void AERC_QPROBE_Fill(uint8 features[AERC_POLICY_FEATURE_SLOTS], uint8 value)
{
    uint8 i;
    for (i = 0u; i < AERC_POLICY_FEATURE_SLOTS; ++i)
    {
        features[i] = value;
    }
}

static CFE_Status_t AERC_QPROBE_SendContext(CFE_SB_MsgId_t mid, uint32 scenario_id)
{
    AERC_QUALIFIER_CONTEXT_Message_t context;
    CFE_Status_t status;

    memset(&context, 0, sizeof(context));
    status = CFE_MSG_Init(&context.TelemetryHeader.Msg, mid, sizeof(context));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    context.ScenarioId = scenario_id;
    context.ExpectedEpoch = 7u;
    context.NowTick = 1000u;
    context.FreshnessMaxAgeTicks = 5u;
    context.ObservedHealthReady = 1u;
    context.SecuritySignal = 1u;

    return CFE_SB_TransmitMsg(&context.TelemetryHeader.Msg, true);
}

static CFE_Status_t AERC_QPROBE_SendEvidence(
    CFE_SB_MsgId_t mid,
    uint32 request_sequence,
    const uint8 body[64],
    const uint8 signature[64],
    bool mutate_epoch_after_signature)
{
    AERC_EVIDENCE_Message_t message;
    CFE_Status_t status;

    memset(&message, 0, sizeof(message));
    status = CFE_MSG_Init(&message.TelemetryHeader.Msg, mid, sizeof(message));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    message.RequestSequence = request_sequence;
    memcpy(message.Body, body, sizeof(message.Body));
    memcpy(message.Signature, signature, sizeof(message.Signature));

    if (mutate_epoch_after_signature)
    {
        message.Body[47] ^= 0x01u;
    }

    return CFE_SB_TransmitMsg(&message.TelemetryHeader.Msg, true);
}

static CFE_Status_t AERC_QPROBE_SendShort(CFE_SB_MsgId_t mid)
{
    AERC_QPROBE_ShortIngress_t message;
    CFE_Status_t status;

    memset(&message, 0, sizeof(message));
    status = CFE_MSG_Init(&message.TelemetryHeader.Msg, mid, sizeof(message));
    if (status == CFE_SUCCESS)
    {
        message.RequestSequence = 99u;
        status = CFE_SB_TransmitMsg(&message.TelemetryHeader.Msg, true);
    }
    return status;
}

static bool AERC_QPROBE_SnapshotMatches(
    const CFE_SB_Buffer_t *received,
    uint32 scenario_id,
    uint8 feature_count,
    const uint8 expected[AERC_POLICY_FEATURE_SLOTS])
{
    CFE_MSG_Size_t size = 0;
    const AERC_POLICY_SNAPSHOT_Message_t *snapshot;

    if (CFE_MSG_GetSize(&received->Msg, &size) != CFE_SUCCESS ||
        size != sizeof(AERC_POLICY_SNAPSHOT_Message_t))
    {
        return false;
    }

    snapshot = (const AERC_POLICY_SNAPSHOT_Message_t *)received;
    return snapshot->ScenarioId == scenario_id &&
           snapshot->FeatureCount == feature_count &&
           memcmp(snapshot->Features, expected, AERC_POLICY_FEATURE_SLOTS) == 0;
}

static bool AERC_QPROBE_DecisionMatches(
    const CFE_SB_Buffer_t *received,
    uint32 scenario_id,
    uint32 decision_sequence,
    uint8 policy_id,
    uint8 action)
{
    CFE_MSG_Size_t size = 0;
    const AERC_POLICY_DECISION_Message_t *decision;

    if (CFE_MSG_GetSize(&received->Msg, &size) != CFE_SUCCESS ||
        size != sizeof(AERC_POLICY_DECISION_Message_t))
    {
        return false;
    }

    decision = (const AERC_POLICY_DECISION_Message_t *)received;
    return decision->ScenarioId == scenario_id &&
           decision->DecisionSequence == decision_sequence &&
           decision->PolicyId == policy_id &&
           decision->Action == action;
}

static bool AERC_QPROBE_RecordMatches(
    const CFE_SB_Buffer_t *received,
    uint32 scenario_id,
    uint32 receipt_sequence,
    uint8 policy_id,
    uint8 action)
{
    CFE_MSG_Size_t size = 0;
    const AERC_RECOVERY_RECORD_Message_t *record;

    if (CFE_MSG_GetSize(&received->Msg, &size) != CFE_SUCCESS ||
        size != sizeof(AERC_RECOVERY_RECORD_Message_t))
    {
        return false;
    }

    record = (const AERC_RECOVERY_RECORD_Message_t *)received;
    return record->ScenarioId == scenario_id &&
           record->ReceiptSequence == receipt_sequence &&
           record->PolicyId == policy_id &&
           record->Action == action;
}

static CFE_Status_t AERC_QPROBE_Expect(
    CFE_SB_MsgId_t ingress_mid,
    CFE_SB_PipeId_t snapshot_pipe,
    CFE_SB_PipeId_t decision_pipe,
    CFE_SB_PipeId_t record_pipe,
    uint32 request_sequence,
    const uint8 body[64],
    const uint8 signature[64],
    bool mutate_epoch_after_signature,
    uint32 scenario_id,
    uint32 decision_sequence,
    uint8 policy_id,
    uint8 action,
    uint8 feature_count,
    const uint8 expected[AERC_POLICY_FEATURE_SLOTS])
{
    CFE_Status_t status;
    CFE_SB_Buffer_t *received = NULL;

    status = AERC_QPROBE_SendEvidence(ingress_mid,
                                      request_sequence,
                                      body,
                                      signature,
                                      mutate_epoch_after_signature);
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    status = CFE_SB_ReceiveBuffer(&received, snapshot_pipe, 2000);
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_QPROBE_SnapshotMatches(received, scenario_id, feature_count, expected))
    {
        return CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    received = NULL;
    status = CFE_SB_ReceiveBuffer(&received, decision_pipe, 2000);
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_QPROBE_DecisionMatches(received,
                                     scenario_id,
                                     decision_sequence,
                                     policy_id,
                                     action))
    {
        return CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    received = NULL;
    status = CFE_SB_ReceiveBuffer(&received, record_pipe, 2000);
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_QPROBE_RecordMatches(received,
                                   scenario_id,
                                   decision_sequence,
                                   policy_id,
                                   action))
    {
        return CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    return CFE_SUCCESS;
}

static bool AERC_QPROBE_ExpectNoSnapshot(CFE_SB_PipeId_t snapshot_pipe)
{
    CFE_SB_Buffer_t *received = NULL;
    CFE_Status_t status = CFE_SB_ReceiveBuffer(&received, snapshot_pipe, 300);
    return status == CFE_SB_TIME_OUT && received == NULL;
}

void AERC_QPROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t base_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_PipeId_t corr_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_PipeId_t decision_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_PipeId_t record_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_MsgId_t ingress_mid = CFE_SB_ValueToMsgId(AERC_EVIDENCE_INGRESS_MID_VALUE);
    CFE_SB_MsgId_t context_mid = CFE_SB_ValueToMsgId(AERC_QUALIFIER_CONTEXT_MID_VALUE);
    CFE_SB_MsgId_t base_mid = CFE_SB_ValueToMsgId(AERC_POLICY_BASE_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t corr_mid = CFE_SB_ValueToMsgId(AERC_POLICY_CORR_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t decision_mid = CFE_SB_ValueToMsgId(AERC_POLICY_DECISION_MID_VALUE);
    CFE_SB_MsgId_t record_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_RECORD_MID_VALUE);
    uint8 features[AERC_POLICY_FEATURE_SLOTS];

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&base_pipe, 8, "AERC_QB_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&corr_pipe, 8, "AERC_QC_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&decision_pipe, 8, "AERC_QD_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&record_pipe, 8, "AERC_QR_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(base_mid, base_pipe);
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(corr_mid, corr_pipe);
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(decision_mid, decision_pipe);
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(record_mid, record_pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_QPROBE initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_QPROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_QPROBE starting producer/qualifier engineering smoke");

    OS_TaskDelay(1200);

    status = AERC_QPROBE_SendContext(context_mid, AERC_Q_SCENARIO_A1);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }
    OS_TaskDelay(100);

    AERC_QPROBE_Fill(features, 0u);
    memset(features, 1, AERC_POLICY_BASE_FEATURE_COUNT);
    status = AERC_QPROBE_Expect(ingress_mid, base_pipe, decision_pipe, record_pipe,
                                1u, A1_PRIMARY_BODY, A1_PRIMARY_SIG, false,
                                AERC_Q_SCENARIO_A1, 1u,
                                AERC_POLICY_D0_BASE, AERC_ACTION_ENTER_RECOVERY_GATE,
                                AERC_POLICY_BASE_FEATURE_COUNT, features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_QPROBE_Fill(features, 1u);
    status = AERC_QPROBE_Expect(ingress_mid, corr_pipe, decision_pipe, record_pipe,
                                2u, A1_CORR_BODY, A1_CORR_SIG, false,
                                AERC_Q_SCENARIO_A1, 2u,
                                AERC_POLICY_D1_CORROBORATED, AERC_ACTION_ENTER_RECOVERY_GATE,
                                AERC_POLICY_CORR_FEATURE_COUNT, features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    status = AERC_QPROBE_SendContext(context_mid, AERC_Q_SCENARIO_A2);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }
    OS_TaskDelay(100);

    AERC_QPROBE_Fill(features, 0u);
    features[AERC_FEATURE_PRIMARY_SOURCE_TRUSTED] = 1u;
    features[AERC_FEATURE_PRIMARY_FRESH] = 1u;
    features[AERC_FEATURE_PRIMARY_NONCONTRADICTORY] = 1u;
    features[AERC_FEATURE_PRIMARY_COMPLETE] = 1u;
    features[AERC_FEATURE_PRIMARY_AUTHORIZATION] = 1u;
    features[AERC_FEATURE_HEALTH_READY] = 1u;
    features[AERC_FEATURE_SECURITY_SIGNAL] = 1u;
    status = AERC_QPROBE_Expect(ingress_mid, base_pipe, decision_pipe, record_pipe,
                                3u, A2_PRIMARY_BODY, A2_PRIMARY_SIG, true,
                                AERC_Q_SCENARIO_A2, 3u,
                                AERC_POLICY_D0_BASE, AERC_ACTION_HOLD,
                                AERC_POLICY_BASE_FEATURE_COUNT, features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    status = AERC_QPROBE_SendContext(context_mid, AERC_Q_SCENARIO_A3);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }
    OS_TaskDelay(100);

    AERC_QPROBE_Fill(features, 0u);
    memset(features, 1, AERC_POLICY_BASE_FEATURE_COUNT);
    status = AERC_QPROBE_Expect(ingress_mid, base_pipe, decision_pipe, record_pipe,
                                4u, A3_TRUE_BODY, A3_TRUE_SIG, false,
                                AERC_Q_SCENARIO_A3, 4u,
                                AERC_POLICY_D0_BASE, AERC_ACTION_ENTER_RECOVERY_GATE,
                                AERC_POLICY_BASE_FEATURE_COUNT, features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_QPROBE_Fill(features, 0u);
    features[AERC_FEATURE_PRIMARY_SIGNATURE_VALID] = 1u;
    features[AERC_FEATURE_PRIMARY_SOURCE_TRUSTED] = 1u;
    features[AERC_FEATURE_PRIMARY_FRESH] = 1u;
    features[AERC_FEATURE_PRIMARY_EPOCH_VALID] = 1u;
    features[AERC_FEATURE_PRIMARY_COMPLETE] = 1u;
    features[AERC_FEATURE_HEALTH_READY] = 1u;
    features[AERC_FEATURE_SECURITY_SIGNAL] = 1u;
    status = AERC_QPROBE_Expect(ingress_mid, base_pipe, decision_pipe, record_pipe,
                                5u, A3_FALSE_BODY, A3_FALSE_SIG, false,
                                AERC_Q_SCENARIO_A3, 5u,
                                AERC_POLICY_D0_BASE, AERC_ACTION_HOLD,
                                AERC_POLICY_BASE_FEATURE_COUNT, features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    status = AERC_QPROBE_SendShort(ingress_mid);
    if (status != CFE_SUCCESS || !AERC_QPROBE_ExpectNoSnapshot(base_pipe))
    {
        goto fail;
    }

    CFE_ES_WriteToSysLog(
        "AERC_QPROBE PASS base_enter=2 corr_enter=1 f9_hold=1 f12_hold=1 malformed=1 decisions=5\n");
    CFE_EVS_SendEvent(AERC_QPROBE_PASS_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_QPROBE producer/qualifier path PASS");
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
    return;

fail:
    CFE_EVS_SendEvent(AERC_QPROBE_ERR_EID,
                      CFE_EVS_EventType_ERROR,
                      "AERC_QPROBE failed RC=0x%08lX",
                      (unsigned long)status);
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
}
