from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PasswordResetPIN
from django.utils import timezone
import random
import datetime
from django.db import models
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, LoginView, INTERNAL_RESET_SESSION_TOKEN
from django.contrib.auth import get_user_model, login, update_session_auth_hash

from django.core.mail import send_mail

from django.conf import settings

#=========================CLASSES=========================#
class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # We override this to PREVENT the form from raising 
        # a ValidationError for inactive users.
        # We want the View to handle the inactive state instead.
        pass

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomAuthenticationForm # Tell it to use our custom form

    def form_valid(self, form):
        user = form.get_user() # The form has already authenticated the user
        
        if not user.is_active:
            # Now we handle the inactive user exactly how we want
            messages.warning(
                self.request, 
                "Your account is pending activation. Please check your email or "
                "<a href='/resend-activation/'>click here to resend the activation link</a>.",
                extra_tags='warning'
            )
            return self.form_invalid(form)
        
        # If they ARE active, log them in normally
        login(self.request, user)
        return redirect(self.get_success_url())

#=========================FUNCTIONS=========================#
import string
import secrets # More secure than 'random' for passwords

def generate_alphanumeric_pin(length=6):
    # We exclude 'O', '0', 'I', '1', 'l' to prevent user confusion
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    return ''.join(secrets.choice(characters) for _ in range(length))


def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 1. Cooldown Check: Prevent more than 1 PIN every 60 seconds
        recent_pin = PasswordResetPIN.objects.filter(
            email=email, 
            created_at__gt=timezone.now() - datetime.timedelta(seconds=2)
        ).exists()

        if recent_pin:
            messages.error(request, "Please wait a minute before requesting another code.")
            return render(request, 'reset_request.html')

        # 2. Generate and Save
        #pin = f"{random.randint(100000, 999999)}"
        pin = generate_alphanumeric_pin()
        PasswordResetPIN.objects.filter(email=email).delete() # Clear old ones
        PasswordResetPIN.objects.create(email=email, pin=pin)

        # 3. Send Email (Replace with your actual send_mail logic)
        print(f"DEBUG: Sent {pin} to {email}") 
        subject = "Your Password Reset PIN"
        message = f"Your 6-digit reset code is: {pin}. It expires in {settings.PASSWORD_PIN_TIMEOUT_MINUTES} minutes."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        
        send_mail(subject, message, from_email, recipient_list)

        # 4. Store email in session so the next view knows who we are verifying
        request.session['reset_email'] = email
        return redirect('verify_pin')

    return render(request, 'reset_request.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings  # Ensure this is imported for your timeout setting
from .models import PasswordResetPIN
import datetime

User = get_user_model()

def verify_pin(request):
    # 1. Safety Check: Ensure user started the reset process
    email = request.session.get('reset_email')
    if not email:
        return redirect('request_password_reset')

    # 2. Initialize variables
    expiry_timestamp = None
    reset_obj = PasswordResetPIN.objects.filter(email=email).first()
    
    # Use your settings variable or default to 10
    timeout = getattr(settings, 'PASSWORD_PIN_TIMEOUT_MINUTES', 10)

    # 3. Calculate Expiry for the frontend timer
    if reset_obj:
        expiry_time = reset_obj.created_at + datetime.timedelta(minutes=timeout)
        expiry_timestamp = expiry_time.isoformat()

    # 4. Handle Form Submission
    if request.method == 'POST':
        entered_pin = request.POST.get('pin', '').strip().upper() # Clean the alphanumeric input
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if reset_obj:
            # --- DEBUG SECTION ---
            now = timezone.now()
            time_remaining = (reset_obj.created_at + datetime.timedelta(minutes=timeout)) - now
            
            print("--- PIN DEBUG INFO ---")
            print(f"Current Time:  {now.strftime('%H:%M:%S')}")
            print(f"PIN Created:   {reset_obj.created_at.strftime('%H:%M:%S')}")
            print(f"Time Left:     {max(0, time_remaining.total_seconds()):.1f} seconds")
            print(f"Is Valid:      {reset_obj.is_valid()}")
            print("-----------------------")

            # --- VALIDATION LOGIC ---
            
            # Check 1: Is the PIN correct and not expired?
            if reset_obj.pin != entered_pin or not reset_obj.is_valid():
                messages.error(request, "Invalid or expired PIN. Please check your email and try again.")
            
            # Check 2: Do the new passwords match?
            elif new_password != confirm_password:
                messages.error(request, "The passwords you entered do not match.")
            
            # Check 3: Is the password long enough? (Optional but recommended)
            elif len(new_password) < 8:
                messages.error(request, "Your new password must be at least 8 characters long.")

            else:
                # SUCCESS: Change password and clean up
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                
                reset_obj.delete() # Remove the used PIN
                del request.session['reset_email'] # Clear the session
                
                messages.success(request, "Success! Your password has been updated.")
                return redirect('login')
        else:
            messages.error(request, "No active reset request found. Please start over.")
            return redirect('request_password_reset')

    # 5. Render Page
    return render(request, 'verify_pin.html', {
        'email': email,
        'expiry_timestamp': expiry_timestamp
    })