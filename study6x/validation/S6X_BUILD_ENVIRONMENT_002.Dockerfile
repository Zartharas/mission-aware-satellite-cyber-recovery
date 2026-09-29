FROM --platform=linux/amd64 amd64/ubuntu:noble-20260911@sha256:496754492fb28b4d3049432f2ca787449331e23fb14f0dd3fffea86bf5a93eb4

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       ca-certificates \
       cmake \
       file \
       git \
       jq \
       openssl \
       python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work

LABEL org.opencontainers.image.title="S6X-EAP-001 build environment v2 candidate" \
      org.opencontainers.image.description="Research-only linux/amd64 environment for NASA cFS v7.0.1 / LC S6X execution; v2 adds jq required by native_std.runtest" \
      org.opencontainers.image.source="Zartharas/mission-aware-satellite-cyber-recovery"
