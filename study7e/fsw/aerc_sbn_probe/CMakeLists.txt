project(CFE_AERC_SBN_PROBE C)

add_cfe_app(aerc_sbn_probe
    fsw/src/aerc_sbn_probe.c
)

target_include_directories(aerc_sbn_probe PUBLIC fsw/inc)
