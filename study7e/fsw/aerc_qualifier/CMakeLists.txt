project(CFE_AERC_QUAL C)

add_cfe_app(aerc_qual
    fsw/src/aerc_qualifier.c
    ../aerc_sigverify/fsw/src/aerc_ed25519_wrapper.c
    ../aerc_sigverify/vendor/monocypher.c
    ../aerc_sigverify/vendor/optional/monocypher-ed25519.c
)

target_include_directories(aerc_qual PUBLIC
    fsw/inc
    ../aerc_evidence_common/inc
    ../aerc_policy/fsw/inc
    ../aerc_sigverify/fsw/inc
    ../aerc_sigverify/vendor
    ../aerc_sigverify/vendor/optional
)
