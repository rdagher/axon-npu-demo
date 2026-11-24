# Compiling a model

`just compile` downloads the four MLPerf Tiny `.tflite` files and runs the Axon compiler on them. It shows how the headers used above are produced.

```sh
just compile                          # needs Docker
just build mlperf_kws model/outputs
```

`just compile`:

1. downloads the four reference models from [mlcommons/tiny](https://github.com/mlcommons/tiny/tree/4addd0fa08d216e20637637874e084895f289da4/benchmark/training) at a pinned commit and checks their SHA-256,
2. writes three random inputs per model with `model/make_test_data.py`, run inside the compiler image,
3. runs the Axon compiler (Docker image built from the add-on) on `model/axon.yaml`.

The compiler writes to `model/outputs/`, which is not committed. For each of `mlperf_kws`, `mlperf_ad`, `mlperf_ic` and `mlperf_vww`:

| File | Content |
|---|---|
| `nrf_axon_model_mlperf_kws_.h` | the compiled model |
| `nrf_axon_model_mlperf_kws_test_vectors_.h` | the three inputs and the outputs the compiler computed for them on the host |
| `nrf_axon_model_mlperf_kws_layers_.h` | per-layer models, not used here |
| `nrf_axon_model_mlperf_kws_test_inference_labels_.csv` | the same expected outputs as CSV, not used here |

`mlperf_kws` is not the add-on's `tinyml_kws`: same layers and sizes, different weights, and `int8` outputs (12 B) where the add-on's header has `int32` (48 B). The inputs are random, so the printed classes mean nothing; only the bit-exact check does.
