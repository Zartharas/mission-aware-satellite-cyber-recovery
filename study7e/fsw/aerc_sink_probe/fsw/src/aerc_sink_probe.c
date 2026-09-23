#include "aerc_sink_probe.h"

#include "osapi.h"
#include <string.h>

#define AERC_SINK_PROBE_INIT_EID 1
#define AERC_SINK_PROBE_PASS_EID 2
#define AERC_SINK_PROBE_ERR_EID  3

static CFE_Status_t AERC_SINK_PROBE_Send(CFE_SB_MsgId_t request_mid,
                                         uint32 scenario_id,
                                         uint8 policy_id,
                                         uint8 action)
{
    AERC_RECOVERY_REQUEST_Message_t request;
    CFE_Status_t status;

    memset(&request, 0, sizeof(request));
    status = CFE_MSG_Init(&request.TelemetryHeader.Msg, request_mid, sizeof(request));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    request.ScenarioId = scenario_id;
    request.PolicyId = policy_id;
    request.Action = action;

    return CFE_SB_TransmitMsg(&request.TelemetryHeader.Msg, true);
}

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
} AERC_SINK_PROBE_ShortRequest_t;

static CFE_Status_t AERC_SINK_PROBE_SendShort(CFE_SB_MsgId_t request_mid)
{
    AERC_SINK_PROBE_ShortRequest_t request;
    CFE_Status_t status;

    memset(&request, 0, sizeof(request));
    status = CFE_MSG_Init(&request.TelemetryHeader.Msg, request_mid, sizeof(request));
    if (status == CFE_SUCCESS)
    {
        request.ScenarioId = AERC_SINK_PROBE_BAD_SCENARIO_ID;
        status = CFE_SB_TransmitMsg(&request.TelemetryHeader.Msg, true);
    }
    return status;
}

static bool AERC_SINK_PROBE_RecordMatches(const AERC_RECOVERY_RECORD_Message_t *record,
                                          uint32 scenario_id,
                                          uint8 policy_id,
                                          uint8 action,
                                          uint32 sequence)
{
    return record->ScenarioId == scenario_id &&
           record->PolicyId == policy_id &&
           record->Action == action &&
           record->ReceiptSequence == sequence;
}

void AERC_SPROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t request_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_REQUEST_MID_VALUE);
    CFE_SB_MsgId_t record_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_RECORD_MID_VALUE);

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 4, "AERC_SP_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(record_mid, pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_SINK_PROBE initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_SINK_PROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SINK_PROBE starting non-canonical sink smoke");

    OS_TaskDelay(1000);

    status = AERC_SINK_PROBE_Send(request_mid,
                                  AERC_SINK_PROBE_HOLD_SCENARIO_ID,
                                  AERC_POLICY_D0_BASE,
                                  AERC_ACTION_HOLD);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_ReceiveBuffer(&received, pipe, 2000);
    }
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_SINK_PROBE_RecordMatches((const AERC_RECOVERY_RECORD_Message_t *)received,
                                      AERC_SINK_PROBE_HOLD_SCENARIO_ID,
                                      AERC_POLICY_D0_BASE,
                                      AERC_ACTION_HOLD,
                                      1u))
    {
        CFE_EVS_SendEvent(AERC_SINK_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_SINK_PROBE HOLD record validation failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    status = AERC_SINK_PROBE_SendShort(request_mid);
    if (status == CFE_SUCCESS)
    {
        status = AERC_SINK_PROBE_Send(request_mid,
                                      AERC_SINK_PROBE_BAD_SCENARIO_ID,
                                      AERC_POLICY_L0_BASE,
                                      0xFFu);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_EVS_SendEvent(AERC_SINK_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_SINK_PROBE negative request transmit failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    received = NULL;
    status = AERC_SINK_PROBE_Send(request_mid,
                                  AERC_SINK_PROBE_ENTER_SCENARIO_ID,
                                  AERC_POLICY_D1_CORROBORATED,
                                  AERC_ACTION_ENTER_RECOVERY_GATE);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_ReceiveBuffer(&received, pipe, 2000);
    }
    if (status != CFE_SUCCESS || received == NULL ||
        !AERC_SINK_PROBE_RecordMatches((const AERC_RECOVERY_RECORD_Message_t *)received,
                                      AERC_SINK_PROBE_ENTER_SCENARIO_ID,
                                      AERC_POLICY_D1_CORROBORATED,
                                      AERC_ACTION_ENTER_RECOVERY_GATE,
                                      2u))
    {
        CFE_EVS_SendEvent(AERC_SINK_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_SINK_PROBE ENTER record validation failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_ES_WriteToSysLog(
        "AERC_SINK_PROBE PASS hold_scenario=0x%08lX enter_scenario=0x%08lX records=2\n",
        (unsigned long)AERC_SINK_PROBE_HOLD_SCENARIO_ID,
        (unsigned long)AERC_SINK_PROBE_ENTER_SCENARIO_ID);
    CFE_EVS_SendEvent(AERC_SINK_PROBE_PASS_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SINK_PROBE PASS valid records verified; malformed/invalid requests rejected");

    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
}
