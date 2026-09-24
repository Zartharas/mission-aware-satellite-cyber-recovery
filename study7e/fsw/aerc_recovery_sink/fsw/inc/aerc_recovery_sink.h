#ifndef AERC_RECOVERY_SINK_H
#define AERC_RECOVERY_SINK_H

#include "cfe.h"

#define AERC_RECOVERY_REQUEST_MID_VALUE 0x0EE3u
#define AERC_RECOVERY_RECORD_MID_VALUE  0x0EE4u

#define AERC_POLICY_D0_BASE        1u
#define AERC_POLICY_L0_BASE        2u
#define AERC_POLICY_D1_CORROBORATED 3u
#define AERC_POLICY_L1_CORROBORATED 4u

#define AERC_ACTION_HOLD                0u
#define AERC_ACTION_ENTER_RECOVERY_GATE 1u

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint8 PolicyId;
    uint8 Action;
    uint16 Reserved;
} AERC_RECOVERY_REQUEST_Message_t;

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint32 ReceiptSequence;
    uint8 PolicyId;
    uint8 Action;
    uint16 Reserved;
} AERC_RECOVERY_RECORD_Message_t;

void AERC_SINK_Main(void);

#endif
