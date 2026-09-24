#include "aerc_eprod.h"

#include <string.h>

#define AERC_EPROD_INIT_EID 1
#define AERC_EPROD_FWD_EID  2
#define AERC_EPROD_ERR_EID  3

void AERC_EPROD_Main(void)
{
    CFE_Status_t status;
    uint32 run_status = CFE_ES_RunStatus_APP_RUN;
    CFE_SB_PipeId_t pipe = CFE_SB_INVALID_PIPE;
    CFE_SB_Buffer_t *received = NULL;
    CFE_SB_MsgId_t ingress_mid = CFE_SB_ValueToMsgId(AERC_EVIDENCE_INGRESS_MID_VALUE);
    CFE_SB_MsgId_t qualifier_mid = CFE_SB_ValueToMsgId(AERC_EVIDENCE_QUALIFIER_MID_VALUE);

    status = CFE_EVS_Register(NULL, 0, CFE_EVS_EventFilter_BINARY);
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_CreatePipe(&pipe, 8, "AERC_EPROD_PIPE");
    }
    if (status == CFE_SUCCESS)
    {
        status = CFE_SB_Subscribe(ingress_mid, pipe);
    }
    if (status != CFE_SUCCESS)
    {
        CFE_ES_WriteToSysLog("AERC_EPROD initialization failed RC=0x%08lX\n",
                             (unsigned long)status);
        CFE_ES_ExitApp(CFE_ES_RunStatus_APP_ERROR);
        return;
    }

    CFE_EVS_SendEvent(AERC_EPROD_INIT_EID,
                      CFE_EVS_EventType_INFORMATION,
                      "AERC_EPROD initialized private-key-free signed-evidence bridge");

    while (CFE_ES_RunLoop(&run_status) == true)
    {
        CFE_MSG_Size_t size = 0;
        const AERC_EVIDENCE_Message_t *input;
        AERC_EVIDENCE_Message_t output;

        status = CFE_SB_ReceiveBuffer(&received, pipe, CFE_SB_PEND_FOREVER);
        if (status != CFE_SUCCESS || received == NULL)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        status = CFE_MSG_GetSize(&received->Msg, &size);
        if (status != CFE_SUCCESS || size != sizeof(AERC_EVIDENCE_Message_t))
        {
            CFE_ES_WriteToSysLog(
                "AERC_EPROD REJECT_LENGTH expected=%lu actual=%lu status=0x%08lX\n",
                (unsigned long)sizeof(AERC_EVIDENCE_Message_t),
                (unsigned long)size,
                (unsigned long)status);
            continue;
        }

        input = (const AERC_EVIDENCE_Message_t *)received;
        memset(&output, 0, sizeof(output));

        status = CFE_MSG_Init(&output.TelemetryHeader.Msg, qualifier_mid, sizeof(output));
        if (status != CFE_SUCCESS)
        {
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        output.RequestSequence = input->RequestSequence;
        memcpy(output.Body, input->Body, sizeof(output.Body));
        memcpy(output.Signature, input->Signature, sizeof(output.Signature));

        status = CFE_SB_TransmitMsg(&output.TelemetryHeader.Msg, true);
        if (status != CFE_SUCCESS)
        {
            CFE_EVS_SendEvent(AERC_EPROD_ERR_EID,
                              CFE_EVS_EventType_ERROR,
                              "AERC_EPROD forward failed RC=0x%08lX",
                              (unsigned long)status);
            run_status = CFE_ES_RunStatus_APP_ERROR;
            continue;
        }

        CFE_ES_WriteToSysLog("AERC_EPROD FORWARD request=%lu body_bytes=64 signature_bytes=64\n",
                             (unsigned long)output.RequestSequence);
        CFE_EVS_SendEvent(AERC_EPROD_FWD_EID,
                          CFE_EVS_EventType_INFORMATION,
                          "AERC_EPROD forwarded signed evidence request=%lu",
                          (unsigned long)output.RequestSequence);
    }

    CFE_ES_ExitApp(run_status);
}
