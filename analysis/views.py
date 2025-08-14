from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import tempfile
import json
from datetime import date

from .services import HuggingFaceLLM, OCRService, SpeechService
from core.models import ConversationHistory, UserFeedback


def calculate_age(birth_date):
    """Calculate age from birth date"""
    if not birth_date:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def get_patient_info(user, include_patient_info=True):
    """Extract patient information for analysis"""
    if not include_patient_info:
        return None
        
    return {
        'age': calculate_age(user.date_of_birth),
        'allergies': user.allergies,
        'chronic_conditions': user.chronic_conditions,
        'current_medications': user.current_medications,
    }


@csrf_exempt
@login_required
def analyze_text(request):
    """Analyze medications from text input"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get medications from POST data
        medications_text = request.POST.get('medications', '')
        if not medications_text:
            return JsonResponse({'error': 'No medications provided'}, status=400)
            
        # Parse medications (assuming comma-separated)
        medications = [med.strip() for med in medications_text.split(',') if med.strip()]
        if not medications:
            return JsonResponse({'error': 'No valid medications found'}, status=400)
            
        include_patient_info = request.POST.get('include_patient_info', 'true').lower() == 'true'
        
        # Get patient information
        patient_info = get_patient_info(request.user, include_patient_info)
        
        # Initialize LLM and analyze
        llm = HuggingFaceLLM()
        analysis_result = llm.analyze_drug_interactions(medications, patient_info)
        
        # Save to conversation history
        conversation = ConversationHistory.objects.create(
            user=request.user,
            analysis_type='text',
            input_text=', '.join(medications),
            medications_analyzed=str(medications),
            drug_interactions=analysis_result,
            recommendations=analysis_result,
            safety_score=85  # Default score
        )
        
        # Prepare response
        result = {
            'analysis_result': analysis_result,
            'medications_found': medications,
            'analysis_type': 'text',
            'conversation_id': conversation.id
        }
        
        return JsonResponse(result)
            
    except Exception as e:
        return JsonResponse({
            'error': 'Analysis failed',
            'detail': str(e)
        }, status=500)


@csrf_exempt
@login_required
def analyze_image(request):
    """Analyze medications from image OCR"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        image_file = request.FILES.get('image')
        include_patient_info = request.POST.get('include_patient_info', 'false').lower() == 'true'
        
        if not image_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)
        
        # Save uploaded image temporarily
        file_name = default_storage.save(f'temp/{image_file.name}', ContentFile(image_file.read()))
        file_path = default_storage.path(file_name)
        
        # Process OCR
        ocr_service = OCRService()
        ocr_text = ocr_service.extract_text_from_image(file_path)
        medications = ocr_service.extract_medications(ocr_text)
        
        # Get patient information
        patient_info = get_patient_info(request.user, include_patient_info)
        
        # Analyze with LLM
        llm = HuggingFaceLLM()
        analysis_result = llm.analyze_drug_interactions(medications, patient_info)
        
        # Save to conversation history
        conversation = ConversationHistory.objects.create(
            user=request.user,
            analysis_type='image',
            input_text=ocr_text,
            input_file=file_name,
            medications_analyzed=str(medications),
            drug_interactions=analysis_result,
            recommendations=analysis_result,
            safety_score=85  # Default score
        )
        
        # Prepare response
        result = {
            'analysis_result': analysis_result,
            'medications_found': medications,
            'analysis_type': 'image',
            'conversation_id': conversation.id,
            'ocr_text': ocr_text
        }
        
        return JsonResponse(result)
            
    except Exception as e:
        return JsonResponse({
            'error': 'Image analysis failed',
            'detail': str(e)
        }, status=500)
        
    finally:
        # Clean up temporary file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


@csrf_exempt
@login_required
def analyze_voice(request):
    """Analyze medications from voice input"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get audio file from request
        if 'audio' not in request.FILES:
            return JsonResponse({'error': 'No audio file provided'}, status=400)
            
        audio_file = request.FILES['audio']
        include_patient_info = request.POST.get('include_patient_info', 'true').lower() == 'true'
        
        # Save uploaded audio temporarily
        file_name = default_storage.save(f'temp/{audio_file.name}', ContentFile(audio_file.read()))
        file_path = default_storage.path(file_name)
        
        # Process speech recognition
        speech_service = SpeechService()
        transcribed_text = speech_service.transcribe_audio(file_path)
        
        # Simple medication extraction from transcribed text
        medications = []
        common_meds = ['aspirin', 'warfarin', 'lisinopril', 'metformin', 'ibuprofen', 'amoxicillin']
        for med in common_meds:
            if med.lower() in transcribed_text.lower():
                medications.append(med)
            
            if not medications:
                return JsonResponse({
                    'error': 'No medications found in audio',
                    'detail': f'Transcribed text: {transcribed_text}'
                }, status=400)
            
            # Get patient information
            patient_info = get_patient_info(request.user, include_patient_info)
            
            # Analyze with LLM
            llm = HuggingFaceLLM()
            analysis_result = llm.analyze_drug_interactions(medications, patient_info)
            
            # Save to conversation history
            conversation = ConversationHistory.objects.create(
                user=request.user,
                analysis_type='voice',
                input_text=transcribed_text,
                input_file=file_name,
                medications_analyzed=str(medications),
                drug_interactions=analysis_result,
                recommendations=analysis_result,
                safety_score=85  # Default score
            )
            
            # Prepare response
            result = {
                'analysis_result': analysis_result,
                'medications_found': medications,
                'analysis_type': 'voice',
                'conversation_id': conversation.id,
                'transcribed_text': transcribed_text
            }
            
            return JsonResponse(result)
            
    except Exception as e:
        return JsonResponse({
            'error': 'Voice analysis failed',
            'detail': str(e)
        }, status=500)
        
    finally:
        # Clean up temporary file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


@login_required
def conversation_history(request):
    """Get user's conversation history"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    conversations = ConversationHistory.objects.filter(user=request.user)
    
    # Apply filters
    analysis_type = request.GET.get('type')
    if analysis_type:
        conversations = conversations.filter(analysis_type=analysis_type)
    
    favorites_only = request.GET.get('favorites')
    if favorites_only == 'true':
        conversations = conversations.filter(is_favorite=True)
    
    # Serialize and return
    serializer_data = []
    for conv in conversations:
        serializer_data.append({
            'id': conv.id,
            'analysis_type': conv.analysis_type,
            'input_text': conv.input_text,
            'medications_analyzed': conv.medications_analyzed,
            'drug_interactions': conv.drug_interactions,
            'recommendations': conv.recommendations,
            'safety_score': conv.safety_score,
            'created_at': conv.created_at,
            'is_favorite': conv.is_favorite,
            'notes': conv.notes,
        })
    
    return JsonResponse(serializer_data, safe=False)


@csrf_exempt
@login_required
def submit_feedback(request):
    """Submit feedback for analysis"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get form data
        conversation_id = request.POST.get('conversation_id')
        rating = request.POST.get('rating')
        feedback_text = request.POST.get('feedback_text', '')
        is_helpful = request.POST.get('is_helpful', 'false').lower() == 'true'
        
        if not conversation_id or not rating:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        conversation = ConversationHistory.objects.get(id=conversation_id, user=request.user)
        
        # Create or update feedback
        feedback, created = UserFeedback.objects.get_or_create(
            user=request.user,
            conversation=conversation,
            defaults={
                'rating': int(rating),
                'feedback_text': feedback_text,
                'is_helpful': is_helpful
            }
        )
        
        if not created:
            feedback.rating = int(rating)
            feedback.feedback_text = feedback_text
            feedback.is_helpful = is_helpful
            feedback.save()
        
        return JsonResponse({
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback.id
        })
        
    except ConversationHistory.DoesNotExist:
        return JsonResponse({
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to submit feedback',
            'detail': str(e)
        }, status=500)
