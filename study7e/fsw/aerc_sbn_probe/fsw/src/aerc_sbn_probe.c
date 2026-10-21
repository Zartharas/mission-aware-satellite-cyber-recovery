#include "aerc_sbn_probe.h"

#include "osapi.h"

#define AERC_SBN_PROBE_INIT_EID 1
#define AERC_SBN_PROBE_PASS_EID 2
#define AERC_SBN_PROBE_ERR_EID  3
#define AERC_SBN_PROBE_INFO_EID 4

static CFE_Status_t AERC_SBN_PROBE_Send(CFE_SB_MsgId_t msg_id, uint16 origin_processor, uint16 receipt_code)
{
    AERC_SBN_PROBE_Message_t message;
    CFE_Status_t status;

    status = CFE_MSG_Init(&message.TelemetryHeader.Msg, msg_id, sizeof(message));
    if (status != CFE_SUCCESS)
    {
        return status;
    }

    message.ScenarioId = AERC_SBN_PROBE_SCENARIO_ID;
    message.Marker = AERC_SBN_PROBE_MARKER;
    message.OriginProcessor = origin_processor;
    message.ReceiptCode = receipt_code;

    return CFE_SB_TransmitMsg(&message.TelemetryHeader.Msg, true);
}

static bool AERC_SBN_PROBE_Validate(const CFE_SB_Buffer_t *received,
                                    uint16 expected_origin,
                                    uint16 expected_receipt)
{
    const AERC_SBN_PROBE_Message_t *message = (const AERC_SBN_PROBE_Message_t *)received;

    return message->ScenarioId == AERC_SBN_PROBE_SCENARIO_ID &&
           message->Marker == AERC_SBN_PROBE_MARKER &&
           message->OriginProcessor == expected_origin &&
           message->ReceiptCode == expected_receipt;
}

void AERC_SBN_PROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t data_mid = CFE_SB_ValueToMsgId(AERC_SBN_PROBE_DATA_MID_VALUE);
    CFE_SB_MsgId_t ack_mid = CFE_SB_ValueToMsgId(AERC_SBN_PROBE_ACK_MID_VALUE);
    uint16 processor_id = (uint16)CFE_PSP_GetProcessorId();
    unsigned int attempt;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_SBN_PROBE EVS registration failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_SBN_PROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_SBN_PROBE starting on processor %u",
                      (unsigned int)processor_id);

    if (processor_id != 1u && processor_id != 2u)
    {
        CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_SBN_PROBE unsupported processor %u",
                          (unsigned int)processor_id);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    status = CFE_SB_CreatePipe(&pipe, 8, "AERC_SBN_PIPE");
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(processor_id == 1u ? ack_mid : data_mid, pipe);
    }

    if (status != CFE_SUCCESS)
    {
        CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_SBN_PROBE pipe/subscription failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    if (processor_id == 2u)
    {
        status = CFE_SB_ReceiveBuffer(&received, pipe, 15000);
        if (status != CFE_SUCCESS || received == NULL ||
            !AERC_SBN_PROBE_Validate(received, 1u, 0u))
        {
            CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_SBN_PROBE CPU2 receive/validate failed RC=0x%08lX",
                              (unsigned long)status);
            CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
            return;
        }

        CFE_EVS_SendEvent(AERC_SBN_PROBE_PASS_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_SBN_CPU2_RX PASS scenario=0x%08lX marker=0x%08lX origin=1",
                          (unsigned long)AERC_SBN_PROBE_SCENARIO_ID,
                          (unsigned long)AERC_SBN_PROBE_MARKER);

        status = AERC_SBN_PROBE_Send(ack_mid, 2u, AERC_SBN_PROBE_RECEIPT);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_SBN_PROBE CPU2 sink receipt transmit failed RC=0x%08lX",
                              (unsigned long)status);
            CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
            return;
        }

        CFE_ES_WriteToSysLog(
            "AERC_SBN_SINK PASS scenario=0x%08lX marker=0x%08lX sink_cpu=2 receipt=0x%04X\n",
            (unsigned long)AERC_SBN_PROBE_SCENARIO_ID,
            (unsigned long)AERC_SBN_PROBE_MARKER,
            (unsigned int)AERC_SBN_PROBE_RECEIPT);

        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
        return;
    }

    /* Allow SBN peer connection and remote-subscription exchange to converge. */
    OS_TaskDelay(5000);

    for (attempt = 1; attempt <= 3; ++attempt)
    {
        status = AERC_SBN_PROBE_Send(data_mid, 1u, 0u);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_SBN_PROBE CPU1 transmit failed attempt=%u RC=0x%08lX",
                              attempt,
                              (unsigned long)status);
            CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
            return;
        }

        CFE_EVS_SendEvent(AERC_SBN_PROBE_INFO_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_SBN_PROBE CPU1 sent fixed scenario attempt=%u",
                          attempt);

        status = CFE_SB_ReceiveBuffer(&received, pipe, 3000);
        if (status == CFE_SUCCESS && received != NULL &&
            AERC_SBN_PROBE_Validate(received, 2u, AERC_SBN_PROBE_RECEIPT))
        {
            CFE_ES_WriteToSysLog(
                "AERC_SBN_ROUNDTRIP PASS scenario=0x%08lX marker=0x%08lX sink_cpu=2 receipt=0x%04X attempt=%u\n",
                (unsigned long)AERC_SBN_PROBE_SCENARIO_ID,
                (unsigned long)AERC_SBN_PROBE_MARKER,
                (unsigned int)AERC_SBN_PROBE_RECEIPT,
                attempt);
            CFE_EVS_SendEvent(AERC_SBN_PROBE_PASS_EID,
                              CFE_EVS_EventType_INFORMATION,
                              "AERC_SBN_ROUNDTRIP PASS scenario=0x%08lX marker=0x%08lX",
                              (unsigned long)AERC_SBN_PROBE_SCENARIO_ID,
                              (unsigned long)AERC_SBN_PROBE_MARKER);
            CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
            return;
        }
    }

    CFE_EVS_SendEvent(AERC_SBN_PROBE_ERR_EID,
                      CFE_EVS_EventType_ERROR,
                      "AERC_SBN_PROBE CPU1 did not receive valid sink receipt");
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
}
