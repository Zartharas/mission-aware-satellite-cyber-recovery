project(CFE_AERC_HS_PROBE C)

add_cfe_app(aerc_hs_probe
    fsw/src/aerc_hs_probe.c
)

target_include_directories(aerc_hs_probe PUBLIC fsw/inc)
