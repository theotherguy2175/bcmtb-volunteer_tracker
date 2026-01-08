from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin): #blank=True makes it optional
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30,)
    last_name = models.CharField(max_length=30,)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '1231231234'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True) # validators should be a list

    address_line_1 = models.CharField(max_length=255, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=20, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "address_line_1", "city", "state", "zip_code"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email



class VolunteerTask(models.Model): #Custom Tasks in Admin Panel
    name = models.CharField(max_length=100, unique=True)
    verbose_name = "Volunteer Task Category"
    verbose_name_plural = "Vounteer Task Categories"

    def __str__(self):
        return self.name
    
class VolunteerLocation(models.Model): #Custom Locations in Admin Panel
    name = models.CharField(max_length=100, unique=True)
    verbose_name = "Volunteer Location"
    verbose_name_plural = "Volunteer Locations"

    def __str__(self):
        return self.name

class VolunteerEntry(models.Model): #Add everything together in one model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(VolunteerTask, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(VolunteerLocation, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.date} ({self.hours}h)"

class VolunteerReward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='reward-images/')
    hours_required = models.IntegerField(default=0) # To know when to show it

    def __str__(self):
        return self.name
    
