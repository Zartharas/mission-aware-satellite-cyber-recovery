project(CFE_AERC_QPROBE C)

add_cfe_app(aerc_qprobe
    fsw/src/aerc_qualifier_probe.c
)

target_include_directories(aerc_qprobe PUBLIC
    fsw/inc
    ../aerc_evidence_common/inc
    ../aerc_policy/fsw/inc
    ../aerc_recovery_sink/fsw/inc
)
