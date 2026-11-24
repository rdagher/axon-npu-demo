ncs    := "v3.4.1"
board  := "nrf54lm20dk/nrf54lm20b/cpuapp"
root   := justfile_directory()
cdir   := "/usr/local/executor_app"
here   := parent_directory(root)
# west workspace: the directory holding this repo, unless AXON_WS points elsewhere
ws     := env_var_or_default("AXON_WS", here)
launch := "nrfutil sdk-manager toolchain launch --ncs-version " + ncs
tc     := launch + " --chdir '" + ws + "' --"
serial := env_var_or_default("DK_SERIAL", "")
# MLPerf Tiny keyword spotting reference model, pinned by commit
tflite := "https://raw.githubusercontent.com/mlcommons/tiny/4addd0fa08d216e20637637874e084895f289da4/benchmark/training/keyword_spotting/trained_models/kws_ref_model.tflite"
sha256 := "aeea436800704fce17b17292e4412630ad856e9d777c044c64ef748a880bd0ae"

default:
    @just --list

# One-time: toolchain, then the SDK pinned in west.yml, checked out next to this repo (~5 GB)
setup *west_update_args:
    nrfutil sdk-manager toolchain install --ncs-version {{ncs}}
    test -d '{{here}}/.west' || {{launch}} -- west init -l '{{root}}'
    {{launch}} --chdir '{{here}}' -- west update --narrow -o=--depth=1 {{west_update_args}}

# Optional: download the MLPerf Tiny KWS .tflite and compile it into model/outputs/ (needs Docker)
compile:
    curl -sSfL -o '{{root}}/model/kws_ref_model.tflite' {{tflite}}
    echo '{{sha256}}  {{root}}/model/kws_ref_model.tflite' | $(command -v sha256sum || echo shasum -a 256) -c -
    # Image built as in the add-on's run_docker.sh; --user and HOME keep the outputs owned by you.
    docker build -t nrf-axon-nn-compiler '{{ws}}/edge-ai/tools/axon/compiler' \
        --build-arg compiler_root=bin --build-arg root_dir={{cdir}}/ \
        --build-arg work_dir=ws --build-arg yaml_file=axon.yaml
    docker run --rm --user $(id -u):$(id -g) -e HOME=/tmp -v '{{root}}/model:{{cdir}}/ws' \
        -w {{cdir}}/ws --entrypoint python3 nrf-axon-nn-compiler make_test_data.py
    docker run --rm --user $(id -u):$(id -g) -e HOME=/tmp \
        -v '{{root}}/model:{{cdir}}/ws' nrf-axon-nn-compiler ./ws/axon.yaml

# Build a model: tinyml_kws, tinyml_ad, tinyml_ic or tinyml_vww from the add-on, or `mlperf_kws model/outputs`
build model="tinyml_kws" headers="":
    {{tc}} west build -p -b {{board}} '{{root}}/app' --build-dir '{{root}}/build' -- -DAXON_MODEL={{model}} \
        {{ if headers == "" { "" } else { "-DAXON_MODEL_DIR='" + absolute_path(headers) + "'" } }}

# Measurement firmware: backend is axon or tflm; add `verify` to keep the UART and print results
bench backend="axon" mode="quiet" model="mlperf_kws" headers="model/outputs" tflite="model/kws_ref_model.tflite":
    {{tc}} west build -p -b {{board}} '{{root}}/bench' --build-dir '{{root}}/build' -- -DAXON_MODEL={{model}} \
        -DAXON_MODEL_DIR='{{absolute_path(headers)}}' -DTFLITE='{{absolute_path(tflite)}}' \
        -DEXTRA_CONF_FILE='{{backend}}.conf{{ if mode == "quiet" { ";quiet.conf" } else { "" } }}' \
        {{ if backend == "axon" { "-DEXTRA_DTC_OVERLAY_FILE=axon.overlay" } else { "" } }}

# Serial number of the kit to use: DK_SERIAL, or the only J-Link kit attached
_kit:
    #!/usr/bin/env bash
    set -euo pipefail
    [ -z "{{serial}}" ] || { echo "{{serial}}"; exit; }
    # `device list` prints one block per kit, starting with its serial number
    kits=$(nrfutil device list --traits jlink | grep -E '^[0-9A-Za-z]+$' || true)
    [ "$(printf '%s' "$kits" | grep -c .)" = 1 ] ||
        { echo "expected one J-Link kit, found: ${kits:-none}. Set DK_SERIAL=<serial number>." >&2; exit 1; }
    echo "$kits"

# Program the kit and reset it
flash:
    #!/usr/bin/env bash
    set -euo pipefail
    kit=$({{just_executable()}} _kit)
    nrfutil device program --serial-number "$kit" --firmware "$(ls '{{root}}'/build/*/zephyr/zephyr.hex)"
    nrfutil device reset --serial-number "$kit"

# App UART is the DK's VCOM1: port from nrfutil, terminal from the toolchain. Ctrl-] quits.
monitor:
    #!/usr/bin/env bash
    set -euo pipefail
    kit=$({{just_executable()}} _kit)
    port=$(nrfutil device list --traits jlink | awk -v sn="$kit" \
        '/^[0-9A-Za-z]+$/ {kit=$1} /vcom: 1/ && kit == sn {gsub(",","",$1); print $1; exit}')
    [ -n "$port" ] || { echo "no VCOM1 port for kit $kit" >&2; exit 1; }
    # macOS lists tty.usbmodem*, but cu.usbmodem* is the device to open
    {{tc}} python3 -m serial.tools.miniterm --raw "${port/tty./cu.}" 115200
