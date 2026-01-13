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


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN
from django.utils.http import urlsafe_base64_decode

class MyCustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        print(f"\n--- [DEBUG] SECURITY CHECK START ---")
        try:
            # 1. Decode User
            uidb64 = kwargs.get('uidb64')
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = get_user_model().objects.get(pk=uid)
            
            # 2. UNIVERSAL TOKEN SURGERY
            raw_token = kwargs.get('token', '')
            
            # Use regex to find all alphanumeric chunks
            # This ignores '=', '-', '_', or any other junk Microsoft injects
            import re
            chunks = re.findall(r'[A-Za-z0-9]+', raw_token)
            
            if len(chunks) >= 2:
                # The Hash is always the LAST chunk
                # The Timestamp is always the SECOND TO LAST chunk
                clean_token = f"{chunks[-2]}-{chunks[-1]}"
            else:
                clean_token = raw_token
                
            print(f"Original Token: {raw_token}")
            print(f"Cleaned Token:  {clean_token}")

            # 3. OFFICIAL SECURITY CHECK
            if self.token_generator.check_token(self.user, clean_token):
                self.validlink = True
                print(f"SECURITY PASS: Valid signature for {self.user.email}")
            else:
                self.validlink = False
                print("SECURITY FAIL: Token is mathematically invalid or expired.")

        except Exception as e:
            print(f"SECURITY ERROR: {e}")
            self.user = None
            self.validlink = False

        if not self.validlink:
            return render(request, self.template_name, {'validlink': False})

        if request.method == 'POST':
            return self.post(request, *args, **kwargs)

        return render(request, self.template_name, self.get_context_data())
            


    def get_context_data(self, **kwargs):
        context = {
            'validlink': self.validlink,
            'form': self.get_form(),
            'user': self.user,
        }
        context.update(kwargs)
        return context

    def get_form_kwargs(self):
        # Use the base View method to get basic kwargs like 'data' and 'files'
        # but avoid the auth version that tries to do token math
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # SUCCESS: The passwords match and meet requirements
            user = form.save()
            print(f"!!! SUCCESS: Password changed for {user.email} !!!")
            return HttpResponseRedirect(self.success_url)
        else:
            # FAIL: Passwords didn't match or were too weak
            print(f"!!! FORM INVALID: {form.errors} !!!")
            return render(request, self.template_name, self.get_context_data(form=form))
    
    
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


