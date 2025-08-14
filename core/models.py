from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ConversationHistory(models.Model):
    """Model to store user conversation history"""
    ANALYSIS_TYPE_CHOICES = [
        ('text', 'Text Input'),
        ('image', 'Image OCR'),
        ('voice', 'Voice Recognition'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    analysis_type = models.CharField(max_length=10, choices=ANALYSIS_TYPE_CHOICES)
    
    # Input data
    input_text = models.TextField(help_text="Original or processed text input")
    input_file = models.FileField(upload_to='conversations/', null=True, blank=True)
    
    # Analysis results
    medications_analyzed = models.JSONField(help_text="List of medications analyzed")
    drug_interactions = models.JSONField(help_text="Drug interaction analysis results")
    recommendations = models.TextField(help_text="AI recommendations")
    safety_score = models.FloatField(null=True, blank=True, help_text="Safety score (0-100)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="User notes")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Conversation History'
        verbose_name_plural = 'Conversation Histories'

    def __str__(self):
        return f"{self.user.email} - {self.analysis_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DrugDatabase(models.Model):
    """Basic drug information database"""
    name = models.CharField(max_length=200, unique=True)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_names = models.JSONField(default=list, help_text="List of brand names")
    
    # Drug information
    drug_class = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    dosage_forms = models.JSONField(default=list, help_text="Available dosage forms")
    common_dosages = models.JSONField(default=list, help_text="Common dosage ranges")
    
    # Safety information
    contraindications = models.TextField(blank=True)
    side_effects = models.JSONField(default=list, help_text="Common side effects")
    warnings = models.TextField(blank=True)
    
    # Interaction data
    major_interactions = models.JSONField(default=list, help_text="Major drug interactions")
    moderate_interactions = models.JSONField(default=list, help_text="Moderate drug interactions")
    minor_interactions = models.JSONField(default=list, help_text="Minor drug interactions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.generic_name})"


class UserFeedback(models.Model):
    """User feedback on analysis results"""
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(ConversationHistory, on_delete=models.CASCADE, related_name='feedback')
    
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True)
    is_helpful = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'conversation']

    def __str__(self):
        return f"Feedback by {self.user.email} - Rating: {self.rating}"
