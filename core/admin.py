from django.contrib import admin
from .models import ConversationHistory, DrugDatabase, UserFeedback


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis_type', 'safety_score', 'is_favorite', 'created_at')
    list_filter = ('analysis_type', 'is_favorite', 'created_at')
    search_fields = ('user__email', 'input_text', 'recommendations')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DrugDatabase)
class DrugDatabaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'generic_name', 'drug_class', 'created_at')
    list_filter = ('drug_class', 'created_at')
    search_fields = ('name', 'generic_name', 'drug_class')
    ordering = ('name',)


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'conversation', 'rating', 'is_helpful', 'created_at')
    list_filter = ('rating', 'is_helpful', 'created_at')
    search_fields = ('user__email', 'feedback_text')
    ordering = ('-created_at',)
