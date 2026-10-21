#include "aerc_policy_probe.h"

#include "osapi.h"
#include <string.h>

#define AERC_PPROBE_INIT_EID 1
#define AERC_PPROBE_PASS_EID 2
#define AERC_PPROBE_ERR_EID  3

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
} AERC_PPROBE_ShortSnapshot_t;

static void AERC_PPROBE_Fill(uint8 features[AERC_POLICY_FEATURE_SLOTS], uint8 value)
{
    uint8 i;

    for (i = 0u; i < AERC_POLICY_FEATURE_SLOTS; ++i)
    {
        features[i] = value;
    }
}

static CFE_Status_t AERC_PPROBE_SendSnapshot(
    CFE_SB_MsgId_t mid,
    uint32 scenario_id,
    uint8 feature_count,
    const uint8 features[AERC_POLICY_FEATURE_SLOTS])
{
    AERC_POLICY_SNAPSHOT_Message_t snapshot;
    CFE_Status_t status;

    memset(&snapshot, 0, sizeof(snapshot));
    status = CFE_MSG_Init(&snapshot.TelemetryHeader.Msg, mid, sizeof(snapshot));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    snapshot.ScenarioId = scenario_id;
    snapshot.FeatureCount = feature_count;
    memcpy(snapshot.Features, features, sizeof(snapshot.Features));

    return CFE_SB_TransmitMsg(&snapshot.TelemetryHeader.Msg, true);
}

static CFE_Status_t AERC_PPROBE_SendShort(CFE_SB_MsgId_t mid)
{
    AERC_PPROBE_ShortSnapshot_t snapshot;
    CFE_Status_t status;

    memset(&snapshot, 0, sizeof(snapshot));
    status = CFE_MSG_Init(&snapshot.TelemetryHeader.Msg, mid, sizeof(snapshot));
    if (status == CFE_SUCCESS)
    {
        snapshot.ScenarioId = AERC_PPROBE_SHORT_SCENARIO;
        status = CFE_SB_TransmitMsg(&snapshot.TelemetryHeader.Msg, true);
    }

    return status;
}

static bool AERC_PPROBE_DecisionMatches(
    const CFE_SB_Buffer_t *received,
    uint32 scenario_id,
    uint32 sequence,
    uint8 policy_id,
    uint8 action,
    uint8 feature_count,
    const uint8 features[AERC_POLICY_FEATURE_SLOTS])
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
           decision->DecisionSequence == sequence &&
           decision->PolicyId == policy_id &&
           decision->Action == action &&
           decision->FeatureCount == feature_count &&
           memcmp(decision->Features, features, AERC_POLICY_FEATURE_SLOTS) == 0;
}

static bool AERC_PPROBE_RecordMatches(
    const CFE_SB_Buffer_t *received,
    uint32 scenario_id,
    uint32 sequence,
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
           record->ReceiptSequence == sequence &&
           record->PolicyId == policy_id &&
           record->Action == action;
}

static CFE_Status_t AERC_PPROBE_Expect(
    CFE_SB_MsgId_t snapshot_mid,
    CFE_SB_PipeId_t decision_pipe,
    CFE_SB_PipeId_t record_pipe,
    uint32 scenario_id,
    uint32 sequence,
    uint8 policy_id,
    uint8 action,
    uint8 feature_count,
    const uint8 features[AERC_POLICY_FEATURE_SLOTS])
{
    CFE_Status_t status;
    CFE_SB_Buffer_t *received = NULL;

    status = AERC_PPROBE_SendSnapshot(snapshot_mid, scenario_id, feature_count, features);
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    status = CFE_SB_ReceiveBuffer(&received, decision_pipe, 2000);
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_PPROBE_DecisionMatches(received,
                                     scenario_id,
                                     sequence,
                                     policy_id,
                                     action,
                                     feature_count,
                                     features))
    {
        return CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    received = NULL;
    status = CFE_SB_ReceiveBuffer(&received, record_pipe, 2000);
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_PPROBE_RecordMatches(received, scenario_id, sequence, policy_id, action))
    {
        return CFE_STATUS_EXTERNAL_RESOURCE_FAIL;
    }

    return CFE_SUCCESS;
}

void AERC_PPROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t decision_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_PipeId_t record_pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_MsgId_t base_mid = CFE_SB_ValueToMsgId(AERC_POLICY_BASE_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t corr_mid = CFE_SB_ValueToMsgId(AERC_POLICY_CORR_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t decision_mid = CFE_SB_ValueToMsgId(AERC_POLICY_DECISION_MID_VALUE);
    CFE_SB_MsgId_t record_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_RECORD_MID_VALUE);
    uint8 features[AERC_POLICY_FEATURE_SLOTS];
    uint8 i;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&decision_pipe, 8, "AERC_PD_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&record_pipe, 8, "AERC_PR_PIPE");
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
        CFE_ES_WriteToSysLog("AERC_PPROBE initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_PPROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_PPROBE starting deterministic D0/D1 engineering smoke");

    OS_TaskDelay(1000);

    AERC_PPROBE_Fill(features, 0u);
    for (i = 0u; i < AERC_POLICY_BASE_FEATURE_COUNT; ++i)
    {
        features[i] = 1u;
    }
    status = AERC_PPROBE_Expect(base_mid,
                                decision_pipe,
                                record_pipe,
                                AERC_PPROBE_D0_ENTER_SCENARIO,
                                1u,
                                AERC_POLICY_D0_BASE,
                                AERC_ACTION_ENTER_RECOVERY_GATE,
                                AERC_POLICY_BASE_FEATURE_COUNT,
                                features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    status = AERC_PPROBE_SendShort(base_mid);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_PPROBE_Fill(features, 1u);
    status = AERC_PPROBE_SendSnapshot(base_mid,
                                      AERC_PPROBE_COUNT_SCENARIO,
                                      AERC_POLICY_CORR_FEATURE_COUNT,
                                      features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_PPROBE_Fill(features, 0u);
    for (i = 0u; i < AERC_POLICY_BASE_FEATURE_COUNT; ++i)
    {
        features[i] = 1u;
    }
    features[AERC_FEATURE_HEALTH_READY] = 0u;
    status = AERC_PPROBE_Expect(base_mid,
                                decision_pipe,
                                record_pipe,
                                AERC_PPROBE_D0_HOLD_SCENARIO,
                                2u,
                                AERC_POLICY_D0_BASE,
                                AERC_ACTION_HOLD,
                                AERC_POLICY_BASE_FEATURE_COUNT,
                                features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_PPROBE_Fill(features, 1u);
    status = AERC_PPROBE_Expect(corr_mid,
                                decision_pipe,
                                record_pipe,
                                AERC_PPROBE_D1_ENTER_SCENARIO,
                                3u,
                                AERC_POLICY_D1_CORROBORATED,
                                AERC_ACTION_ENTER_RECOVERY_GATE,
                                AERC_POLICY_CORR_FEATURE_COUNT,
                                features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_PPROBE_Fill(features, 1u);
    features[AERC_FEATURE_CORR_SIGNATURE_VALID] = 2u;
    status = AERC_PPROBE_SendSnapshot(corr_mid,
                                      AERC_PPROBE_BINARY_SCENARIO,
                                      AERC_POLICY_CORR_FEATURE_COUNT,
                                      features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    AERC_PPROBE_Fill(features, 1u);
    features[AERC_FEATURE_CORR_AUTHORIZATION] = 0u;
    status = AERC_PPROBE_Expect(corr_mid,
                                decision_pipe,
                                record_pipe,
                                AERC_PPROBE_D1_HOLD_SCENARIO,
                                4u,
                                AERC_POLICY_D1_CORROBORATED,
                                AERC_ACTION_HOLD,
                                AERC_POLICY_CORR_FEATURE_COUNT,
                                features);
    if (status != CFE_SUCCESS)
    {
        goto fail;
    }

    CFE_ES_WriteToSysLog(
        "AERC_POLICY_PROBE PASS decisions=4 negatives=3 d0_enter=0x%08lX d0_hold=0x%08lX d1_enter=0x%08lX d1_hold=0x%08lX\n",
        (unsigned long)AERC_PPROBE_D0_ENTER_SCENARIO,
        (unsigned long)AERC_PPROBE_D0_HOLD_SCENARIO,
        (unsigned long)AERC_PPROBE_D1_ENTER_SCENARIO,
        (unsigned long)AERC_PPROBE_D1_HOLD_SCENARIO);
    CFE_EVS_SendEvent(AERC_PPROBE_PASS_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_POLICY_PROBE PASS deterministic D0/D1 records verified");

    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
    return;

fail:
    CFE_EVS_SendEvent(AERC_PPROBE_ERR_EID,
                      CFE_EVS_EventType_ERROR,
                      "AERC_PPROBE validation failed RC=0x%08lX",
                      (unsigned long)status);
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
}
