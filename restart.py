import os
import shutil
import subprocess

def restart_app():
    # Clear Streamlit cache directory
    cache_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("✓ Cleared Streamlit cache")
    
    # Create fresh cache directory
    os.makedirs(cache_dir, exist_ok=True)
    print("✓ Created fresh cache directory")
    
    # Start Streamlit
    print("Starting Streamlit app...")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    restart_app()
