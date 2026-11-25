# SPDX-License-Identifier: Apache-2.0
"""TFLite on the host against the outputs the Axon compiler expects, on the test vectors."""

import re
import sys

import numpy as np
import tensorflow as tf

TOLERANCE = 2  # as CONFIG_BENCH_TOLERANCE of the bench
failed = False

for name in sys.argv[1:]:
    interpreter = tf.lite.Interpreter(f"{name}.tflite")
    interpreter.allocate_tensors()
    inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    header = open(f"outputs/nrf_axon_model_{name}_test_vectors_.h").read()
    worst = 0
    for v in range(3):
        def vector(kind):
            body = re.search(rf"{name}_{kind}_vector_{v}\[[^=]*=\s*\{{(.*?)\}};", header, re.S).group(1)
            return np.array(re.findall(r"-?\d+", body), dtype=np.int64)
        x, expected = vector("test_input").astype(np.int8), vector("expected_output")
        shape = inp["shape"]
        if len(shape) == 4 and shape[3] > 1:  # the vectors are channel first, the tensor channel last
            x = x.reshape(shape[3], shape[1], shape[2]).transpose(1, 2, 0)
        interpreter.set_tensor(inp["index"], x.reshape(shape))
        interpreter.invoke()
        got = interpreter.get_tensor(out["index"]).astype(np.int64).ravel()
        worst = max(worst, int(np.abs(got - expected[:got.size]).max()))
    print(f"{name}: largest difference {worst} of 255")
    failed |= worst > TOLERANCE

sys.exit(failed)
