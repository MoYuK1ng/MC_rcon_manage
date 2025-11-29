"""
Language switching view
"""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def set_language(request):
    """
    Set user language preference via cookie
    """
    lang = request.GET.get('lang', 'en')
    
    # Validate language
    if lang not in ['en', 'zh']:
        lang = 'en'
    
    response = redirect(request.META.get('HTTP_REFERER', '/dashboard/'))
    response.set_cookie('user_lang', lang, max_age=365*24*60*60)  # 1 year
    
    return response
