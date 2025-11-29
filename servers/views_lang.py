"""
Language switching view
"""
from django.shortcuts import redirect
from django.conf import settings

def set_language(request):
    """
    Set user language preference via cookie and Django's language session.
    Works for both user frontend and admin backend.
    """
    from django.utils import translation
    
    lang = request.GET.get('lang', 'en')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    
    # Validate language is in our supported list
    supported_langs = [code for code, name in settings.LANGUAGES]
    if lang not in supported_langs:
        lang = settings.LANGUAGE_CODE
    
    # Activate the language for Django (for admin)
    translation.activate(lang)
    
    # Redirect back to the previous page or specified next URL
    response = redirect(next_url)
    
    # Set the cookie for 1 year (for user frontend)
    response.set_cookie(
        'user_lang', 
        lang, 
        max_age=365*24*60*60,
        samesite='Lax'
    )
    
    # Set Django's language cookie (for admin backend)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=365*24*60*60,
        samesite='Lax'
    )
    
    return response