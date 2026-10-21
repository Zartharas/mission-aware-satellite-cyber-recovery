project(CFE_AERC_SIGVERIFY C)

foreach(REQUIRED_FILE
    vendor/monocypher.c
    vendor/monocypher.h
    vendor/optional/monocypher-ed25519.c
    vendor/optional/monocypher-ed25519.h
)
    if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${REQUIRED_FILE}")
        message(FATAL_ERROR "Missing pinned Monocypher source: ${REQUIRED_FILE}. Run bootstrap_monocypher.sh before cFS configure.")
    endif()
endforeach()

add_cfe_app(aerc_sigv
    fsw/src/aerc_sigverify.c
    fsw/src/aerc_ed25519_wrapper.c
    vendor/monocypher.c
    vendor/optional/monocypher-ed25519.c
)

target_include_directories(aerc_sigv PUBLIC
    fsw/inc
    vendor
    vendor/optional
)
