# SPDX-License-Identifier: Apache-2.0
#
# Copyright (c) 2023, BUGSENG Srl

find_program(ECLAIR_ENV eclair_env REQUIRED)
message(STATUS "Found eclair_env: ${ECLAIR_ENV}")

find_program(ECLAIR_REPORT eclair_report REQUIRED)
message(STATUS "Found eclair_report: ${ECLAIR_REPORT}")

# ECLAIR Settings
set(ECLAIR_PROJECT_NAME "Zephyr-${BOARD}")
set(ECLAIR_OUTPUT_DIR ${CMAKE_BINARY_DIR}/sca/eclair_out)
set(ECLAIR_ECL_DIR "${ZEPHYR_BASE}/cmake/sca/eclair/ECL")
set(ECLAIR_DIAGNOSTICS_OUTPUT "${ECLAIR_OUTPUT_DIR}/DIAGNOSTIC.txt")
set(ECLAIR_DATA_DIR "${ECLAIR_OUTPUT_DIR}/data")
set(ECLAIR_BUILD_DIR "${ECLAIR_OUTPUT_DIR}/build")
set(ECLAIR_PROJECT_ECD "${ECLAIR_OUTPUT_DIR}/PROJECT.ecd")
set(CC_ALIASES "${CMAKE_C_COMPILER}")
set(CXX_ALIASES "${CMAKE_CXX_COMPILER}")
set(AS_ALIASES "${CMAKE_AS}")
set(LD_ALIASES "${CMAKE_LINKER}")
set(AR_ALIASES "${CMAKE_ASM_COMPILER_AR} ${CMAKE_C_COMPILER_AR} ${CMAKE_CXX_COMPILER_AR}")
if(NOT ECLAIR_RULES_SET)
  set(ECLAIR_RULES_SET first_analysis)
endif()

# Create Output Directory
file(REMOVE_RECURSE ${ECLAIR_OUTPUT_DIR})
file(MAKE_DIRECTORY ${ECLAIR_OUTPUT_DIR})
file(MAKE_DIRECTORY ${ECLAIR_DATA_DIR})
message(STATUS "ECLAIR outputs have been written to: ${ECLAIR_OUTPUT_DIR}")
message(STATUS "ECLAIR ECB files have been written to: ${ECLAIR_DATA_DIR}")
message(STATUS "ECLAIR BUILD DIR is: ${ECLAIR_BUILD_DIR}")

add_custom_target(eclair ALL
  COMMAND sh -c "ECLAIR_PROJECT_NAME=${ECLAIR_PROJECT_NAME} \
    ECLAIR_PROJECT_ROOT=${ZEPHYR_BASE} \
    ECLAIR_DIAGNOSTICS_OUTPUT=${ECLAIR_DIAGNOSTICS_OUTPUT} \
    ECLAIR_DATA_DIR=${ECLAIR_DATA_DIR} \
    ECLAIR_RULES_SET=${ECLAIR_RULES_SET} \
    CC_ALIASES=\"${CC_ALIASES}\" \
    CXX_ALIASES=\"${CXX_ALIASES}\" \
    AS_ALIASES=\"${AS_ALIASES}\" \
    LD_ALIASES=\"${LD_ALIASES}\" \
    AR_ALIASES=\"${AR_ALIASES}\" \
    ${ECLAIR_ENV} \
    -verbose \
    -eval_file=${ECLAIR_ECL_DIR}/analysis.ecl \
    -- west build -p always \
                  -b ${BOARD} \
                  --build-dir ${ECLAIR_BUILD_DIR} \
                  ${APPLICATION_SOURCE_DIR} \
                  | tee ${ECLAIR_OUTPUT_DIR}/analysis.log"
  BYPRODUCTS ${ECLAIR_OUTPUT_DIR}/analysis.log ${ECLAIR_OUTPUT_DIR}/report.log
  VERBATIM
  USES_TERMINAL
  COMMAND_EXPAND_LISTS
)

add_custom_command(
  TARGET eclair POST_BUILD
  COMMAND sh -c "ECLAIR_DATA_DIR=${ECLAIR_DATA_DIR} \
  ECLAIR_OUTPUT_DIR=${ECLAIR_OUTPUT_DIR} \
  ECLAIR_PROJECT_ECD=${ECLAIR_PROJECT_ECD} \
  ECLAIR_metrics_tab=${ECLAIR_metrics_tab} \
  ECLAIR_reports_tab=${ECLAIR_reports_tab} \
  ECLAIR_summary_txt=${ECLAIR_summary_txt} \
  ECLAIR_summary_doc=${ECLAIR_summary_doc} \
  ECLAIR_summary_odt=${ECLAIR_summary_odt} \
  ECLAIR_full_txt_areas=${ECLAIR_full_txt_areas} \
  ECLAIR_full_txt=${ECLAIR_full_txt} \
  ECLAIR_full_doc_areas=${ECLAIR_full_doc_areas} \
  ECLAIR_full_doc=${ECLAIR_full_doc} \
  ECLAIR_full_odt=${ECLAIR_full_odt} \
  ${ECLAIR_REPORT} \
  -eval_file=${ECLAIR_ECL_DIR}/reports.ecl \
  | tee ${ECLAIR_OUTPUT_DIR}/report.log"
  COMMAND ${ECLAIR_REPORT} -db=${ECLAIR_PROJECT_ECD} -overall_txt=/dev/stdin
  VERBATIM
  USES_TERMINAL
  COMMAND_EXPAND_LISTS
)

unset(ECLAIR_RULES_SET CACHE)
unset(ECLAIR_metrics_tab CACHE)
unset(ECLAIR_reports_tab CACHE)
unset(ECLAIR_summary_txt CACHE)
unset(ECLAIR_summary_doc CACHE)
unset(ECLAIR_summary_odt CACHE)
unset(ECLAIR_full_txt_areas CACHE)
unset(ECLAIR_full_txt CACHE)
unset(ECLAIR_full_doc_areas CACHE)
unset(ECLAIR_full_doc CACHE)
unset(ECLAIR_full_odt CACHE)
