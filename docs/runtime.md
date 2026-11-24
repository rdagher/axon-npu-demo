# Runtime flow

See `app/src/main.c`:

1. `nrf_axon_platform_init()`: IRQ, power and locking for the NPU.
2. `nrf_axon_nn_model_init_vars()` resets the model's persistent variables (these models have none).
   `nrf_axon_nn_model_validate()` checks that the interlayer buffer is large enough and the driver recent enough.
   The app also refuses a model with several inputs or outputs.
3. `nrf_axon_nn_model_infer_sync(&model, in, out)` powers the NPU on, takes its lock and copies `in` into the interlayer buffer.
   It hands the command stream to the NPU and sleeps until the completion interrupt.
   Then it copies the result to `out` and powers the NPU off.
4. `nrf_axon_nn_get_classification()`: index and label of the highest output.

Not every layer runs on the NPU: the command streams of the three classifiers end with a softmax computed on the CPU, in `drivers/axon/nrf_axon_nn_op_extensions.c`.

An application needs three things to use the NPU: `CONFIG_NRF_AXON=y` and `CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE` in `prj.conf`, and the `axon` node enabled in a devicetree overlay (`app/boards/`), since it is disabled by default.

## Add-on files

| Path under `edge-ai/` | Content |
|---|---|
| `include/drivers/axon/`, `include/axon/` | public headers |
| `drivers/axon/nrf_axon_nn_infer.c` | inference entry points (source provided) |
| `lib/axon/platform/src/zephyr/nrf_axon_platform_zephyr.c` | OS glue: IRQ, semaphores, power, interlayer buffer |
| `lib/axon/bin/arm/libnrf-axon-driver-internal.a` | NPU driver core (prebuilt) |
| `tools/axon/compiler/` | compiler (Docker) |
| `tests/axon/compiled_models/` | the compiled models and test vectors used here |
| `tests/axon/inference/` | Nordic's own test app for these models |
| `samples/axon/hello_axon/` | Nordic's own minimal sample |

References:
- [Edge AI Add-on](https://nrfconnectdocs.nordicsemi.com/addons/addon-edge-ai/3.0.0/),
- [Axon compiler](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/doc/axon_compiler/Axon_npu_tflite_compiler.rst),
- [MLPerf Tiny models on Axon](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/doc/axon_compiler/mlperf_tiny_models.rst),
- [supported operators](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/doc/axon_compiler/supported_operators.rst).
