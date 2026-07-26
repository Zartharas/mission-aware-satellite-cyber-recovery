#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static int bind_udp(uint16_t port)
{
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0)
    {
        return -1;
    }

    struct sockaddr_in address;
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(port);
    if (bind(fd, (const struct sockaddr *)&address, sizeof(address)) != 0)
    {
        int saved_errno = errno;
        close(fd);
        errno = saved_errno;
        return -1;
    }
    return fd;
}

static int send_to_port(int fd, uint16_t port, const unsigned char *payload, size_t length)
{
    struct sockaddr_in destination;
    memset(&destination, 0, sizeof(destination));
    destination.sin_family = AF_INET;
    destination.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    destination.sin_port = htons(port);
    ssize_t result = sendto(
        fd,
        payload,
        length,
        0,
        (const struct sockaddr *)&destination,
        sizeof(destination));
    return result == (ssize_t)length ? 0 : -1;
}

int main(void)
{
    const unsigned char sample[4] = {0x10, 0x20, 0x30, 0x40};
    unsigned char buffer[16];

    int radio_ingress = bind_udp(5011);
    int radio_egress = bind_udp(8011);
    int sender = socket(AF_INET, SOCK_DGRAM, 0);
    if (radio_ingress < 0 || radio_egress < 0 || sender < 0)
    {
        perror("socket setup");
        return 2;
    }

    if (send_to_port(sender, 5011, sample, sizeof(sample)) != 0)
    {
        perror("send ingress");
        return 3;
    }

    ssize_t received = recvfrom(radio_ingress, buffer, sizeof(buffer), 0, NULL, NULL);
    if (received != (ssize_t)sizeof(sample) || memcmp(buffer, sample, sizeof(sample)) != 0)
    {
        fprintf(stderr, "radio ingress self-test mismatch\n");
        return 4;
    }

    if (send_to_port(radio_ingress, 8011, buffer, (size_t)received) != 0)
    {
        perror("send egress");
        return 5;
    }

    received = recvfrom(radio_egress, buffer, sizeof(buffer), 0, NULL, NULL);
    if (received != (ssize_t)sizeof(sample) || memcmp(buffer, sample, sizeof(sample)) != 0)
    {
        fprintf(stderr, "radio egress self-test mismatch\n");
        return 6;
    }

    close(sender);
    close(radio_ingress);
    close(radio_egress);
    puts("RADIO_SOCKET_METADATA_SHIM_SELF_TEST=PASS");
    return 0;
}
