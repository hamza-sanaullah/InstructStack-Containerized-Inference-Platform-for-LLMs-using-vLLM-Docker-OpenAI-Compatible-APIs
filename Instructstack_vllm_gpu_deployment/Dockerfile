# Stage 1: Get Miniconda
FROM continuumio/miniconda3 as conda-base

# Stage 2: CUDA + Conda
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Copy Conda from Stage 1
COPY --from=conda-base /opt/conda /opt/conda

# Set global env
ENV PATH=/opt/conda/bin:$PATH
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /Instructstack

# Install system dependencies and Rust
RUN apt-get update && apt-get install -y \
    curl wget git build-essential gcc g++ pkg-config libssl-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

# Add Rust/uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Create Conda environment
RUN conda create -n vllm_env python=3.11 -y

# Use conda env for following commands
SHELL ["conda", "run", "-n", "vllm_env", "/bin/bash", "-c"]

# Install uv and then vllm inside the conda env
RUN curl -LsSf https://astral.sh/uv/install.sh | sh 
# Add uv install path to PATH
ENV PATH="$PATH:/root/.local/bin"
RUN uv pip install vllm

# Set UV env vars
ENV UV_HTTP_TIMEOUT=500

# Restore default shell
SHELL ["/bin/bash", "-c"]

# Expose API port
EXPOSE 8000

# Run vLLM server
CMD ["conda", "run", "--no-capture-output", "--prefix", "/opt/conda/envs/vllm_env", "vllm", "serve", "--model", "yasserrmd/Text2SQL-1.5B", "--port", "8000"]
