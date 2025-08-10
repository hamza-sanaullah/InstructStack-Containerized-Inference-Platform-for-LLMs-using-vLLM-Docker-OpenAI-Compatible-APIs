# vLLM CPU-Based Deployment with Multi-Model Setup

A production-ready deployment of vLLM on CPU infrastructure with FastAPI web interface and comprehensive monitoring stack.

## 📖 Introduction & Goal

**vLLM** is a high-throughput serving framework for large language models that uses:
- **KV Cache Optimization**: PagedAttention algorithm for efficient memory management
- **Memory-Efficient Serving**: Advanced memory techniques for resource optimization
- **Attention Optimization**: Reduced inference latency through optimized computations

**🎯 Project Goal**: Deploy vLLM on **CPU-only infrastructure** for **learning and experimentation purposes**.

### Why CPU-Based Deployment?
> **⚠️ Note**: CPU deployment is **NOT recommended for production** due to significantly slower inference speeds compared to GPU. This project is designed for:

- **Learning Experience**: Understanding vLLM deployment without expensive GPU hardware
- **Development/Testing**: Prototyping and testing model serving concepts
- **Educational Purpose**: Exploring containerization and orchestration concepts
- **Resource Constraints**: Working with limited hardware for educational projects

## 🏗️ Architecture Overview

![CPU-Based vLLM Architecture](CPU-Based-VLLM%20-Architecture.png)

*Complete system architecture showing the multi-container deployment with vLLM, FastAPI, and monitoring stack*

## 🤖 Models Selected for CPU Deployment

### Why These Models?
Selected **lightweight models** specifically for efficient CPU inference:

| Model | Parameters | Why CPU-Friendly |
|-------|------------|------------------|
| `facebook/opt-125m` | 125M | Small footprint, optimized for text generation |
| `sshleifer/tiny-gpt2` | Minimal | Lightweight variant, perfect for testing/development |

**Deployment Strategy**: Each model runs in a **separate vLLM container** on different ports, enabling independent scaling and resource management.

## 🚀 Deployment Journey: Local → Docker → Production

### Step 1: Local Setup ✅
- Created Python 3.11 virtual environment
- Built vLLM from source with CPU optimizations
- Tested models locally with `vllm serve` command
- Configured CPU-specific environment variables

### Step 2: Docker Implementation ✅
1. **Dockerfile Creation**: Multi-stage build with Miniconda base
2. **Error Resolution**: Fixed GCC/libstdc++ compatibility issues during container build
3. **Environment Variables**: Set critical vLLM CPU settings (see `Dockerfile`)
4. **Image Creation**: Built and tested Docker images locally

### Step 3: Container Deployment ✅
- **Container Execution**: Ran vLLM inside containers with proper port mapping
- **Multi-Model Setup**: Configured separate containers for each model
- **Docker Hub**: Published images as `hamzaak4/vllm-cpu-image:Latest1.1`

### FastAPI Integration Role 🔄
**FastAPI serves as a request proxy/interface:**
- Receives user requests via web UI (`templates/index.html`)
- Forwards requests to vLLM server endpoints
- Provides clean API abstraction layer
- Handles model switching between containers
- **Files**: `Fastapi_vllm_web/app/` contains the web interface and API routing

## 📁 Project Files & Structure

### Key Files Explained

#### **Root Directory**
- **`Dockerfile`** - Main container definition for vLLM CPU deployment. Contains all dependencies, environment setup, and vLLM compilation from source with CPU optimizations.
- **`docker-compose.yml`** - Orchestrates the entire multi-service stack (vLLM, FastAPI, Prometheus, Grafana, cAdvisor). Defines networks, volumes, and service dependencies.
- **`environment.yml`** - Conda environment specification with Python 3.11 and required packages for vLLM CPU build.
- **`test_vllm.py`** - Testing script to validate vLLM inference functionality and API endpoints after deployment.
- **`download_model.py`** - Utility script to download and prepare models for local storage before containerization.

#### **Fastapi_vllm_web/** - Web Interface Layer
- **`app/main.py`** - FastAPI application entry point. Sets up CORS, static files, templates, and includes API routes.
- **`app/api/routes.py`** - API endpoint definitions that proxy requests to vLLM containers and handle model switching.
- **`app/templates/index.html`** - Web UI for interacting with the models through a browser interface.
- **`app/services/vllm_client.py`** - Service layer for communicating with vLLM containers and managing requests.
- **`app/switch_model.py`** - Utility for dynamically switching between different model containers.
- **`Dockerfile`** - Lightweight FastAPI container build with Python 3.11-slim base.
- **`requirements.txt`** - Python dependencies for FastAPI, including uvicorn, requests, jinja2, and prometheus instrumentation.

#### **models/** - Model Storage
- **`facebook/opt-125m/`** - Contains the downloaded Facebook OPT-125M model files (config.json, pytorch_model.bin, tokenizer files).
- **`sshleifer/tiny-gpt2/`** - Contains the downloaded Tiny GPT-2 model files for testing and development.

#### **prometheus/** - Monitoring Configuration  
- **`prometheus.yml`** - Prometheus scraping configuration defining targets for all services (FastAPI, vLLM, Node Exporter, cAdvisor).

### Docker Images
- **vLLM**: `hamzaak4/vllm-cpu-image:Latest1.1`
- **FastAPI**: `hamzaak4/fastapi_vllm_cpu:Latest`

## 🏃‍♂️ Running the System

> **⚠️ Ubuntu/Linux Required**: This setup is optimized for **Ubuntu or other Linux distributions**. Windows users should use WSL2.

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM
- Ubuntu 20.04+ (recommended)

### 🚀 Quick Start (Recommended)
**Simple one-command deployment** - Docker Compose will automatically pull images and start all containers:

```bash
# Just run this - it handles everything automatically
docker-compose up -d

# Verify all services are running
docker-compose ps
```
> **Note**: First run will take time as it downloads images (~2-3GB total)

### 🔄 Pre-pull Images (Optional)
If you want to download images beforehand:

```bash
# Pull vLLM CPU image
docker pull hamzaak4/vllm-cpu-image:Latest1.1

# Pull FastAPI image  
docker pull hamzaak4/fastapi_vllm_cpu:Latest

# Then start the stack
docker-compose up -d
```

### 🔧 Running Individual Containers (Manual Setup)

#### Run vLLM Container Only
```bash
# Start vLLM container with interactive shell
docker run -it --rm --privileged --name vllm_server \
  -p 8000:8000 \
  -v $(pwd)/models:/models \
  hamzaak4/vllm-cpu-image:Latest1.1 /bin/bash

# Inside the container:
conda activate vllm_env

# Serve model (if models are in /models directory)
vllm serve /models/facebook/opt-125m --device cpu --host 0.0.0.0 --port 8000 --dtype float32 --enforce-eager
```

#### Run FastAPI Container Only
```bash
# Start FastAPI container with interactive shell
docker run -it --rm --name fastapi_server \
  -p 9000:9000 \
  -v $(pwd)/models:/models \
  hamzaak4/fastapi_vllm_cpu:Latest /bin/bash

# Inside the container:
cd /FASTAPI/app
uvicorn main:app --host 0.0.0.0 --port 9000
```

### 🌐 Service Endpoints
| Service | Port | Description |
|---------|------|-------------|
| vLLM API | 8000 | Model inference |
| FastAPI Web | 9000 | Web interface |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Monitoring dashboard |

### 📡 vLLM Model Serving Commands
These commands are used to serve models with vLLM:

```bash
# Facebook OPT-125M
vllm serve facebook/opt-125m --device cpu --port 8000 --dtype float32 --enforce-eager

# Tiny GPT-2
vllm serve sshleifer/tiny-gpt2 --device cpu --port 8000 --dtype float32 --enforce-eager

# Custom model from local directory
vllm serve ./models/your-model-name --device cpu --host 0.0.0.0 --port 8000
```

## 📊 Monitoring Stack

**Comprehensive monitoring** via `docker-compose.yml`:
- **Prometheus**: Metrics collection (5s intervals)
- **Grafana**: Visualization dashboards 
- **Node Exporter**: System metrics
- **cAdvisor**: Container resource monitoring

**Configuration**: `prometheus/prometheus.yml` defines scraping targets for all services.

## 🧪 Testing the Deployment

### API Testing with cURL
```bash
# Test vLLM API directly
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/opt-125m", 
    "prompt": "Once upon a time", 
    "max_tokens": 20,
    "temperature": 0.7
  }'

# Test FastAPI web interface
curl http://localhost:9000/

# Health check
curl http://localhost:8000/health

# Test with different model
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sshleifer/tiny-gpt2", 
    "prompt": "The future of AI is", 
    "max_tokens": 30
  }'
```

### Comprehensive Testing
```bash
# Use the provided test script
python test_vllm.py
```

## 🛠️ Troubleshooting

### Common Issues & Solutions
```bash
# Check logs
docker-compose logs vllm
docker-compose logs fastapi_app

# Verify services
docker-compose ps

# Container access
docker exec -it vllm_server bash
```

**Memory Issues**: Increase Docker memory allocation (minimum 4GB)
**Port Conflicts**: Ensure ports 8000, 9000, 9090, 3000 are available

## 📚 References

### Documentation
- [vLLM Official Documentation](https://docs.vllm.ai/)
- [vLLM CPU Installation Guide](https://docs.vllm.ai/en/stable/getting_started/installation/cpu.html)

### Models
- [Facebook OPT-125M](https://huggingface.co/facebook/opt-125m)
- [Tiny GPT-2](https://huggingface.co/sshleifer/tiny-gpt2)

### Docker Images
- [vLLM CPU Image](https://hub.docker.com/repository/docker/hamzaak4/vllm-cpu-image/general) - `hamzaak4/vllm-cpu-image:Latest1.1`
- [FastAPI Image](https://hub.docker.com/repository/docker/hamzaak4/fastapi_vllm_cpu/general) - `hamzaak4/fastapi_vllm_cpu:Latest`

---

*CPU-optimized vLLM deployment for accessible AI inference*
