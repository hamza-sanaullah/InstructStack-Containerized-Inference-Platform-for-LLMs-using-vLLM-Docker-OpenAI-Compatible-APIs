# vLLM GPU-Based Multi-Model Deployment

![GPU-Based vLLM Architecture](GPU-Based-VLLM%20-Architecture.png)

A production-ready deployment solution for serving multiple language models efficiently using vLLM with GPU acceleration, comprehensive monitoring, and FastAPI backend integration.

## Table of Contents

- [Introduction](#introduction)
- [Models Served](#models-served)
- [Deployment Journey](#deployment-journey)
- [Technical Details](#technical-details)
- [Running the Project](#running-the-project)
- [Monitoring Setup](#monitoring-setup)
- [Credits & References](#credits--references)

---

## Introduction

**vLLM** (Very Large Language Model) is a high-throughput and memory-efficient inference and serving engine for Large Language Models (LLMs). It revolutionizes LLM serving through advanced optimization techniques:

### Key Features

- **KV Cache Optimization**: vLLM implements PagedAttention, which manages attention keys and values in non-contiguous memory pages, similar to how operating systems manage virtual memory. This eliminates memory fragmentation and enables dynamic allocation based on sequence length.

- **Attention Optimization**: Uses advanced attention mechanisms that reduce computational complexity while maintaining model accuracy, enabling faster inference speeds.

- **Efficient GPU Memory Usage**: vLLM maximizes GPU memory utilization through intelligent memory management, allowing larger batch sizes and higher throughput compared to traditional serving methods.

- **GPU Full Utilization**: This deployment ensures complete GPU resource utilization through optimized memory allocation and parallel processing capabilities.

### Project Scope

This project implements a **multi-model serving architecture** with **high concurrency support** using GPU acceleration. The system serves multiple language models simultaneously through separate vLLM containers, enabling efficient resource sharing and scalable inference capabilities for production environments.

---

## Models Served

This deployment serves two specialized SQL generation models optimized for different use cases:

### 1. yasserrmd/Text2SQL-1.5B
- **Repository**: [https://huggingface.co/yasserrmd/Text2SQL-1.5B](https://huggingface.co/yasserrmd/Text2SQL-1.5B)
- **Purpose**: Advanced text-to-SQL generation with 1.5B parameters
- **Port**: 8000
- **Specialization**: Complex query generation and natural language to SQL conversion

### 2. premai-io/prem-1B-SQL  
- **Repository**: [https://huggingface.co/premai-io/prem-1B-SQL](https://huggingface.co/premai-io/prem-1B-SQL)
- **Purpose**: Lightweight SQL generation with 1B parameters
- **Port**: 8001 (when enabled)
- **Specialization**: Fast SQL query generation for real-time applications

Both models are served via **separate vLLM containers** running on different ports, enabling true multi-model support with independent scaling and resource allocation.

---

## Deployment Journey

### Docker Images Built

#### 1. vLLM GPU Image
- **Docker Hub**: [https://hub.docker.com/repository/docker/hamzaak4/vllm-gpu-image/general](https://hub.docker.com/repository/docker/hamzaak4/vllm-gpu-image/general)
- **Features**: GPU-optimized vLLM runtime with CUDA 12.1.1 support
- **Base**: NVIDIA CUDA runtime with Miniconda integration
- **Optimizations**: Rust-compiled dependencies and UV package manager for faster installs

#### 2. FastAPI Backend for vLLM GPU
- **Docker Hub**: [https://hub.docker.com/repository/docker/hamzaak4/fastapi-vllm/general](https://hub.docker.com/repository/docker/hamzaak4/fastapi-vllm/general)
- **Features**: RESTful API interface with model switching capabilities
- **Integrations**: Pydantic Logfire monitoring and Prometheus metrics

### Key Achievements

✅ **Pydantic Logfire Integration**: Implemented comprehensive LLM monitoring in FastAPI backend for request tracing, performance metrics, and error tracking

![Pydantic Logfire Setup](Pydantic_Logfire_Setup.png)

✅ **Complete Monitoring Stack**: Integrated Prometheus, Grafana, Node Exporter, cAdvisor, and DCGM Exporter for full-stack observability

✅ **Concurrency Testing**: Successfully achieved multi-user concurrent requests with GPU acceleration

✅ **Multi-Model Architecture**: Parallel execution of multiple vLLM containers, each serving different models on dedicated ports

✅ **Production-Ready**: Containerized deployment with proper resource management and monitoring

---

## Technical Details

### Docker Architecture

This project leverages several key Docker concepts for scalable deployment:

- **Images**: Pre-built containers with vLLM GPU runtime and FastAPI backend
- **Containers**: Isolated runtime environments for each service component  
- **Volumes**: Persistent storage for models and configuration files
- **Docker Compose**: Multi-container orchestration and service management
- **Port Mapping**: Network routing between containers and host system

### Repository Structure

#### Core Configuration Files

- **`docker-compose.yml`**: 
  - Orchestrates multi-container setup including vLLM servers, FastAPI backend, and monitoring stack
  - Manages service dependencies, networking, and volume mounts
  - Configures GPU access and environment variables

- **`Dockerfile`** (vLLM GPU):
  - Defines GPU-enabled vLLM environment with CUDA 12.1.1 runtime
  - Sets up Miniconda environment with Python 3.11
  - Installs Rust toolchain and UV package manager for optimized builds

- **`Fastapi_vllm_web/Dockerfile`** (FastAPI):
  - Creates lightweight Python 3.11 environment for API backend
  - Installs FastAPI, Prometheus instrumentation, and Logfire monitoring
  - Configures proper networking and port exposure

- **`prometheus/prometheus.yml`**:
  - Defines scrape configurations for all monitoring targets
  - Monitors vLLM containers, FastAPI backend, Node Exporter, cAdvisor, and DCGM Exporter
  - Sets collection intervals and service discovery rules

- **`download_model.py`**:
  - Automated script for downloading Hugging Face models locally
  - Handles model repository cloning and local storage setup
  - Supports both models with configurable download paths

### vLLM Serving Commands

#### GPU-Optimized Model Serving
```bash
# Basic vLLM serving with GPU optimization
vllm serve <model_name> --tensor-parallel-size 1 --gpu-memory-utilization 0.9 --port <port>

# OpenAI-compatible API server
python -m vllm.entrypoints.openai.api_server --model <model_name>

# Production configuration with batching
vllm serve <model_name> --max-num-seqs 10 --gpu-memory-utilization 0.3 --max-model-len 2048
```

#### Parameter Explanations

**`--gpu-memory-utilization`**: 
- Controls the percentage of GPU memory allocated to the model
- `0.9` = Uses 90% of available GPU memory for maximum performance
- `0.3` = Uses 30% of GPU memory, leaving space for multiple models or other processes
- Lower values enable multi-model serving on the same GPU

**`--max-model-len`**: 
- Sets the maximum sequence length (context window) the model can handle
- `2048` = Maximum of 2048 tokens for input + output combined
- Affects memory usage - longer sequences require more GPU memory
- Must be within the model's trained context length limits

**`--max-num-seqs`**: 
- Maximum number of sequences (requests) processed simultaneously in a batch
- `10` = Process up to 10 concurrent requests in parallel
- Higher values increase throughput but require more GPU memory
- Enables efficient batching for better GPU utilization

#### Multi-Model Configuration
Each model runs in a **separate container** with dedicated resources:
- **Model 1**: `yasserrmd/Text2SQL-1.5B` on port 8000
- **Model 2**: `premai-io/prem-1B-SQL` on port 8001  
- **Independent Scaling**: Each container can be scaled separately based on demand
- **Resource Isolation**: GPU memory allocation managed per container

#### Concurrency Performance Results

**Single Model Serving** (yasserrmd/Text2SQL-1.5B):
- **Average Response Time**: 0.2 seconds
- **Configuration**: `--gpu-memory-utilization 0.9` for maximum performance
- **Concurrent Requests**: Optimized for high-frequency single model queries

**Multi-Model Serving** (Two separate vLLM containers):
- **Average Response Time**: 1.4 seconds  
- **Configuration**: `--gpu-memory-utilization 0.3` per container
- **Architecture**: Two independent vLLM containers running simultaneously
- **Benefit**: True parallel model serving with isolated resource allocation

> **Multi-Model Implementation**: Achieved using **2 separate vLLM containers**, each serving different models on dedicated ports. This approach ensures complete resource isolation and enables independent scaling of each model based on demand.

### Key Features

- **GPU Memory Management**: Optimized allocation with configurable utilization limits
- **Concurrent Request Handling**: Multi-sequence processing with batching support
- **OpenAI-Compatible API**: Standard endpoints for easy integration
- **Dynamic Model Loading**: Runtime model switching capabilities
- **Comprehensive Logging**: Request tracing and performance monitoring

---

## Running the Project

> **System Requirements**: This setup is designed for Ubuntu/Linux distributions with NVIDIA GPU support and Docker with GPU runtime.

### Prerequisites

- NVIDIA GPU with CUDA support
- Docker with NVIDIA Container Runtime
- Docker Compose v3.8+
- At least 8GB GPU memory (recommended)

### Environment Variables Configuration

The project uses environment variables for flexible configuration. You can configure VLLM parameters, GPU settings, and API endpoints without modifying the docker-compose.yml file.

#### Configuration Methods

**Option 1: .env File (Recommended)**
```bash
# The .env file is already created for you
# Just edit it with your desired values
nano .env
```

**Option 2: Terminal Export**
```bash
# Set variables in your terminal before running docker-compose
export MAX_NUM_SEQS=20
export GPU_MEMORY_UTILIZATION=0.5
export LOGFIRE_TOKEN="your_actual_logfire_key_here"
export NVIDIA_VISIBLE_DEVICES=1

# Then run docker-compose
docker-compose up
```

**Option 3: Direct Command Line**
```bash
# Set variables directly in the same command line as docker-compose
# This means setting the variable and running docker-compose in one line
MAX_NUM_SEQS=20 GPU_MEMORY_UTILIZATION=0.5 docker-compose up
```

#### Running with Default Values
If you want to run the project with the default configuration values defined in docker-compose.yml, simply run:
```bash
docker-compose up
```

#### Customizing Configuration
If you want to customize VLLM parameters, GPU settings, or API endpoints, you can use environment variables in two ways:

#### Key Configurable Variables

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `MAX_NUM_SEQS` | 10 | Maximum concurrent sequences | `20` for high throughput |
| `VLLM_PORT` | 8000 | Primary VLLM server port | `8000` |
| `GPU_MEMORY_UTILIZATION` | 0.3 | GPU memory usage (0.0-1.0) | `0.5` for balanced usage |
| `MAX_MODEL_LEN` | 2048 | Maximum sequence length | `4096` for longer contexts |
| `NVIDIA_VISIBLE_DEVICES` | 0 | GPU device ID | `1` for second GPU |
| `DEFAULT_MODEL` | yasserrmd/Text2SQL-1.5B | Primary model | Custom model path |
| `LOGFIRE_TOKEN` | - | Your Logfire serve key | `pylf_v1_...` |
| `MODEL_REPO_ID` | premai-io/prem-1B-SQL | Model to download | Custom Hugging Face model |
| `MODEL_LOCAL_DIR` | models/premai-io/prem-1B-SQL | Local model directory | Custom local path |
| `MODEL_USE_SYMLINKS` | False | Use symlinks for models | True/False |
| `MODELS_TO_DOWNLOAD` | - | Multiple models (comma-separated) | "model1,model2,model3" |

#### Secondary VLLM Service Variables
For the second VLLM container (vllm1), use variables with `_1` suffix:
- `MAX_NUM_SEQS_1`: Secondary server sequence limit
- `VLLM_PORT_1`: Secondary server port (default: 8001)
- `GPU_MEMORY_UTILIZATION_1`: Secondary GPU memory usage
- `DEFAULT_MODEL_1`: Secondary model path

#### Example .env File
```bash
# Primary VLLM Configuration
MAX_NUM_SEQS=15
VLLM_PORT=8000
GPU_MEMORY_UTILIZATION=0.4
MAX_MODEL_LEN=4096
NVIDIA_VISIBLE_DEVICES=0
DEFAULT_MODEL=yasserrmd/Text2SQL-1.5B

# Secondary VLLM Configuration  
MAX_NUM_SEQS_1=5
VLLM_PORT_1=8001
GPU_MEMORY_UTILIZATION_1=0.3
DEFAULT_MODEL_1=premai-io/prem-1B-SQL

# FastAPI Configuration
LOGFIRE_TOKEN=pylf_v1_your_actual_key_here
VLLM_API_URL=http://vllm:8000/v1/completions
```

#### What You Can Do With Environment Variables

**1. Optimize Performance for Different Use Cases**
- **High Throughput**: Set `MAX_NUM_SEQS=20` for processing many requests simultaneously
- **Low Latency**: Set `MAX_NUM_SEQS=5` for faster individual response times
- **Memory Optimization**: Adjust `GPU_MEMORY_UTILIZATION` based on your GPU capacity
- **Long Context**: Increase `MAX_MODEL_LEN=4096` for handling longer conversations

**2. Multi-GPU Configuration**
- **Single GPU**: Use `NVIDIA_VISIBLE_DEVICES=0` (default)
- **Second GPU**: Use `NVIDIA_VISIBLE_DEVICES=1` for dedicated GPU processing
- **Multiple GPUs**: Configure different services to use different GPUs

**3. Model Customization**
- **Switch Models**: Change `DEFAULT_MODEL` to use different Hugging Face models
- **Custom Paths**: Point to locally stored models or different model versions
- **Model Comparison**: Run different models on different ports for A/B testing

**4. Production vs Development Settings**
- **Development**: Lower memory usage, smaller batch sizes for testing
- **Production**: Higher throughput, optimized memory allocation for live serving
- **Staging**: Balanced settings for pre-production testing

**5. Resource Management**
- **Memory Constraints**: Reduce `GPU_MEMORY_UTILIZATION` if running other GPU workloads
- **Port Conflicts**: Change ports if 8000/8001 are already in use
- **Load Balancing**: Distribute load across multiple VLLM instances

**6. Monitoring and Logging**
- **Logfire Integration**: Set your `LOGFIRE_TOKEN` for comprehensive LLM monitoring
- **API Endpoints**: Configure `VLLM_API_URL` for different deployment scenarios
- **Custom Metrics**: Adjust monitoring parameters for your specific needs

**7. Scaling and Deployment**
- **Horizontal Scaling**: Run multiple VLLM containers with different configurations
- **Load Distribution**: Use different ports and memory allocations per instance
- **Failover**: Configure backup models and endpoints for high availability

### Option 1: Full Setup with Docker Compose (Recommended)

#### Step 1: Clone Repository
```bash
git clone <your-repository-url>
cd Instructstack_vllm_gpu
```

#### Step 2: Download Models Locally
```bash
# Install Hugging Face Hub if not already installed
pip install huggingface_hub

# Download models using environment variables
python download_model.py
```

**Model Download Configuration Options:**

**Single Model Download:**
```bash
# Use default model (premai-io/prem-1B-SQL)
python download_model.py

# Or specify custom model
MODEL_REPO_ID=yasserrmd/Text2SQL-1.5B python download_model.py
```

**Multiple Models Download:**
```bash
# Download multiple models at once
MODELS_TO_DOWNLOAD="yasserrmd/Text2SQL-1.5B,premai-io/prem-1B-SQL" python download_model.py
```

**Custom Download Directory:**
```bash
# Specify custom local directory
MODEL_LOCAL_DIR=models/custom/path python download_model.py
```

#### Step 3: Launch Complete Stack
```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up --build -d
```

#### Step 4: Verify Services
- **vLLM Server**: http://localhost:8000
- **FastAPI Backend**: http://localhost:9000  
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Node Exporter**: http://localhost:9100
- **cAdvisor**: http://localhost:8081
- **DCGM Exporter**: http://localhost:9400

### Option 2: Manual Container Execution

#### vLLM GPU Container
```bash
# Run yasserrmd/Text2SQL-1.5B model
docker run --gpus all -p 8000:8000 \
  -v ./models:/models \
  hamzaak4/vllm-gpu-image:latest \
  --model yasserrmd/Text2SQL-1.5B \
  --gpu-memory-utilization 0.9

# Run premai-io/prem-1B-SQL model  
docker run --gpus all -p 8001:8001 \
  -v ./models:/models \
  hamzaak4/vllm-gpu-image:latest \
  --model premai-io/prem-1B-SQL \
  --gpu-memory-utilization 0.3 \
  --port 8001
```

#### FastAPI Backend Container
```bash
docker run -p 9000:9000 \
  -e VLLM_API_URL=http://localhost:8000/v1/completions \
  -e LOGFIRE_TOKEN=your_logfire_token \
  hamzaak4/fastapi-vllm:latest
```

### API Usage Examples

#### cURL Examples
```bash
# Test model completion
curl -X POST "http://localhost:8000/v1/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "yasserrmd/Text2SQL-1.5B",
    "prompt": "Generate SQL to find all users with age greater than 25",
    "max_tokens": 100,
    "temperature": 0.7
  }'

# Health check
curl http://localhost:8000/health
```

#### Postman Collection
Create a new request with:
- **Method**: POST
- **URL**: `http://localhost:9000/api/generate`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "prompt": "Create a SQL query to select all products with price > 100",
  "max_tokens": 150,
  "temperature": 0.5
}
```

---

## Monitoring Setup

### Comprehensive Observability Stack

#### Prometheus Metrics Collection
Prometheus scrapes metrics from multiple sources every 5 seconds:

- **vLLM GPU Containers** (ports 8000, 8001):
  - Request latency and throughput
  - GPU memory utilization  
  - Model inference metrics
  - Queue lengths and batch sizes

- **FastAPI Backend** (port 9000):
  - HTTP request metrics
  - API endpoint performance
  - Error rates and status codes
  - Custom business metrics

- **Node Exporter** (port 9100):
  - System CPU, memory, disk usage
  - Network interface statistics
  - Filesystem metrics

- **cAdvisor** (port 8080):
  - Container resource usage
  - Memory and CPU consumption per container
  - Container health status

- **DCGM Exporter** (port 9400):
  - GPU utilization and temperature
  - GPU memory usage
  - Power consumption
  - SM (Streaming Multiprocessor) utilization

#### Grafana Dashboards
Grafana (port 3000) provides pre-configured dashboards for:
- **GPU Performance**: Real-time GPU metrics and utilization
- **Container Metrics**: Resource usage across all services  
- **API Performance**: Request rates, latency percentiles, error tracking
- **System Overview**: Host system performance and health

#### Pydantic Logfire Integration
Advanced LLM monitoring capabilities:
- **Request Tracing**: Complete request lifecycle tracking
- **Performance Analytics**: Inference time analysis and optimization insights
- **Error Monitoring**: Detailed error tracking and debugging information
- **Model Performance**: Token generation rates and model efficiency metrics

### Accessing Monitoring

1. **Grafana**: http://localhost:3000 (admin/admin)
2. **Prometheus**: http://localhost:9090  
3. **Logfire Dashboard**: Access via your Pydantic Logfire account
4. **Individual Exporters**: Available on their respective ports

---

## Credits & References

### Documentation & Resources
- **vLLM Documentation**: [https://docs.vllm.ai/](https://docs.vllm.ai/)
- **vLLM GitHub Repository**: [https://github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- **Pydantic Logfire**: [https://logfire.pydantic.dev/](https://logfire.pydantic.dev/)
- **NVIDIA DCGM**: [https://docs.nvidia.com/datacenter/dcgm/](https://docs.nvidia.com/datacenter/dcgm/)

### Model Repositories
- **yasserrmd/Text2SQL-1.5B**: [https://huggingface.co/yasserrmd/Text2SQL-1.5B](https://huggingface.co/yasserrmd/Text2SQL-1.5B)
- **premai-io/prem-1B-SQL**: [https://huggingface.co/premai-io/prem-1B-SQL](https://huggingface.co/premai-io/prem-1B-SQL)

### Docker Images  
- **vLLM GPU Image**: [https://hub.docker.com/repository/docker/hamzaak4/vllm-gpu-image/general](https://hub.docker.com/repository/docker/hamzaak4/vllm-gpu-image/general)
- **FastAPI vLLM Backend**: [https://hub.docker.com/repository/docker/hamzaak4/fastapi-vllm/general](https://hub.docker.com/repository/docker/hamzaak4/fastapi-vllm/general)

### Technology Stack
- **FastAPI**: High-performance Python web framework
- **Prometheus**: Time-series monitoring and alerting
- **Grafana**: Metrics visualization and dashboarding  
- **Docker & Docker Compose**: Containerization and orchestration
- **NVIDIA CUDA**: GPU acceleration framework

---

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests to improve this deployment solution.

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ for efficient LLM serving and GPU optimization*
