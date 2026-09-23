#include "aerc_recovery_sink.h"

#include <string.h>

#define AERC_RECOVERY_SINK_INIT_EID 1
#define AERC_RECOVERY_SINK_REC_EID  2
#define AERC_RECOVERY_SINK_ERR_EID  3

static bool AERC_RECOVERY_SINK_IsPolicyIdAllowed(uint8 policy_id)
{
    return policy_id >= AERC_POLICY_D0_BASE && policy_id <= AERC_POLICY_L1_CORROBORATED;
}

static bool AERC_RECOVERY_SINK_IsActionAllowed(uint8 action)
{
    return action == AERC_ACTION_HOLD || action == AERC_ACTION_ENTER_RECOVERY_GATE;
}

static const char *AERC_RECOVERY_SINK_ActionName(uint8 action)
{
    return action == AERC_ACTION_ENTER_RECOVERY_GATE ? "ENTER_RECOVERY_GATE" : "HOLD";
}

void AERC_SINK_Main(void)
{
    CFE_Status_t status;
    uint32 run_status = CFE_ES_RunStatus_APP_RUN;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t request_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_REQUEST_MID_VALUE);
    CFE_SB_MsgId_t record_mid = CFE_SB_ValueToMsgId(AERC_RECOVERY_RECORD_MID_VALUE);
    uint32 receipt_sequence = 0;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 8, "AERC_SINK_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(request_mid, pipe);
    }

    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_RECOVERY_SINK initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_RECOVERY_SINK_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_RECOVERY_SINK initialized; records requested actions only");

    while (CFE_ES_RunLoop(&run_status) == true)
    {
        status = CFE_SB_ReceiveBuffer(&received, pipe, CFE_SB_PEND_FOREVER);
        if (status != CFE_SUCCESS || received == NULL)
        {
            CFE_EVS_SendEvent(AERC_RECOVERY_SINK_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_RECOVERY_SINK receive failed RC=0x%08lX",
                              (unsigned long)status);
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        CFE_MSG_Size_t request_size = 0;
        status = CFE_MSG_GetSize(&received->Msg, &request_size);
        if (status != CFE_SUCCESS || request_size != sizeof(AERC_RECOVERY_REQUEST_Message_t))
        {
            CFE_ES_WriteToSysLog(
                "AERC_RECOVERY_SINK REJECT_LENGTH expected=%lu actual=%lu status=0x%08lX\n",
                (unsigned long)sizeof(AERC_RECOVERY_REQUEST_Message_t),
                (unsigned long)request_size,
                (unsigned long)status);
            CFE_EVS_SendEvent(AERC_RECOVERY_SINK_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_RECOVERY_SINK rejected malformed request length");
            continue;
        }

        const AERC_RECOVERY_REQUEST_Message_t *request =
            (const AERC_RECOVERY_REQUEST_Message_t *)received;

        if (!AERC_RECOVERY_SINK_IsPolicyIdAllowed(request->PolicyId) ||
            !AERC_RECOVERY_SINK_IsActionAllowed(request->Action))
        {
            CFE_ES_WriteToSysLog(
                "AERC_RECOVERY_SINK REJECT_ACTION scenario=0x%08lX policy=%u action=%u\n",
                (unsigned long)request->ScenarioId,
                (unsigned int)request->PolicyId,
                (unsigned int)request->Action);
            CFE_EVS_SendEvent(AERC_RECOVERY_SINK_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_RECOVERY_SINK rejected request scenario=0x%08lX policy=%u action=%u",
                              (unsigned long)request->ScenarioId,
                              (unsigned int)request->PolicyId,
                              (unsigned int)request->Action);
            continue;
        }

        AERC_RECOVERY_RECORD_Message_t record;
        memset(&record, 0, sizeof(record));

        status = CFE_MSG_Init(&record.TelemetryHeader.Msg, record_mid, sizeof(record));
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_RECOVERY_SINK_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_RECOVERY_SINK record init failed RC=0x%08lX",
                              (unsigned long)status);
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        ++receipt_sequence;
        record.ScenarioId = request->ScenarioId;
        record.ReceiptSequence = receipt_sequence;
        record.PolicyId = request->PolicyId;
        record.Action = request->Action;

        status = CFE_SB_TransmitMsg(&record.TelemetryHeader.Msg, true);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_RECOVERY_SINK_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_RECOVERY_SINK record transmit failed RC=0x%08lX",
                              (unsigned long)status);
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        CFE_ES_WriteToSysLog(
            "AERC_RECOVERY_SINK RECORD scenario=0x%08lX policy=%u action=%s sequence=%lu\n",
            (unsigned long)record.ScenarioId,
            (unsigned int)record.PolicyId,
            AERC_RECOVERY_SINK_ActionName(record.Action),
            (unsigned long)record.ReceiptSequence);

        CFE_EVS_SendEvent(AERC_RECOVERY_SINK_REC_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_RECOVERY_SINK recorded scenario=0x%08lX policy=%u action=%s sequence=%lu",
                          (unsigned long)record.ScenarioId,
                          (unsigned int)record.PolicyId,
                          AERC_RECOVERY_SINK_ActionName(record.Action),
                          (unsigned long)record.ReceiptSequence);
    }

    CFE_ES_ExitApp(run_status);
}
