project(CFE_AERC_RECOVERY_SINK C)

add_cfe_app(aerc_recovery_sink
    fsw/src/aerc_recovery_sink.c
)

target_include_directories(aerc_recovery_sink PUBLIC fsw/inc)
