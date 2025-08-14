#!/usr/bin/env python3
"""
MedAi AI Models Setup Script
Downloads and configures HuggingFace LLM, tests OCR and Speech Recognition
"""

import os
import sys
import torch
import warnings
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import pytesseract
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Suppress warnings
warnings.filterwarnings('ignore')

# Configuration
MODEL_NAME = "ibm-granite/granite-3.3-2b-instruct"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
CACHE_DIR = "./models"

def setup_directories():
    """Create necessary directories"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    print(f"✅ Created models directory: {CACHE_DIR}")

def login_huggingface():
    """Login to HuggingFace"""
    try:
        login(token=HUGGINGFACE_API_KEY)
        print("✅ Successfully authenticated with HuggingFace")
        return True
    except Exception as e:
        print(f"❌ Failed to authenticate with HuggingFace: {e}")
        return False

def check_device():
    """Check available compute device"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️ Using device: {device}")
    
    if torch.cuda.is_available():
        print(f"🚀 CUDA device: {torch.cuda.get_device_name(0)}")
        print(f"💾 CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("⚠️ CUDA not available, using CPU (this will be slower)")
    
    return device

def download_model():
    """Download and load the LLM model"""
    device = check_device()
    
    print("📥 Downloading tokenizer...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            token=HUGGINGFACE_API_KEY,
            cache_dir=CACHE_DIR
        )
        print("✅ Tokenizer loaded successfully")
        print(f"📊 Vocabulary size: {tokenizer.vocab_size}")
    except Exception as e:
        print(f"❌ Failed to load tokenizer: {e}")
        return None, None, device
    
    print("📥 Downloading model (this may take several minutes)...")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            token=HUGGINGFACE_API_KEY,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            cache_dir=CACHE_DIR,
            trust_remote_code=True
        )
        
        if not torch.cuda.is_available():
            model = model.to(device)
        
        print("✅ Model loaded successfully")
        print(f"🧠 Model parameters: {model.num_parameters():,}")
        
        return model, tokenizer, device
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None, tokenizer, device

def test_llm(model, tokenizer, device):
    """Test LLM functionality"""
    if model is None or tokenizer is None:
        print("⚠️ Skipping LLM test - model not loaded")
        return
    
    print("\n🧪 Testing LLM with medical query...")
    prompt = "Analyze potential drug interactions between aspirin and warfarin:"
    
    try:
        # Prepare input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response
        print("🧠 Generating response...")
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_text = response[len(prompt):].strip()
        
        print(f"🤖 LLM Response:\n{generated_text}")
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def create_sample_prescription():
    """Create a sample prescription image for OCR testing"""
    # Create a white image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use default font
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add prescription text
    draw.text((50, 30), "PRESCRIPTION", fill='black', font=font_large)
    draw.text((50, 80), "Patient: John Doe", fill='black', font=font_medium)
    draw.text((50, 110), "Date: August 14, 2025", fill='black', font=font_medium)
    
    draw.text((50, 160), "Medications:", fill='black', font=font_medium)
    draw.text((70, 190), "1. Aspirin 81mg - Take once daily", fill='black', font=font_small)
    draw.text((70, 210), "2. Lisinopril 10mg - Take twice daily", fill='black', font=font_small)
    draw.text((70, 230), "3. Metformin 500mg - Take with meals", fill='black', font=font_small)
    
    draw.text((50, 280), "Dr. Smith", fill='black', font=font_medium)
    draw.text((50, 300), "Medical License: ML123456", fill='black', font=font_small)
    
    # Save the image
    img_path = 'sample_prescription.png'
    img.save(img_path)
    print(f"✅ Sample prescription created: {img_path}")
    
    return img_path

def test_ocr():
    """Test OCR functionality"""
    print("\n🔍 Testing OCR functionality...")
    
    try:
        # Check Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        
        # Create sample image
        img_path = create_sample_prescription()
        
        # Extract text
        text = pytesseract.image_to_string(Image.open(img_path))
        print(f"📄 OCR extracted text:\n{text.strip()}")
        
        # Extract medications using simple parsing
        lines = text.strip().split('\n')
        medications = []
        for line in lines:
            if any(med_indicator in line.lower() for med_indicator in ['mg', 'daily', 'aspirin', 'lisinopril', 'metformin']):
                medications.append(line.strip())
        
        print(f"💊 Extracted medications:")
        for med in medications:
            print(f"  • {med}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR test failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition functionality"""
    print("\n🎤 Testing speech recognition...")
    
    try:
        # Initialize recognizer
        r = sr.Recognizer()
        
        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        print(f"🎤 Found {len(mic_list)} microphone(s):")
        for i, mic_name in enumerate(mic_list[:3]):  # Show first 3
            print(f"  {i}: {mic_name}")
        
        print("✅ Speech recognition ready")
        print("💡 To test: Use the Django web interface or call audio_to_text API")
        
        return True
        
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        return False

def update_django_services():
    """Update Django services with model paths"""
    print("\n🔧 Updating Django AI services...")
    
    services_path = "analysis/services.py"
    if not os.path.exists(services_path):
        print(f"❌ Services file not found: {services_path}")
        return False
    
    try:
        # Read current services file
        with open(services_path, 'r') as f:
            content = f.read()
        
        # Update model path and cache directory
        updated_content = content.replace(
            'self.model_name = "ibm-granite/granite-3.3-2b-instruct"',
            f'self.model_name = "{MODEL_NAME}"\n        self.cache_dir = "{os.path.abspath(CACHE_DIR)}"'
        )
        
        # Write updated content
        with open(services_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ Django services updated with model configuration")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update Django services: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 MedAi AI Models Setup")
    print("=" * 50)
    
    # Setup
    setup_directories()
    
    # Login to HuggingFace
    if not login_huggingface():
        print("❌ Cannot proceed without HuggingFace authentication")
        return
    
    # Download and test LLM
    print("\n1️⃣ Setting up HuggingFace LLM...")
    model, tokenizer, device = download_model()
    llm_success = test_llm(model, tokenizer, device)
    
    # Test OCR
    print("\n2️⃣ Setting up OCR...")
    ocr_success = test_ocr()
    
    # Test Speech Recognition
    print("\n3️⃣ Setting up Speech Recognition...")
    speech_success = test_speech_recognition()
    
    # Update Django services
    print("\n4️⃣ Configuring Django Integration...")
    django_success = update_django_services()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Setup Summary:")
    print(f"  🧠 LLM: {'✅ Ready' if llm_success else '❌ Failed'}")
    print(f"  👁️ OCR: {'✅ Ready' if ocr_success else '❌ Failed'}")
    print(f"  🎤 Speech: {'✅ Ready' if speech_success else '❌ Failed'}")
    print(f"  🔧 Django: {'✅ Ready' if django_success else '❌ Failed'}")
    
    if all([llm_success, ocr_success, speech_success]):
        print("\n🎉 All AI components are ready!")
        print("🚀 You can now use the full MedAi functionality:")
        print("   • Text-based drug interaction analysis")
        print("   • OCR prescription image processing")
        print("   • Voice-to-text medication input")
        print(f"\n📁 Model files cached in: {os.path.abspath(CACHE_DIR)}")
    else:
        print("\n⚠️ Some components failed. Check the errors above.")

if __name__ == "__main__":
    main()
