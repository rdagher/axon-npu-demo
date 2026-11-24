# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(axon_npu_bench)

# AXON_MODEL / AXON_MODEL_DIR: as in ../app. TFLITE: the .tflite the model was compiled from.
zephyr_get(AXON_MODEL)
zephyr_get(AXON_MODEL_DIR)
zephyr_get(TFLITE)
foreach(header ${AXON_MODEL}_.h ${AXON_MODEL}_test_vectors_.h)
  if(NOT EXISTS ${AXON_MODEL_DIR}/nrf_axon_model_${header})
    message(FATAL_ERROR "${AXON_MODEL_DIR}/nrf_axon_model_${header} not found: run `just compile`")
  endif()
endforeach()

target_sources(app PRIVATE src/main.c)
target_include_directories(app PRIVATE ${AXON_MODEL_DIR})
target_compile_definitions(app PRIVATE MODEL_NAME=${AXON_MODEL})

if(CONFIG_BENCH_TFLM)
  if(NOT EXISTS ${TFLITE})
    message(FATAL_ERROR "TFLITE=${TFLITE} not found")
  endif()
  target_sources(app PRIVATE src/tflm.cc)
  set(gen ${ZEPHYR_BINARY_DIR}/include/generated)
  generate_inc_file_for_target(app ${TFLITE} ${gen}/model.tflite.inc)
  target_include_directories(app PRIVATE ${gen})
else()
  target_sources(app PRIVATE src/axon.c)
endif()
