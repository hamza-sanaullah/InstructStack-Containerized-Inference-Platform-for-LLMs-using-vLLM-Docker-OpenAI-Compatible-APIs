#!/usr/bin/env python3
"""
Concurrency Test Script for VLLM API

This script tests the concurrent performance of the VLLM API by simulating
multiple users making simultaneous requests. It measures response times
and provides performance statistics.

Usage:
    python concurrency_test.py
    # Or with custom configuration:
    CONCURRENCY=20 REQUESTS_PER_CLIENT=10 python concurrency_test.py
"""

import asyncio
import time
import aiohttp
import random
import os
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Configuration - can be overridden by environment variables
API_URL = os.getenv("VLLM_API_URL", "http://localhost:8000/v1/completions")
MODEL = os.getenv("VLLM_MODEL", "/models/yasserrmd/Text2SQL-1.5B")
CONCURRENCY = int(os.getenv("CONCURRENCY", "10"))  # Number of simulated users
REQUESTS_PER_CLIENT = int(os.getenv("REQUESTS_PER_CLIENT", "5"))  # Requests per user
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))  # Request timeout in seconds
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "128"))  # Maximum tokens in response
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))  # Response temperature

# Shared list of prompts (same schema)
PROMPT_POOL = [
    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nList all employees hired after 2020.\n\n### SQL:\n",

    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nFind employees in department 5 earning more than 100000.\n\n### SQL:\n",

    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nShow employee names and salaries ordered by salary descending.\n\n### SQL:\n",

    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nCount the number of employees in each department.\n\n### SQL:\n",

    "### Database Schema:\nTable: employees\nColumns: id, name, department_id, salary, hire_date\n\n"
    "### Question:\nWhat is the average salary of employees hired after 2015?\n\n### SQL:\n"
]

@dataclass
class RequestResult:
    """Data class to store request results and timing information."""
    user_id: int
    request_id: int
    prompt: str
    start_time: float
    end_time: float
    response_time: float
    success: bool
    error_message: str = ""
    output: str = ""

class ConcurrencyTest:
    """Main class for running concurrency tests."""
    
    def __init__(self):
        self.results: List[RequestResult] = []
        self.start_time = None
        self.end_time = None
    
    async def worker(self, user_id: int, session: aiohttp.ClientSession) -> None:
        """
        Simulate one user making multiple requests.
        
        Args:
            user_id: Unique identifier for the user
            session: HTTP session for making requests
        """
        prompts = random.sample(PROMPT_POOL, REQUESTS_PER_CLIENT)
        
        for i, prompt in enumerate(prompts):
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "stop": [";"]
            }
            
            start_time = time.perf_counter()
            
            try:
                # Add timeout to prevent hanging requests
                timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
                async with session.post(API_URL, json=payload, timeout=timeout) as resp:
                    end_time = time.perf_counter()
                    response_time = end_time - start_time
                    
                    if resp.status == 200:
                        result = await resp.json()
                        output = result['choices'][0]['text'].strip()
                        
                        # Store successful result
                        request_result = RequestResult(
                            user_id=user_id,
                            request_id=i+1,
                            prompt=prompt,
                            start_time=start_time,
                            end_time=end_time,
                            response_time=response_time,
                            success=True,
                            output=output
                        )
                        self.results.append(request_result)
                        
                        print(f"[User {user_id:2d}][Req {i+1:2d}] {response_time:.3f}s ✓ {output[:50]}{'...' if len(output) > 50 else ''}")
                    else:
                        # Handle HTTP error
                        error_msg = f"HTTP {resp.status}: {await resp.text()}"
                        request_result = RequestResult(
                            user_id=user_id,
                            request_id=i+1,
                            prompt=prompt,
                            start_time=start_time,
                            end_time=time.perf_counter(),
                            response_time=time.perf_counter() - start_time,
                            success=False,
                            error_message=error_msg
                        )
                        self.results.append(request_result)
                        print(f"[User {user_id:2d}][Req {i+1:2d}] ERROR: {error_msg}")
                        
            except asyncio.TimeoutError:
                # Handle timeout
                end_time = time.perf_counter()
                request_result = RequestResult(
                    user_id=user_id,
                    request_id=i+1,
                    prompt=prompt,
                    start_time=start_time,
                    end_time=end_time,
                    response_time=end_time - start_time,
                    success=False,
                    error_message="Request timeout"
                )
                self.results.append(request_result)
                print(f"[User {user_id:2d}][Req {i+1:2d}] TIMEOUT after {REQUEST_TIMEOUT}s")
                
            except Exception as e:
                # Handle other exceptions
                end_time = time.perf_counter()
                request_result = RequestResult(
                    user_id=user_id,
                    request_id=i+1,
                    prompt=prompt,
                    start_time=start_time,
                    end_time=end_time,
                    response_time=end_time - start_time,
                    success=False,
                    error_message=str(e)
                )
                self.results.append(request_result)
                print(f"[User {user_id:2d}][Req {i+1:2d}] ERROR: {e}")
    
    def print_summary(self) -> None:
        """Print summary statistics of the test run."""
        if not self.results:
            print("No results to summarize.")
            return
        
        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r.success)
        failed_requests = total_requests - successful_requests
        
        if successful_requests > 0:
            response_times = [r.response_time for r in self.results if r.success]
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print("\n" + "="*60)
            print("CONCURRENCY TEST SUMMARY")
            print("="*60)
            print(f"Test Configuration:")
            print(f"  API URL: {API_URL}")
            print(f"  Model: {MODEL}")
            print(f"  Concurrency: {CONCURRENCY} users")
            print(f"  Requests per user: {REQUESTS_PER_CLIENT}")
            print(f"  Total expected requests: {CONCURRENCY * REQUESTS_PER_CLIENT}")
            print(f"  Request timeout: {REQUEST_TIMEOUT}s")
            print(f"  Max tokens: {MAX_TOKENS}")
            print(f"  Temperature: {TEMPERATURE}")
            
            print(f"\nResults:")
            print(f"  Total requests: {total_requests}")
            print(f"  Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
            print(f"  Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
            
            if successful_requests > 0:
                print(f"\nResponse Time Statistics (successful requests):")
                print(f"  Average: {avg_response_time:.3f}s")
                print(f"  Minimum: {min_response_time:.3f}s")
                print(f"  Maximum: {max_response_time:.3f}s")
                
                # Calculate throughput
                total_time = self.end_time - self.start_time if self.start_time and self.end_time else 0
                if total_time > 0:
                    throughput = successful_requests / total_time
                    print(f"  Throughput: {throughput:.2f} requests/second")
        
        if failed_requests > 0:
            print(f"\nError Summary:")
            error_counts = {}
            for result in self.results:
                if not result.success:
                    error_type = result.error_message.split(':')[0] if ':' in result.error_message else result.error_message
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            for error_type, count in error_counts.items():
                print(f"  {error_type}: {count} occurrences")
    
    async def run_test(self) -> None:
        """Run the main concurrency test."""
        print(f"Starting concurrency test...")
        print(f"Configuration: {CONCURRENCY} users, {REQUESTS_PER_CLIENT} requests per user")
        print(f"API Endpoint: {API_URL}")
        print(f"Model: {MODEL}")
        print("-" * 60)
        
        self.start_time = time.perf_counter()
        
        # Configure client session with connection pooling
        connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2, limit_per_host=CONCURRENCY)
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [
                asyncio.create_task(self.worker(user_id + 1, session))
                for user_id in range(CONCURRENCY)
            ]
            await asyncio.gather(*tasks)
        
        self.end_time = time.perf_counter()
        
        print("-" * 60)
        self.print_summary()

async def main():
    """Main entry point for the concurrency test."""
    try:
        test = ConcurrencyTest()
        await test.run_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
