import importlib
import sys

required_packages = [
    ('python-dotenv', 'dotenv'),  # Package name, Import name
    'streamlit',
    'pandas',
    'requests',
    'folium',
    'streamlit_folium',
    'pydantic',
    'cachetools',
    'tenacity',
    'retry',
    'langchain',
    'langchain_community',
    'openai',
    'tiktoken',
    'chromadb',
    'sentence_transformers',
    'transformers',
    'hnswlib'
]

def check_installations():
    missing = []
    for package in required_packages:
        try:
            if isinstance(package, tuple):
                pkg_name, import_name = package
                module = importlib.import_module(import_name)
            else:
                module = importlib.import_module(package)
            print(f"✓ {package} is installed")
        except ImportError:
            pkg_name = package[0] if isinstance(package, tuple) else package
            missing.append(pkg_name)
            print(f"✗ {pkg_name} is NOT installed")
    
    return missing

if __name__ == "__main__":
    print("Checking package installations...")
    missing = check_installations()
    
    if missing:
        print("\nMissing packages. Install them using:")
        print(f"pip install {' '.join(missing)}")
    else:
        print("\nAll required packages are installed!")
