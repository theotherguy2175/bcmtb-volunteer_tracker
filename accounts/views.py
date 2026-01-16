# Python Standard Library
import datetime
import secrets
import string

# Django Core - Shortcuts & Settings
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.html import strip_tags

# Django Core - Auth & Forms
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN

# Django Core - Mail & Templates
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

# Django Core - Database
from django.db import models

# Local App Imports
from .models import PasswordResetPIN
from .forms import UserProfileForm

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

#=========================VIEWS=========================#
# PROFILE VIEW
@login_required
def profile_view(request):
    if request.method == 'POST':
        # Pass instance=request.user so it updates the existing record
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'profile_form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        # Pass the current user (your CustomUser) into the form
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # This is crucial: it keeps the user logged in after the password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'password_change.html', {
        'form': form
    })



def generate_alphanumeric_pin(length=6):
    # We exclude 'O', '0', 'I', '1', 'l' to prevent user confusion
    characters = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" 
    return ''.join(secrets.choice(characters) for _ in range(length))


def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # 1. Cooldown Check: Prevent spamming requests
        # (Using 60 seconds is standard for production)
        recent_pin = PasswordResetPIN.objects.filter(
            email=email, 
            created_at__gt=timezone.now() - datetime.timedelta(seconds=60)
        ).exists()

        if recent_pin:
            messages.error(request, "Please wait a minute before requesting another code.")
            return render(request, 'reset_request.html')

        # 2. Generate and Save PIN
        pin = generate_alphanumeric_pin()
        PasswordResetPIN.objects.filter(email=email).delete() # Clear old ones
        PasswordResetPIN.objects.create(email=email, pin=pin)

        # 3. Prepare Nice HTML Email
        timeout = getattr(settings, 'PASSWORD_PIN_TIMEOUT_MINUTES', 10)
        context = {
            'pin': pin,
            'timeout': timeout,
        }
        
        subject = f"Your Reset Code: {pin}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
        
        # Render the HTML template we created
        html_content = render_to_string('email_reset_pin.html', context)
        # Create a plain-text version for backup
        text_content = strip_tags(html_content) 

        # 4. Send Multi-Part Email
        from email import charset
        try:
            charset.add_charset('utf-8', charset.SHORTEST, charset.BASE64, 'utf-8')
            msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.encoding = 'utf-8'
            msg.send()
            
            print(f"DEBUG: HTML Email sent with PIN {pin} to {email}") 
            
            # 5. Store email in session for the verification view
            request.session['reset_email'] = email
            return redirect('accounts:verify_pin')
            
        except Exception as e:
            print(f"Email Error: {e}")
            messages.error(request, "There was an error sending the email. Please try again later.")

    return render(request, 'reset_request.html')

User = get_user_model()
def verify_pin(request):
    # 1. Safety Check: Ensure user started the reset process
    email = request.session.get('reset_email')
    if not email:
        return redirect('accounts:request_password_reset')

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
                return redirect('accounts:login')
        else:
            messages.error(request, "No active reset request found. Please start over.")
            return redirect('accounts:request_password_reset')

    # 5. Render Page
    return render(request, 'verify_pin.html', {
        'email': email,
        'expiry_timestamp': expiry_timestamp
    })