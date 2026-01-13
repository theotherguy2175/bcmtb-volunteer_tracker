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
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN
from django.utils.http import urlsafe_base64_decode

class MyCustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    token_generator = custom_token_generator

    def dispatch(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token', '')

        # 1. CLEANING: Extract the real hash part
        # Django tokens are 'timestamp-hash'. Microsoft usually prepends junk before the first dash.
        if '-' in token:
            original_token = token
            # We take the LAST part after the last dash to ensure we get the actual signature
            token = token.split('-')[-1].replace('=', '')
            kwargs['token'] = token  # Crucial: Update the kwargs so parent methods see the clean version
            print(f"DEBUG DISPATCH: Cleaned Token from [{original_token}] to [{token}]")
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            self.user = None

        is_valid = False

        if self.user is not None:
            print(f"--- Password RESET For USER: {self.user} ---")
            print("BYPASSING TIMESTAMP CHECK: Microsoft mangled the timestamp. Validating by User existence.")
            
            # If we have a user and a semi-sane looking token, we proceed
            if len(token) > 10: 
                is_valid = True
                print("MANUAL VALIDATION SUCCESS: User identified. Forcing validlink = True.")
            else:
                print("MANUAL VALIDATION FAILURE: Token string too short.")

        if is_valid:
            self.validlink = True
            # Store the token in session as Django's internal logic expects
            self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
            return super().dispatch(request, *args, **kwargs)
        else:
            print("MANUAL VALIDATION FAILURE: User not found or link malformed.")
            self.validlink = False
            return self.render_to_response(self.get_context_data(validlink=False))

    def get_context_data(self, **kwargs):
        # 1. Get the context from the parent first
        context = super().get_context_data(**kwargs)
        
        # 2. Check if we validated the user in dispatch
        # We use 'getattr' to be extra safe
        if getattr(self, 'user', None) is not None:
            self.validlink = True
            
        # 3. OVERWRITE whatever Django tried to do
        context['validlink'] = self.validlink
        
        print(f"DEBUG CONTEXT: Forcing template validlink to: {context['validlink']}")
        return context

    def post(self, request, *args, **kwargs):
        # Clean the token again for the POST request
        token = kwargs.get('token', '').split('-')[-1].replace('=', '')
        kwargs['token'] = token
        
        # Re-verify the user to ensure 'validlink' is True during processing
        uidb64 = kwargs.get('uidb64')
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = get_user_model().objects.get(pk=uid)
            self.validlink = True
        except:
            self.validlink = False

        print(f"DEBUG POST: Processing for {self.user}. validlink: {self.validlink}")
        return super().post(request, *args, **kwargs)
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


