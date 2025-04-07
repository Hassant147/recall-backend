#!/bin/bash

# Stripe Transaction Sync Utility Script
# Usage: ./stripe_sync.sh [option] [parameters]
#
# Options:
#   sync-all              - Sync all missing transactions from Stripe
#   sync-customer <email> - Sync transactions for a specific customer by email
#   sync-id <customer_id> - Sync transactions for a specific customer by Stripe ID
#   update-plans          - Update Stripe plans and prices
#   help                  - Show this help message

# Get the project directory - assumes script is in a 'scripts' directory
PROJECT_DIR=$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")

# Change to the project directory
cd "$PROJECT_DIR"

function show_help {
    echo "Stripe Transaction Sync Utility"
    echo "==============================="
    echo ""
    echo "Usage: ./stripe_sync.sh [option] [parameters]"
    echo ""
    echo "Options:"
    echo "  sync-all              - Sync all missing transactions from Stripe"
    echo "  sync-customer <email> - Sync transactions for a specific customer by email"
    echo "  sync-id <customer_id> - Sync transactions for a specific customer by Stripe ID"
    echo "  update-plans          - Update Stripe plans and prices"
    echo "  help                  - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./stripe_sync.sh sync-all"
    echo "  ./stripe_sync.sh sync-customer user@example.com"
    echo "  ./stripe_sync.sh sync-id cus_ABC123XYZ"
    echo "  ./stripe_sync.sh update-plans"
    echo ""
}

# If no arguments provided, show help
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Process command-line arguments
case "$1" in
    sync-all)
        echo "Syncing all transactions from Stripe..."
        python manage.py sync_stripe_transactions
        ;;
    sync-customer)
        if [ -z "$2" ]; then
            echo "Error: Email address required"
            echo "Usage: ./stripe_sync.sh sync-customer <email>"
            exit 1
        fi
        echo "Syncing transactions for customer: $2"
        python manage.py sync_customer_transactions --email "$2"
        ;;
    sync-id)
        if [ -z "$2" ]; then
            echo "Error: Stripe customer ID required"
            echo "Usage: ./stripe_sync.sh sync-id <customer_id>"
            exit 1
        fi
        echo "Syncing transactions for Stripe customer ID: $2"
        python manage.py sync_customer_transactions --customer-id "$2"
        ;;
    update-plans)
        echo "Updating Stripe plans and prices..."
        python manage.py update_stripe_prices
        ;;
    help)
        show_help
        ;;
    *)
        echo "Error: Unknown option '$1'"
        show_help
        exit 1
        ;;
esac

echo "Done!" 