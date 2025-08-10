from huggingface_hub import snapshot_download

# Replace with the model you want to download
snapshot_download(
    repo_id="premai-io/prem-1B-SQL",
    local_dir="models/premai-io/prem-1B-SQL",
    local_dir_use_symlinks=False
)


# snapshot_download is used to dowwnload the whole model repository from Hugging Face Hub.
# The `local_dir` specifies where to save the downloaded model files.
# The `local_dir_use_symlinks` parameter is set to False to ensure that files
# are copied rather than symlinked, which is useful for environments where symlinks may not be supported.
# You can replace `repo_id` with the ID of any model you wish to download from the Hugging Face Hub.
# Make sure to have the `huggingface_hub` library installed in your environment.
# You can install it using pip:
# pip install huggingface_hub
# This script is useful for downloading models for use in various machine learning tasks, such as natural
# language processing, computer vision, etc. The downloaded model can then be loaded and used in
# applications that support the Hugging Face Transformers library or similar frameworks.











