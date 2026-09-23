#ifndef AERC_HS_PROBE_H
#define AERC_HS_PROBE_H

#include "cfe.h"

#define AERC_HS_HK_TLM_TOPIC_ID 0xADu
#define AERC_HS_SEND_HK_TOPIC_ID 0xAFu

typedef struct
{
    CFE_MSG_CommandHeader_t CommandHeader;
} AERC_HS_SEND_HK_Command_t;

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint8 CmdCount;
    uint8 CmdErrCount;
    uint8 CurrentAppMonState;
    uint8 CurrentEventMonState;
    uint8 CurrentAlivenessState;
    uint8 CurrentCPUHogState;
    uint8 StatusFlags;
    uint8 SpareBytes;
} AERC_HS_HK_Prefix_t;

void AERC_HS_PROBE_Main(void);

#endif
