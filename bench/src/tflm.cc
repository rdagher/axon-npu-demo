/* SPDX-License-Identifier: Apache-2.0 */

#include <string.h>

#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/micro/micro_mutable_op_resolver.h>
#include <tensorflow/lite/schema/schema_generated.h>

#include "backend.h"

alignas(16) static const unsigned char model_data[] = {
#include "model.tflite.inc"
};
alignas(16) static uint8_t arena[CONFIG_BENCH_TFLM_ARENA_SIZE];
static tflite::MicroInterpreter *interpreter;

int backend_init(void)
{
	/* The operators of the four MLPerf Tiny reference models. */
	static tflite::MicroMutableOpResolver<7> ops;
	ops.AddConv2D();
	ops.AddDepthwiseConv2D();
	ops.AddFullyConnected();
	ops.AddAveragePool2D();
	ops.AddAdd();
	ops.AddReshape();
	ops.AddSoftmax();

	static tflite::MicroInterpreter instance(tflite::GetModel(model_data), ops, arena, sizeof(arena));
	if (instance.AllocateTensors() != kTfLiteOk) {
		return -1;
	}
	interpreter = &instance;
	return interpreter->output(0)->bytes;
}

int backend_infer(const int8_t *in, size_t in_len, int8_t *out)
{
	TfLiteTensor *input = interpreter->input(0);

	if (input->bytes != in_len) {
		return -1;
	}
	memcpy(input->data.int8, in, in_len);
	if (interpreter->Invoke() != kTfLiteOk) {
		return -1;
	}
	memcpy(out, interpreter->output(0)->data.int8, interpreter->output(0)->bytes);
	return 0;
}
