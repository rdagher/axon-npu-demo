/* SPDX-License-Identifier: Apache-2.0 */

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Returns the size of the model output in bytes, or a negative value. */
int backend_init(void);
int backend_infer(const int8_t *in, size_t in_len, int8_t *out);

#ifdef __cplusplus
}
#endif
