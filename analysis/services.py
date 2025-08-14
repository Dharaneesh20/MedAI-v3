"""
AI Services for MedAi - Drug Interaction Analysis
"""

import json
import os
import torch
from transformers import pipeline
import pytesseract
import speech_recognition as sr
from PIL import Image
import cv2
import numpy as np
from django.conf import settings

class HuggingFaceLLM:
    """HuggingFace LLM service with fallback to rule-based system"""
    
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-medium"
        self.cache_dir = "./models"
        self.model = None
        self.tokenizer = None
        self.drug_interactions = self.load_drug_interactions()
        
        # Try to initialize the model, fallback to rule-based if it fails
        try:
            self.initialize_model()
        except Exception as e:
            print(f"Warning: LLM model unavailable, using rule-based system: {e}")
    
    def load_drug_interactions(self):
        """Load drug interactions database"""
        try:
            with open('drug_interactions.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "aspirin": {
                    "warfarin": "HIGH RISK: Increased bleeding risk. Monitor INR closely.",
                    "ibuprofen": "MODERATE: Increased GI bleeding risk.",
                    "metformin": "LOW RISK: Generally safe combination."
                },
                "warfarin": {
                    "aspirin": "HIGH RISK: Increased bleeding risk. Monitor INR closely.",
                    "amoxicillin": "MODERATE: May increase warfarin effect.",
                    "vitamin_k": "MODERATE: May decrease warfarin effect."
                },
                "lisinopril": {
                    "potassium": "MODERATE: Risk of hyperkalemia.",
                    "aspirin": "LOW: May reduce antihypertensive effect.",
                    "metformin": "LOW RISK: Generally safe combination."
                },
                "metformin": {
                    "aspirin": "LOW RISK: Generally safe combination.",
                    "lisinopril": "LOW RISK: Generally safe combination.",
                    "alcohol": "MODERATE: Risk of lactic acidosis."
                }
            }
    
    def initialize_model(self):
        """Initialize the HuggingFace model"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from huggingface_hub import login
        
        # Login to HuggingFace
        api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        login(token=api_key)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir
        )
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        ).to(device)
    
    def analyze_drug_interactions(self, medications, user_profile=None):
        """Analyze drug interactions"""
        try:
            if self.model and self.tokenizer:
                return self._llm_analysis(medications, user_profile)
            else:
                return self._rule_based_analysis(medications)
        except Exception as e:
            return self._rule_based_analysis(medications)
    
    def _llm_analysis(self, medications, user_profile):
        """Use LLM for analysis"""
        prompt = f"Analyze drug interactions for: {', '.join(medications)}. Provide warnings and recommendations:"
        
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        device = next(self.model.parameters()).device
        inputs = inputs.to(device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 150,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):].strip()
    
    def _rule_based_analysis(self, medications):
        """Fallback rule-based analysis"""
        if not medications:
            return "No medications provided for analysis."
        
        medications = [med.lower().strip() for med in medications]
        warnings = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                if med1 in self.drug_interactions:
                    if med2 in self.drug_interactions[med1]:
                        warning = f"{med1.title()} + {med2.title()}: {self.drug_interactions[med1][med2]}"
                        warnings.append(warning)
        
        if warnings:
            result = "Drug Interaction Analysis:\n\n" + "\n".join(warnings)
            result += "\n\nAlways consult with your healthcare provider before making medication changes."
        else:
            result = f"No known interactions found for: {', '.join([m.title() for m in medications])}\n\n"
            result += "This is a basic analysis. Always consult with your healthcare provider."
        
        return result

class OCRService:
    """OCR service for extracting text from prescription images"""
    
    def __init__(self):
        self.tesseract_available = self.check_tesseract()
    
    def check_tesseract(self):
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
    
    def extract_text_from_image(self, image_file):
        """Extract text from prescription image"""
        if not self.tesseract_available:
            return "OCR service unavailable - Tesseract not installed"
        
        try:
            # Open and preprocess image
            image = Image.open(image_file)
            
            # Convert to OpenCV format for preprocessing
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply preprocessing
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Extract text
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            return f"OCR error: {str(e)}"
    
    def extract_medications(self, ocr_text):
        """Extract medication names from OCR text"""
        import re
        
        # Common medication patterns
        patterns = [
            r'(\w+)\s+(\d+(?:\.\d+)?\s*mg)',  # Name + dosage
            r'\d+\.\s*([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(\d+(?:\.\d+)?\s*mg)',  # Number. Name dosage
        ]
        
        medications = []
        for pattern in patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    med_name = match[0].strip()
                    dosage = match[1].strip() if len(match) > 1 else ""
                    medications.append(f"{med_name} {dosage}")
        
        return list(set(medications))

class SpeechService:
    """Speech-to-text service for voice input"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone_available = self.check_microphone()
    
    def check_microphone(self):
        """Check if microphone is available"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            return len(mic_list) > 0
        except:
            return False
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio file to text"""
        if not self.microphone_available:
            return "Speech recognition unavailable - no microphone detected"
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text.strip()
            
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"
        except Exception as e:
            return f"Audio processing error: {e}"
    
    def record_and_transcribe(self, duration=5):
        """Record audio from microphone and transcribe"""
        if not self.microphone_available:
            return "Speech recognition unavailable - no microphone detected"
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            text = self.recognizer.recognize_google(audio)
            return text.strip()
            
        except sr.WaitTimeoutError:
            return "Recording timeout - no speech detected"
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except Exception as e:
            return f"Recording error: {e}"
