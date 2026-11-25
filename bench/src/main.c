/* SPDX-License-Identifier: Apache-2.0 */

#include <stdlib.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>

#include <ppk2_trace.h>

#include "backend.h"

/* Inputs and expected outputs come from the compiler's test vectors, for both backends. */
#define CAT_(a, b) a##b
#define CAT(a, b)  CAT_(a, b)
#include STRINGIFY(CAT(CAT(nrf_axon_model_, MODEL_NAME), _test_vectors_.h))
#define INPUTS     CAT(MODEL_NAME, _input_test_vectors)
#define EXPECTED   CAT(MODEL_NAME, _expected_output_vectors)
#define INPUT_LEN  sizeof(CAT(MODEL_NAME, _test_input_vector_0))
#define OUTPUT_LEN sizeof(CAT(MODEL_NAME, _expected_output_vector_0))

PPK2_TRACE_CLAIM(0, infer);

/* The Axon driver pads its output to a multiple of 4 bytes. */
static int8_t out[ROUND_UP(OUTPUT_LEN, 4)] __aligned(4);

int main(void)
{
	int out_len = backend_init();

	if (out_len < (int)OUTPUT_LEN || out_len > (int)sizeof(out)) {
		printk("init failed: %d bytes out, %u expected\n", out_len, (unsigned int)OUTPUT_LEN);
		return -1;
	}
	printk("%s on %s\n", STRINGIFY(MODEL_NAME), IS_ENABLED(CONFIG_BENCH_TFLM) ? "TFLM" : "Axon");

	while (1) {
		for (size_t i = 0; i < ARRAY_SIZE(INPUTS); i++) {
			uint32_t t0 = k_cycle_get_32();
			int err;
			{
				PPK2_TRACE_SCOPE(ppk2_ch_infer);
				err = backend_infer((const int8_t *)INPUTS[i], INPUT_LEN, out);
			}
			uint32_t us = k_cyc_to_us_floor32(k_cycle_get_32() - t0);

			int diff = 0;

			for (size_t j = 0; j < OUTPUT_LEN; j++) {
				diff = MAX(diff, abs(out[j] - ((const int8_t *)EXPECTED[i])[j]));
			}
			printk("vector %zu: %s  %u us  largest difference %d\n", i,
			       err ? "FAILED" : diff ? "differs" : "bit exact", us, diff);
			if (err || diff > CONFIG_BENCH_TOLERANCE) {
				return -1; /* no more markers: a wrong inference is not measured */
			}
			if (CONFIG_BENCH_GAP_MS > 0) {
				k_sleep(K_MSEC(CONFIG_BENCH_GAP_MS));
			} else {
				k_busy_wait(100); /* back to back: awake, with the marker low for 10 samples */
			}
		}
	}
}
