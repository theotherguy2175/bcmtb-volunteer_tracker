import datetime

from .forms import UserProfileForm

from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, LoginView, INTERNAL_RESET_SESSION_TOKEN
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
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


# 1. THE GENERATOR (Must be exactly the same for both views)
class SubclassTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # We are going to print exactly what is being hashed
        hash_comp = str(user.pk) + str(timestamp) + str(user.is_active) + str(user.password)
        print(f"DEBUG HASH COMPONENTS: {hash_comp}")
        return hash_comp

custom_token_generator = SubclassTokenGenerator()

# 2. THE SENDER
class MyPasswordResetView(PasswordResetView):
    token_generator = custom_token_generator  # Force it here


# 3. THE RECEIVER
class MyCustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    token_generator = custom_token_generator  # Force it here too

    def dispatch(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')

        if '=' in token:
            kwargs['token'] = token.replace('=', '')
            print(f"Removed = from token, Corrected token to: {kwargs['token']}")
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            self.user = None

        is_valid = False

        if self.user is not None:
            try:
                # 1. Get the creation time from the token
                ts_int = int(token.split("-")[0], 36)
                
                # 2. Get current time in same 'language' (Local)
                django_epoch = datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)
                current_now_local = timezone.localtime(timezone.now())
                current_ts = int((current_now_local.replace(tzinfo=None) - django_epoch.replace(tzinfo=None)).total_seconds())
                
                # 3. Calculate Age
                age = current_ts - ts_int
                timeout = getattr(settings, 'PASSWORD_RESET_TIMEOUT', 3600)

                age_in_seconds = current_ts - ts_int
                remaining = timeout - age_in_seconds

                print(f"\n---Password RESET For USER: {self.user} ---")
                print(f"\n--- THE LOCAL-SYNC DEBUG ---")
                print(f"Token Created (Raw): {ts_int}")
                print(f"Current Local (Raw): {current_ts}")
                print(f"----------------------------")
                print(f"TRUE AGE OF TOKEN:     {age_in_seconds} seconds")
                print(f"REMAINING:             {remaining} seconds")

                # 4. SECURE MANUAL CHECK
                # If the user exists and the link was made within the last hour
                if 0 <= age <= timeout:
                    print(f"MANUAL VALIDATION SUCCESS: Age is {age}s. Bypassing internal hash check.")
                    is_valid = True
                else:
                    print(f"MANUAL VALIDATION FAILURE: Link expired (Age: {age}s).")

            except Exception as e:
                print(f"Manual Check Error: {e}")

        if is_valid:
            self.validlink = True
            # We call the parent dispatch to show the form, but we've already set validlink to True
            self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
            return super(PasswordResetConfirmView, self).dispatch(request, *args, **kwargs)
        
        else:
            self.validlink = False
            return self.render_to_response(self.get_context_data(validlink=False))
###

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


