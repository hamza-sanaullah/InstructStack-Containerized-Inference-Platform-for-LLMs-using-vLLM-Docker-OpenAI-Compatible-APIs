"""
API Routes for vLLM AI Assistant

This module contains the main UI routes for the vLLM AI Assistant web application.
It handles the home page display and AI text generation requests.

Author: AI Assistant
Version: 1.0.0
"""

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from vllm.config import VLLM_API_URL, AVAILABLE_MODELS
from services.vllm_client import call_vllm

# Initialize router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with model selection and prompt input form.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered home page template
    """
    try:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "models": AVAILABLE_MODELS,
            "response": None,
            "selected_model": None,
            "prompt": "",
            "max_tokens": 50
        })
    except Exception as e:
        # Log the error in production
        print(f"Error rendering home page: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    model: str = Form(..., description="The AI model to use for text generation"),
    prompt: str = Form(..., description="The input prompt for text generation"),
    max_tokens: int = Form(50, description="Maximum number of tokens to generate")
):
    """
    Generate AI text response based on the provided prompt and model.
    
    Args:
        request (Request): FastAPI request object
        model (str): The AI model to use for generation
        prompt (str): The input prompt for text generation
        max_tokens (int): Maximum number of tokens to generate (1-512)
        
    Returns:
        HTMLResponse: Rendered template with the generated response
        
    Raises:
        HTTPException: If validation fails or generation errors occur
    """
    try:
        # Input validation
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if max_tokens < 1 or max_tokens > 512:
            raise HTTPException(status_code=400, detail="Max tokens must be between 1 and 512")
        
        if model not in AVAILABLE_MODELS:
            raise HTTPException(status_code=400, detail="Invalid model selection")
        
        # Prepare payload for vLLM service
        payload = {
            "model": model,
            "prompt": prompt.strip(),
            "max_tokens": max_tokens
        }
        
        # Call vLLM service for text generation
        result = call_vllm(payload)
        
        # Check if generation was successful
        if result.startswith("❌"):
            # Handle error responses from vLLM service
            return templates.TemplateResponse("index.html", {
                "request": request,
                "models": AVAILABLE_MODELS,
                "response": f"Error: {result}",
                "selected_model": model,
                "prompt": prompt,
                "max_tokens": max_tokens
            })
        
        # Return successful response
        return templates.TemplateResponse("index.html", {
            "request": request,
            "models": AVAILABLE_MODELS,
            "response": result,
            "selected_model": model,
            "prompt": prompt,
            "max_tokens": max_tokens
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors in production
        print(f"Unexpected error in generate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during text generation")
