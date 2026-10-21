#include "aerc_hs_probe.h"

#include "osapi.h"

#define AERC_HS_PROBE_INIT_EID 1
#define AERC_HS_PROBE_PASS_EID 2
#define AERC_HS_PROBE_ERR_EID  3

void AERC_HS_PROBE_Main(void)
{
    CFE_Status_t status;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t hk_mid =
        CFE_SB_ValueToMsgId(CFE_SB_LocalTlmTopicIdToMsgId(AERC_HS_HK_TLM_TOPIC_ID));
    CFE_SB_MsgId_t send_hk_mid =
        CFE_SB_ValueToMsgId(CFE_SB_LocalCmdTopicIdToMsgId(AERC_HS_SEND_HK_TOPIC_ID));
    AERC_HS_SEND_HK_Command_t command;
    CFE_MSG_Size_t received_size = 0;
    unsigned int attempt;

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_HS_PROBE EVS registration failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_HS_PROBE_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_HS_PROBE starting non-canonical HS observation");

    status = CFE_SB_CreatePipe(&pipe, 4, "AERC_HS_PIPE");
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(hk_mid, pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_EVS_SendEvent(AERC_HS_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_HS_PROBE pipe/subscription failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    status = CFE_MSG_Init(&command.CommandHeader.Msg, send_hk_mid, sizeof(command));
    if (status != CFE_SUCCESS)
    {
        CFE_EVS_SendEvent(AERC_HS_PROBE_ERR_EID,
                          CFE_EVS_EventType_ERROR,
                          "AERC_HS_PROBE send-HK command init failed RC=0x%08lX",
                          (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    OS_TaskDelay(1000);

    for (attempt = 1; attempt <= 3; ++attempt)
    {
        status = CFE_SB_TransmitMsg(&command.CommandHeader.Msg, true);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_HS_PROBE_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_HS_PROBE send-HK transmit failed attempt=%u RC=0x%08lX",
                              attempt,
                              (unsigned long)status);
            CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
            return;
        }

        status = CFE_SB_ReceiveBuffer(&received, pipe, 2000);
        if (status == CFE_SUCCESS && received != NULL)
        {
            const AERC_HS_HK_Prefix_t *hk = (const AERC_HS_HK_Prefix_t *)received;

            if (CFE_MSG_GetSize(&received->Msg, &received_size) == CFE_SUCCESS &&
                received_size >= sizeof(AERC_HS_HK_Prefix_t))
            {
                CFE_ES_WriteToSysLog(
                    "AERC_HS_OBSERVER PASS appmon=%u eventmon=%u aliveness=%u cpuhog=%u status=0x%02X cmd_count=%u cmd_err=%u\n",
                    (unsigned int)hk->CurrentAppMonState,
                    (unsigned int)hk->CurrentEventMonState,
                    (unsigned int)hk->CurrentAlivenessState,
                    (unsigned int)hk->CurrentCPUHogState,
                    (unsigned int)hk->StatusFlags,
                    (unsigned int)hk->CmdCount,
                    (unsigned int)hk->CmdErrCount);
                CFE_EVS_SendEvent(AERC_HS_PROBE_PASS_EID,
                                  CFE_EVS_EventType_INFORMATION,
                                  "AERC_HS_OBSERVER PASS received HS housekeeping");
                CFE_ES_ExitApp(CFE_ES_RunStatus_APP_EXIT);
                return;
            }
        }
    }

    CFE_EVS_SendEvent(AERC_HS_PROBE_ERR_EID,
                      CFE_EVS_EventType_ERROR,
                      "AERC_HS_PROBE did not receive valid HS housekeeping");
    CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
}
