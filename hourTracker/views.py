from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VolunteerEntry
from .forms import VolunteerEntryForm, CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test


@login_required
def dashboard(request):
    current_year = timezone.now().year
    selected_year = request.GET.get('year', str(current_year))
    
    # 1. Base queryset for this user
    entries = VolunteerEntry.objects.filter(user=request.user)
    
    # 2. Get unique years for the dropdown (always ordered newest first)
    years_available = entries.dates('date', 'year', order='DESC')
    year_list = [d.year for d in years_available]
    
    # Ensure current year is in the list even if no entries exist yet
    if current_year not in year_list:
        year_list.insert(0, current_year)

    # 3. Apply year filtering ONLY if not "all"
    if selected_year != 'all':
        try:
            entries = entries.filter(date__year=int(selected_year))
        except (ValueError, TypeError):
            # Fallback to current year if something goes wrong
            entries = entries.filter(date__year=current_year)
            selected_year = str(current_year)

    # 4. Final ordering and calculation
    entries = entries.order_by('-date', '-pk')
    total_hours = entries.aggregate(total=Sum('hours'))['total'] or 0

    context = {
        'entries': entries,
        'total_hours': total_hours,
        'selected_year': selected_year, # This could be an int or the string 'all'
        'year_list': year_list,
    }
    return render(request, 'hourTracker/dashboard.html', context)
@login_required
def admin_dashboard(request):
    current_year = timezone.now().year
    selected_year = request.GET.get('year', str(current_year))
    
    # 1. Determine the Base Queryset
    if request.user.is_staff:
        # Admin sees everything
        base_entries = VolunteerEntry.objects.all()
    else:
        # Regular user sees only their own
        base_entries = VolunteerEntry.objects.filter(user=request.user)
    
    # 2. Get unique years for the dropdown based on the base queryset
    years_available = base_entries.dates('date', 'year', order='DESC')
    year_list = [d.year for d in years_available]
    
    if current_year not in year_list:
        year_list.insert(0, current_year)

    # 3. Apply Year Filtering to a working queryset
    filtered_entries = base_entries
    if selected_year != 'all':
        try:
            filtered_entries = filtered_entries.filter(date__year=int(selected_year))
        except (ValueError, TypeError):
            filtered_entries = filtered_entries.filter(date__year=current_year)
            selected_year = str(current_year)

    # 4. Final ordering and calculation
    # Note: total_hours will respect the selected year and the user permissions
    filtered_entries = filtered_entries.order_by('-date', '-pk')
    total_hours = filtered_entries.aggregate(total=Sum('hours'))['total'] or 0

    context = {
        'entries': filtered_entries,
        'total_hours': total_hours,
        'selected_year': selected_year,
        'year_list': year_list,
        'is_admin': request.user.is_staff, # Useful for template logic
    }
    
    return render(request, 'hourTracker/admin_dashboard.html', context)

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
        form = VolunteerEntryForm(initial={'date': timezone.now().date()})
    
    # Adding the context variables here
    context = {
        'form': form,
        'form_title': 'Add Entry',
        'button_text': 'Add Entry'
    }
    return render(request, 'hourTracker/entry_form.html', context)

from django.contrib.admin.views.decorators import staff_member_required
from .forms import AdminVolunteerEntryForm

@login_required
@staff_member_required
def admin_add_entry(request):
    User = get_user_model()
    if request.method == 'POST':
        form = AdminVolunteerEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = AdminVolunteerEntryForm(initial={'date': timezone.now().date()})

    # Prepare the data for JavaScript
    users_list_json = [
        {'label': f"{u.first_name} {u.last_name}", 'value': f"{u.first_name} {u.last_name}", 'id': u.id}
        for u in User.objects.all()
    ]

    context = {
        'form': form,
        'users_list_json': users_list_json, # Use this for the script
        'form_title': 'Admin: Add Entry',
        'button_text': 'Add Entry'
    }
    return render(request, 'hourTracker/entry_form.html', context)

@login_required
def edit_entry(request, pk):
    # Security check: Staff see anything, users see only their own
    if request.user.is_staff or request.user.is_superuser:
        entry = get_object_or_404(VolunteerEntry, pk=pk)
    else:
        entry = get_object_or_404(VolunteerEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = VolunteerEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            # Redirect to the 'next' URL if it exists, otherwise back to dashboard
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
    else:
        form = VolunteerEntryForm(instance=entry)

    # Get 'next' from the GET parameters to maintain the return path
    next_url = request.GET.get('next', '')

    context = {
        'form': form,
        'vol_firstname': entry.user.first_name,
        'vol_lastname': entry.user.last_name,
        'next_url': next_url,
        'form_title': 'Edit Entry',       # The dynamic title
        'button_text': 'Edit Entry'     # The dynamic button label
    }

    if request.user.is_staff or request.user.is_superuser: #only render username if admin, no need for regular users
        context['vol_email'] = entry.user.email

    return render(request, 'hourTracker/entry_form.html', context)

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


#Export Table to CSV
import csv
from django.http import HttpResponse

from django.db.models import Q,Sum

def export_csv(request):
    search_query = request.GET.get('search', '')
    print(search_query)
    # Start with all entries
    entries = VolunteerEntry.objects.all()

    # If there is a search term, filter the results
    if search_query:
        entries = entries.filter(
            Q(user__email__icontains=search_query) | 
            Q(date__icontains=search_query) |
            Q(hours__icontains=search_query)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="filtered_hours.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Hours', 'User'])

    for entry in entries:
        writer.writerow([entry.date, entry.hours, entry.user.email])

    return response

#=======================Rewards Views========================
from django.shortcuts import render
from .models import VolunteerReward, VolunteerEntry
from django.db.models import Sum

def rewards(request):

    # Get all rewards, ordered by the hours required
    rewards = VolunteerReward.objects.all().order_by('hours_required')
    #current_year = timezone.now().year
    # Regular user sees only their entries
    entries = VolunteerEntry.objects.filter(user=request.user)
    #current year
    current_year = timezone.now().year
    #Sum all hours for the current user in the current year
    total_hours = VolunteerEntry.objects.filter(
        user=request.user,
        date__year=current_year
        ).aggregate(total=Sum('hours'))['total'] or 0  # Defaults to 0 if no entries

    context = {
        'rewards': rewards,
        'entries': entries,
        'total_hours': total_hours,
        'current_year': current_year,
    }

    print(context)

    return render(request, 'rewards.html', context)

#=======================Reports Views========================
import csv
from django.http import HttpResponse
from django.shortcuts import render
from .models import CustomUser, VolunteerEntry, VolunteerTask # Use your actual models
from django.core.exceptions import PermissionDenied

def if_staff_check(user):
    if user.is_authenticated and user.is_staff:
        return True
    # If they aren't staff, stop here and throw the 403 error
    raise PermissionDenied


@user_passes_test(if_staff_check)
def reports_page(request):
    return render(request, 'reports.html')

@user_passes_test(if_staff_check)
def export_volunteer_entries_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="volunteer_hours_report.csv"'

    writer = csv.writer(response)
    # Header row matching your VolunteerEntry fields
    writer.writerow(['User Email', 'Date', 'Hours', 'Category', 'Location'])

    # Fetch data and use 'select_related' to make the query faster
    entries = VolunteerEntry.objects.select_related('user', 'category', 'location').all()
    
    for entry in entries:
        writer.writerow([
            entry.user.email, 
            entry.date, 
            entry.hours, 
            entry.category.name if entry.category else 'N/A', 
            entry.location.name if entry.location else 'N/A'
        ])

    return response

@user_passes_test(if_staff_check)
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="volunteer_users_list.csv"'

    writer = csv.writer(response)
    # Added address headers
    writer.writerow([
        'Email', 'First Name', 'Last Name', 'Phone', 
        'Address 1', 'Address 2', 'City', 'State', 'Zip'
    ])

    users = CustomUser.objects.all()
    for user in users:
        writer.writerow([
            user.email, 
            user.first_name, 
            user.last_name, 
            user.phone_number,
            user.address_line_1,
            user.address_line_2,
            user.city,
            user.state,
            user.zip_code
        ])

    return response

@user_passes_test(if_staff_check)
def export_user_yearly_totals_csv(request):
    current_year = timezone.now().year
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_totals_{current_year}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email', 'First Name', 'Last Name', f'Total Hours ({current_year})'])

    # Annotate: This creates a virtual field called 'total_hours' on each user
    # It only sums VolunteerEntry records where the date's year matches current_year
    users = CustomUser.objects.annotate(
        total_hours=Sum(
            'volunteerentry__hours',
            filter=Q(volunteerentry__date__year=current_year)
        )
    )

    for user in users:
        # If a user has no entries, total_hours will be None. We convert that to 0.
        hours = user.total_hours if user.total_hours is not None else 0
        
        writer.writerow([
            user.email,
            user.first_name,
            user.last_name,
            hours
        ])

    return response