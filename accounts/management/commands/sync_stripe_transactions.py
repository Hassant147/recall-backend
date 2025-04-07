from django.core.management.base import BaseCommand
from accounts.stripe_webhooks import sync_missing_transactions

class Command(BaseCommand):
    help = 'Syncs missing transactions from Stripe'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting to sync transactions from Stripe..."))
        
        # Call the sync utility
        sync_missing_transactions()
        
        self.stdout.write(self.style.SUCCESS("Transaction sync completed!")) 