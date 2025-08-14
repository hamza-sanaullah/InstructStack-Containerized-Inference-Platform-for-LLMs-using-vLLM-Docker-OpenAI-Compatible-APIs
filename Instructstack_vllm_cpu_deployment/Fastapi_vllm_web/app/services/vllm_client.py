"""
vLLM Client Service

This module provides the interface for communicating with the vLLM inference server.
It handles model validation, API requests, and response processing for text generation.

Author: AI Assistant
Version: 1.0.0
"""

import requests
import time
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
MODEL_PORT_MAPPING = {
    "facebook/opt-125m": 8000,
    "sshleifer/tiny-gpt2": 8001
}

REQUEST_TIMEOUT = 60  # seconds
MODEL_CHECK_TIMEOUT = 5  # seconds


def call_vllm(payload: Dict[str, any]) -> str:
    """
    Generate text using the vLLM inference server.
    
    This function handles the complete flow of:
    1. Model validation and port selection
    2. Current model verification
    3. Text generation request
    4. Response processing and error handling
    
    Args:
        payload (Dict[str, any]): Request payload containing:
            - model: The model identifier
            - prompt: Input text for generation
            - max_tokens: Maximum tokens to generate
            
    Returns:
        str: Generated text or error message prefixed with "❌"
        
    Raises:
        requests.exceptions.RequestException: For network/HTTP errors
        Exception: For unexpected errors during processing
    """
    try:
        # Extract and validate model name
        model_name = payload.get("model")
        if not model_name:
            return "❌ No model specified in payload"
        
        # Determine port based on model
        port = MODEL_PORT_MAPPING.get(model_name)
        if port is None:
            return f"❌ Unknown model: {model_name}. Supported models: {list(MODEL_PORT_MAPPING.keys())}"
        
        # Transform model name to vLLM's expected format
        vllm_model_name = f"/models/{model_name}"
        payload["model"] = vllm_model_name
        
        logger.info(f"Processing request - Original model: {model_name}, Port: {port}")
        logger.info(f"Transformed model path: {vllm_model_name}")
        
        # Step 1: Verify current model served on the specified port
        if not _verify_current_model(port, model_name):
            return f"❌ Wrong model served on port {port}. Please restart the server with the correct model."
        
        # Step 2: Send text generation request
        return _generate_text(port, payload)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"


def _verify_current_model(port: int, expected_model: str) -> bool:
    """
    Verify that the expected model is currently served on the specified port.
    
    Args:
        port (int): Port number to check
        expected_model (str): Expected model name
        
    Returns:
        bool: True if correct model is served, False otherwise
    """
    try:
        models_url = f"http://vllm_server:{port}/v1/models"
        logger.info(f"Checking models endpoint: {models_url}")
        
        response = requests.get(models_url, timeout=MODEL_CHECK_TIMEOUT)
        
        if response.status_code == 200:
            model_data = response.json()
            if model_data.get("data") and len(model_data["data"]) > 0:
                current_model = model_data["data"][0]["id"].split("/")[-1]
                expected_model_name = expected_model.split("/")[-1]
                
                logger.info(f"Current model on port {port}: {current_model}")
                logger.info(f"Expected model: {expected_model_name}")
                
                return current_model == expected_model_name
            else:
                logger.warning(f"No model data found in response from port {port}")
                return False
        else:
            logger.error(f"Failed to get models from port {port}. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed while checking model on port {port}: {str(e)}")
        return False


def _generate_text(port: int, payload: Dict[str, any]) -> str:
    """
    Send text generation request to the vLLM server.
    
    Args:
        port (int): Port number for the vLLM server
        payload (Dict[str, any]): Generation request payload
        
    Returns:
        str: Generated text or error message
    """
    try:
        api_url = f"http://vllm_server:{port}/v1/completions"
        logger.info(f"Sending generation request to: {api_url}")
        logger.info(f"Payload: {payload}")
        
        response = requests.post(api_url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Extract generated text from response
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            generated_text = response_data["choices"][0]["text"].strip()
            logger.info(f"Successfully generated text with {len(generated_text)} characters")
            return generated_text
        else:
            error_msg = "No choices found in response"
            logger.error(error_msg)
            return f"❌ {error_msg}"
            
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {REQUEST_TIMEOUT} seconds"
        logger.error(error_msg)
        return f"❌ {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ {error_msg}"
