from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from accounts.models import (
    CustomUser, IndividualUser, StudentUser, Company, Employee, 
    Query, SubscriptionPlan, Subscription, Transaction, UserSearchCount
)
from accounts.stripe_webhooks import sync_missing_transactions

# Custom User Admin with fields specific to our implementation
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_staff', 'is_company', 'is_student', 'is_active')
    list_filter = ('is_staff', 'is_company', 'is_student', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_company', 'is_student', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_company', 'is_student'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

class IndividualUserAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'first_name', 'last_name', 'phone_number', 'date_joined')
    search_fields = ('user__email', 'first_name', 'last_name', 'phone_number')
    date_hierarchy = 'date_joined'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

class StudentUserAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'first_name', 'last_name', 'student_id', 'student_organisation_name', 'date_joined', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__email', 'first_name', 'last_name', 'student_id', 'student_organisation_name')
    date_hierarchy = 'date_joined'
    actions = ['approve_students', 'disapprove_students']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def approve_students(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} student(s) have been approved.')
    approve_students.short_description = "Approve selected students"
    
    def disapprove_students(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} student(s) have been disapproved.')
    disapprove_students.short_description = "Disapprove selected students"

class CompanyAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'name', 'website', 'phone_number', 'employee_count')
    search_fields = ('user__email', 'name', 'website', 'phone_number')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'first_name', 'last_name', 'company_name', 'phone_number')
    list_filter = ('company',)
    search_fields = ('user__email', 'first_name', 'last_name', 'company__name')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def company_name(self, obj):
        return obj.company.name
    company_name.short_description = 'Company'
    company_name.admin_order_field = 'company__name'

class QueryAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'query', 'timestamp')
    search_fields = ('user__email', 'query', 'response_text', 'summary')
    date_hierarchy = 'timestamp'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_id', 'name', 'price', 'validity', 'is_popular')
    search_fields = ('plan_id', 'name')
    list_filter = ('is_popular',)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'plan_id', 'status', 'current_period_start', 'current_period_end')
    list_filter = ('plan_id', 'status')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id')
    actions = ['sync_stripe_transactions']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def sync_stripe_transactions(self, request, queryset):
        try:
            # Call the sync function (this will sync all transactions, not just for the selected subscriptions)
            sync_missing_transactions()
            self.message_user(
                request, 
                "Successfully synchronized transactions from Stripe.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Error synchronizing transactions: {str(e)}", 
                messages.ERROR
            )
    sync_stripe_transactions.short_description = "Sync missing transactions from Stripe"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'amount', 'status', 'description', 'date')
    list_filter = ('status',)
    search_fields = ('user__email', 'stripe_invoice_id', 'stripe_payment_intent_id', 'description')
    date_hierarchy = 'date'
    actions = ['sync_stripe_transactions']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def sync_stripe_transactions(self, request, queryset):
        try:
            # Call the sync function (this will sync all transactions, not just for the selected items)
            sync_missing_transactions()
            self.message_user(
                request, 
                "Successfully synchronized transactions from Stripe.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Error synchronizing transactions: {str(e)}", 
                messages.ERROR
            )
    sync_stripe_transactions.short_description = "Sync missing transactions from Stripe"

class UserSearchCountAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'date', 'count')
    date_hierarchy = 'date'
    search_fields = ('user__email',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

# Create a proxy model for Stripe operations admin panel
class StripeAdmin(Transaction):
    class Meta:
        proxy = True
        verbose_name = 'Stripe Operations'
        verbose_name_plural = 'Stripe Operations'

class StripeAdminPanel(admin.ModelAdmin):
    """
    A dedicated admin panel for Stripe operations.
    This doesn't manage any specific model but provides a central place for Stripe admin actions.
    """
    # We don't want to show any records since this is just for actions
    def get_queryset(self, request):
        return Transaction.objects.none()
    
    # Add custom actions to the dropdown
    actions = ['sync_stripe_transactions', 'update_stripe_plans']
    
    def sync_stripe_transactions(self, request, queryset):
        try:
            # Call the sync function
            sync_missing_transactions()
            self.message_user(
                request, 
                "Successfully synchronized transactions from Stripe.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Error synchronizing transactions: {str(e)}", 
                messages.ERROR
            )
    sync_stripe_transactions.short_description = "Sync missing transactions from Stripe"
    
    def update_stripe_plans(self, request, queryset):
        """Runs the management command to update stripe plans and prices"""
        try:
            from django.core.management import call_command
            call_command('update_stripe_prices')
            self.message_user(
                request, 
                "Successfully updated Stripe plans and prices.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Error updating Stripe plans: {str(e)}", 
                messages.ERROR
            )
    update_stripe_plans.short_description = "Update Stripe plans and prices"
    
    # Ensure the actions appear on the changelist even with no records
    def changelist_view(self, request, extra_context=None):
        # Get the actions from self.actions
        actions = self.get_actions(request)
        # Add them to the empty changelist via extra_context
        if not extra_context:
            extra_context = {}
        extra_context['title'] = "Stripe Admin Operations"
        extra_context['has_add_permission'] = False  # Don't show the 'Add' button
        return super().changelist_view(request, extra_context=extra_context)

    # No add, change or delete permissions since we don't manage records
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True  # Need this for the changelist to show
    
    def has_delete_permission(self, request, obj=None):
        return False

# Register all models with their respective admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(IndividualUser, IndividualUserAdmin)
admin.site.register(StudentUser, StudentUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(UserSearchCount, UserSearchCountAdmin)

# Register the Stripe Admin Panel
admin.site.register(StripeAdmin, StripeAdminPanel)

