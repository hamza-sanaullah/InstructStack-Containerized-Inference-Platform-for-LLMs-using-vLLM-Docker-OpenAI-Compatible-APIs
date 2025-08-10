import requests
import time
import logfire
import tiktoken

VLLM_API_URL_TEMPLATE = "http://vllm_server:{port}/v1/completions"
VLLM_MODELS_URL_TEMPLATE = "http://vllm_server:{port}/v1/models"

llm_calls = logfire.metric_counter("llm.calls", unit="1",
                                    description="Total vLLM inference requests")
llm_in = logfire.metric_counter("llm.tokens.input", unit="tokens",
                                description="Input tokens sent to vLLM")
llm_out = logfire.metric_counter("llm.tokens.output", unit="tokens",
                                 description="Output tokens returned from vLLM")
latency_ms = logfire.metric_histogram("llm.latency_ms", unit="ms",
                                      description="vLLM request latency")


def get_tokenizer_for_model(model_name: str):
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def call_vllm(payload: dict) -> str:
    try:
        llm_calls.add(1)
        logfire.info("LLM call starting", model=payload.get("model"), payload_size=len(str(payload)))

        model_name = payload["model"]
        vllm_model_name = f"/models/{model_name}"
        payload["model"] = vllm_model_name

        print(f"Original model: {model_name}")
        print(f"Transformed model: {vllm_model_name}")

        # Select port based on model
        if model_name == "yasserrmd/Text2SQL-1.5B":
            port = 8000
        elif model_name == "premai-io/prem-1B-SQL":
            port = 8001
        else:
            return f"❌ Unknown model: {model_name}"

        # ✅ Check if the correct model is currently served on this port
        try:
            resp = requests.get(VLLM_MODELS_URL_TEMPLATE.format(port=port), timeout=2)
            if not (resp.status_code == 200 and model_name in resp.json()["data"][0]["id"]):
                return f"❌ Model {model_name} is not currently loaded on port {port}"
        except requests.exceptions.RequestException as e:
            return f"❌ Could not connect to vLLM server on port {port}: {str(e)}"

        # Send request if model check passed
        VLLM_API_URL = VLLM_API_URL_TEMPLATE.format(port=port)
        response = requests.post(VLLM_API_URL, json=payload, timeout=60)
        response.raise_for_status()

        latency = response.elapsed.total_seconds() * 1000
        latency_ms.record(latency)

        text = response.json()["choices"][0]["text"].strip()

        encoding = get_tokenizer_for_model(model_name)

        input_tokens = len(encoding.encode(payload.get("prompt", "") or ""))
        output_tokens = len(encoding.encode(text))

        llm_in.add(input_tokens)
        llm_out.add(output_tokens)

        gen_ai_attrs = {
            "gen_ai.request.model": payload["model"],
            "gen_ai.response.model": payload["model"],
            "gen_ai.latency.ms": latency,
            "gen_ai.usage.input_tokens": input_tokens,
            "gen_ai.usage.output_tokens": output_tokens,
            "gen_ai.usage.total_tokens": input_tokens + output_tokens,
        }

        logfire.info("LLM completion", **gen_ai_attrs)
        return text

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
