# Stage 1: Build
FROM rust:1.85-slim-bookworm AS builder
WORKDIR /src
COPY runtime-v2/ .
RUN cargo build --release --bin aigon-runtime-v2 && \
    strip target/release/aigon-runtime-v2

# Stage 2: Runtime
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/target/release/aigon-runtime-v2 /usr/local/bin/
EXPOSE 7000 8080

ENV RUST_LOG=info
ENV AIGON_MODE=standalone
ENV QWEN_API_KEY=""
ENV QWEN_ENDPOINT="https://ws-h3ayxryayp3b7ad5.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
ENV QWEN_MODEL="qwen3.7-max"

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:7000/health || exit 1

ENTRYPOINT ["/usr/local/bin/aigon-runtime-v2"]
CMD ["--mode", "standalone", "--listen", "0.0.0.0:7000"]
