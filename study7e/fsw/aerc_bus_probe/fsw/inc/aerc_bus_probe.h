#ifndef AERC_BUS_PROBE_H
#define AERC_BUS_PROBE_H

#include "cfe.h"

#define AERC_BUS_PROBE_MID_VALUE 0x0EE0u
#define AERC_BUS_PROBE_SCENARIO_ID 0x53374531u
#define AERC_BUS_PROBE_MARKER 0xA37C0DE1u

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint32 Marker;
} AERC_BUS_PROBE_Message_t;

void AERC_BUS_PROBE_Main(void);

#endif
