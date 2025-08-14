from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medai.settings')
django.setup()

from authentication.models import User
from api.routers.auth import get_current_user
from analysis.services import HuggingFaceLLM, OCRProcessor, SpeechProcessor
from core.models import ConversationHistory

router = APIRouter()


class TextAnalysisRequest(BaseModel):
    medications: List[str]
    include_patient_info: bool = True


class AnalysisResponse(BaseModel):
    medications_analyzed: List[str]
    drug_interactions: Dict[str, Any]
    safety_score: float
    recommendations: str
    analysis_type: str
    conversation_id: int


class ConversationHistoryResponse(BaseModel):
    id: int
    analysis_type: str
    input_text: str
    medications_analyzed: List[str]
    drug_interactions: Dict[str, Any]
    recommendations: str
    safety_score: float
    created_at: str
    is_favorite: bool
    notes: str


def get_patient_info(user: User, include_patient_info: bool = True):
    """Get patient information for analysis"""
    if not include_patient_info:
        return None
        
    return {
        'allergies': user.allergies,
        'chronic_conditions': user.chronic_conditions,
        'current_medications': user.current_medications,
    }


@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze medications from text input"""
    try:
        medications = request.medications
        
        if not medications:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No medications provided"
            )
        
        # Get patient information
        patient_info = get_patient_info(current_user, request.include_patient_info)
        
        # Initialize LLM and analyze
        llm = HuggingFaceLLM()
        analysis_result = llm.analyze_drug_interactions(medications, patient_info)
        
        # Save to conversation history
        conversation = ConversationHistory.objects.create(
            user=current_user,
            analysis_type='text',
            input_text=', '.join(medications),
            medications_analyzed=analysis_result['medications_analyzed'],
            drug_interactions=analysis_result['drug_interactions'],
            recommendations=analysis_result['recommendations'],
            safety_score=analysis_result['safety_score']
        )
        
        return AnalysisResponse(
            medications_analyzed=analysis_result['medications_analyzed'],
            drug_interactions=analysis_result['drug_interactions'],
            safety_score=analysis_result['safety_score'],
            recommendations=analysis_result['recommendations'],
            analysis_type='text',
            conversation_id=conversation.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/image", response_model=AnalysisResponse)
async def analyze_image(
    image: UploadFile = File(...),
    include_patient_info: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Analyze medications from image OCR"""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            content = await image.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Process OCR
            ocr_processor = OCRProcessor()
            ocr_result = ocr_processor.extract_text_from_image(tmp_path)
            
            if 'error' in ocr_result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"OCR processing failed: {ocr_result['error']}"
                )
            
            medications = ocr_result['extracted_medications']
            
            if not medications:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No medications found in image"
                )
            
            # Get patient information
            patient_info = get_patient_info(current_user, include_patient_info)
            
            # Analyze with LLM
            llm = HuggingFaceLLM()
            analysis_result = llm.analyze_drug_interactions(medications, patient_info)
            
            # Save to conversation history
            conversation = ConversationHistory.objects.create(
                user=current_user,
                analysis_type='image',
                input_text=ocr_result['cleaned_text'],
                medications_analyzed=analysis_result['medications_analyzed'],
                drug_interactions=analysis_result['drug_interactions'],
                recommendations=analysis_result['recommendations'],
                safety_score=analysis_result['safety_score']
            )
            
            return AnalysisResponse(
                medications_analyzed=analysis_result['medications_analyzed'],
                drug_interactions=analysis_result['drug_interactions'],
                safety_score=analysis_result['safety_score'],
                recommendations=analysis_result['recommendations'],
                analysis_type='image',
                conversation_id=conversation.id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


@router.post("/voice", response_model=AnalysisResponse)
async def analyze_voice(
    audio: UploadFile = File(...),
    include_patient_info: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Analyze medications from voice input"""
    try:
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            content = await audio.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Process speech recognition
            speech_processor = SpeechProcessor()
            speech_result = speech_processor.process_audio_file(tmp_path)
            
            if 'error' in speech_result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Speech recognition failed: {speech_result['error']}"
                )
            
            medications = speech_result['extracted_medications']
            
            if not medications:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No medications found in audio"
                )
            
            # Get patient information
            patient_info = get_patient_info(current_user, include_patient_info)
            
            # Analyze with LLM
            llm = HuggingFaceLLM()
            analysis_result = llm.analyze_drug_interactions(medications, patient_info)
            
            # Save to conversation history
            conversation = ConversationHistory.objects.create(
                user=current_user,
                analysis_type='voice',
                input_text=speech_result['recognized_text'],
                medications_analyzed=analysis_result['medications_analyzed'],
                drug_interactions=analysis_result['drug_interactions'],
                recommendations=analysis_result['recommendations'],
                safety_score=analysis_result['safety_score']
            )
            
            return AnalysisResponse(
                medications_analyzed=analysis_result['medications_analyzed'],
                drug_interactions=analysis_result['drug_interactions'],
                safety_score=analysis_result['safety_score'],
                recommendations=analysis_result['recommendations'],
                analysis_type='voice',
                conversation_id=conversation.id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice analysis failed: {str(e)}"
        )
