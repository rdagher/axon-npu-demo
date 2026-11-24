# Models

The four models of the add-on, their sizes in this app, and what a compiled model header contains.

## Build sizes

```sh
just build tinyml_ad     # anomaly detection, no class line
just build tinyml_ic     # image classification
just build tinyml_vww    # visual wake words
```

Build sizes on add-on v3.0.0. RAM includes the 52,224 B interlayer buffer, flash the three test vectors:

| Model | Input | Output | Interlayer buffer needed | Flash | RAM |
|---|---:|---:|---:|---:|---:|
| `tinyml_kws` | 490 B | 48 B | 13,548 B | 85,028 B | 60,032 B |
| `tinyml_ad` | 640 B | 2,560 B | 2,688 B | 323,396 B | 62,376 B |
| `tinyml_ic` | 3,072 B | 40 B | 52,224 B | 172,320 B | 60,016 B |
| `tinyml_vww` | 27,648 B | 8 B | 46,080 B | 389,256 B | 59,952 B |

## Compiled model header

The compiler writes `nrf_axon_model_<name>_.h` (the model), `..._test_vectors_.h` and `..._layers_.h`. The add-on's four can be read online:

| Model | Compiled model | Test vectors |
|---|---|---|
| `tinyml_kws` | [`nrf_axon_model_tinyml_kws_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_kws_.h) | [`nrf_axon_model_tinyml_kws_test_vectors_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_kws_test_vectors_.h) |
| `tinyml_ad` | [`nrf_axon_model_tinyml_ad_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_ad_.h) | [`nrf_axon_model_tinyml_ad_test_vectors_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_ad_test_vectors_.h) |
| `tinyml_ic` | [`nrf_axon_model_tinyml_ic_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_ic_.h) | [`nrf_axon_model_tinyml_ic_test_vectors_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_ic_test_vectors_.h) |
| `tinyml_vww` | [`nrf_axon_model_tinyml_vww_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_vww_.h) | [`nrf_axon_model_tinyml_vww_test_vectors_.h`](https://github.com/nrfconnect/sdk-edge-ai/blob/v3.0.0/tests/axon/compiled_models/nrf_axon_model_tinyml_vww_test_vectors_.h) |

For `tinyml_kws`:

| Symbol | Where | What |
|---|---|---|
| `cmd_buffer_tinyml_kws[]` | flash | NPU command stream, 3,613 words |
| `axon_model_const_tinyml_kws` | flash | weights and biases, 22,064 B |
| `model_tinyml_kws` | flash | descriptor: buffer pointers, I/O shapes, quantisation, labels |

The header also states the RAM the model needs for its activations, the interlayer buffer (`NRF_AXON_MODEL_TINYML_KWS_MAX_IL_BUFFER_USED`; the app prints it as "workspace"). That RAM is not inside the NPU: it is the global array `nrf_axon_interlayer_buffer`, defined in the add-on's Zephyr platform file and sized by `CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE` in `app/prj.conf`. The same buffer holds the model's input and output. The header fails to compile if the buffer is too small.
