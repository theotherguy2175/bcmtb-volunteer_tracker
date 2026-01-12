from django.utils import timezone
import os

def global_context(request):
    # USE THIS: timezone.localtime(timezone.now()) 
    # This forces Django to convert the UTC 'now' into Indianapolis time
    now_local = timezone.localtime(timezone.now())
    
    app_version = os.getenv('APP_VERSION')
    if not app_version:
        app_version = f"v.{now_local.strftime('%y.%m.%d.%H.%M-dev')}"
    
    return {
        'current_year': now_local.year,
        'app_version': app_version,
    }