ARG PYTHON_IMAGE=python:3.12.11-slim-bookworm
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

WORKDIR /app
COPY pre_freeze_dataset_validator.py /app/pre_freeze_dataset_validator.py

ENTRYPOINT ["python3", "/app/pre_freeze_dataset_validator.py"]
