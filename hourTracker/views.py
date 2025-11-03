from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VolunteerEntry
from .forms import VolunteerEntryForm, CustomUserCreationForm



@login_required
def dashboard(request):
    if request.user.is_staff:  # or request.user.is_superuser
        # Admin sees all entries
        entries = VolunteerEntry.objects.all()
    else:
        # Regular user sees only their entries
        entries = VolunteerEntry.objects.filter(user=request.user)
    
    return render(request, 'hourTracker/dashboard.html', {'entries': entries})

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = VolunteerEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('dashboard')
    else:
        form = VolunteerEntryForm()
    return render(request, 'hourTracker/form.html', {'form': form})

@login_required
def edit_entry(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        # Admins can edit any entry
        entry = get_object_or_404(VolunteerEntry, pk=pk)
    else:
        # Regular users can only edit their own entries
        entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = VolunteerEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VolunteerEntryForm(instance=entry)

    # Pass username to the template for display
    return render(request, 'hourTracker/form.html', {
        'form': form,
        'username': entry.user.email,  # 👈 add this
    })



@login_required
def delete_entry(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        entry = get_object_or_404(VolunteerEntry, pk=pk)
    else:
        entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)
    
    entry.delete()
    return redirect('dashboard')


from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib import messages
# from .forms import RegisterForm

def register_view(request):
    User = get_user_model()  # ✅ ensures we are using CustomUser
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # creates a CustomUser instance
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'hourTracker/register.html', {'form': form})

