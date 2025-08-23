from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from .utils import to_lowercase

# Create your models here.


class User(AbstractBaseUser):
    name = models.CharField(max_length=255,validators=[to_lowercase])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    gender  = models.CharField(max_length=7, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    is_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6)
    otp_limit = models.IntegerField(default=5)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email
    



class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    kyc_document = models.FileField(upload_to='kyc_docs/', blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=15)
    phone = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='seller_profiles/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_orders = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.business_name
