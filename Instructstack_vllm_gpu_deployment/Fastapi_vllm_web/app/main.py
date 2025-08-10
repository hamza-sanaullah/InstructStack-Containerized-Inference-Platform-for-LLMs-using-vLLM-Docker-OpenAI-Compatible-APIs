from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from api.routes import router as ui_router
from prometheus_fastapi_instrumentator import Instrumentator
import logfire
import os


app = FastAPI()
Instrumentator().instrument(app).expose(app)



logfire.configure(
    service_name="llm-fastapi",        # override default name
    environment=os.getenv("ENVIRONMENT", "production"),
    # you can also pass things like service_version, if needed
)

# AUTO-INSTRUMENT your FastAPI HTTP handlers
logfire.instrument_fastapi(app)
logfire.instrument_requests()
# If your FastAPI app makes outgoing HTTPX calls (e.g. talking to vLLM),
# this captures those too, including bodies when `capture_all=True`
logfire.instrument_httpx(capture_all=True)

# (Optional) instrument your Pydantic models or LLM client if needed:
logfire.instrument_pydantic(record="failure")

# or for OpenAI / Pydantic‑AI:
# logfire.instrument_openai()
# logfire.instrument_pydantic_ai()




# Middleware (for potential frontend extensions)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routes
app.include_router(ui_router)
