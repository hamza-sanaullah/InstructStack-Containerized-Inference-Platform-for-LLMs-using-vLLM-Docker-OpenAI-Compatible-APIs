import asyncio
import time
import aiohttp
import random

API_URL = "http://localhost:8000/v1/completions"
MODEL = "/models/yasserrmd/Text2SQL-1.5B"
CONCURRENCY = 10  # Number of simulated users
REQUESTS_PER_CLIENT = 5  # Requests per user

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

# One worker simulates one user
async def worker(user_id, session):
    prompts = random.sample(PROMPT_POOL, REQUESTS_PER_CLIENT)
    for i, prompt in enumerate(prompts):
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "max_tokens": 128,
            "temperature": 0.3,
            "stop": [";"]
        }
        start = time.perf_counter()
        print(start)
        try:
            async with session.post(API_URL, json=payload) as resp:
                delta = time.perf_counter() - start
                result = await resp.json()
                output = result['choices'][0]['text'].strip()
                print(f"[User {user_id}][Req {i+1}] {delta:.2f}s → {output}")
        except Exception as e:
            print(f"[User {user_id}][Req {i+1}] ERROR: {e}")

# Launch all workers concurrently
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(worker(user_id+1, session))
            for user_id in range(CONCURRENCY)
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
