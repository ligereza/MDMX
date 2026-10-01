cmake_minimum_required(VERSION 3.13)

# Pico SDK component scaffold.
# Include this subtree after pico_sdk_init() in the top-level firmware app.

add_library(mdmx_core STATIC
    src/mdmx_protocol.c
    src/mdmx_state.c
)

target_include_directories(mdmx_core PUBLIC
    ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(mdmx_core PUBLIC
    pico_stdlib
    hardware_sync
)

target_compile_features(mdmx_core PUBLIC c_std_11)
