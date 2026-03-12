cmake_minimum_required(VERSION 3.10)
project(AI_Monero_Miner)

# Rust integration
find_program(CARGO_EXECUTABLE cargo REQUIRED)

add_custom_target(rust_miner ALL
    COMMAND ${CARGO_EXECUTABLE} build --release
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src-rust
    COMMENT "Building Rust components..."
)

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src-rust/target/release/
    DESTINATION bin
    FILES_MATCHING PATTERN "ai_monero_miner*"
)
