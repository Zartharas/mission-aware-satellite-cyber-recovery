#include <stdint.h>
#include <stdio.h>

#include "monocypher.h"
#include "monocypher-ed25519.h"

int main(void)
{
    uint8_t seed[32];
    uint8_t secret_key[64];
    uint8_t public_key[32];
    size_t i;

    if (fread(seed, 1, sizeof(seed), stdin) != sizeof(seed))
    {
        return 1;
    }

    crypto_ed25519_key_pair(secret_key, public_key, seed);

    for (i = 0; i < sizeof(public_key); ++i)
    {
        printf("%02x", public_key[i]);
    }
    putchar('\n');

    crypto_wipe(seed, sizeof(seed));
    crypto_wipe(secret_key, sizeof(secret_key));
    return 0;
}
