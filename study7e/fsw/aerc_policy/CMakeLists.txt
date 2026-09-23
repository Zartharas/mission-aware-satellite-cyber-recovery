project(CFE_AERC_POLICY C)

add_cfe_app(aerc_policy
    fsw/src/aerc_policy.c
)

target_include_directories(aerc_policy PUBLIC
    fsw/inc
    ../aerc_recovery_sink/fsw/inc
)
