# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023, Basalte bv

find_program(CPPCHECK_EXE cppcheck REQUIRED)
message(STATUS "Found CPPCHECK: ${CPPCHECK_EXE}")

# CodeChecker uses the compile_commands.json as input
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CODECHECKER_ANALYZE_OPTS "--config;${ZEPHYR_BASE}/codechecker.json;--timeout;60")

#set(CODECHECKER_ANALYZE_OPTS "--analyzer-config;cppcheck:inconclusive=false;cppcheck:addons=misra.py;--timeout;60")
set(CODECHECKER_EXPORT "html,json")

include(${ZEPHYR_BASE}/cmake/sca/codechecker/sca.cmake)

