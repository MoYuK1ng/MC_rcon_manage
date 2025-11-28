"""
Context processors for making data available to all templates.
"""

import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def version_context(request):
    """
    Read version from VERSION file and add to template context.
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: {'app_version': str} containing version number or 'Unknown'
    """
    try:
        # Get path to VERSION file in project root
        version_file_path = os.path.join(settings.BASE_DIR, 'VERSION')
        
        # Read and strip whitespace (including all types of line endings)
        with open(version_file_path, 'r', encoding='utf-8', newline=None) as f:
            version = f.read().strip()
            
        return {'app_version': version}
        
    except (FileNotFoundError, IOError, OSError) as e:
        logger.warning(f"Could not read VERSION file: {e}")
        return {'app_version': 'Unknown'}
