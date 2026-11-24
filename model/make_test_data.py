# SPDX-License-Identifier: Apache-2.0
"""Random inputs for the compiler's test vectors: no dataset involved."""

import sys

import numpy as np
import tensorflow as tf

rng = np.random.default_rng(0)
for name, tflite in zip(sys.argv[1::2], sys.argv[2::2]):
    inp = tf.lite.Interpreter(tflite).get_input_details()[0]
    scale, zero_point = inp["quantization"]
    # Floats that quantise to values spread over the int8 range.
    q = rng.integers(-127, 127, (3, *inp["shape"][1:]))
    np.save(f"{name}_x.npy", ((q - zero_point) * scale).astype(np.float32))
    # Arbitrary: random inputs have no true class.
    np.save(f"{name}_y.npy", np.zeros(3, dtype=np.int64))
