#define _GNU_SOURCE

#include <arpa/inet.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

typedef ssize_t (*recvfrom_fn_t)(int, void *, size_t, int, struct sockaddr *, socklen_t *);
typedef ssize_t (*sendto_fn_t)(int, const void *, size_t, int, const struct sockaddr *, socklen_t);

static recvfrom_fn_t real_recvfrom_fn = NULL;
static sendto_fn_t real_sendto_fn = NULL;
static int trace_fd = -1;
static atomic_ulong trace_sequence = 1;

static void resolve_symbols(void)
{
    if (real_recvfrom_fn == NULL)
    {
        real_recvfrom_fn = (recvfrom_fn_t)dlsym(RTLD_NEXT, "recvfrom");
    }
    if (real_sendto_fn == NULL)
    {
        real_sendto_fn = (sendto_fn_t)dlsym(RTLD_NEXT, "sendto");
    }
    if (real_recvfrom_fn == NULL || real_sendto_fn == NULL)
    {
        _exit(127);
    }
}

static int socket_port(const struct sockaddr *address, socklen_t length)
{
    if (address == NULL)
    {
        return 0;
    }
    if (address->sa_family == AF_INET && length >= sizeof(struct sockaddr_in))
    {
        const struct sockaddr_in *ipv4 = (const struct sockaddr_in *)address;
        return (int)ntohs(ipv4->sin_port);
    }
    if (address->sa_family == AF_INET6 && length >= sizeof(struct sockaddr_in6))
    {
        const struct sockaddr_in6 *ipv6 = (const struct sockaddr_in6 *)address;
        return (int)ntohs(ipv6->sin6_port);
    }
    return 0;
}

static int local_port_for_fd(int fd)
{
    struct sockaddr_storage address;
    socklen_t length = sizeof(address);
    if (getsockname(fd, (struct sockaddr *)&address, &length) != 0)
    {
        return 0;
    }
    return socket_port((const struct sockaddr *)&address, length);
}

static void emit_metadata(
    const char *event,
    int fd,
    int local_port,
    int peer_port,
    size_t requested,
    ssize_t result,
    int saved_errno)
{
    if (trace_fd < 0)
    {
        return;
    }

    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0)
    {
        now.tv_sec = 0;
        now.tv_nsec = 0;
    }

    unsigned long sequence = atomic_fetch_add(&trace_sequence, 1);
    long long monotonic_ns = (long long)now.tv_sec * 1000000000LL + now.tv_nsec;
    char line[384];
    int length = snprintf(
        line,
        sizeof(line),
        "RADIO_SOCKET_METADATA sequence=%lu event=%s monotonic_ns=%lld fd=%d local_port=%d peer_port=%d requested=%zu result=%zd errno=%d\n",
        sequence,
        event,
        monotonic_ns,
        fd,
        local_port,
        peer_port,
        requested,
        result,
        saved_errno);
    if (length > 0)
    {
        size_t bytes = (size_t)length < sizeof(line) ? (size_t)length : sizeof(line) - 1;
        (void)write(trace_fd, line, bytes);
    }
}

__attribute__((constructor)) static void initialize_radio_socket_metadata_shim(void)
{
    resolve_symbols();
    const char *path = getenv("RADIO_SOCKET_TRACE_PATH");
    if (path != NULL && path[0] != '\0')
    {
        trace_fd = open(path, O_WRONLY | O_CREAT | O_APPEND | O_CLOEXEC, 0600);
    }
}

__attribute__((destructor)) static void close_radio_socket_metadata_shim(void)
{
    if (trace_fd >= 0)
    {
        (void)close(trace_fd);
        trace_fd = -1;
    }
}

ssize_t recvfrom(
    int fd,
    void *buffer,
    size_t length,
    int flags,
    struct sockaddr *source_address,
    socklen_t *source_length)
{
    resolve_symbols();
    errno = 0;
    ssize_t result = real_recvfrom_fn(fd, buffer, length, flags, source_address, source_length);
    int saved_errno = errno;
    int local_port = local_port_for_fd(fd);
    if (local_port == 5011)
    {
        int peer_port = 0;
        if (source_address != NULL && source_length != NULL)
        {
            peer_port = socket_port((const struct sockaddr *)source_address, *source_length);
        }
        emit_metadata("recvfrom", fd, local_port, peer_port, length, result, saved_errno);
    }
    errno = saved_errno;
    return result;
}

ssize_t sendto(
    int fd,
    const void *buffer,
    size_t length,
    int flags,
    const struct sockaddr *destination_address,
    socklen_t destination_length)
{
    resolve_symbols();
    int local_port = local_port_for_fd(fd);
    int peer_port = socket_port(destination_address, destination_length);
    errno = 0;
    ssize_t result = real_sendto_fn(
        fd,
        buffer,
        length,
        flags,
        destination_address,
        destination_length);
    int saved_errno = errno;
    if (local_port == 5011 || peer_port == 8011)
    {
        emit_metadata("sendto", fd, local_port, peer_port, length, result, saved_errno);
    }
    errno = saved_errno;
    return result;
}
