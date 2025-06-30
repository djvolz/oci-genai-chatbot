#!/usr/bin/env python3
"""
Convenience script to run the Streamlit app.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit application."""
    
    # Get the path to the streamlit app
    app_path = os.path.join(
        os.path.dirname(__file__), 
        "src", 
        "oci_genai_chatbot", 
        "streamlit_app.py"
    )
    
    if not os.path.exists(app_path):
        print(f"Error: Streamlit app not found at {app_path}")
        sys.exit(1)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--theme.base", "light"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit app stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()