from rest_framework import serializers


class TextAnalysisSerializer(serializers.Serializer):
    """Serializer for text-based drug analysis"""
    medications = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text="List of medications to analyze"
    )
    include_patient_info = serializers.BooleanField(default=True)


class ImageAnalysisSerializer(serializers.Serializer):
    """Serializer for image-based drug analysis"""
    image = serializers.ImageField(help_text="Image file containing medication information")
    include_patient_info = serializers.BooleanField(default=True)


class VoiceAnalysisSerializer(serializers.Serializer):
    """Serializer for voice-based drug analysis"""
    audio = serializers.FileField(help_text="Audio file with medication information")
    include_patient_info = serializers.BooleanField(default=True)


class AnalysisResultSerializer(serializers.Serializer):
    """Serializer for analysis results"""
    medications_analyzed = serializers.ListField(child=serializers.CharField())
    drug_interactions = serializers.DictField()
    safety_score = serializers.FloatField()
    recommendations = serializers.CharField()
    analysis_type = serializers.CharField()
    conversation_id = serializers.IntegerField(read_only=True)


class ConversationHistorySerializer(serializers.Serializer):
    """Serializer for conversation history"""
    id = serializers.IntegerField(read_only=True)
    analysis_type = serializers.CharField()
    input_text = serializers.CharField()
    medications_analyzed = serializers.JSONField()
    drug_interactions = serializers.JSONField()
    recommendations = serializers.CharField()
    safety_score = serializers.FloatField()
    created_at = serializers.DateTimeField(read_only=True)
    is_favorite = serializers.BooleanField()
    notes = serializers.CharField(allow_blank=True)


class FeedbackSerializer(serializers.Serializer):
    """Serializer for user feedback"""
    conversation_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    feedback_text = serializers.CharField(allow_blank=True)
    is_helpful = serializers.BooleanField(default=True)
