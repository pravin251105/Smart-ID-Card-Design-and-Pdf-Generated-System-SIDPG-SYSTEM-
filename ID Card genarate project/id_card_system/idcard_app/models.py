from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("student", "Student"),
        ("staff", "Staff"),
        ("employee", "Employee"),
        ("user", "User"),
    )

    RESIDENCE_STATUS_CHOICES = (
        ("resident", "Resident"),
        ("non-resident", "Non-Resident"),
        ("temporary", "Temporary"),
        ("international", "International"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    # EXTRA USER DETAILS
    age = models.IntegerField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    roll_no = models.CharField(max_length=50, null=True, blank=True)
    photo = models.ImageField(upload_to="photos/", null=True, blank=True)
    residence_status = models.CharField(max_length=20, choices=RESIDENCE_STATUS_CHOICES, null=True, blank=True, default="resident")
    
    # NEW FIELDS FOR ID CARD
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_mobile = models.CharField(max_length=15, null=True, blank=True)
    valid_upto = models.DateField(null=True, blank=True)
    signature = models.ImageField(upload_to="signatures/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class DashboardSettings(models.Model):
    show_age = models.BooleanField(default=True)
    show_department = models.BooleanField(default=True)
    show_photo = models.BooleanField(default=True)
    show_phone = models.BooleanField(default=True)
    show_blood_group = models.BooleanField(default=True)
    show_roll_no = models.BooleanField(default=True)
    show_date_of_birth = models.BooleanField(default=True)
    show_emergency_mobile = models.BooleanField(default=True)
    show_valid_upto = models.BooleanField(default=True)
    show_signature = models.BooleanField(default=True)
    show_address = models.BooleanField(default=True)
    show_role = models.BooleanField(default=True)
    show_residence_status = models.BooleanField(default=True)

    def __str__(self):
        return "User Dashboard Settings"


class TemplateDesign(models.Model):
    """Stores a saved ID card design (front/back JSON from the designer)."""
    name = models.CharField(max_length=200)
    json_data = models.TextField(help_text='Fabric.js JSON for both sides')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.id})"
class IDTemplate(models.Model):
    name = models.CharField(max_length=200)
    template_json = models.JSONField()   # stores full canvas data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SavedTemplate(models.Model):
    name = models.CharField(max_length=255)
    json = models.JSONField()   # stores full template JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

