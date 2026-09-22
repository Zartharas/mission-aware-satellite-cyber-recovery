#include "aerc_bus_probe.h"

#include <string.h>

#define AERC_BUS_PROBE_INIT_EID 1
#define AERC_BUS_PROBE_PASS_EID 2
#define AERC_BUS_PROBE_ERR_EID  3

void AERC_BUS_PROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t msg_id = CFE_SB_ValueToMsgId(AERC_BUS_PROBE_MID_VALUE);
    AERC_BUS_PROBE_Message_t message;
    const AERC_BUS_PROBE_Message_t *received_message;

    memset(&message, 0, sizeof(message));

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_BUS_PROBE: EVS registration failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_BUS_PROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_BUS_PROBE starting non-canonical Software Bus smoke check");

    if (!CFE_SB_IsValidMsgId(msg_id))
    {
        CFE_EVS_SendEvent(AERC_BUS_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_BUS_PROBE invalid experimental MID 0x%X",
                          (unsigned int)AERC_BUS_PROBE_MID_VALUE);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    status = CFE_SB_CreatePipe(&pipe, 4, "AERC_PROBE_PIPE");
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(msg_id, pipe);
    }

    if (status == CFE_SUCCESS)
    {
        status = CFE_MSG_Init(&message.Message, msg_id, sizeof(message));
    }

    if (status == CFE_SUCCESS)
    {
        message.ScenarioId = AERC_BUS_PROBE_SCENARIO_ID;
        message.Marker = AERC_BUS_PROBE_MARKER;
        status = CFE_SB_TransmitMsg(&message.Message, true);
    }

    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_ReceiveBuffer(&received, pipe, 1000);
    }

    if (status != CFE_SUCCESS || received == NULL)
    {
        CFE_EVS_SendEvent(AERC_BUS_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_BUS_PROBE receive failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    received_message = (const AERC_BUS_PROBE_Message_t *)received;
    if (received_message->ScenarioId != AERC_BUS_PROBE_SCENARIO_ID ||
        received_message->Marker != AERC_BUS_PROBE_MARKER)
    {
        CFE_EVS_SendEvent(AERC_BUS_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_BUS_PROBE payload mismatch scenario=0x%08lX marker=0x%08lX",
                          (unsigned long)received_message->ScenarioId,
                          (unsigned long)received_message->Marker);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_BUS_PROBE_PASS_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_BUS_PROBE PASS scenario=0x%08lX marker=0x%08lX",
                      (unsigned long)received_message->ScenarioId,
                      (unsigned long)received_message->Marker);
    CFE_ES_WriteToSysLog("AERC_BUS_PROBE PASS scenario=0x%08lX marker=0x%08lX\n",
                         (unsigned long)received_message->ScenarioId,
                         (unsigned long)received_message->Marker);

    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
}
