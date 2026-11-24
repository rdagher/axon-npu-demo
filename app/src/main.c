/* SPDX-License-Identifier: Apache-2.0 */

#include <assert.h> /* the model header needs static_assert */
#include <string.h>

#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>

#include <drivers/axon/nrf_axon_nn_infer.h>
#include <axon/nrf_axon_platform.h>

/* MODEL_NAME comes from CMake, e.g. tinyml_kws. */
#define CAT_(a, b)      a##b
#define CAT(a, b)       CAT_(a, b)
#define HEADER(suffix)  STRINGIFY(CAT(CAT(nrf_axon_model_, MODEL_NAME), suffix))

#include HEADER(_.h)
#include HEADER(_test_vectors_.h)

#define MODEL      CAT(model_, MODEL_NAME)
#define INPUTS     CAT(MODEL_NAME, _input_test_vectors)
#define EXPECTED   CAT(MODEL_NAME, _expected_output_vectors)
#define OUTPUT_LEN sizeof(CAT(MODEL_NAME, _expected_output_vector_0))

/* The driver pads the output to a multiple of 4 bytes. */
static int8_t out[ROUND_UP(OUTPUT_LEN, 4)] __aligned(4);

static void run_vectors(void)
{
	int matches = 0;

	for (size_t i = 0; i < ARRAY_SIZE(INPUTS); i++) {
		uint32_t t0 = k_cycle_get_32();
		nrf_axon_result_e res = nrf_axon_nn_model_infer_sync(&MODEL, INPUTS[i], out);
		uint32_t us = k_cyc_to_us_floor32(k_cycle_get_32() - t0);

		if (res != NRF_AXON_RESULT_SUCCESS) {
			printk("vector %zu: inference failed (%d)\n", i, res);
			continue;
		}

		bool match = memcmp(out, EXPECTED[i], OUTPUT_LEN) == 0;

		matches += match;
		printk("vector %zu: %s  %u us", i, match ? "bit exact" : "MISMATCH", us);
		if (MODEL.labels != NULL) {
			const char *label;
			int16_t class = nrf_axon_nn_get_classification(&MODEL, out, &label, NULL);

			printk("  class %d (%s)", class, label);
		}
		printk("\n");
	}
	printk("%d/%d outputs bit exact\n\n", matches, (int)ARRAY_SIZE(INPUTS));
}

int main(void)
{
	if (nrf_axon_platform_init() != NRF_AXON_RESULT_SUCCESS) {
		printk("axon platform init failed\n");
		return -1;
	}
	if (nrf_axon_nn_model_init_vars(&MODEL) != 0 ||
	    nrf_axon_nn_model_validate(&MODEL) != NRF_AXON_RESULT_SUCCESS) {
		printk("model rejected\n");
		return -1;
	}
	/* out[] holds one output, of the size of the expected vectors. */
	if (MODEL.input_cnt != 1 || MODEL.output_cnt != 1 ||
	    MODEL.outputs[0].packed_size != sizeof(out)) {
		printk("unsupported model: %d inputs, %u outputs, %u bytes out, %u expected\n",
		       MODEL.input_cnt, MODEL.output_cnt,
		       (unsigned int)MODEL.outputs[0].packed_size, (unsigned int)sizeof(out));
		return -1;
	}
	printk("model %s ready: %u bytes out, %u bytes of workspace\n", MODEL.model_name,
	       (unsigned int)OUTPUT_LEN, (unsigned int)MODEL.interlayer_buffer_needed);

	while (1) {
		run_vectors();
		k_sleep(K_SECONDS(2));
	}
}
