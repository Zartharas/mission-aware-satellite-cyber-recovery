project(CFE_AERC_PPROBE C)

add_cfe_app(aerc_pprobe
    fsw/src/aerc_policy_probe.c
)

target_include_directories(aerc_pprobe PUBLIC
    fsw/inc
    ../aerc_policy/fsw/inc
    ../aerc_recovery_sink/fsw/inc
)
