# Notes

What the recipes assume, and what the compiler and the build system need.

## Workspace

If nRF Connect SDK v3.4.1 is already on disk, let west clone from it
instead of downloading (`--path-cache`, see `west update --help`):

```sh
just setup --path-cache /opt/nordic/ncs/v3.4.1
```

`just setup` can be run again after an interrupted download.

To reuse an existing add-on v3.0.0 workspace instead, skip `just setup`, install the toolchain
(`nrfutil sdk-manager toolchain install --ncs-version v3.4.1`) and prefix the other recipes:
`AXON_WS=/path/to/workspace just build`.

## Recipes, compiler and build

- `just flash` and `just monitor` use the only J-Link kit attached. With several, they stop and ask for `DK_SERIAL=<serial number>`, as listed by `nrfutil device list`.
- The compiler in add-on v3.0.0 (Axon compiler v2.0.1) fails without the `classification_labels` key in `model/axon.yaml`. A model without classes, like anomaly detection, takes the key empty and no `test_labels`.
- The compiler writes the test vectors header only with `test_data` and `header_file_test_vector_cnt` above 0; the default is 0.
- The `us` column is the time of one `nrf_axon_nn_model_infer_sync()` call, measured with `k_cycle_get_32()` (1 µs resolution). It includes NPU power-up and locking, the input copy, the NPU run, any CPU layer, the output copy and power-down.
- `just flash` and `just monitor` need `bash`.
- A model header defines its data, so it can be included in one C file only.
- `just build` passes `-DAXON_MODEL` and `-DAXON_MODEL_DIR` to CMake; `app/CMakeLists.txt` reads them with `zephyr_get()`, since a plain cache variable does not reach the app image under sysbuild.
- Paths containing spaces are not supported by the SDK's build system.
