project(CFE_AERC_EPROD C)

add_cfe_app(aerc_eprod
    fsw/src/aerc_eprod.c
)

target_include_directories(aerc_eprod PUBLIC
    fsw/inc
    ../aerc_evidence_common/inc
)
