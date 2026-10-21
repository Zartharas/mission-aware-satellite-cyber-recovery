#include "aerc_ed25519_wrapper.h"

#include "monocypher-ed25519.h"

int AERC_ED25519_Verify(const uint8_t *signature,
                        size_t signature_size,
                        const uint8_t *public_key,
                        size_t public_key_size,
                        const uint8_t *message,
                        size_t message_size)
{
    int rc;

    if (signature == NULL || public_key == NULL || message == NULL)
    {
        return AERC_ED25519_VERIFY_INPUT_ERROR;
    }

    if (signature_size != AERC_ED25519_SIGNATURE_BYTES ||
        public_key_size != AERC_ED25519_PUBLIC_KEY_BYTES ||
        message_size > AERC_ED25519_MESSAGE_CAPACITY)
    {
        return AERC_ED25519_VERIFY_INPUT_ERROR;
    }

    rc = crypto_ed25519_check(signature, public_key, message, message_size);
    return rc == 0 ? AERC_ED25519_VERIFY_OK : AERC_ED25519_VERIFY_REJECT;
}
