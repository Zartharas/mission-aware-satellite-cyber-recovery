project(CFE_AERC_SVPROBE C)

add_cfe_app(aerc_svprobe
    fsw/src/aerc_sigverify_probe.c
)

target_include_directories(aerc_svprobe PUBLIC
    fsw/inc
    ../aerc_sigverify/fsw/inc
)
