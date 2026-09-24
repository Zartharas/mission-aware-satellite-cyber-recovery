#ifndef AERC_ED25519_WRAPPER_H
#define AERC_ED25519_WRAPPER_H

#include <stddef.h>
#include <stdint.h>

#define AERC_ED25519_PUBLIC_KEY_BYTES 32u
#define AERC_ED25519_SIGNATURE_BYTES 64u
#define AERC_ED25519_MESSAGE_CAPACITY 64u

#define AERC_ED25519_VERIFY_OK 0
#define AERC_ED25519_VERIFY_REJECT 1
#define AERC_ED25519_VERIFY_INPUT_ERROR (-1)

int AERC_ED25519_Verify(const uint8_t *signature,
                        size_t signature_size,
                        const uint8_t *public_key,
                        size_t public_key_size,
                        const uint8_t *message,
                        size_t message_size);

#endif
