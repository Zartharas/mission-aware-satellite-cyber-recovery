#include "aerc_policy.h"
#include "aerc_recovery_sink.h"

#include <string.h>

#define AERC_POLICY_INIT_EID 1
#define AERC_POLICY_DEC_EID  2
#define AERC_POLICY_ERR_EID  3

typedef enum
{
    AERC_POLICY_VALID = 0,
    AERC_POLICY_BAD_COUNT,
    AERC_POLICY_BAD_RESERVED,
    AERC_POLICY_BAD_UNUSED,
    AERC_POLICY_BAD_FEATURE
} AERC_POLICY_Validation_t;

static const char *AERC_POLICY_PolicyName(uint8 policy_id)
{
    return policy_id == AERC_POLICY_D0_BASE ? "D0_BASE" : "D1_CORROBORATED";
}

static const char *AERC_POLICY_ActionName(uint8 action)
{
    return action == AERC_ACTION_ENTER_RECOVERY_GATE ? "ENTER_RECOVERY_GATE" : "HOLD";
}

static AERC_POLICY_Validation_t AERC_POLICY_ValidateSnapshot(
    const AERC_POLICY_SNAPSHOT_Message_t *snapshot,
    uint8 expected_count,
    bool base_contract,
    uint8 *bad_index)
{
    uint8 i;

    if (snapshot->FeatureCount != expected_count)
    {
        return AERC_POLICY_BAD_COUNT;
    }

    if (snapshot->Reserved[0] != 0u || snapshot->Reserved[1] != 0u || snapshot->Reserved[2] != 0u)
    {
        return AERC_POLICY_BAD_RESERVED;
    }

    for (i = 0u; i < expected_count; ++i)
    {
        if (snapshot->Features[i] > 1u)
        {
            *bad_index = i;
            return AERC_POLICY_BAD_FEATURE;
        }
    }

    if (base_contract)
    {
        for (i = AERC_POLICY_BASE_FEATURE_COUNT; i < AERC_POLICY_FEATURE_SLOTS; ++i)
        {
            if (snapshot->Features[i] != 0u)
            {
                *bad_index = i;
                return AERC_POLICY_BAD_UNUSED;
            }
        }
    }

    return AERC_POLICY_VALID;
}

static uint8 AERC_POLICY_Decide(const AERC_POLICY_SNAPSHOT_Message_t *snapshot, uint8 feature_count)
{
    uint8 i;

    for (i = 0u; i < feature_count; ++i)
    {
        if (snapshot->Features[i] != 1u)
        {
            return AERC_ACTION_HOLD;
        }
    }

    return AERC_ACTION_ENTER_RECOVERY_GATE;
}

static CFE_Status_t AERC_POLICY_Emit(
    const AERC_POLICY_SNAPSHOT_Message_t *snapshot,
    CFE_SB_MsgId_t decision_mid,
    CFE_SB_MsgId_t request_mid,
    uint8 policy_id,
    uint8 action,
    uint32 decision_sequence)
{
    AERC_POLICY_DECISION_Message_t decision;
    AERC_RECOVERY_REQUEST_Message_t request;
    CFE_Status_t status;

    memset(&decision, 0, sizeof(decision));
    status = CFE_MSG_Init(&decision.TelemetryHeader.Msg, decision_mid, sizeof(decision));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    decision.ScenarioId = snapshot->ScenarioId;
    decision.DecisionSequence = decision_sequence;
    decision.PolicyId = policy_id;
    decision.Action = action;
    decision.FeatureCount = snapshot->FeatureCount;
    memcpy(decision.Features, snapshot->Features, sizeof(decision.Features));

    status = CFE_SB_TransmitMsg(&decision.TelemetryHeader.Msg, true);
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    memset(&request, 0, sizeof(request));
    status = CFE_MSG_Init(&request.TelemetryHeader.Msg, request_mid, sizeof(request));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    request.ScenarioId = snapshot->ScenarioId;
    request.PolicyId = policy_id;
    request.Action = action;

    return CFE_SB_TransmitMsg(&request.TelemetryHeader.Msg, true);
}

void AERC_POLICY_Main(void)
{
    CFE_Status_t status;
    uint32 run_status = CFE_ES_RunStatus_APP_RUN;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t base_mid = CFE_SB_ValueToMsgId(AERC_POLICY_BASE_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t corr_mid = CFE_SB_ValueToMsgId(AERC_POLICY_CORR_SNAPSHOT_MID_VALUE);
    CFE_SB_MsgId_t decision_mid = CFE_SB_ValueToMsgId(AERC_POLICY_DECISION_MID_VALUE);
    CFE_SB_MsgId_t request_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_REQUEST_MID_VALUE);
    uint32 decision_sequence = 0u;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 8, "AERC_POL_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(base_mid, pipe);
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(corr_mid, pipe);
    }

    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_POLICY initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_POLICY_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_POLICY initialized deterministic D0/D1 snapshot path");

    while (CFE_ES_RunLoop(&run_status) == true)
    {
        CFE_MSG_Size_t size = 0;
        CFE_SB_MsgId_t msg_id = CFE_SB_INVALID_MSG_ID;
        const AERC_POLICY_SNAPSHOT_Message_t *snapshot;
        uint8 expected_count;
        uint8 policy_id;
        uint8 bad_index = 0u;
        bool base_contract;
        AERC_POLICY_Validation_t validation;
        uint8 action;

        status = CFE_SB_ReceiveBuffer(&received, pipe, CFE_SB_PEND_FOREVER);
        if (status != CFE_SUCCESS || received == NULL)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        status = CFE_MSG_GetSize(&received->Msg, &size);
        if (status != CFE_SUCCESS || size != sizeof(AERC_POLICY_SNAPSHOT_Message_t))
        {
            CFE_ES_WriteToSysLog(
                "AERC_POLICY REJECT_LENGTH expected=%lu actual=%lu status=0x%08lX\n",
                (unsigned long)sizeof(AERC_POLICY_SNAPSHOT_Message_t),
                (unsigned long)size,
                (unsigned long)status);
            continue;
        }

        status = CFE_MSG_GetMsgId(&received->Msg, &msg_id);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_POLICY_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_POLICY message-id read failed RC=0x%08lX",
                              (unsigned long)status);
            continue;
        }

        snapshot = (const AERC_POLICY_SNAPSHOT_Message_t *)received;
        if (CFE_SB_MsgId_Equal(msg_id, base_mid))
        {
            expected_count = AERC_POLICY_BASE_FEATURE_COUNT;
            policy_id = AERC_POLICY_D0_BASE;
            base_contract = true;
        }
        else if (CFE_SB_MsgId_Equal(msg_id, corr_mid))
        {
            expected_count = AERC_POLICY_CORR_FEATURE_COUNT;
            policy_id = AERC_POLICY_D1_CORROBORATED;
            base_contract = false;
        }
        else
        {
            CFE_EVS_SendEvent(AERC_POLICY_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_POLICY received unexpected MID");
            continue;
        }

        validation = AERC_POLICY_ValidateSnapshot(snapshot, expected_count, base_contract, &bad_index);
        if (validation == AERC_POLICY_BAD_FEATURE)
        {
            CFE_ES_WriteToSysLog(
                "AERC_POLICY REJECT_FEATURE scenario=0x%08lX index=%u value=%u\n",
                (unsigned long)snapshot->ScenarioId,
                (unsigned int)bad_index,
                (unsigned int)snapshot->Features[bad_index]);
            continue;
        }
        if (validation != AERC_POLICY_VALID)
        {
            CFE_ES_WriteToSysLog(
                "AERC_POLICY REJECT_CONTRACT scenario=0x%08lX policy=%s reason=%u expected_count=%u actual_count=%u index=%u\n",
                (unsigned long)snapshot->ScenarioId,
                AERC_POLICY_PolicyName(policy_id),
                (unsigned int)validation,
                (unsigned int)expected_count,
                (unsigned int)snapshot->FeatureCount,
                (unsigned int)bad_index);
            continue;
        }

        action = AERC_POLICY_Decide(snapshot, expected_count);
        ++decision_sequence;

        status = AERC_POLICY_Emit(snapshot,
                                  decision_mid,
                                  request_mid,
                                  policy_id,
                                  action,
                                  decision_sequence);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_POLICY_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_POLICY output failed RC=0x%08lX",
                              (unsigned long)status);
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        CFE_ES_WriteToSysLog(
            "AERC_POLICY DECISION scenario=0x%08lX policy=%s action=%s sequence=%lu feature_count=%u\n",
            (unsigned long)snapshot->ScenarioId,
            AERC_POLICY_PolicyName(policy_id),
            AERC_POLICY_ActionName(action),
            (unsigned long)decision_sequence,
            (unsigned int)expected_count);

        CFE_EVS_SendEvent(AERC_POLICY_DEC_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_POLICY emitted %s action=%s sequence=%lu",
                          AERC_POLICY_PolicyName(policy_id),
                          AERC_POLICY_ActionName(action),
                          (unsigned long)decision_sequence);
    }

    CFE_ES_ExitApp(run_status);
}
