from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medai.settings')
django.setup()

from authentication.models import User
from api.routers.auth import get_current_user
from core.models import ConversationHistory, UserFeedback

router = APIRouter()


class ConversationResponse(BaseModel):
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


class FeedbackRequest(BaseModel):
    conversation_id: int
    rating: int
    feedback_text: Optional[str] = ""
    is_helpful: bool = True


@router.get("/", response_model=List[ConversationResponse])
async def get_conversation_history(
    analysis_type: Optional[str] = None,
    favorites_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get user's conversation history"""
    try:
        conversations = ConversationHistory.objects.filter(user=current_user)
        
        # Apply filters
        if analysis_type:
            conversations = conversations.filter(analysis_type=analysis_type)
        
        if favorites_only:
            conversations = conversations.filter(is_favorite=True)
        
        # Convert to response format
        result = []
        for conv in conversations:
            result.append(ConversationResponse(
                id=conv.id,
                analysis_type=conv.analysis_type,
                input_text=conv.input_text,
                medications_analyzed=conv.medications_analyzed,
                drug_interactions=conv.drug_interactions,
                recommendations=conv.recommendations,
                safety_score=conv.safety_score,
                created_at=conv.created_at.isoformat(),
                is_favorite=conv.is_favorite,
                notes=conv.notes
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_detail(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get specific conversation details"""
    try:
        conversation = ConversationHistory.objects.get(id=conversation_id, user=current_user)
        
        return ConversationResponse(
            id=conversation.id,
            analysis_type=conversation.analysis_type,
            input_text=conversation.input_text,
            medications_analyzed=conversation.medications_analyzed,
            drug_interactions=conversation.drug_interactions,
            recommendations=conversation.recommendations,
            safety_score=conversation.safety_score,
            created_at=conversation.created_at.isoformat(),
            is_favorite=conversation.is_favorite,
            notes=conversation.notes
        )
        
    except ConversationHistory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@router.post("/{conversation_id}/favorite")
async def toggle_favorite(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """Toggle favorite status of a conversation"""
    try:
        conversation = ConversationHistory.objects.get(id=conversation_id, user=current_user)
        conversation.is_favorite = not conversation.is_favorite
        conversation.save()
        
        return {
            "message": "Favorite status updated",
            "is_favorite": conversation.is_favorite
        }
        
    except ConversationHistory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update favorite status: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for a conversation"""
    try:
        # Validate rating
        if feedback.rating < 1 or feedback.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
        
        # Get conversation
        conversation = ConversationHistory.objects.get(
            id=feedback.conversation_id, 
            user=current_user
        )
        
        # Create or update feedback
        user_feedback, created = UserFeedback.objects.get_or_create(
            user=current_user,
            conversation=conversation,
            defaults={
                'rating': feedback.rating,
                'feedback_text': feedback.feedback_text,
                'is_helpful': feedback.is_helpful
            }
        )
        
        if not created:
            user_feedback.rating = feedback.rating
            user_feedback.feedback_text = feedback.feedback_text
            user_feedback.is_helpful = feedback.is_helpful
            user_feedback.save()
        
        return {
            "message": "Feedback submitted successfully",
            "feedback_id": user_feedback.id
        }
        
    except ConversationHistory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation"""
    try:
        conversation = ConversationHistory.objects.get(id=conversation_id, user=current_user)
        conversation.delete()
        
        return {"message": "Conversation deleted successfully"}
        
    except ConversationHistory.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )
