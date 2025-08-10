import docker
import time
import requests
import os

def switch_model(model_name: str) -> bool:
    """Restarts the vLLM container with the specified model."""
    try:
        print(model_name)
        host_models_path = os.environ["HOST_MODEL_PATH"]
        print(host_models_path)

        container_models_path = '/models'
        full_model_path = os.path.join(host_models_path, model_name)
        print(full_model_path)




        client = docker.from_env()

        # 1. Stop and remove existing container
        try:
            container = client.containers.get('vllm_server')
            print("🛑 Stopping existing container...")
            container.stop()
            container.remove()
            time.sleep(2)
        except docker.errors.NotFound:
            print("ℹ️ No existing container found")
            pass

        # 2. Start new container
        print(f"\n🚀 Starting new container with model: {model_name}")
        print("="*50)

        
        container = client.containers.run(
            image="hamzaak4/vllm-cpu-image:Latest1.1",
            name="vllm_server",
            command=[
                "/bin/bash", 
                "-c", 
                f"source /opt/conda/etc/profile.d/conda.sh && "
                f"conda activate vllm_env && "
                f"vllm serve {container_models_path}/{model_name} --device cpu --host 0.0.0.0 --port 8000"
            ],
            volumes={str(host_models_path): {'bind': container_models_path, 'mode': 'ro'}},

            network="vllm-net",
            privileged=True,
            detach=True,
            remove=True
        )


        # 3. Stream logs properly
        print("\n📜 Container logs:")
        print("="*50)
        for chunk in container.logs(stream=True, follow=True):
            # Properly decode and print whole lines
            for line in chunk.decode('utf-8').splitlines():
                print(line)

        # 4. Wait for server readiness
        print("\n⏳ Waiting for server to be ready...")
        start_time = time.time()
        timeout = 90
        while time.time() - start_time < timeout:
            try:
                resp = requests.get("http://vllm_server:8000/v1/models", timeout=2)
                if resp.status_code == 200:
                    print("\n✅ Server is ready!")
                    return True
                time.sleep(1)
            except Exception as e:
                print(f"⏱️ Waiting... ({int(time.time() - start_time)}s/{timeout}s)")
                time.sleep(1)
        
        print("\n❌ Timeout waiting for server")
        return False

    except Exception as e:
        print(f"\n🔥 Model switch failed: {str(e)}")
        return False