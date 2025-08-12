import os
from huggingface_hub import snapshot_download

# Model configuration using environment variables with defaults
MODEL_REPO_ID = os.getenv("MODEL_REPO_ID", "premai-io/prem-1B-SQL")
MODEL_LOCAL_DIR = os.getenv("MODEL_LOCAL_DIR", "models/premai-io/prem-1B-SQL")
USE_SYMLINKS = os.getenv("MODEL_USE_SYMLINKS", "False").lower() == "true"

def download_model():
    """Download model from Hugging Face Hub using environment variables"""
    print(f"Downloading model: {MODEL_REPO_ID}")
    print(f"Local directory: {MODEL_LOCAL_DIR}")
    print(f"Use symlinks: {USE_SYMLINKS}")
    
    try:
        snapshot_download(
            repo_id=MODEL_REPO_ID,
            local_dir=MODEL_LOCAL_DIR,
            local_dir_use_symlinks=USE_SYMLINKS
        )
        print(f"✅ Successfully downloaded {MODEL_REPO_ID} to {MODEL_LOCAL_DIR}")
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False
    
    return True

def download_multiple_models():
    """Download multiple models if specified"""
    models = os.getenv("MODELS_TO_DOWNLOAD", "").strip()
    
    if not models:
        # Download single model
        return download_model()
    
    # Download multiple models
    model_list = [model.strip() for model in models.split(",")]
    success_count = 0
    
    for model in model_list:
        if model:
            # Set environment variable for this model
            os.environ["MODEL_REPO_ID"] = model
            os.environ["MODEL_LOCAL_DIR"] = f"models/{model.replace('/', '/')}"
            
            if download_model():
                success_count += 1
    
    print(f"\n📊 Download Summary: {success_count}/{len(model_list)} models downloaded successfully")
    return success_count == len(model_list)

if __name__ == "__main__":
    print("🚀 Starting model download process...")
    print("=" * 50)
    
    # Check if downloading multiple models or single model
    if os.getenv("MODELS_TO_DOWNLOAD"):
        success = download_multiple_models()
    else:
        success = download_model()
    
    if success:
        print("\n🎉 All downloads completed successfully!")
    else:
        print("\n⚠️  Some downloads failed. Check the error messages above.")
        exit(1)











