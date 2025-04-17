import os
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

employee_limit = os.getenv('EMPLOYEE_LIMIT', 10)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class IndividualUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    terms_and_conditions = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class StudentUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    student_id = models.FileField(upload_to='student_ids/', null=True, blank=True)
    student_id_text = models.CharField(max_length=100, null=True, blank=True)
    student_organisation_name = models.CharField(max_length=255)
    terms_and_conditions = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    terms_and_conditions = models.BooleanField(default=False)
    employee_limit = models.PositiveIntegerField(default=employee_limit)

    def employee_count(self):
        return self.employees.count()

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.name}"


class Query(models.Model):
    query_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='queries')
    query = models.TextField()
    corrected_query = models.TextField(null=True, blank=True)
    documents = models.JSONField(default=list)  # Store list of document references
    summary = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.query[:50]}..."

class SubscriptionPlan(models.Model):
    plan_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    validity = models.PositiveIntegerField()
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class UserSubscriptionManagement(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    subscribed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.is_active


# Stripe Subscription Models
class Subscription(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='stripe_subscription')
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    plan_id = models.CharField(max_length=50)  # 'free', 'pro', 'premium' or the actual plan ID
    status = models.CharField(max_length=50, default='inactive')  # 'active', 'canceled', 'past_due'
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan_id} - {self.status}"
    
    @property
    def is_active(self):
        return self.status == 'active'

    def can_perform_search(self):
        """Check if user can perform a search based on their subscription plan"""
        # Paid plans can always search
        if self.status == 'active' and self.plan_id != 'free':
            return True, None

        # Free plan has limited searches
        if self.plan_id == 'free':
            current_count = UserSearchCount.get_search_count(self.user)
            if current_count < 3:  # Free plan: 3 searches limit
                return True, None
            else:
                return False, "You've reached your daily search limit of 3 searches. Please upgrade your plan."

        # Inactive subscription
        return False, "Your subscription is not active. Please subscribe to continue searching."

    def can_export_summaries(self):
        """Check if user can export/copy summaries based on their subscription plan"""
        if self.status != 'active':
            return False
            
        # These plans have export capability
        exportable_plans = ['monthly', 'annual', 'student_monthly', 'student_annual']
        return self.plan_id in exportable_plans


class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    stripe_invoice_id = models.CharField(max_length=100)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)  # 'succeeded', 'pending', 'failed'
    description = models.CharField(max_length=255)
    receipt_url = models.URLField(blank=True, null=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"


class UserSearchCount(models.Model):
    """Tracks user search usage for limiting free tier users"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='search_counts')
    date = models.DateField(default=timezone.now)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    @classmethod
    def increment_search_count(cls, user):
        """Increment the search count for a user for the current day"""
        today = timezone.now().date()
        count_obj, created = cls.objects.get_or_create(
            user=user,
            date=today,
            defaults={'count': 1}
        )
        
        if not created:
            count_obj.count += 1
            count_obj.save()
            
        return count_obj.count

    @classmethod
    def get_search_count(cls, user):
        """Get the search count for a user for the current day"""
        today = timezone.now().date()
        try:
            count_obj = cls.objects.get(user=user, date=today)
            return count_obj.count
        except cls.DoesNotExist:
            return 0

