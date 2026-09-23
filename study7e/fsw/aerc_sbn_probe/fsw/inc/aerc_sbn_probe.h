#ifndef AERC_SBN_PROBE_H
#define AERC_SBN_PROBE_H

#include "cfe.h"

#define AERC_SBN_PROBE_DATA_MID_VALUE 0x0EE1u
#define AERC_SBN_PROBE_ACK_MID_VALUE  0x0EE2u

#define AERC_SBN_PROBE_SCENARIO_ID 0x53374532u
#define AERC_SBN_PROBE_MARKER      0xA37C0DE2u
#define AERC_SBN_PROBE_RECEIPT     0xBEEFu

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint32 Marker;
    uint16 OriginProcessor;
    uint16 ReceiptCode;
} AERC_SBN_PROBE_Message_t;

void AERC_SBN_PROBE_Main(void);

#endif
