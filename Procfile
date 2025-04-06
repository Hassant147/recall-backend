web: python manage.py migrate && \
    python manage.py update_plans && \
    python manage.py update_stripe_prices && \
    python manage.py collectstatic --noinput && \
    echo "✅ Migrations and setup completed successfully!" && \
    gunicorn Search.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --log-level info 