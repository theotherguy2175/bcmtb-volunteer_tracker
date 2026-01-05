from django.contrib.auth import get_user_model  # <--- Import this
from django.core.mail import send_mail

# Get the correct User class (CustomUser in your case)
User = get_user_model()

def test_yearly_reminder_output():
    # Now this will use hourTracker.CustomUser correctly
    emails = User.objects.values_list('email', flat=True)
    
    print("--- STARTING EMAIL DRY RUN ---")
    for email in emails:
        if email:
            print(f"SIMULATED: Sending email to -> {email}")
    print(f"--- COMPLETED: Processed {len(emails)} users ---")

from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()

def send_yearly_reminder():
    # Only target your specific email address for this test
    target_email = "codycasteel2178.5@gmail.com"
    
    # Check if a user with this email exists
    users = User.objects.filter(email=target_email)
    
    if not users.exists():
        print(f"Error: No user found with email {target_email}")
        return

    print(f"--- STARTING LIVE EMAIL TEST FOR {target_email} ---")
    
    for user in users:
        send_mail(
            'Submit Your Hours',
            f'Hi {user.first_name or user.username}, please submit your hours!',
            'cody.casteel@browncountymtb.org', # Ensure this is a valid sender for your SMTP provider
            [user.email],
            fail_silently=False,
        )
        print(f"SUCCESS: Email sent to {user.email}")

    print("--- COMPLETED TEST ---")

#     export POSTGRES_HOST=10.0.10.102
# export MODE=dev
# export SSL_CERT_FILE=/opt/homebrew/etc/ca-certificates/cert.pem