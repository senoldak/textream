import os
import sys
import zipfile
import urllib.request
import shutil

# Top 5 + Turkish
MODELS = {
    "tr": "https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip",
    "en": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
    "es": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
    "fr": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
    "de": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
    "cn": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
}

def download_hook(count, block_size, total_size):
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\rDownloading... {percent}%")
        sys.stdout.flush()

def download_language(lang_code, parent_dir="."):
    """Downloads a specific language model."""
    if lang_code not in MODELS:
        print(f"Unknown language code: {lang_code}")
        return False
        
    url = MODELS[lang_code]
    target_dir = os.path.join(parent_dir, "models", lang_code)
    
    if os.path.exists(target_dir):
        print(f"Model '{lang_code}' already exists.")
        return True
        
    models_root = os.path.join(parent_dir, "models")
    if not os.path.exists(models_root):
        os.makedirs(models_root)
        
    zip_name = f"{lang_code}_model.zip"
    print(f"\nDownloading {lang_code.upper()} model from {url}...")
    
    try:
        urllib.request.urlretrieve(url, zip_name, download_hook)
        print(f"\nExtracting {lang_code.upper()}...")
        
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            # Create a unique temp folder for extraction
            extract_temp = f"temp_extract_{lang_code}"
            if os.path.exists(extract_temp):
                shutil.rmtree(extract_temp)
            os.makedirs(extract_temp)
            
            zip_ref.extractall(extract_temp)
            
            # Find the inner folder and move it to models/lang
            extracted_items = os.listdir(extract_temp)
            model_folder = None
            for item in extracted_items:
                full_path = os.path.join(extract_temp, item)
                if os.path.isdir(full_path) and item.startswith("vosk-model"):
                    model_folder = full_path
                    break
            
            if model_folder:
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                shutil.move(model_folder, target_dir)
                print(f"Installed to {target_dir}")
            else:
                 # Fallback: maybe the zip contents were flat?
                 # If no folder starting with vosk-model found, assume the extract_temp IS the model
                 # But usually vosk zips have a root folder.
                 print("Could not identify model folder structure. Check zip content.")

            # Cleanup temp
            shutil.rmtree(extract_temp)

    except Exception as e:
        print(f"Failed to process {lang_code}: {e}")
        return False
    finally:
        if os.path.exists(zip_name):
            os.remove(zip_name)
            
    return True

def main():
    # Helper to download all defined models
    for lang in MODELS:
        download_language(lang)

if __name__ == "__main__":
    main()
