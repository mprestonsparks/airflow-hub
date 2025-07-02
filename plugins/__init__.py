# Ensure plugins directory is in Python path
import sys
import os

# Add plugins directory to Python path
plugins_dir = os.path.dirname(os.path.abspath(__file__))
if plugins_dir not in sys.path:
    sys.path.insert(0, plugins_dir)