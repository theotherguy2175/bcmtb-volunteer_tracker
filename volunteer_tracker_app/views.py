from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# volunteer_tracker_app/views.py
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# This handles the password change page
from django.shortcuts import redirect
from django.urls import reverse

from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# # The Custom View
# class MyPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
#     template_name = 'password_change.html'
#     success_url = reverse_lazy('profile')
#     success_message = "Your password was changed successfully!"

# The Profile View
@login_required
def profile_view(request):
    return render(request, 'profile.html')

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