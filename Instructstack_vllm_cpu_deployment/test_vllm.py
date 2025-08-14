#!/usr/bin/env python3
"""
VLLM CPU Deployment Testing Script
==================================

This script provides comprehensive testing for the VLLM CPU deployment.
It demonstrates both Python-based testing and curl command testing approaches.

Testing Strategy:
1. First, ensure VLLM server is running with a model
2. Test the model using Python vLLM client
3. Test the model using curl commands (recommended for production testing)
4. Test the FastAPI web interface

Usage:
    python test_vllm.py                    # Run all tests
    python test_vllm.py --python-only      # Run only Python tests
    python test_vllm.py --curl-only        # Show only curl commands
"""

import os
import sys
import json
import time
import argparse
import requests
from typing import List, Dict, Any

# Set environment variable for CPU device
os.environ["VLLM_DEVICE"] = "cpu"

def test_vllm_python_client():
    """
    Test VLLM using the Python client directly.
    This is useful for development and debugging.
    """
    print("🧪 Testing VLLM with Python Client")
    print("=" * 50)
    
    try:
        from vllm import LLM, SamplingParams
        
        # Define test prompts
        prompts = [
            "Hello, my name is",
            "The president of the United States is",
            "The capital of France is",
            "The future of AI is",
            "Once upon a time in a galaxy far far away",
        ]
        
        # Configure sampling parameters
        sampling_params = SamplingParams(
            temperature=0.8,
            top_p=0.95,
            max_tokens=50,
            stop=["\n", ".", "!"]
        )
        
        print(f"📝 Testing with {len(prompts)} prompts...")
        print(f"🔧 Sampling params: {sampling_params}")
        
        # Initialize LLM (this will download the model if not present)
        print("🚀 Initializing LLM...")
        llm = LLM(model="facebook/opt-125m")
        
        # Generate responses
        print("⚡ Generating responses...")
        outputs = llm.generate(prompts, sampling_params)
        
        # Display results
        print("\n📊 Results:")
        print("-" * 50)
        for i, output in enumerate(outputs, 1):
            prompt = output.prompt
            generated_text = output.outputs[0].text
            print(f"Test {i}:")
            print(f"  Prompt: {prompt!r}")
            print(f"  Generated: {generated_text!r}")
            print(f"  Tokens: {len(output.outputs[0].token_ids)}")
            print()
        
        print("✅ Python client test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure vLLM is installed: pip install vllm")
        return False
    except Exception as e:
        print(f"❌ Error during Python testing: {e}")
        return False

def test_vllm_api_endpoints():
    """
    Test VLLM API endpoints using HTTP requests.
    This tests the actual deployed VLLM server.
    """
    print("\n🌐 Testing VLLM API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        print("🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"⚠️  Health check returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        print("💡 Make sure VLLM server is running on port 8000")
        return False
    
    # Test completions endpoint
    try:
        print("\n📝 Testing completions endpoint...")
        test_prompt = "The future of artificial intelligence is"
        
        payload = {
            "model": "facebook/opt-125m",
            "prompt": test_prompt,
            "max_tokens": 30,
            "temperature": 0.7,
            "top_p": 0.95
        }
        
        response = requests.post(
            f"{base_url}/v1/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Completions API working")
            print(f"📝 Prompt: {test_prompt}")
            print(f"🤖 Response: {result['choices'][0]['text']}")
        else:
            print(f"❌ Completions API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Completions API test failed: {e}")
        return False
    
    return True

def test_fastapi_interface():
    """
    Test the FastAPI web interface.
    """
    print("\n🌍 Testing FastAPI Web Interface")
    print("=" * 50)
    
    try:
        print("🏠 Testing FastAPI home endpoint...")
        response = requests.get("http://localhost:9000/", timeout=10)
        if response.status_code == 200:
            print("✅ FastAPI web interface accessible")
            print("💡 Open http://localhost:9000 in your browser")
        else:
            print(f"⚠️  FastAPI returned status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ FastAPI test failed: {e}")
        print("💡 Make sure FastAPI server is running on port 9000")
        return False
    
    return True

def show_curl_examples():
    """
    Display comprehensive curl command examples for testing.
    These are the recommended way to test the deployed VLLM server.
    """
    print("\n🔄 CURL Command Examples (Recommended Testing Method)")
    print("=" * 60)
    print("💡 These commands test the ACTUAL deployed VLLM server")
    print("💡 Make sure VLLM server is running first: ./deploy.sh")
    print()
    
    # Health check
    print("🏥 1. Health Check:")
    print("   curl http://localhost:8000/health")
    print()
    
    # Basic completion
    print("📝 2. Basic Text Completion:")
    print("   curl -X POST http://localhost:8000/v1/completions \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{")
    print("       \"model\": \"facebook/opt-125m\",")
    print("       \"prompt\": \"The future of AI is\",")
    print("       \"max_tokens\": 30,")
    print("       \"temperature\": 0.7")
    print("     }'")
    print()
    
    # More complex completion
    print("🚀 3. Advanced Completion with Parameters:")
    print("   curl -X POST http://localhost:8000/v1/completions \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{")
    print("       \"model\": \"facebook/opt-125m\",")
    print("       \"prompt\": \"Once upon a time in a galaxy far far away\",")
    print("       \"max_tokens\": 50,")
    print("       \"temperature\": 0.8,")
    print("       \"top_p\": 0.95,")
    print("       \"stop\": [\"\\n\", \".\"]")
    print("     }'")
    print()
    
    # FastAPI test
    print("🌍 4. Test FastAPI Web Interface:")
    print("   curl http://localhost:9000/")
    print()
    
    # Model info
    print("ℹ️  5. Get Model Information:")
    print("   curl http://localhost:8000/v1/models")
    print()
    
    print("💡 Testing Tips:")
    print("   • Start with health check to ensure server is running")
    print("   • Use basic completion first, then try advanced parameters")
    print("   • Monitor server logs: ./deploy.sh --logs")
    print("   • Check Prometheus metrics: http://localhost:9090")
    print("   • View Grafana dashboards: http://localhost:3000")

def main():
    """
    Main function to run tests based on command line arguments.
    """
    parser = argparse.ArgumentParser(description="Test VLLM CPU Deployment")
    parser.add_argument("--python-only", action="store_true", 
                       help="Run only Python client tests")
    parser.add_argument("--curl-only", action="store_true", 
                       help="Show only curl command examples")
    parser.add_argument("--api-only", action="store_true", 
                       help="Run only API endpoint tests")
    
    args = parser.parse_args()
    
    print("🚀 VLLM CPU Deployment Testing Suite")
    print("=" * 50)
    print("📋 This script tests your VLLM deployment in multiple ways")
    print()
    
    if args.curl_only:
        show_curl_examples()
        return
    
    if args.python_only:
        test_vllm_python_client()
        return
    
    if args.api_only:
        test_vllm_api_endpoints()
        test_fastapi_interface()
        return
    
    # Run all tests
    print("🔄 Running comprehensive test suite...")
    print()
    
    # Test Python client
    python_success = test_vllm_python_client()
    
    # Test API endpoints
    api_success = test_vllm_api_endpoints()
    
    # Test FastAPI interface
    fastapi_success = test_fastapi_interface()
    
    # Show curl examples
    show_curl_examples()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Python Client: {'✅ PASS' if python_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"FastAPI Web:   {'✅ PASS' if fastapi_success else '❌ FAIL'}")
    
    if python_success and api_success and fastapi_success:
        print("\n🎉 All tests passed! Your VLLM deployment is working correctly.")
        print("💡 Use the curl commands above for production testing.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("💡 Make sure all services are running: ./deploy.sh")

if __name__ == "__main__":
    main()
