#ifndef AERC_EVIDENCE_COMMON_H
#define AERC_EVIDENCE_COMMON_H

#include "cfe.h"

#define AERC_EVIDENCE_INGRESS_MID_VALUE   0x0EEAu
#define AERC_EVIDENCE_QUALIFIER_MID_VALUE 0x0EEBu
#define AERC_QUALIFIER_CONTEXT_MID_VALUE  0x0EECu

#define AERC_EVIDENCE_BODY_BYTES      64u
#define AERC_EVIDENCE_SIGNATURE_BYTES 64u

#define AERC_EVIDENCE_ROLE_PRIMARY      1u
#define AERC_EVIDENCE_ROLE_CORROBORATOR 2u

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 RequestSequence;
    uint8 Body[AERC_EVIDENCE_BODY_BYTES];
    uint8 Signature[AERC_EVIDENCE_SIGNATURE_BYTES];
} AERC_EVIDENCE_Message_t;

typedef struct
{
    CFE_MSG_TelemetryHeader_t TelemetryHeader;
    uint32 ScenarioId;
    uint64 ExpectedEpoch;
    uint64 NowTick;
    uint32 FreshnessMaxAgeTicks;
    uint8 ObservedHealthReady;
    uint8 SecuritySignal;
    uint8 Reserved[2];
} AERC_QUALIFIER_CONTEXT_Message_t;

#endif
