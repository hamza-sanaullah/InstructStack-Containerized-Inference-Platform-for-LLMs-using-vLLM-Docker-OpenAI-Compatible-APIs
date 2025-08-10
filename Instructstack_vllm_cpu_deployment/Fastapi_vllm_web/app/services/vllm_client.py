import requests
import time

def call_vllm(payload: dict) -> str:
    try:
        # Get original model name from payload
        model_name = payload["model"]

        # Decide port based on model
        if model_name == "facebook/opt-125m":
            port = 8000
        elif model_name == "sshleifer/tiny-gpt2":
            port = 8001
        else:
            return f"❌ Unknown model: {model_name}"

        # Transform to vLLM's expected format
        vllm_model_name = f"/models/{model_name}"
        payload["model"] = vllm_model_name

        print(f"Original model: {model_name}")
        print(f"Transformed model: {vllm_model_name}")
        print(f"Using port: {port}")

        # 1. Check current model served on that port
        try:
            resp = requests.get(f"http://vllm_server:{port}/v1/models", timeout=5)
            if resp.status_code == 200:
                current_model = resp.json()["data"][0]["id"].split("/")[-1]
                print(f"Current model: {current_model}")
                if current_model != model_name.split("/")[-1]:
                    return f"❌ Wrong model served on port {port}"
            else:
                return f"❌ Failed to get models from port {port}"
        except requests.exceptions.RequestException as e:
            return f"Request failed while checking model: {str(e)}"

        # 2. Send generation request
        VLLM_API_URL = f"http://vllm_server:{port}/v1/completions"
        response = requests.post(VLLM_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip()

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
