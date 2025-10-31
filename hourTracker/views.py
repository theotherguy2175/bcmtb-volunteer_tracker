from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VolunteerEntry
from .forms import VolunteerEntryForm

@login_required
def dashboard(request):
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
    entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = VolunteerEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = VolunteerEntryForm(instance=entry)
    return render(request, 'hourTracker/form.html', {'form': form})

@login_required
def delete_entry(request, pk):
    entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)
    entry.delete()
    return redirect('dashboard')
