#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting deployment process..."

# Run database migrations
echo "⏳ Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ Error: Database migrations failed. Exiting."
    exit 1
fi
echo "✅ Database migrations completed successfully."

# Update subscription plans
echo "⏳ Updating subscription plans..."
python manage.py update_plans
if [ $? -ne 0 ]; then
    echo "❌ Error: Plan update failed. Exiting."
    exit 1
fi
echo "✅ Subscription plans updated successfully."

# Update Stripe prices
echo "⏳ Updating Stripe prices..."
python manage.py update_stripe_prices
if [ $? -ne 0 ]; then
    echo "⚠️ Warning: Stripe price update failed, but continuing deployment."
fi
echo "✅ Stripe prices updated successfully."

# Collect static files
echo "⏳ Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "❌ Error: Static file collection failed. Exiting."
    exit 1
fi
echo "✅ Static files collected successfully."

# Start the application server
echo "🚀 Starting Gunicorn server..."
exec gunicorn Search.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --log-level info 