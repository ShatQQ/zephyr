# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023, Baumer (www.baumer.com)

find_program(CPPCHECK_TOOL cppcheck REQUIRED)
message(STATUS "Found cppcheck: ${CPPCHECK_TOOL}")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(output_dir ${CMAKE_BINARY_DIR}/sca/cppcheck)
file(MAKE_DIRECTORY ${output_dir})

set_property(GLOBAL APPEND PROPERTY extra_post_build_commands COMMAND
  ${CMAKE_COMMAND} -E touch ${output_dir}/cppcheck.ready)
set_property(GLOBAL APPEND PROPERTY extra_post_build_byproducts
  ${output_dir}/cppcheck.ready)

add_custom_target(cppchecker ALL
  COMMAND ${CPPCHECK_TOOL}
  ${ZEPHYR_BASE}/kernel/thread.c
  --enable=performance,information
  --suppress=missingInclude
  --template=gcc
  --inconclusive
  --force
  --addon=${ZEPHYR_BASE}/guidelines.json
  --output-file=${output_dir}/cppcheck_report.txt
  -I${ZEPHYR_BASE}/
  CACHE INTERNAL ""
  DEPENDS
  BYPRODUCTS
  VERBATIM
  USES_TERMINAL
  COMMAND_EXPAND_LISTS
)

