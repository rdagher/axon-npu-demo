# SPDX-License-Identifier: Apache-2.0
"""Random inputs for the compiler's test vectors: no dataset involved."""

import numpy as np

rng = np.random.default_rng(0)
# The model quantises its input as q = x / 0.5847 + 83; this range spans int8.
np.save("x_test.npy", rng.uniform(-123, 25, (3, 49, 10, 1)).astype(np.float32))
# Arbitrary: random inputs have no true class.
np.save("y_test.npy", np.zeros(3, dtype=np.int64))
