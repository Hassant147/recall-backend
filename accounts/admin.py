from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import (
    CustomUser, IndividualUser, StudentUser, Company, Employee, 
    Query, SubscriptionPlan, Subscription, Transaction, UserSearchCount
)

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
    list_display = ('user_email', 'first_name', 'last_name', 'student_id', 'student_organisation_name', 'date_joined')
    search_fields = ('user__email', 'first_name', 'last_name', 'student_id', 'student_organisation_name')
    date_hierarchy = 'date_joined'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

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
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'amount', 'status', 'description', 'date')
    list_filter = ('status',)
    search_fields = ('user__email', 'stripe_invoice_id', 'stripe_payment_intent_id', 'description')
    date_hierarchy = 'date'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

class UserSearchCountAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'date', 'count')
    date_hierarchy = 'date'
    search_fields = ('user__email',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

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

