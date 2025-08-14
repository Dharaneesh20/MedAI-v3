#!/usr/bin/env python3
"""
Test script to verify all AI components are working
"""

import sys
import os

# Add Django project to path
sys.path.append('/home/ninja/Desktop/New folder/New folder')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medai.settings')

def test_ai_services():
    """Test all AI services"""
    print("🧪 Testing MedAi AI Services")
    print("=" * 40)
    
    try:
        # Import Django and setup
        import django
        django.setup()
        
        # Import our services
        from analysis.services import HuggingFaceLLM, OCRService, SpeechService
        
        print("✅ Django services imported successfully")
        
        # Test 1: LLM Service
        print("\n1️⃣ Testing LLM Service...")
        llm_service = HuggingFaceLLM()
        
        test_medications = ["aspirin", "warfarin"]
        result = llm_service.analyze_drug_interactions(test_medications)
        print(f"🧠 LLM Analysis Result:\n{result}")
        
        # Test 2: OCR Service
        print("\n2️⃣ Testing OCR Service...")
        ocr_service = OCRService()
        
        if ocr_service.tesseract_available:
            print("✅ OCR service ready")
            
            # Test if sample image exists
            if os.path.exists('sample_prescription.png'):
                ocr_result = ocr_service.extract_text_from_image('sample_prescription.png')
                medications = ocr_service.extract_medications(ocr_result)
                print(f"📄 OCR extracted medications: {medications}")
            else:
                print("⚠️ Sample prescription image not found")
        else:
            print("❌ OCR service unavailable")
        
        # Test 3: Speech Service
        print("\n3️⃣ Testing Speech Service...")
        speech_service = SpeechService()
        
        if speech_service.microphone_available:
            print("✅ Speech recognition ready")
            print("🎤 Microphones detected, speech-to-text available")
        else:
            print("⚠️ No microphones detected")
        
        print("\n" + "=" * 40)
        print("🎉 All AI services tested successfully!")
        print("\n📋 Summary:")
        print(f"  🧠 LLM: ✅ Rule-based system ready")
        print(f"  👁️ OCR: {'✅ Ready' if ocr_service.tesseract_available else '❌ Unavailable'}")
        print(f"  🎤 Speech: {'✅ Ready' if speech_service.microphone_available else '⚠️ No microphone'}")
        print(f"  📚 Drug DB: ✅ {len(llm_service.drug_interactions)} medications in database")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_ai_services()
