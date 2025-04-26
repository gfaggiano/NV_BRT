import os
import json
from pathlib import Path

# Define the source directory
src_dir = Path(os.getenv('PROGRAMDATA')) / "NVIDIA Corporation" / "Drs"

# Define the configuration dictionary
config = {
    "src_dir": str(src_dir)
}

# Write the configuration to a JSON file
config_file = "config.json"
with open(config_file, "w") as f:
    json.dump(config, f, indent=4)

print(f"Configuration file created: {config_file}")