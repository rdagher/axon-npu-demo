/* SPDX-License-Identifier: Apache-2.0 */

#include <string.h>

#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>

#include "backend.h"

/* Inputs and expected outputs come from the compiler's test vectors, for both backends. */
#define CAT_(a, b) a##b
#define CAT(a, b)  CAT_(a, b)
#include STRINGIFY(CAT(CAT(nrf_axon_model_, MODEL_NAME), _test_vectors_.h))
#define INPUTS     CAT(MODEL_NAME, _input_test_vectors)
#define EXPECTED   CAT(MODEL_NAME, _expected_output_vectors)
#define INPUT_LEN  sizeof(CAT(MODEL_NAME, _test_input_vector_0))
#define OUTPUT_LEN sizeof(CAT(MODEL_NAME, _expected_output_vector_0))

static const struct gpio_dt_spec trace = GPIO_DT_SPEC_GET(DT_PATH(zephyr_user), trace_gpios);
/* The Axon driver pads its output to a multiple of 4 bytes. */
static int8_t out[ROUND_UP(OUTPUT_LEN, 4)] __aligned(4);

int main(void)
{
	int out_len = backend_init();

	if (out_len < (int)OUTPUT_LEN || out_len > (int)sizeof(out) || gpio_pin_configure_dt(&trace, GPIO_OUTPUT_INACTIVE) != 0) {
		printk("init failed: %d bytes out, %u expected\n", out_len, (unsigned int)OUTPUT_LEN);
		return -1;
	}
	printk("%s on %s\n", STRINGIFY(MODEL_NAME), IS_ENABLED(CONFIG_BENCH_TFLM) ? "TFLM" : "Axon");

	while (1) {
		for (size_t i = 0; i < ARRAY_SIZE(INPUTS); i++) {
			gpio_pin_set_dt(&trace, 1);
			uint32_t t0 = k_cycle_get_32();
			int err = backend_infer((const int8_t *)INPUTS[i], INPUT_LEN, out);
			uint32_t us = k_cyc_to_us_floor32(k_cycle_get_32() - t0);
			gpio_pin_set_dt(&trace, 0);

			printk("vector %zu: %s  %u us  out[0..3] %d %d %d %d\n", i,
			       err ? "FAILED" : memcmp(out, EXPECTED[i], OUTPUT_LEN) ? "differs" : "bit exact",
			       us, out[0], out[1], out[2], out[3]);
			k_sleep(K_MSEC(CONFIG_BENCH_GAP_MS));
		}
	}
}
