project(CFE_AERC_SINK_PROBE C)

add_cfe_app(aerc_sink_probe
    fsw/src/aerc_sink_probe.c
)

target_include_directories(aerc_sink_probe PUBLIC
    fsw/inc
    ../aerc_recovery_sink/fsw/inc
)
