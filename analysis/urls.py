from django.urls import path
from . import views

urlpatterns = [
    path('text/', views.analyze_text, name='analyze_text'),
    path('image/', views.analyze_image, name='analyze_image'),
    path('voice/', views.analyze_voice, name='analyze_voice'),
    path('history/', views.conversation_history, name='conversation_history'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]
