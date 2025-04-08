from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def send_template_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Send an email using an HTML template.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        html_message = render_to_string(template_name, context)
        
        # Send the email
        send_mail(
            subject=subject,
            message='',  # Plain text version - empty as we're using HTML
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Email sent to {', '.join(recipient_list)} using template {template_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_employee_registration_email(employee, company):
    """
    Send notification to company admin when a new employee registers.
    """
    context = {
        'company_name': company.name,
        'employee_name': f"{employee.first_name} {employee.last_name}",
        'employee_email': employee.user.email,
        'employee_position': employee.position,
        'registration_date': timezone.now().strftime('%B %d, %Y'),
        'dashboard_url': f"{settings.FRONTEND_URL}/company/employees"
    }
    
    return send_template_email(
        subject=f"New Employee Registration: {employee.first_name} {employee.last_name}",
        template_name='email/employee_registered.html',
        context=context,
        recipient_list=[company.user.email]
    )

def send_subscription_invoice_email(user, invoice, plan_name):
    """
    Send invoice email when a subscription is created or renewed.
    """
    # Get user's name based on user type
    user_name = user.email.split('@')[0]  # Default fallback
    try:
        from .models import IndividualUser, Company
        individual = IndividualUser.objects.filter(user=user).first()
        if individual:
            user_name = f"{individual.first_name} {individual.last_name}"
        else:
            company = Company.objects.filter(user=user).first()
            if company:
                user_name = company.name
    except Exception:
        pass
    
    context = {
        'user_name': user_name,
        'invoice_id': invoice['id'],
        'invoice_date': datetime.fromtimestamp(invoice['created']).strftime('%B %d, %Y'),
        'plan_name': plan_name,
        'amount': "{:.2f}".format(invoice['amount_paid'] / 100),  # Convert cents to dollars
        'period_start': datetime.fromtimestamp(invoice['period_start']).strftime('%B %d, %Y'),
        'period_end': datetime.fromtimestamp(invoice['period_end']).strftime('%B %d, %Y'),
        'status': invoice['status'],
        'next_billing_date': datetime.fromtimestamp(invoice['period_end']).strftime('%B %d, %Y'),
        'receipt_url': invoice.get('hosted_invoice_url', f"{settings.FRONTEND_URL}/dashboard"),
        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
    }
    
    return send_template_email(
        subject=f"Your Recall Subscription Invoice",
        template_name='email/subscription_invoice.html',
        context=context,
        recipient_list=[user.email]
    )

def send_subscription_renewed_email(user, invoice, plan_name):
    """
    Send notification when a subscription is automatically renewed.
    """
    # Get user's name based on user type
    user_name = user.email.split('@')[0]  # Default fallback
    try:
        from .models import IndividualUser, Company
        individual = IndividualUser.objects.filter(user=user).first()
        if individual:
            user_name = f"{individual.first_name} {individual.last_name}"
        else:
            company = Company.objects.filter(user=user).first()
            if company:
                user_name = company.name
    except Exception:
        pass
    
    context = {
        'user_name': user_name,
        'plan_name': plan_name,
        'amount': "{:.2f}".format(invoice['amount_paid'] / 100),  # Convert cents to dollars
        'billing_date': datetime.fromtimestamp(invoice['created']).strftime('%B %d, %Y'),
        'next_billing_date': datetime.fromtimestamp(invoice['period_end']).strftime('%B %d, %Y'),
        'receipt_url': invoice.get('hosted_invoice_url', f"{settings.FRONTEND_URL}/dashboard"),
        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard"
    }
    
    return send_template_email(
        subject=f"Your Recall Subscription Has Been Renewed",
        template_name='email/subscription_renewed.html',
        context=context,
        recipient_list=[user.email]
    )

def send_subscription_cancelled_email(user, subscription, plan_name):
    """
    Send notification when a subscription is cancelled.
    """
    # Get user's name based on user type
    user_name = user.email.split('@')[0]  # Default fallback
    try:
        from .models import IndividualUser, Company
        individual = IndividualUser.objects.filter(user=user).first()
        if individual:
            user_name = f"{individual.first_name} {individual.last_name}"
        else:
            company = Company.objects.filter(user=user).first()
            if company:
                user_name = company.name
    except Exception:
        pass
    
    access_until = subscription.current_period_end.strftime('%B %d, %Y') if subscription.current_period_end else "immediately"
    
    context = {
        'user_name': user_name,
        'plan_name': plan_name,
        'cancellation_date': timezone.now().strftime('%B %d, %Y'),
        'access_until': access_until,
        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
        'resubscribe_url': f"{settings.FRONTEND_URL}/plans"
    }
    
    return send_template_email(
        subject=f"Your Recall Subscription Has Been Cancelled",
        template_name='email/subscription_cancelled.html',
        context=context,
        recipient_list=[user.email]
    )

def send_welcome_email(user, user_type='individual'):
    """
    Send welcome email to new users upon registration completion.
    
    Parameters:
    - user: The CustomUser instance
    - user_type: 'individual', 'company', 'student', or 'employee'
    """
    # Get user's name based on user type
    user_name = user.email.split('@')[0]  # Default fallback
    company_name = None
    
    try:
        from .models import IndividualUser, Company, StudentUser, Employee, Subscription
        
        if user_type == 'company':
            company = Company.objects.filter(user=user).first()
            if company:
                user_name = company.name
        elif user_type == 'individual':
            individual = IndividualUser.objects.filter(user=user).first()
            if individual:
                user_name = f"{individual.first_name} {individual.last_name}"
        elif user_type == 'student':
            student = StudentUser.objects.filter(user=user).first()
            if student:
                user_name = f"{student.first_name} {student.last_name}"
        elif user_type == 'employee':
            employee = Employee.objects.filter(user=user).first()
            if employee:
                user_name = f"{employee.first_name} {employee.last_name}"
                if employee.company:
                    company_name = employee.company.name
    except Exception as e:
        logger.error(f"Error getting user name for welcome email: {str(e)}")
    
    # Get subscription plan information
    plan_id = 'free'  # Default
    plan_name = 'Free Plan'
    
    try:
        # For employees, get their company's subscription
        if user_type == 'employee':
            employee = Employee.objects.filter(user=user).first()
            if employee and employee.company:
                subscription = Subscription.objects.filter(user=employee.company.user).first()
            else:
                subscription = None
        else:
            subscription = Subscription.objects.filter(user=user).first()
            
        if subscription and subscription.plan_id:
            plan_id = subscription.plan_id
            # Try to get a better plan name
            from .models import SubscriptionPlan
            plan = SubscriptionPlan.objects.filter(plan_id=plan_id).first()
            if plan and plan.name:
                plan_name = plan.name
            else:
                # Fallback to a formatted version of the plan ID
                plan_name = plan_id.replace('_', ' ').title() + ' Plan'
    except Exception as e:
        logger.error(f"Error getting subscription plan for welcome email: {str(e)}")
    
    context = {
        'user_name': user_name,
        'user_type': user_type,
        'plan_id': plan_id,
        'plan_name': plan_name,
        'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
        'plans_url': f"{settings.FRONTEND_URL}/plans"
    }
    
    # Add company name for employees
    if company_name:
        context['company_name'] = company_name
    
    return send_template_email(
        subject=f"Welcome to Recall",
        template_name='email/welcome_user.html',
        context=context,
        recipient_list=[user.email]
    )

def send_otp_email(email, otp_code, action_type='registration', expiry_minutes=5, user_name=None):
    """
    Send a professionally-designed OTP email.
    
    Parameters:
    - email: The recipient's email address
    - otp_code: The OTP code to send
    - action_type: What the OTP is for (e.g., 'registration', 'password reset')
    - expiry_minutes: How many minutes until the OTP expires
    - user_name: Optional user name for personalization
    """
    site_name = "Recall"
    
    context = {
        'otp_code': otp_code,
        'action_type': action_type,
        'expiry_minutes': expiry_minutes,
        'site_name': site_name,
        'action_url': f"{settings.FRONTEND_URL}/login",
        'user_name': user_name
    }
    
    subject_prefix = "Verification Code"
    if action_type.lower() == 'password reset':
        subject_prefix = "Password Reset Code"
    
    return send_template_email(
        subject=f"{subject_prefix} for {site_name}",
        template_name='email/otp_code.html',
        context=context,
        recipient_list=[email]
    )

def send_employee_invitation_email(email, company_name, registration_url):
    """
    Send invitation email to potential employee.
    """
    context = {
        'company_name': company_name,
        'registration_url': registration_url
    }
    
    try:
        html_message = render_to_string('email/employee_invitation.html', context)
        
        # Send the email with proper content type
        send_mail(
            subject=f"Invitation to Join {company_name} on Recall",
            message='',  # Empty plain text version
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Employee invitation email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send employee invitation email: {str(e)}")
        return False 