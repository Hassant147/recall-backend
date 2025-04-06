from django.core.management.base import BaseCommand
from accounts.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Updates subscription plans with new pricing structure'

    def handle(self, *args, **kwargs):
        # Define the new plans
        plans = [
            {
                'plan_id': 'free',
                'name': 'Free Plan',
                'price': 0,  # Price in cents
                'validity': 0,  # Unlimited
                'is_popular': False,
                'stripe_price_id': None,
                'features': ['3 free searches']
            },
            {
                'plan_id': 'daily',
                'name': 'Daily Plan',
                'price': 149,  # £1.49 in cents
                'validity': 1,  # 1 day
                'is_popular': False,
                'stripe_price_id': None,  # Update with your Stripe price ID
                'features': ['Unlimited searches']
            },
            {
                'plan_id': 'monthly',
                'name': 'Monthly Plan',
                'price': 1499,  # £14.99 in cents
                'validity': 30,  # 30 days
                'is_popular': True,
                'stripe_price_id': None,  # Update with your Stripe price ID
                'features': ['Unlimited searches', 'Ability to copy summaries and export', 'Cancel any time']
            },
            {
                'plan_id': 'annual',
                'name': 'Annual Plan',
                'price': 14999,  # £149.99 in cents
                'validity': 365,  # 365 days
                'is_popular': False,
                'stripe_price_id': None,  # Update with your Stripe price ID
                'features': ['Unlimited searches', 'Ability to copy summaries and export', 
                             'Cancel any time, with partial refund available for any unused months']
            },
            {
                'plan_id': 'student_monthly',
                'name': 'Student Monthly Plan',
                'price': 799,  # £7.99 in cents
                'validity': 30,  # 30 days
                'is_popular': False,
                'stripe_price_id': None,  # Update with your Stripe price ID
                'features': ['Unlimited searches', 'Ability to copy summaries and export', 'Cancel any time']
            },
            {
                'plan_id': 'student_annual',
                'name': 'Student Annual Plan',
                'price': 7999,  # £79.99 in cents
                'validity': 365,  # 365 days
                'is_popular': False,
                'stripe_price_id': None,  # Update with your Stripe price ID
                'features': ['Unlimited searches', 'Ability to copy summaries and export', 
                             'Cancel any time, with partial refund available for any unused months']
            }
        ]

        # Update or create each plan
        for plan_data in plans:
            features = plan_data.pop('features')  # Remove features from plan_data
            
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_id=plan_data['plan_id'],
                defaults=plan_data
            )
            
            # Store features in a JSON field if your model supports it
            # Or implement a separate model for features if needed
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} plan: {plan.name}')) 