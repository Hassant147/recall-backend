from django.core.management.base import BaseCommand, CommandError
import stripe
from django.conf import settings
from accounts.models import CustomUser, Subscription, Transaction
from accounts.stripe_webhooks import create_transaction_from_invoice

class Command(BaseCommand):
    help = 'Syncs transactions for a specific customer from Stripe'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='User email to sync transactions for')
        parser.add_argument('--customer-id', type=str, help='Stripe customer ID to sync transactions for')

    def handle(self, *args, **kwargs):
        email = kwargs.get('email')
        customer_id = kwargs.get('customer_id')
        
        if not email and not customer_id:
            raise CommandError('You must provide either --email or --customer-id')
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get the subscription based on provided criteria
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                self.stdout.write(f"Found user: {user.email}")
                
                subscription = Subscription.objects.filter(user=user).first()
                if not subscription:
                    raise CommandError(f"No subscription found for user: {email}")
                    
                customer_id = subscription.stripe_customer_id
                if not customer_id:
                    raise CommandError(f"User {email} has no Stripe customer ID")
                
            except CustomUser.DoesNotExist:
                raise CommandError(f"User with email {email} not found")
        
        # Fetch and sync invoices
        try:
            self.stdout.write(f"Fetching invoices for Stripe customer: {customer_id}")
            
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=100
            )
            
            self.stdout.write(f"Found {len(invoices.data)} invoices")
            synced_count = 0
            
            # Find the user for this customer ID if email wasn't provided
            if not email:
                subscription = Subscription.objects.filter(stripe_customer_id=customer_id).first()
                if not subscription:
                    raise CommandError(f"No subscription found for Stripe customer: {customer_id}")
                user = subscription.user
            
            # Process each invoice
            for invoice in invoices.data:
                # Skip if not paid
                if invoice.status != 'paid':
                    self.stdout.write(f"Skipping invoice {invoice.id} (status: {invoice.status})")
                    continue
                
                # Check if transaction already exists
                existing = Transaction.objects.filter(stripe_invoice_id=invoice.id).exists()
                if existing:
                    self.stdout.write(f"Transaction for invoice {invoice.id} already exists, skipping")
                    continue
                
                # Create transaction
                try:
                    create_transaction_from_invoice(user, invoice)
                    synced_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Created transaction for invoice {invoice.id}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating transaction for invoice {invoice.id}: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} transactions for customer {customer_id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error syncing transactions: {str(e)}")) 