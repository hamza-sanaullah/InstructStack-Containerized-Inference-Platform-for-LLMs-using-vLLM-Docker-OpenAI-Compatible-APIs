from huggingface_hub import snapshot_download

# Replace with the model you want to download
snapshot_download(
    repo_id="facebook/opt-125m",
    local_dir="models/facebook/opt-125m",
    local_dir_use_symlinks=False
)










