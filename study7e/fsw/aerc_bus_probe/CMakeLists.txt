project(CFE_AERC_BUS_PROBE C)

add_cfe_app(aerc_bus_probe
    fsw/src/aerc_bus_probe.c
)

target_include_directories(aerc_bus_probe PUBLIC fsw/inc)
