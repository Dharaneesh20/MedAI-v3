from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Home page view"""
    return render(request, 'core/home.html')


def dashboard(request):
    """Dashboard view for authenticated users"""
    if not request.user.is_authenticated:
        return render(request, 'core/login_required.html')
    
    # Get recent conversations
    recent_conversations = request.user.conversations.all()[:5]
    
    context = {
        'user': request.user,
        'recent_conversations': recent_conversations,
    }
    return render(request, 'core/dashboard.html', context)
