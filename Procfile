web: python manage.py migrate && gunicorn BuynSell.wsgi:application --bind 0.0.0.0:10000 --workers 2 --timeout 60
release: python manage.py migrate && python manage.py collectstatic --noinput
