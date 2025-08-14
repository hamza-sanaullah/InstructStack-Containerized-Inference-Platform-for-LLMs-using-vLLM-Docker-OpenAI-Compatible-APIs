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
- **`deploy.sh`** - **Automated deployment script** that handles the complete setup process including prerequisites, environment setup, model downloads, and service deployment.
- **`env-template.txt`** - Environment variables template file for easy configuration.
- **`environment.yml`** - Conda environment specification with Python 3.11 and required packages for vLLM CPU build.
- **`test_vllm.py`** - **Comprehensive testing script** that validates VLLM inference functionality, API endpoints, and provides curl command examples for production testing.
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

### Environment Configuration

The deployment supports comprehensive environment variable configuration. You have **two ways** to configure your deployment:

#### **Option 1: Using .env file (Recommended)**
1. **Copy the environment template**:
   ```bash
   cp env-template.txt .env
   ```

2. **Edit the `.env` file** with your preferred values:
   - Model configuration (DEFAULT_MODEL, etc.)
   - Service ports (VLLM_PORT, FASTAPI_PORT, etc.)
   - Container naming (optional)
   - Logfire token for logging
   - Model download settings

#### **Option 2: Direct Docker Compose editing**
You can also edit the `docker-compose.yml` file directly and modify the default values in the configuration section.

#### **Key Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_MODEL` | `facebook/opt-125m` | Model to load |
| `VLLM_PORT` | `8000` | VLLM server port |
| `FASTAPI_PORT` | `9000` | FastAPI web interface port |
| `PROMETHEUS_PORT` | `9090` | Prometheus metrics port |
| `GRAFANA_PORT` | `3000` | Grafana dashboard port |
| `NODE_EXPORTER_PORT` | `9100` | Node Exporter port |
| `CADVISOR_PORT` | `8081` | cAdvisor monitoring port |
| `LOGFIRE_TOKEN` | `your_logfire_token_here` | Your Logfire serve key |
| `MODEL_REPO_ID` | `sshleifer/tiny-gpt2` | Model to download |

#### **Download Models:**
```bash
# Download single model
python download_model.py

# Download multiple models
export MODELS_TO_DOWNLOAD="model1,model2,model3"
python download_model.py
```

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM
- Ubuntu 20.04+ (recommended)

### 🚀 Quick Start (Recommended)

#### **Option 1: Using deploy.sh script (Easiest)**
The easiest way to deploy is using the provided deployment script:

```bash
# Make the script executable (first time only)
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

> **🚀 One-Command Deployment**: Just run `./deploy.sh` and the script will handle everything automatically!

This script will:
- ✅ Check prerequisites (Docker, Docker Compose)
- ✅ Set up environment configuration
- ✅ Create necessary directories
- ✅ Download models if needed
- ✅ Start all services
- ✅ Run health checks
- ✅ Show service URLs and management commands

#### **Option 2: Manual Docker Compose**
Traditional Docker Compose deployment:

```bash
# Start all services
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

### 🛠️ Deploy.sh Script Features

The `deploy.sh` script provides comprehensive deployment automation with these features:

#### **Available Commands:**
```bash
./deploy.sh              # Full deployment (default)
./deploy.sh --start      # Start services only
./deploy.sh --stop       # Stop services only
./deploy.sh --restart    # Restart services
./deploy.sh --logs       # Show service logs
./deploy.sh --clean      # Clean up everything
./deploy.sh --help       # Show help
```

#### **What the Script Does:**
- 🔍 **Prerequisites Check**: Verifies Docker and Docker Compose installation
- ⚙️ **Environment Setup**: Creates `.env` file from template if needed
- 📁 **Directory Creation**: Sets up models, prometheus, and logs directories
- 🤖 **Model Management**: Offers to download models if not present
- 🚀 **Service Deployment**: Starts all services with proper sequencing
- ✅ **Health Checks**: Verifies services are running correctly
- 📊 **Status Display**: Shows all service URLs and management commands
- 📝 **Log Access**: Option to view real-time service logs

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
| Service | Port | Description | Environment Variable |
|---------|------|-------------|---------------------|
| vLLM API | 8000 | Model inference | `VLLM_PORT` |
| FastAPI Web | 9000 | Web interface | `FASTAPI_PORT` |
| Prometheus | 9090 | Metrics collection | `PROMETHEUS_PORT` |
| Grafana | 3000 | Monitoring dashboard | `GRAFANA_PORT` |
| Node Exporter | 9100 | System metrics | `NODE_EXPORTER_PORT` |
| cAdvisor | 8081 | Container monitoring | `CADVISOR_PORT` |

> **Note**: All ports are configurable via environment variables. Default values shown above.

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

### 🎯 Testing Strategy

**The correct way to test your VLLM deployment:**

1. **First**: Ensure VLLM server is running with a model (`./deploy.sh`)
2. **Then**: Test the model using curl commands (recommended for production)
3. **Finally**: Use Python testing for development and debugging

### 🚀 Quick Testing with cURL (Recommended)

**Start with these essential tests:**

#### **1. Health Check**
```bash
curl http://localhost:8000/health
```

#### **2. Basic Text Completion**
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/opt-125m", 
    "prompt": "The future of AI is", 
    "max_tokens": 30,
    "temperature": 0.7
  }'
```

#### **3. Advanced Completion with Parameters**
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "facebook/opt-125m", 
    "prompt": "Once upon a time in a galaxy far far away", 
    "max_tokens": 50,
    "temperature": 0.8,
    "top_p": 0.95,
    "stop": ["\n", "."]
  }'
```

#### **4. Test FastAPI Web Interface**
```bash
curl http://localhost:9000/
```

### 🧪 Comprehensive Testing Suite

**Use the enhanced test script for thorough testing:**

```bash
# Run all tests
python test_vllm.py

# Show only curl commands
python test_vllm.py --curl-only

# Run only Python client tests
python test_vllm.py --python-only

# Run only API endpoint tests
python test_vllm.py --api-only
```

### 💡 Why cURL Commands Are Better for Production Testing

- ✅ **Test the actual deployed server** (not local Python client)
- ✅ **Verify HTTP endpoints** are working correctly
- ✅ **Check network connectivity** and port accessibility
- ✅ **Test real-world usage** scenarios
- ✅ **Easy to automate** in CI/CD pipelines
- ✅ **No Python dependencies** required on target machine

### 🔍 Testing Checklist

Before running tests, ensure:
- [ ] VLLM server is running (`./deploy.sh`)
- [ ] Model is loaded and accessible
- [ ] Ports 8000 and 9000 are accessible
- [ ] No firewall blocking the connections

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

> **💡 Tip**: Use `./deploy.sh --logs` to view real-time logs or `./deploy.sh --clean` to completely reset the deployment if you encounter issues.

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
