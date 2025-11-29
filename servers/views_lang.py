"""
Language switching view
"""
from django.shortcuts import redirect
from django.conf import settings

def set_language(request):
    """
    Set user language preference via cookie.
    This is a simplified approach for this project's specific needs.
    """
    lang = request.GET.get('lang', 'en')
    
    # Validate language is in our supported list
    supported_langs = [code for code, name in settings.LANGUAGES]
    if lang not in supported_langs:
        lang = settings.LANGUAGE_CODE
    
    # Redirect back to the previous page
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Set the cookie for 1 year
    response.set_cookie(
        'user_lang', 
        lang, 
        max_age=365*24*60*60,
        samesite='Lax'
    )
    
    return response
