import torch

# Check if CUDA (GPU support) is available
print("CUDA available:", torch.cuda.is_available())

# Check the name of your GPU
if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))
