import stripe
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Updates Stripe products and prices to match the subscription plans'

    def handle(self, *args, **kwargs):
        # Set up Stripe API key
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Define plan configurations
        plans = [
            {
                'plan_id': 'free',
                'name': 'Free Plan',
                'description': '3 free searches',
                'price': 0,
                'interval': None
            },
            {
                'plan_id': 'daily',
                'name': 'Daily Plan',
                'description': 'Unlimited searches for one day',
                'price': 149,  # £1.49 in pence
                'interval': 'day'
            },
            {
                'plan_id': 'monthly',
                'name': 'Monthly Plan',
                'description': 'Unlimited searches with export capability',
                'price': 1499,  # £14.99 in pence
                'interval': 'month'
            },
            {
                'plan_id': 'annual',
                'name': 'Annual Plan',
                'description': 'Unlimited searches with export capability at a discount',
                'price': 14999,  # £149.99 in pence
                'interval': 'year'
            },
            {
                'plan_id': 'student_monthly',
                'name': 'Student Monthly Plan',
                'description': 'Discounted monthly plan for students',
                'price': 799,  # £7.99 in pence
                'interval': 'month'
            },
            {
                'plan_id': 'student_annual',
                'name': 'Student Annual Plan',
                'description': 'Discounted annual plan for students',
                'price': 7999,  # £79.99 in pence
                'interval': 'year'
            }
        ]
        
        # Update or create products and prices in Stripe
        for plan in plans:
            try:
                # Skip free plan in Stripe
                if plan['plan_id'] == 'free':
                    self.stdout.write(self.style.SUCCESS(f"Skipping free plan in Stripe"))
                    continue
                
                # Create or update product
                product_data = {
                    'name': plan['name'],
                    'description': plan['description'],
                    'metadata': {
                        'plan_id': plan['plan_id']
                    }
                }
                
                # Check if product exists
                existing_products = stripe.Product.list(limit=100)
                product = next((p for p in existing_products.data if p.metadata.get('plan_id') == plan['plan_id']), None)
                
                if product:
                    # Update existing product
                    product = stripe.Product.modify(
                        product.id,
                        **product_data
                    )
                    self.stdout.write(self.style.SUCCESS(f"Updated product: {product.name}"))
                else:
                    # Create new product
                    product = stripe.Product.create(**product_data)
                    self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))
                
                # Create price for the product
                if plan['interval']:
                    price_data = {
                        'unit_amount': plan['price'],
                        'currency': 'gbp',
                        'recurring': {'interval': plan['interval']},
                        'product': product.id,
                        'metadata': {
                            'plan_id': plan['plan_id']
                        }
                    }
                    
                    # Create new price
                    price = stripe.Price.create(**price_data)
                    self.stdout.write(self.style.SUCCESS(f"Created price: {price.id} for {product.name}"))
                    
                    # Update local database
                    try:
                        subscription_plan = SubscriptionPlan.objects.get(plan_id=plan['plan_id'])
                        subscription_plan.stripe_price_id = price.id
                        subscription_plan.save()
                        self.stdout.write(self.style.SUCCESS(f"Updated local plan with Stripe price ID: {price.id}"))
                    except SubscriptionPlan.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Local plan not found: {plan['plan_id']}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating plan {plan['plan_id']}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Stripe products and prices updated successfully!")) 