release: python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && python manage.py create_superuser_if_none
web: gunicorn ecommerce_project.wsgi:application --bind 0.0.0.0:$PORT
