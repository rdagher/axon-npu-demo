/* SPDX-License-Identifier: Apache-2.0 */

#include <assert.h> /* the model header needs static_assert */

#include <zephyr/sys/util.h>

#include <drivers/axon/nrf_axon_nn_infer.h>
#include <axon/nrf_axon_platform.h>

#include "backend.h"

#define CAT_(a, b) a##b
#define CAT(a, b)  CAT_(a, b)
#include STRINGIFY(CAT(CAT(nrf_axon_model_, MODEL_NAME), _.h))
#define MODEL CAT(model_, MODEL_NAME)

int backend_init(void)
{
	if (nrf_axon_platform_init() != NRF_AXON_RESULT_SUCCESS ||
	    nrf_axon_nn_model_init_vars(&MODEL) != 0 ||
	    nrf_axon_nn_model_validate(&MODEL) != NRF_AXON_RESULT_SUCCESS ||
	    MODEL.input_cnt != 1 || MODEL.output_cnt != 1) {
		return -1;
	}
	return MODEL.outputs[0].packed_size;
}

int backend_infer(const int8_t *in, size_t in_len, int8_t *out)
{
	ARG_UNUSED(in_len);
	return nrf_axon_nn_model_infer_sync(&MODEL, in, out) == NRF_AXON_RESULT_SUCCESS ? 0 : -1;
}
