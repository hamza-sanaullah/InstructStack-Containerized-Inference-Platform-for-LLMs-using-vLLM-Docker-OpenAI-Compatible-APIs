# Use Miniconda as the base image
FROM continuumio/miniconda3

# System-level setup (matches your host setup)
RUN apt-get update -y && \
    apt-get install -y gcc-12 g++-12 libnuma-dev python3-dev build-essential cmake make g++ wget curl unzip git libtcmalloc-minimal4 ninja-build && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 10 --slave /usr/bin/g++ g++ /usr/bin/g++-12

# Create root project directory
WORKDIR /Instructstack

# Copy the Conda environment file
COPY environment.yml ./environment.yml

# Create Conda environment
RUN conda env create -f environment.yml

# Use conda environment by default
SHELL ["conda", "run", "-n", "vllm_env", "/bin/bash", "-c"]

# Clone the vLLM repo
RUN git clone https://github.com/vllm-project/vllm.git /Instructstack/vllm_source

# Install Rust (for compiling some packages like outlines_core)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Upgrade pip
WORKDIR /Instructstack/vllm_source
RUN pip install --upgrade pip --retries 10

# Install build tools and dependencies
RUN pip install --retries 10 \
    "cmake>=3.26.1" wheel packaging ninja "setuptools-scm>=8" numpy

# Install CPU-specific dependencies
RUN pip install --retries 10 -v -r requirements/cpu.txt --extra-index-url https://download.pytorch.org/whl/cpu

ENV VLLM_CPU_CUSTOM_OPS=""
# Build the VLLM repo with CPU target
RUN VLLM_TARGET_DEVICE=cpu MAX_JOBS=1 python setup.py install

# Set environment variables inside container
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4:$LD_PRELOAD 

# (Optional Debug) Print path to libtcmalloc to verify it's there
RUN find / -name *libtcmalloc* 2>/dev/null

# Geting this error while inferencing
# ImportError: ...libstdc++.so.6: version `GLIBCXX_3.4.30` not found (required by ...intel_extension_for_pytorch...)
# `GLIBCXX_3.4.30`is part of GCC 13
# Updating the libstdc++ Version
RUN conda install -c conda-forge libstdcxx-ng
# Uninstall the Broken VLLm build
RUN pip uninstall vllm -y
ENV VLLM_DISABLE_CUSTOM_OPS=1

#Installing VLLM in the editable mode
 RUN VLLM_TARGET_DEVICE=cpu python setup.py develop



# Doing Optimizations
ENV VLLM_DISABLE_CHUNKED_PREFILL=1
ENV VLLM_CPU_KVCACHE_SPACE=4
ENV VLLM_CPU_OMP_THREADS_BIND=0-7
ENV VLLM_DISABLE_PREFIX_CACHE=1
ENV VLLM_TARGET_DEVICE=cpu


# Final workdir for serving
WORKDIR /Instructstack/vllm_source



# Expose API port
EXPOSE 8000




# Serve the model
CMD ["conda","run","-n","vllm_env","vllm","serve","facebook/opt-125m","--port","8000", "--device", "cpu", "--dtype","float32","--enforce-eager"]


# COPY vllm_source /Instructstack/vllm_source

