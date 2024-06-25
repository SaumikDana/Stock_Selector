import os
import sys

# Determine the path of the parent directory of the current script
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Add the parent directory to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)