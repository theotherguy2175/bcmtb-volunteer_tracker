from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import CustomUser, VolunteerEntry, RewardSettings

# --- HELPERS ---
def get_year_total(user, year):
    """Calculates total hours for a user in a specific year."""
    return VolunteerEntry.objects.filter(
        user=user, 
        date__year=year
    ).aggregate(Sum('hours'))['hours__sum'] or 0

# --- SIGNALS ---

@receiver(post_save, sender=VolunteerEntry)
def check_milestone(sender, instance, **kwargs):
    user = instance.user
    current_year = timezone.now().year
    
    settingsRewares = RewardSettings.objects.first()
    if not settingsRewares or not settingsRewares.enable_notifications:
        return 

    total = get_year_total(user, current_year)
    already_sent_this_year = (user.last_milestone_sent_year == current_year)
    
    # Trigger if they hit the goal and we haven't emailed them this year
    if total >= settingsRewares.hour_requirement and not already_sent_this_year:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
        
        send_mail(
            f'Milestone Reached: {settingsRewares.hour_requirement} Hours',
            f'Volunteer {user.first_name} {user.last_name} reached {total} hours in {current_year}.',
            from_email,
            [settingsRewares.notification_email],
            fail_silently=False,
        )

        user.last_milestone_sent_year = current_year
        user.save(update_fields=['last_milestone_sent_year'])
        print(f"!!! SUCCESS: Email sent for {user.email} ({total}h in {current_year})")
    else:
        print(f"DEBUG: Save trigger. {user.email} total: {total}. Sent this year: {already_sent_this_year}")


@receiver(post_delete, sender=VolunteerEntry)
def reset_milestone_on_delete(sender, instance, **kwargs):
    user = instance.user
    current_year = timezone.now().year
    
    settingsRewares = RewardSettings.objects.first()
    if not settingsRewares:
        return

    total = get_year_total(user, current_year)
    
    # If they drop below the goal, "re-open" the chance to get the email
    if total < settingsRewares.hour_requirement and user.last_milestone_sent_year == current_year:
        user.last_milestone_sent_year = 0
        user.save(update_fields=['last_milestone_sent_year'])
        print(f"DEBUG: Deletion trigger. {user.email} dropped to {total}h. Milestone reset to 0.")