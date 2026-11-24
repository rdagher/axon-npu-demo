# Licences

The licence of this repository, and of what the build and `just compile` fetch.

| Files | Licence |
|---|---|
| Everything in this repository | [Apache-2.0](../LICENSE) |
| nRF Connect SDK, Edge AI Add-on | Not in this repository. `west` fetches them under their own licences: Nordic's 5-Clause licence, which restricts use to Nordic devices, for the add-on, sdk-nrf and nrfxlib; Apache-2.0 for Zephyr; others for the remaining modules. The compiled models and test vectors are part of the add-on |
| MLPerf Tiny `.tflite` models | Not in this repository. `just compile` downloads them from [mlcommons/tiny](https://github.com/mlcommons/tiny), which is Apache-2.0. Each was trained on a public dataset named in its folder of that repository (Speech Commands v2 for keyword spotting, released under CC BY 4.0 according to [its paper](https://arxiv.org/abs/1804.03209)); the licences of the other three datasets were not checked here |
