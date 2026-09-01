FROM python:3.11-slim-bookworm@sha256:c425d915a89a6dcd3183b1797ad9bd8878caff5a417f6371c8df93c8ea8b727f

ARG TLC_VERSION=1.7.4
ARG TLC_SHA1=bee4a54f3ee3d4afc347c3240ec2d9e93b075104
ARG TLC_SHA256=936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL \
      "https://github.com/tlaplus/tlaplus/releases/download/v${TLC_VERSION}/tla2tools.jar" \
      -o /opt/tla2tools.jar \
    && echo "${TLC_SHA1}  /opt/tla2tools.jar" | sha1sum -c - \
    && echo "${TLC_SHA256}  /opt/tla2tools.jar" | sha256sum -c -

COPY study2/requirements.txt /tmp/study2-requirements.txt
RUN python -m pip install --no-cache-dir --only-binary=:all: \
    --requirement /tmp/study2-requirements.txt

WORKDIR /workspace
COPY . .

ENV PYTHONPATH=/workspace/src:/workspace/study2/src

ENTRYPOINT ["bash", "study2/scripts/validate.sh"]
