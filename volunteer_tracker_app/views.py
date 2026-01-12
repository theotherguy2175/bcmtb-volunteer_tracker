from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# volunteer_tracker_app/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# This handles the password change page
from django.shortcuts import redirect
from django.urls import reverse



from .forms import UserProfileForm
@login_required
def profile_view(request):
    if request.method == 'POST':
        # Pass instance=request.user so it updates the existing record
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'profile_form': form})

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keeps the user logged in
            update_session_auth_hash(request, user)
            
            # 1. Add the success message
            messages.success(request, 'Your password was successfully updated!')
            
            # 2. Redirect to the PROFILE page (not the password page)
            return redirect('profile') 
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'password_change.html', {'form': form})

from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
import datetime
import logging
class MyCustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'

    def dispatch(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        
        # 1. Manually find the user
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            self.user = None

        # 2. Timing Debug Block
        # 2. Timing Debug Block
        if self.user is not None:
            try:
                ts_int = int(token.split("-")[0], 36)
                
                # Internal Django Epoch
                django_epoch = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
                
                # --- THE FIX IS HERE ---
                # Instead of now_utc, we use LOCALTIME to match your Token Generator
                current_now_local = timezone.localtime(timezone.now())
                
                # We strip the timezone info to make it a "Naive" comparison 
                # because your Token Generator likely used a Naive timestamp
                current_ts = int((current_now_local.replace(tzinfo=None) - django_epoch.replace(tzinfo=None)).total_seconds())
                
                # Now the math compares Local-to-Local
                age_in_seconds = current_ts - ts_int
                
                # Your Setting (e.g., 60 or 3600)
                timeout_setting = getattr(settings, 'PASSWORD_RESET_TIMEOUT', 60)
                remaining = timeout_setting - age_in_seconds
                print(f"\n---Password RESET For USER: {self.user} ---")
                print(f"\n--- THE LOCAL-SYNC DEBUG ---")
                print(f"Token Created (Raw): {ts_int}")
                print(f"Current Local (Raw): {current_ts}")
                print(f"----------------------------")
                print(f"TRUE AGE OF TOKEN:     {age_in_seconds} seconds")
                print(f"REMAINING:             {remaining} seconds")
                
                logging.debug(f"\n---Password RESET For USER: {self.user} ---")
                logging.debug(f"\n--- THE LOCAL-SYNC DEBUG ---")
                logging.debug(f"Token Created (Raw): {ts_int}")
                logging.debug(f"Current Local (Raw): {current_ts}")
                logging.debug(f"----------------------------")
                logging.debug(f"TRUE AGE OF TOKEN:     {age_in_seconds} seconds")
                logging.debug(f"REMAINING:             {remaining} seconds")

                if remaining < 0:
                    print(f"STATUS: EXPIRED")
                else:
                    print(f"STATUS: VALID")
                print(f"----------------------------\n")

            except Exception as e:
                print(f"Math Error: {e}")
                

        # 3. Validation Logic
        token_generator = PasswordResetTokenGenerator()
        print(f"DEBUG: User PK: {self.user.pk}")
        print(f"DEBUG: User Password Hash: {self.user.password[:15]}...")
        print(f"DEBUG: User Last Login: {self.user.last_login}")

        logging.debug(f"DEBUG: User PK: {self.user.pk}")
        logging.debug(f"DEBUG: User Password Hash: {self.user.password[:15]}...")

        if self.user is not None and token_generator.check_token(self.user, token):
            print("VALIDATION SUCCESS: Token is valid for this user.")
            self.validlink = True
            return super(PasswordResetConfirmView, self).dispatch(request, *args, **kwargs)
        else:
            print("VALIDATION FAILED: Token is invalid or has expired.")
            self.validlink = False
            return self.render_to_response(self.get_context_data(validlink=False))