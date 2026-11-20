# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(axon_npu_demo)

# Model name, and the directory holding nrf_axon_model_<name>_.h and
# nrf_axon_model_<name>_test_vectors_.h. Default: the add-on's own test models.
# zephyr_get() also finds -DAXON_MODEL=... when it was given to sysbuild.
zephyr_get(AXON_MODEL)
zephyr_get(AXON_MODEL_DIR)
if(NOT AXON_MODEL)
  set(AXON_MODEL tinyml_kws)
endif()
if(NOT AXON_MODEL_DIR)
  set(AXON_MODEL_DIR ${ZEPHYR_EDGE_AI_MODULE_DIR}/tests/axon/compiled_models)
endif()
message(STATUS "Axon model: ${AXON_MODEL} from ${AXON_MODEL_DIR}")

foreach(header ${AXON_MODEL}_.h ${AXON_MODEL}_test_vectors_.h)
  if(NOT EXISTS ${AXON_MODEL_DIR}/nrf_axon_model_${header})
    message(FATAL_ERROR "${AXON_MODEL_DIR}/nrf_axon_model_${header} not found")
  endif()
endforeach()

target_sources(app PRIVATE src/main.c)
target_include_directories(app PRIVATE ${AXON_MODEL_DIR})
target_compile_definitions(app PRIVATE MODEL_NAME=${AXON_MODEL})
