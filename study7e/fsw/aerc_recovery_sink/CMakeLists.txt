project(CFE_AERC_SINK C)

add_cfe_app(aerc_sink
    fsw/src/aerc_recovery_sink.c
)

target_include_directories(aerc_sink PUBLIC fsw/inc)
