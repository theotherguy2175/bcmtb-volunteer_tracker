import os
from django.utils import timezone

# Look for 'APP_VERSION' from Docker. 
# Fallback to a "Dev" timestamp if running locally without Docker.
VERSION = os.getenv('APP_VERSION', f"v.{timezone.now().strftime('%y.%m.%d.dev')}")

def global_context(request):
    return {
        'current_year': timezone.now().year,
        'app_version': VERSION,
    }